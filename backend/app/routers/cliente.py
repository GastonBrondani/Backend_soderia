from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from sqlalchemy.orm import Session,selectinload
from sqlalchemy import and_
from app.core.database import get_db
from app.models.cliente import Cliente
from app.models.persona import Persona
from app.models.direccionCliente import DireccionCliente
from app.models.telefonoCliente import TelefonoCliente
from app.models.emailCliente import MailCliente
from app.models.clienteDiaSemana import ClienteDiaSemana
from app.models.diaSemana import DiaSemana
from sqlalchemy import select
from app.schemas.cliente import ClienteCreate, ClienteOut,ClienteUpdate,DiaSemanaEnum,TurnoVisitaEnum

from app.services.clienteService import ClienteService
from app.schemas.clienteDetalle import ClienteDetalleOut

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=ClienteDetalleOut, status_code=status.HTTP_201_CREATED)
def CrearCliente(payload: ClienteCreate, db: Session = Depends(get_db)):
    try:
        # 1) DNI / Persona
        dni_final = payload.persona.dni if payload.persona else payload.dni
        persona = db.get(Persona, dni_final)

        if payload.persona:
            if not persona:
                persona = Persona(**payload.persona.model_dump())
                db.add(persona)
                db.flush()
        else:
            if not persona:
                raise HTTPException(404, "La persona (dni) no existe. Enviá 'persona' para crearla.")

        # 2) Duplicado por empresa
        existe = db.query(Cliente).filter(and_(Cliente.dni == dni_final, Cliente.id_empresa == 1)).first()
        if existe:
            raise HTTPException(409, "Ya existe un cliente para ese DNI en esta empresa.")

        # 3) Crear cliente
        nuevo = Cliente(id_empresa=1, observacion=payload.observacion)
        nuevo.persona = persona
        db.add(nuevo)
        db.flush()  # tiene legajo

        # 4) Hijos anidados (con mapeos de nombres)
        if payload.direcciones:
            direcciones = []
            for d in payload.direcciones:
                direcciones.append(DireccionCliente(
                    legajo=nuevo.legajo,
                    direccion=d.direccion,
                    entre_calle1=d.entre_calle1,  # map
                    entre_calle2=d.entre_calle2,       # map
                    zona=d.zona            # map
                ))
            db.add_all(direcciones)

        if payload.telefonos:
            telefonos = []
            for t in payload.telefonos:
                telefonos.append(TelefonoCliente(
                    legajo=nuevo.legajo,
                    nro_telefono=t.nro_telefono  # map
                ))
            db.add_all(telefonos)

        if payload.emails:
            emails = []
            for e in payload.emails:
                emails.append(MailCliente(
                    legajo=nuevo.legajo,
                    mail=e.mail
                ))
            db.add_all(emails)

        # 5) Días + turno → cliente_dia_semana
        if payload.dias_visita:
            # Traigo todos los días (id_dia, nombre_dia) y armo índice por "lun/mar/..."
            dias_db = db.execute(select(DiaSemana)).scalars().all()
            idx: Dict[str, int] = {}
            for d in dias_db:
                nombre = (d.nombre_dia or "").strip().lower()
                # normalizo a las 3 letras esperadas por el enum
                if nombre.startswith("lu"): idx["lun"] = d.id_dia
                elif nombre.startswith("ma") and "r" in nombre: idx["mar"] = d.id_dia
                elif nombre.startswith("mi"): idx["mie"] = d.id_dia
                elif nombre.startswith("ju"): idx["jue"] = d.id_dia
                elif nombre.startswith("vi"): idx["vie"] = d.id_dia
                elif nombre.startswith("sa"): idx["sab"] = d.id_dia
                elif nombre.startswith("do"): idx["dom"] = d.id_dia

            dias_unicos: List[DiaSemanaEnum] = list(dict.fromkeys(payload.dias_visita))
            faltantes: List[str] = []
            registros: List[ClienteDiaSemana] = []

            turno_val = (
                payload.turno_visita.value
                if isinstance(payload.turno_visita, TurnoVisitaEnum)
                else payload.turno_visita
            )

            for dia in dias_unicos:
                id_dia = idx.get(dia.value)  # "lun".."dom"
                if not id_dia:
                    faltantes.append(dia.value)
                    continue
                registros.append(ClienteDiaSemana(
                    id_cliente=nuevo.legajo,
                    id_dia=id_dia,
                    turno_visita=turno_val  # puede ser None, queda NULL
                ))

            if faltantes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Días no encontrados en 'dia_semana': {faltantes}"
                )

            if registros:
                db.add_all(registros)

        db.commit()
        return ClienteService.get_detalle_cliente(db, nuevo.legajo)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando cliente: {e}")
    
@router.get("/", response_model=List[ClienteOut])
def ListarClientes(db: Session = Depends(get_db),):
        return db.query(Cliente).options(selectinload(Cliente.persona)).all()

#Trae un solo cliente por legajo y es para hacer request individuales.
@router.get("/{legajo}", response_model=ClienteOut)
def BuscarCliente(legajo: int, db: Session = Depends(get_db)):
    cliente = (
        db.query(Cliente)
        .options(selectinload(Cliente.persona))
        .filter(Cliente.legajo == legajo)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

#Get masivo que trae todo lo relacionado al cliente mediante el legajo.
@router.get("/{legajo}/detalle", response_model=ClienteDetalleOut,status_code=status.HTTP_200_OK)
def ObtenerDetalleCliente(legajo: int, db: Session = Depends(get_db)):
    return ClienteService.get_detalle_cliente(db, legajo)


@router.put("/{legajo}", response_model=ClienteOut)
def ActualizarCliente(legajo: int, payload: ClienteUpdate, db: Session = Depends(get_db)):
    try:
        cliente = db.get(Cliente, legajo)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # dump parcial, EXCLUYENDO id_empresa para que jamás lo toquemos
        data_cliente = payload.model_dump(
            exclude_unset=True,
            exclude={"id_empresa"}
        )
        persona_patch = data_cliente.pop("persona", None)

        # setear solo campos con valor NO None (evita overwrites a NULL)
        for campo, valor in data_cliente.items():
            if valor is not None:
                setattr(cliente, campo, valor)

        if persona_patch:
            persona = db.get(Persona, cliente.dni)
            if not persona:
                raise HTTPException(status_code=409, detail="Inconsistencia: el cliente no tiene persona asociada.")
            for campo, valor in persona_patch.items():
                if valor is not None:
                    setattr(persona, campo, valor)

        db.commit()
        # asegurar persona en salida
        cliente = (
            db.query(Cliente)
              .options(selectinload(Cliente.persona))
              .filter(Cliente.legajo == legajo)
              .first()
        )
        return cliente

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error actualizando cliente: {e}")



@router.delete("/{legajo}", status_code=status.HTTP_204_NO_CONTENT)
def BorrarCliente(legajo: int, db: Session = Depends(get_db)):
    try:
        cliente = db.get(Cliente, legajo)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        db.delete(cliente)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        # Si hay FKs (pedidos, usuarios, etc.) puede fallar por restricción
        raise HTTPException(status_code=409, detail=f"No se pudo eliminar el cliente (referencias activas): {e}")
