from datetime import date,datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.clienteServicio import ClienteServicio
from app.models.clienteServicioPeriodo import ClienteServicioPeriodo
from app.services.pagoService import PagoService

from app.utils.periodos import mes_inicio, vencimiento_mes, periodo_yyyymm


def crear_servicio_alquiler_dispenser(db: Session, legajo: int, monto_mensual: Decimal, fecha_inicio: date) -> ClienteServicio:
    # evita duplicar alquiler activo
    existe = db.execute(
        select(ClienteServicio).where(
            ClienteServicio.legajo == legajo,
            ClienteServicio.tipo_servicio == "ALQUILER_DISPENSER",
            ClienteServicio.activo,
        )
    ).scalar_one_or_none()

    if existe:
        raise HTTPException(status_code=409, detail="El cliente ya tiene un alquiler de dispenser activo.")

    srv = ClienteServicio(
        legajo=legajo,
        tipo_servicio="ALQUILER_DISPENSER",
        monto_mensual=monto_mensual,
        fecha_inicio=fecha_inicio,
        activo=True,
    )
    db.add(srv)
    db.flush()  # para obtener id_cliente_servicio

    # crear período del mes actual (o del mes de inicio) como pendiente
    hoy = date.today()
    p = mes_inicio(hoy if fecha_inicio <= hoy else fecha_inicio)
    _upsert_periodo(db, srv, p)

    return srv

def _upsert_periodo(db: Session, srv: ClienteServicio, periodo: date) -> ClienteServicioPeriodo:
    per = db.execute(
        select(ClienteServicioPeriodo).where(
            ClienteServicioPeriodo.id_cliente_servicio == srv.id_cliente_servicio,
            ClienteServicioPeriodo.periodo == periodo,
        )
    ).scalar_one_or_none()

    if per:
        return per

    per = ClienteServicioPeriodo(
        id_cliente_servicio=srv.id_cliente_servicio,
        periodo=periodo,
        monto=srv.monto_mensual,
        estado="PENDIENTE",
        fecha_vencimiento=vencimiento_mes(periodo),
        fecha_pago=None,
    )
    db.add(per)
    return per

def asegurar_periodo_mes_actual(db: Session, legajo: int) -> None:
    hoy = date.today()
    periodo = mes_inicio(hoy)

    servicios = db.execute(
        select(ClienteServicio).where(ClienteServicio.legajo == legajo, ClienteServicio.activo)
    ).scalars().all()

    for srv in servicios:
        _upsert_periodo(db, srv, periodo)

def listar_pendientes_cliente(db: Session, legajo: int):
    # asegura período actual antes de listar
    asegurar_periodo_mes_actual(db, legajo)

    stmt = (
        select(ClienteServicioPeriodo)
        .join(ClienteServicio, ClienteServicio.id_cliente_servicio == ClienteServicioPeriodo.id_cliente_servicio)
        .where(
            ClienteServicio.legajo == legajo,
            ClienteServicio.activo,
            ClienteServicioPeriodo.estado.in_(["PENDIENTE", "VENCIDO"]),
        )
        .order_by(ClienteServicioPeriodo.periodo.desc())
    )
    return db.execute(stmt).scalars().all()

def marcar_vencidos(db: Session) -> int:
    hoy = date.today()
    stmt = select(ClienteServicioPeriodo).where(
        ClienteServicioPeriodo.estado == "PENDIENTE",
        ClienteServicioPeriodo.fecha_vencimiento < hoy,
    )
    periodos = db.execute(stmt).scalars().all()
    for p in periodos:
        p.estado = "VENCIDO"
    return len(periodos)

def pagar_periodo_servicio(db: Session, id_periodo: int, legajo: int, id_medio_pago: int, observacion: str | None = None):
    per = db.execute(
        select(ClienteServicioPeriodo)
        .where(ClienteServicioPeriodo.id_periodo == id_periodo)
        .with_for_update()
    ).scalar_one_or_none()

    if not per:
        raise HTTPException(status_code=404, detail="Periodo inexistente.")

    srv = db.execute(
        select(ClienteServicio).where(ClienteServicio.id_cliente_servicio == per.id_cliente_servicio)
    ).scalar_one()

    if srv.legajo != legajo:
        raise HTTPException(status_code=403, detail="El periodo no pertenece al cliente.")
    if per.estado == "PAGADO":
        raise HTTPException(status_code=409, detail="El periodo ya está pagado.")

    # Crear el pago con el service (esto impacta caja_empresa automáticamente)
    pago = PagoService.crear(
        db,
        id_empresa=1,  # en tu caso 1 sola empresa
        id_medio_pago=id_medio_pago,
        fecha=datetime.now(),
        monto=per.monto,
        tipo_pago="SERVICIO",
        observacion=observacion or f"Pago alquiler dispenser {per.periodo.strftime('%Y-%m')}",
        legajo=legajo,
        id_cliente_servicio_periodo=per.id_periodo,  # <-- link al periodo
        
    )

    # Marcar periodo pagado
    per.estado = "PAGADO"
    per.fecha_pago = date.today()

    return pago
