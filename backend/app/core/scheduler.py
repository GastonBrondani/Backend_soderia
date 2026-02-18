from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.orm import Session
import os
from app.core.security import hash_password

from app.core.database import SessionLocal
from app.models.repartoDia import RepartoDia
from app.models.empresa import Empresa
from app.models.usuario import Usuario

# from app.services.cajaEmpresaService import CajaEmpresaService


scheduler: AsyncIOScheduler | None = None


def ensure_usuario_sis(db: Session) -> Usuario:
    stmt = select(Usuario).where(Usuario.nombre_usuario == "sis")
    usuario = db.execute(stmt).scalars().first()  # tolera duplicados sin explotar

    if usuario:
        return usuario

    if os.getenv("AUTO_CREATE_SIS", "0") != "1":
        raise RuntimeError(
            "No existe el usuario de sistema 'sis' y AUTO_CREATE_SIS != 1"
        )

    password = os.getenv("SIS_PASSWORD", "sis")
    hashed = hash_password(password)

    usuario = Usuario(
        nombre_usuario="sis",
        legajo_empleado=None,
        legajo_cliente=None,
    )

    # Setea contraseña sin asumir el nombre exacto del atributo en el modelo
    if hasattr(usuario, "contraseña"):
        setattr(usuario, "contraseña", hashed)
    elif hasattr(usuario, "contrasena"):
        setattr(usuario, "contrasena", hashed)
    else:
        raise RuntimeError(
            "No encuentro el atributo de contraseña en el modelo Usuario (contraseña/contrasena)"
        )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)
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

    usuario_sis = ensure_usuario_sis(db)

    empresas_ids = db.execute(select(Empresa.id_empresa)).scalars().all()

    for id_empresa in empresas_ids:
        reparto = (
            db.execute(
                select(RepartoDia).where(
                    RepartoDia.id_empresa == id_empresa,
                    RepartoDia.fecha == fecha,
                )
            )
            .scalars()
            .first()
        )

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

    # No lo usamos porque esta duplicando los montos en caja empresa
    # @scheduler.scheduled_job(CronTrigger(hour=23, minute=55))
    # def job_cerrar_caja():
    #    db = SessionLocal()
    #    try:
    #        CajaEmpresaService.generar_cierre_repartos_por_fecha(db)
    #    finally:
    #        db.close()

    scheduler.start()


def stop_scheduler() -> None:
    """
    Detiene el scheduler cuando se apaga la app.
    """
    global scheduler

    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
