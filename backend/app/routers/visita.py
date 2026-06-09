from datetime import datetime,date
from typing import Optional

from fastapi import Depends,status,APIRouter,HTTPException,Query,Response
from app.core.security import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db


from app.models.cliente import Cliente
from app.models.visita import Visita
from app.schemas.visita import VisitaCreate, VisitaOut
from app.api.deps import get_cliente_or_404_dep

from app.services.historicoService import registrar_evento_cliente
from app.services.idempotencyService import buscar_por_idempotency_key
from app.schemas.enumsHistorico import TipoEventoCodigoEnum


router = APIRouter(prefix="/visitas",tags=["Visitas"],dependencies=[Depends(get_current_user)],)

@router.post("/{legajo}",response_model=VisitaOut,status_code=status.HTTP_201_CREATED,)
def crear_visita_cliente(payload: VisitaCreate, response: Response, cliente: Cliente = Depends(get_cliente_or_404_dep), db: Session = Depends(get_db),):
    """
    Registra una visita. Soporta idempotencia (offline sync): si llega un
    `idempotency_key` ya usado, no se duplica la visita y se devuelve la
    original con 200.
    """
    # 0) Idempotencia: si ya llegó esta misma visita, devolver la original
    existente = buscar_por_idempotency_key(db, Visita, payload.idempotency_key)
    if existente is not None:
        response.status_code = status.HTTP_200_OK
        return existente

    fecha = payload.fecha or datetime.now()

    visita = Visita(
        legajo=cliente.legajo,
        fecha=fecha,
        estado=payload.estado,
        idempotency_key=payload.idempotency_key,
        client_uuid=payload.client_uuid,
    )

    db.add(visita)

    try:
        db.flush()  # 👈 genera id_visita sin hacer commit

        # 2) Registrar evento histórico
        registrar_evento_cliente(
            db,
            legajo=cliente.legajo,
            codigo_evento=TipoEventoCodigoEnum.VISITA_REGISTRADA,
            observacion=f"Visita registrada con estado: {payload.estado}",
            datos={
                "id_visita": visita.id_visita,
                "estado": visita.estado,
                "fecha": fecha.isoformat(),
            },
        )

        db.commit()
    except IntegrityError:
        # Carrera entre dos reintentos de la misma visita: devolver la que sí
        # se creó (el índice único de idempotency_key rechazó el segundo).
        db.rollback()
        existente = buscar_por_idempotency_key(db, Visita, payload.idempotency_key)
        if existente is not None:
            response.status_code = status.HTTP_200_OK
            return existente
        raise

    db.refresh(visita)

    return visita


@router.get("/visitas", response_model=list[VisitaOut])
def listar_visitas(
    legajo: Optional[int] = Query(None),
    fecha: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    - Si se envía `legajo`, devuelve todas las visitas de ese cliente.
    - Si se envía `fecha`, devuelve todas las visitas de esa fecha.
    - Si se envían ambos, filtra por ambos (legajo + fecha).
    - Si no se envía ninguno, devuelve 400.
    """
    if legajo is None and fecha is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes indicar al menos legajo o fecha.",
        )

    stmt = select(Visita)

    if legajo is not None:
        stmt = stmt.where(Visita.legajo == legajo)

    if fecha is not None:
        # compara solo la parte de fecha del DateTime
        stmt = stmt.where(func.date(Visita.fecha) == fecha)

    stmt = stmt.order_by(Visita.fecha.desc())

    visitas = db.execute(stmt).scalars().all()
    return visitas