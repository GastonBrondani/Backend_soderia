from datetime import date
from sqlalchemy import select, and_,func
from decimal import Decimal
from sqlalchemy.orm import Session

from app.models.repartoDia import RepartoDia
from app.models.cajaEmpresa import CajaEmpresa
from app.models.tipoMovimientoCaja import TipoMovimientoCaja
from app.models.medioPago import MedioPago



class CajaEmpresaService:
    #Cierre automatico del dia.
    @staticmethod
    def generar_cierre_repartos_por_fecha(db: Session,fecha: date,) -> int:
        """
        Genera movimientos de caja por cada reparto_dia de esa fecha.
        Devuelve cuántos movimientos creó.
        """
        # 1) Buscar repartos del día
        repartos = (
            db.execute(
                select(RepartoDia).where(RepartoDia.fecha == fecha)
            )
            .scalars()
            .all()
        )

        if not repartos:
            return 0

        # 2) Resolver IDs fijos de tipo_movimiento e id_medio_pago
        #    (podés cachearlos o tenerlos en Enum)
        tipo_mov_ingreso = (
            db.execute(
                select(TipoMovimientoCaja).where(
                    TipoMovimientoCaja.descripcion == "INGRESO_REPARTO"
                )
            )
            .scalars()
            .first()
        )
        if not tipo_mov_ingreso:
            raise ValueError("Falta tipo_movimiento_caja 'INGRESO_REPARTO'")

        medio_pago_mixto = (
            db.execute(
                select(MedioPago).where(MedioPago.nombre == "MIXTO_REPARTO")
            )
            .scalars()
            .first()
        )
        if not medio_pago_mixto:
            raise ValueError("Falta medio_pago 'MIXTO_REPARTO'")

        creados = 0

        for r in repartos:
            # 3) Evitar duplicados: chequear si ya generaste el cierre
            existe = (
                db.execute(
                    select(CajaEmpresa).where(
                        and_(
                            CajaEmpresa.id_empresa == r.id_empresa,
                            CajaEmpresa.fecha == r.fecha,
                            CajaEmpresa.tipo == "CIERRE_REPARTO",
                            CajaEmpresa.observacion
                            == f"Cierre automático reparto {r.id_repartodia}",
                        )
                    )
                )
                .scalars()
                .first()
            )
            if existe:
                continue

            mov = CajaEmpresa(
                id_empresa=r.id_empresa,
                id_tipo_movimiento=tipo_mov_ingreso.id_tipo_movimiento,
                id_medio_pago=medio_pago_mixto.id_medio_pago,
                fecha=r.fecha,
                tipo="CIERRE_REPARTO",
                monto=r.total_recaudado,
                observacion=f"Cierre automático reparto {r.id_repartodia}",
            )
            db.add(mov)
            creados += 1

        db.commit()
        return creados
    
    @staticmethod
    def _sum_query(
        db: Session,
        *,
        id_empresa: int | None = None,
        fecha: date | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> Decimal:
        conds = []

        if id_empresa is not None:
            conds.append(CajaEmpresa.id_empresa == id_empresa)

        if fecha is not None:
            conds.append(CajaEmpresa.fecha == fecha)

        if fecha_desde is not None:
            conds.append(CajaEmpresa.fecha >= fecha_desde)

        if fecha_hasta is not None:
            conds.append(CajaEmpresa.fecha <= fecha_hasta)

        stmt = select(func.coalesce(func.sum(CajaEmpresa.monto), 0))

        if conds:
            stmt = stmt.where(and_(*conds))

        total: Decimal = db.execute(stmt).scalar_one()
        return total

    @staticmethod
    def total_general(db: Session, id_empresa: int | None = None) -> Decimal:
        """Total de toda la caja (opcional filtrado por empresa)."""
        return CajaEmpresaService._sum_query(db, id_empresa=id_empresa)

    @staticmethod
    def total_por_fecha(
        db: Session,
        fecha: date,
        id_empresa: int | None = None,
    ) -> Decimal:
        """Total de la caja para una fecha puntual."""
        return CajaEmpresaService._sum_query(
            db, id_empresa=id_empresa, fecha=fecha
        )

    @staticmethod
    def total_por_rango(
        db: Session,
        fecha_desde: date,
        fecha_hasta: date,
        id_empresa: int | None = None,
    ) -> Decimal:
        """Total de la caja dentro de un rango de fechas (inclusive)."""
        return CajaEmpresaService._sum_query(
            db,
            id_empresa=id_empresa,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
