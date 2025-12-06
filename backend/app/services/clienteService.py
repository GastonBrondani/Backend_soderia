from sqlalchemy import select, delete
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException
from typing import Any


#Modelos utilizados
from app.models.cliente import Cliente
from app.models.persona import Persona
from app.models.direccionCliente import DireccionCliente
from app.models.telefonoCliente import TelefonoCliente
from app.models.emailCliente import MailCliente
from app.models.clienteCuenta import ClienteCuenta
from app.models.clienteDiaSemana import ClienteDiaSemana

#Schemas utilizados
from app.schemas.clienteDetalle import ClienteDetalleOut, ClienteDetalleUpdate

#Utilizados para guardar un historico del cliente
from app.services.historicoService import registrar_evento_cliente
from app.schemas.enumsHistorico import TipoEventoCodigoEnum



class ClienteService:

    #Muestro todo lo detallado al cliente.
    @staticmethod
    def get_detalle_cliente(db:Session,legajo:int) ->ClienteDetalleOut:
        stmt = (select(Cliente).options(joinedload(Cliente.persona),
                                        selectinload(Cliente.direcciones),
                                        selectinload(Cliente.telefonos),
                                        selectinload(Cliente.emails),
                                        selectinload(Cliente.productos),
                                        selectinload(Cliente.cuentas),
                                        selectinload(Cliente.dias_semanas),
                                        selectinload(Cliente.historicos),
                                        )
                                        .where(Cliente.legajo == legajo))
        cliente=db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return ClienteDetalleOut.model_validate(cliente)
    
    #Actualizo todo lo relacionado al cliente.
    @staticmethod
    def update_detalle_cliente(
        db: Session, legajo: int, data: ClienteDetalleUpdate
    ) -> ClienteDetalleOut:
        # 1) Traer cliente con todas las relaciones que vamos a tocar
        stmt = (
            select(Cliente)
            .options(
                joinedload(Cliente.persona),
                selectinload(Cliente.direcciones),
                selectinload(Cliente.telefonos),
                selectinload(Cliente.emails),
                selectinload(Cliente.cuentas),
                selectinload(Cliente.dias_semanas),
            )
            .where(Cliente.legajo == legajo)
        )
        cliente = db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Acumulador de cambios para el histórico
        cambios: dict[str, Any] = {}

        # 2) Actualizar persona (y registrar diferencias)
        if data.persona is not None:
            persona_data = data.persona.model_dump(exclude_unset=True)
            if cliente.persona is None:
                # Crear una nueva persona ligada al cliente
                persona = Persona(**persona_data)
                db.add(persona)
                cliente.persona = persona
                cambios["persona"] = {
                    "creado": persona_data
                }
            else:
                persona_cambios: dict[str, Any] = {}
                for field, value in persona_data.items():
                    old_value = getattr(cliente.persona, field)
                    if old_value != value:
                        persona_cambios[field] = {
                            "antes": old_value,
                            "despues": value,
                        }
                        setattr(cliente.persona, field, value)
                if persona_cambios:
                    cambios["persona"] = {
                        "actualizados": persona_cambios
                    }

        # helper genérico para colecciones 1–N, con registro de cambios
        def sync_collection(
            existing_list,
            incoming_list,
            id_attr: str,
            model_cls,
            key_hist: str,
        ):
            existing_by_id = {
                getattr(obj, id_attr): obj
                for obj in existing_list
                if getattr(obj, id_attr) is not None
            }

            result = []
            col_cambios = {
                "creados": [],
                "actualizados": [],
                "eliminados": [],
            }

            for item in incoming_list:
                payload = item.model_dump(exclude_unset=True)
                obj_id = payload.pop(id_attr, None)

                if obj_id is not None and obj_id in existing_by_id:
                    # UPDATE
                    obj = existing_by_id.pop(obj_id)
                    campos_cambiados = {}
                    for field, value in payload.items():
                        old_value = getattr(obj, field)
                        if old_value != value:
                            campos_cambiados[field] = {
                                "antes": old_value,
                                "despues": value,
                            }
                            setattr(obj, field, value)

                    if campos_cambiados:
                        col_cambios["actualizados"].append(
                            {
                                id_attr: obj_id,
                                "campos": campos_cambiados,
                            }
                        )

                else:
                    # INSERT
                    obj = model_cls(**payload, legajo=cliente.legajo)
                    db.add(obj)
                    col_cambios["creados"].append(
                        {
                            **payload,
                            id_attr: None,  # todavía no tiene ID
                        }
                    )

                result.append(obj)

            # DELETE: lo que quedó en existing_by_id no vino en el payload
            for obj in existing_by_id.values():
                col_cambios["eliminados"].append(
                    {
                        id_attr: getattr(obj, id_attr),
                    }
                )
                db.delete(obj)

            # Solo guardamos en cambios si hubo algo
            if (
                col_cambios["creados"]
                or col_cambios["actualizados"]
                or col_cambios["eliminados"]
            ):
                cambios[key_hist] = col_cambios

            return result

        # 3) Direcciones
        if data.direcciones is not None:
            cliente.direcciones = sync_collection(
                cliente.direcciones,
                data.direcciones,
                "id_direccion",
                DireccionCliente,
                "direcciones",
            )

        # 4) Teléfonos
        if data.telefonos is not None:
            cliente.telefonos = sync_collection(
                cliente.telefonos,
                data.telefonos,
                "id_telefono",
                TelefonoCliente,
                "telefonos",
            )

        # 5) Emails
        if data.emails is not None:
            cliente.emails = sync_collection(
                cliente.emails,
                data.emails,
                "id_mail",
                MailCliente,
                "emails",
            )

        # 6) Cuentas
        if data.cuentas is not None:
            cliente.cuentas = sync_collection(
                cliente.cuentas,
                data.cuentas,
                "id_cuenta",
                ClienteCuenta,
                "cuentas",
            )

        # 7) Días de visita: borramos todos y reinsertamos
        if data.dias_semanas is not None:
            # snapshot "antes"
            dias_antes = [
                {
                    "id_dia": ds.id_dia,
                    "turno_visita": ds.turno_visita,
                    "orden": ds.orden,
                }
                for ds in cliente.dias_semanas
            ]

            db.execute(
                delete(ClienteDiaSemana).where(
                    ClienteDiaSemana.id_cliente == cliente.legajo
                )
            )

            dias_despues = []
            if data.dias_semanas:
                for item in data.dias_semanas:
                    payload = item.model_dump(exclude_unset=True)
                    nuevo = ClienteDiaSemana(
                        id_cliente=cliente.legajo,
                        id_dia=payload["id_dia"],
                        turno_visita=payload.get("turno_visita"),
                        orden=payload.get("orden"),
                    )
                    dias_despues.append(
                        {
                            "id_dia": nuevo.id_dia,
                            "turno_visita": nuevo.turno_visita,
                            "orden": nuevo.orden,
                        }
                    )
                    db.add(nuevo)

            # registrar cambios si efectivamente cambió algo
            if dias_antes != dias_despues:
                cambios["dias_semanas"] = {
                    "antes": dias_antes,
                    "despues": dias_despues,
                }

        # Registrar histórico SOLO si hubo cambios
        if cambios:
            registrar_evento_cliente(
                db,
                legajo=cliente.legajo,
                codigo_evento=TipoEventoCodigoEnum.CLIENTE_ACTUALIZADO,
                observacion="Actualización de datos del cliente (detalle)",
                datos={"cambios": cambios},
            )

        db.commit()
        db.refresh(cliente)

        return ClienteDetalleOut.model_validate(cliente)
