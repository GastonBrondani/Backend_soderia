from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.api.deps import get_cliente_or_404_dep  
from app.core.database import get_db
from app.models.clienteDiaSemana import ClienteDiaSemana
from app.models.diaSemana import DiaSemana
from app.models.cliente import Cliente
from app.models.persona import Persona
from app.models.visita import Visita
from sqlalchemy import and_, func
from sqlalchemy import select, delete, func
from sqlalchemy.sql import over
from app.models.visita import Visita


from sqlalchemy.dialects.postgresql import insert as pg_insert




router = APIRouter(prefix="/clientes", tags=["Cliente - días de visita"])

# ---- Schemas específicos del router (payload/response del endpoint) ----
class ClienteDiaVisitaIn(BaseModel):
    id_dia: int
    turno_visita: Optional[str] = None  # "mañana", "tarde", etc.

class ClienteDiasVisitaUpsert(BaseModel):
    dias: List[ClienteDiaVisitaIn]

class ClienteDiaVisitaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_dia: int
    nombre_dia: str
    turno_visita: Optional[str] = None

   

# ===== Schemas de respuesta =====
class ClientePorDiaItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    legajo: int
    dni: Optional[int] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    turno_visita: Optional[str] = None
    estado_visita: str   

class ClientesPorDiaOut(BaseModel):
    fecha: date
    id_dia: int
    nombre_dia: str
    clientes: List[ClientePorDiaItem]

class ClientesPorDiaSinFechaOut(BaseModel):
    id_dia: int
    nombre_dia: str
    clientes: List[ClientePorDiaItem] 

#Este router maneja los días de visita de los clientes pasandome una fecha te muestro todos los clientes de ese dia.(Funciona)
@router.get("/agenda/visitas", response_model=ClientesPorDiaOut)
def listar_clientes_por_fecha(
    fecha: date = Query(..., description="YYYY-MM-DD"),
    turno: Optional[str] = Query(None, description="Mañana | Tarde | ..."),
    db: Session = Depends(get_db),
):
    id_dia = fecha.isoweekday()

    # Subquery: última visita por cliente en esa fecha
    v = (
        select(
            Visita.legajo.label("legajo"),
            Visita.estado.label("estado_visita"),
            over(
                func.row_number(),
                partition_by=Visita.legajo,
                order_by=Visita.fecha.desc(),
            ).label("rn"),
        )
        .where(func.date(Visita.fecha) == fecha)
        .subquery()
    )

    stmt = (
        select(
            Cliente.legajo,
            Cliente.dni,
            Persona.nombre,
            Persona.apellido,
            ClienteDiaSemana.turno_visita,
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            func.coalesce(v.c.estado_visita, "pendiente").label("estado_visita"),
        )
        .select_from(ClienteDiaSemana)
        .join(Cliente, Cliente.legajo == ClienteDiaSemana.id_cliente)
        .outerjoin(Persona, Persona.dni == Cliente.dni)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .outerjoin(
            v,
            (v.c.legajo == Cliente.legajo) & (v.c.rn == 1),
        )
        .where(ClienteDiaSemana.id_dia == id_dia)
        .order_by(ClienteDiaSemana.turno_visita, Persona.apellido, Persona.nombre)
    )

    if turno:
        stmt = stmt.where(ClienteDiaSemana.turno_visita.ilike(turno))

    rows = db.execute(stmt).all()

    nombre_dia = rows[0].nombre_dia if rows else db.execute(
        select(DiaSemana.nombre_dia).where(DiaSemana.id_dia == id_dia)
    ).scalar_one()

    return ClientesPorDiaOut(
        fecha=fecha,
        id_dia=id_dia,
        nombre_dia=nombre_dia,
        clientes=[
            ClientePorDiaItem(
                legajo=r.legajo,
                dni=r.dni,
                nombre=r.nombre,
                apellido=r.apellido,
                turno_visita=r.turno_visita,
                estado_visita=r.estado_visita,  # 👈 ya viene siempre (pendiente si no hay visita)
            )
            for r in rows
        ],
    )



# ---- Helper de validación ----
def _validar_dias_existen(db: Session, ids: List[int]) -> None:
    if not ids:
        return  # permitir limpiar días (lista vacía)
    existentes = {
        row.id_dia
        for row in db.execute(
            select(DiaSemana.id_dia).where(DiaSemana.id_dia.in_(ids))
        ).all()
    }
    faltantes = set(ids) - existentes
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Días inexistentes: {sorted(faltantes)}"
        )
    
#Trae los dias de visita del cliente por los id del dia (Funciona)
@router.get("/agenda/visitas/dia/{id_dia}", response_model=ClientesPorDiaSinFechaOut)
def listar_clientes_por_id_dia(
    id_dia: int,
    turno: Optional[str] = Query(None),
    fecha: Optional[date] = Query(None, description="YYYY-MM-DD (opcional para estado_visita)"),
    db: Session = Depends(get_db),
):
    # Validación de rango
    if not (1 <= id_dia <= 7):
        raise HTTPException(status_code=400, detail="id_dia debe estar entre 1 y 7 (Lunes=1, Domingo=7)")

    # Consulta base (misma forma que tu endpoint por fecha)
    stmt = (
        select(
            Cliente.legajo,
            Cliente.dni,
            Persona.nombre,
            Persona.apellido,
            ClienteDiaSemana.turno_visita,
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
        )
        .select_from(ClienteDiaSemana)
        .join(Cliente, Cliente.legajo == ClienteDiaSemana.id_cliente)
        .outerjoin(Persona, Persona.dni == Cliente.dni)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_dia == id_dia)
        .order_by(
            ClienteDiaSemana.turno_visita,
            ClienteDiaSemana.orden,
            Persona.apellido,
            Persona.nombre,
        )
    )

    if turno:
        stmt = stmt.where(ClienteDiaSemana.turno_visita.ilike(turno))

    rows = db.execute(stmt).all()

    # nombre del día (si no hay filas, lo saco de la tabla de días)
    nombre_dia = rows[0].nombre_dia if rows else db.execute(
        select(DiaSemana.nombre_dia).where(DiaSemana.id_dia == id_dia)
    ).scalar_one_or_none()

    if not nombre_dia:
        raise HTTPException(status_code=404, detail="Día inexistente.")

    return ClientesPorDiaSinFechaOut(
        id_dia=id_dia,
        nombre_dia=nombre_dia,
        clientes=[
            ClientePorDiaItem(
                legajo=r.legajo,
                dni=r.dni,
                nombre=r.nombre,
                apellido=r.apellido,
                turno_visita=r.turno_visita,
            )
            for r in rows
        ],
    )
#-----------------------------------


#Muestra el dia de la semana que visita el cliente (Funciona)
@router.get("/{legajo}/dias-visita", response_model=List[ClienteDiaVisitaOut])
def listar_dias_visita_cliente(
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            ClienteDiaSemana.turno_visita,
        )
        .select_from(ClienteDiaSemana)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_cliente == cliente.legajo)
        .order_by(ClienteDiaSemana.id_dia)
    )
    rows = db.execute(stmt).all()
    return [
        ClienteDiaVisitaOut(
            id_dia=r.id_dia,
            nombre_dia=r.nombre_dia,
            turno_visita=r.turno_visita,
        )
        for r in rows
    ]

""" #Le asignamos un dia de visita al cliente (Funciona)
@router.put("/{legajo}/dias-visita", response_model=List[ClienteDiaVisitaOut])
def upsert_dias_visita_cliente(
    payload: ClienteDiasVisitaUpsert,
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    ids = [d.id_dia for d in payload.dias]
    _validar_dias_existen(db, ids)

    # borrar asociaciones actuales del cliente
    db.execute(
        delete(ClienteDiaSemana).where(ClienteDiaSemana.id_cliente == cliente.legajo)
    )

    # insertar nuevas (si hay)
    if payload.dias:
        db.add_all([
            ClienteDiaSemana(
                id_cliente=cliente.legajo,
                id_dia=item.id_dia,
                turno_visita=item.turno_visita,
            )
            for item in payload.dias
        ])

    db.commit()

    # devolver el estado actual (misma consulta que en GET)
    stmt = (
        select(
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            ClienteDiaSemana.turno_visita,
        )
        .select_from(ClienteDiaSemana)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_cliente == cliente.legajo)
        .order_by(ClienteDiaSemana.id_dia)
    )
    rows = db.execute(stmt).all()
    return [
        ClienteDiaVisitaOut(
            id_dia=r.id_dia,
            nombre_dia=r.nombre_dia,
            turno_visita=r.turno_visita,
        )
        for r in rows
    ] """

#Elimina un dia de visita del cliente (Funciona)
@router.delete("/{legajo}/dias-visita/{id_dia}", status_code=204)
def eliminar_dia_visita_cliente(
    id_dia: int,
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    db.execute(
        delete(ClienteDiaSemana).where(
            ClienteDiaSemana.id_cliente == cliente.legajo,
            ClienteDiaSemana.id_dia == id_dia,
        )
    )
    db.commit()

def _validar_dias_existen(db: Session, ids: list[int]) -> None:
    if not ids:
        return
    rows = db.execute(
        select(DiaSemana.id_dia).where(DiaSemana.id_dia.in_(ids))
    ).scalars().all()
    faltantes = set(ids) - set(rows)
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Días inexistentes: {sorted(faltantes)}",
        )
    
""" @router.post("/{legajo}/dias-visita",
             response_model=List[ClienteDiaVisitaOut],
             status_code=status.HTTP_201_CREATED)
def agregar_dias_visita_cliente(
    payload: ClienteDiasVisitaUpsert,
    cliente: Cliente = Depends(get_cliente_or_404_dep),
    db: Session = Depends(get_db),
):
    # Validaciones
    ids = [d.id_dia for d in payload.dias]
    _validar_dias_existen(db, ids)

    # Nada que agregar
    if not payload.dias:
        # Devolver estado actual
        stmt = (
            select(
                ClienteDiaSemana.id_dia,
                DiaSemana.nombre_dia,
                ClienteDiaSemana.turno_visita,
            )
            .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
            .where(ClienteDiaSemana.id_cliente == cliente.legajo)
            .order_by(ClienteDiaSemana.id_dia)
        )
        rows = db.execute(stmt).all()
        return [
            ClienteDiaVisitaOut(
                id_dia=r.id_dia,
                nombre_dia=r.nombre_dia,
                turno_visita=r.turno_visita,
            )
            for r in rows
        ]

    # Insertar nuevos sin borrar existentes
    valores = [
        {
            "id_cliente": cliente.legajo,
            "id_dia": item.id_dia,
            "turno_visita": item.turno_visita,
        }
        for item in payload.dias
    ]

    # INSERT ... ON CONFLICT DO NOTHING sobre (id_cliente, id_dia)
    stmt_insert = (
        pg_insert(ClienteDiaSemana)
        .values(valores)
        .on_conflict_do_nothing(
            index_elements=["id_cliente", "id_dia"]
        )
    )
    db.execute(stmt_insert)
    db.commit()

    # Devolver estado actual (mismo SELECT que en tu PUT/GET)
    stmt = (
        select(
            ClienteDiaSemana.id_dia,
            DiaSemana.nombre_dia,
            ClienteDiaSemana.turno_visita,
        )
        .select_from(ClienteDiaSemana)
        .join(DiaSemana, DiaSemana.id_dia == ClienteDiaSemana.id_dia)
        .where(ClienteDiaSemana.id_cliente == cliente.legajo)
        .order_by(ClienteDiaSemana.id_dia)
    )
    rows = db.execute(stmt).all()
    return [
        ClienteDiaVisitaOut(
            id_dia=r.id_dia,
            nombre_dia=r.nombre_dia,
            turno_visita=r.turno_visita,
        )
        for r in rows
    ] """
