from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.repartoDia import RepartoDia
from app.models.empresa import Empresa
from app.models.usuario import Usuario


scheduler: AsyncIOScheduler | None = None


def _get_usuario_sis_or_fail(db: Session) -> Usuario:
    """
    Devuelve el usuario de sistema 'sis' o levanta error si no existe.
    """
    stmt = select(Usuario).where(Usuario.nombre_usuario == "sis")
    usuario = db.execute(stmt).scalar_one_or_none()

    if not usuario:
        raise RuntimeError("No existe el usuario de sistema 'sis' en la tabla usuario")

    return usuario


def crear_repartos_del_dia_automaticos(
    db: Session,
    fecha: Optional[date] = None,
) -> None:
    """
    Crea, para cada empresa, un registro reparto_dia en la fecha indicada
    (o en hoy si no se pasa fecha), usando el usuario 'sis'.

    Si para una empresa ya existe reparto_dia con esa fecha, no hace nada.
    """
    if fecha is None:
        fecha = date.today()

    usuario_sis = _get_usuario_sis_or_fail(db)

    empresas_ids = db.execute(
        select(Empresa.id_empresa)
    ).scalars().all()

    for id_empresa in empresas_ids:
        reparto = db.execute(
            select(RepartoDia).where(
                RepartoDia.id_empresa == id_empresa,
                RepartoDia.fecha == fecha,
            )
        ).scalar_one_or_none()

        if reparto:
            continue

        nuevo = RepartoDia(
            id_usuario=usuario_sis.id_usuario,
            id_empresa=id_empresa,
            fecha=fecha,
            total_recaudado=Decimal("0"),
            total_efectivo=Decimal("0"),
            total_virtual=Decimal("0"),
            observacion="Creado automáticamente por el sistema (usuario sis)",
        )
        db.add(nuevo)

    db.commit()


def start_scheduler() -> None:
    """
    - Asegura que exista el reparto_dia de HOY al arrancar.
    - Arranca el scheduler para crear repartos todos los días a las 00:05.
    """
    global scheduler

    if scheduler is not None and scheduler.running:
        return

    # 1) Crear repartos del día actual (si no existen)
    db = SessionLocal()
    try:
        crear_repartos_del_dia_automaticos(db)
    finally:
        db.close()

    # 2) Scheduler diario
    scheduler = AsyncIOScheduler(timezone="America/Argentina/Cordoba")

    @scheduler.scheduled_job(CronTrigger(hour=0, minute=5))
    def job_crear_repartos():
        db = SessionLocal()
        try:
            crear_repartos_del_dia_automaticos(db)
        finally:
            db.close()

    scheduler.start()


def stop_scheduler() -> None:
    """
    Detiene el scheduler cuando se apaga la app.
    """
    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
