from sqlalchemy import select, delete
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException


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
                                        )
                                        .where(Cliente.legajo == legajo))
        cliente=db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return ClienteDetalleOut.model_validate(cliente)
    
    #Actualizo todo lo relacionado al cliente.
    @staticmethod
    def update_detalle_cliente(db: Session, legajo: int, data: ClienteDetalleUpdate) -> ClienteDetalleOut:
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
        
        # 2) Actualizar persona
        if data.persona is not None:
            persona_data = data.persona.model_dump(exclude_unset=True)
            if cliente.persona is None:
                # Crear una nueva persona ligada al cliente
                persona = Persona(**persona_data)
                db.add(persona)
                cliente.persona = persona
            else:
                for field, value in persona_data.items():
                    setattr(cliente.persona, field, value)
            
        # helper genérico para colecciones 1–N
        def sync_collection(existing_list, incoming_list, id_attr: str, model_cls):
            existing_by_id = {
                getattr(obj, id_attr): obj
                for obj in existing_list
                if getattr(obj, id_attr) is not None
            }

            result = []

            for item in incoming_list:
                payload = item.model_dump(exclude_unset=True)
                obj_id = payload.pop(id_attr, None)

                if obj_id is not None and obj_id in existing_by_id:
                    # UPDATE
                    obj = existing_by_id.pop(obj_id)
                    for field, value in payload.items():
                        setattr(obj, field, value)
                else:
                    # INSERT
                    # importante: forzamos legajo del cliente actual
                    obj = model_cls(**payload, legajo=cliente.legajo)
                    db.add(obj)

                result.append(obj)

            # DELETE: lo que quedó en existing_by_id no vino en el payload
            for obj in existing_by_id.values():
                db.delete(obj)

            return result
        
        # 3) Direcciones
        if data.direcciones is not None:
            cliente.direcciones = sync_collection(
                cliente.direcciones, data.direcciones, "id_direccion", DireccionCliente
            )

        # 4) Teléfonos
        if data.telefonos is not None:
            cliente.telefonos = sync_collection(
                cliente.telefonos, data.telefonos, "id_telefono", TelefonoCliente
            )

        # 5) Emails
        if data.emails is not None:
            cliente.emails = sync_collection(
                cliente.emails, data.emails, "id_mail", MailCliente
            )

        # 6) Cuentas
        if data.cuentas is not None:
            cliente.cuentas = sync_collection(
                cliente.cuentas, data.cuentas, "id_cuenta", ClienteCuenta
            )

        # 7) Días de visita: borramos todos y reinsertamos (como tu endpoint actual)
        if data.dias_semanas is not None:
            db.execute(
                delete(ClienteDiaSemana).where(
                    ClienteDiaSemana.id_cliente == cliente.legajo
                )
            )
            if data.dias_semanas:
                for item in data.dias_semanas:
                    payload = item.model_dump(exclude_unset=True)
                    db.add(
                        ClienteDiaSemana(
                            id_cliente=cliente.legajo,
                            id_dia=payload["id_dia"],
                            turno_visita=payload.get("turno_visita"),
                            orden=payload.get("orden"),
                        )
                    )

        db.commit()
        db.refresh(cliente)

        return ClienteDetalleOut.model_validate(cliente)
    
    