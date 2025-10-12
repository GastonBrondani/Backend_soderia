# app/services/clienteRepartoDiaService.py
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.clienteRepartoDia import ClienteRepartoDia
from app.models.repartoDia import RepartoDia
from app.models.recorrido import Recorrido
from app.models.movimientoStock import MovimientoStock

from app.schemas.clienteRepartoDia import (
    ClienteRepartoDiaCreate,
    PlanificarClientesIn,
    ClienteRepartoDiaUpdate,
)


class ClienteRepartoDiaService:
    # -------------------------- Helpers --------------------------

    @staticmethod
    def _get_reparto_or_404(db: Session, id_repartodia: int) -> RepartoDia:
        reparto = db.get(RepartoDia, id_repartodia)
        if not reparto:
            raise HTTPException(status_code=404, detail="Reparto del día no encontrado.")
        return reparto

    @staticmethod
    def _get_recorrido_por_reparto_or_404(db: Session, id_repartodia: int) -> Recorrido:
        stmt = select(Recorrido).where(Recorrido.id_repartodia == id_repartodia)
        recs = db.execute(stmt).scalars().all()
        if not recs:
            raise HTTPException(status_code=409, detail="No hay recorrido abierto para este reparto.")
        if len(recs) > 1:
            raise HTTPException(status_code=409, detail="Hay múltiples recorridos para este reparto.")
        return recs[0]

    @staticmethod
    def _registrar_mov_egreso(
        db: Session,
        *,
        id_recorrido: int,
        id_producto_bidon: int,
        cantidad: int,
        id_repartodia: int,
        legajo: int,
    ) -> MovimientoStock:
        if cantidad <= 0:
            raise ValueError("La cantidad de egreso debe ser positiva.")

        mov = MovimientoStock(
            id_producto=id_producto_bidon,
            id_recorrido=id_recorrido,
            id_pedido=None,
            fecha=datetime.utcnow(),
            tipo_movimiento="EGRESO",  # usa tu Enum si lo tenés
            cantidad=cantidad,
            observacion=f"Reparto {id_repartodia} - Cliente {legajo}",
        )
        db.add(mov)
        return mov

    # -------------------------- CRUD usados por el router --------------------------

    @staticmethod
    def get_or_404(db: Session, id_repartodia: int, legajo: int) -> ClienteRepartoDia:
        pk = (id_repartodia, legajo)
        row = db.get(ClienteRepartoDia, pk)
        if not row:
            raise HTTPException(status_code=404, detail="Cliente no planificado en este reparto.")
        return row

    @staticmethod
    def listar_por_reparto(db: Session, id_repartodia: int) -> list[ClienteRepartoDia]:
        stmt = (
            select(ClienteRepartoDia)
            .where(ClienteRepartoDia.id_repartodia == id_repartodia)
            .order_by(ClienteRepartoDia.legajo)
        )
        return db.execute(stmt).scalars().all()

    @staticmethod
    def planificar_cliente(db: Session, id_repartodia: int, payload: ClienteRepartoDiaCreate) -> ClienteRepartoDia:
        # Asegura que el reparto exista
        ClienteRepartoDiaService._get_reparto_or_404(db, id_repartodia)

        # Evita duplicado
        existe = db.get(ClienteRepartoDia, (id_repartodia, payload.legajo))
        if existe:
            raise HTTPException(status_code=409, detail="El cliente ya está planificado para este reparto.")

        row = ClienteRepartoDia(
            id_repartodia=id_repartodia,
            legajo=payload.legajo,
            turno_de_la_visita=payload.turno_de_la_visita,
            observacion=payload.observacion,
            estado_de_la_visita="pendiente",
            bidones_entregado=0,
            monto_abonado=Decimal("0.00"),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def planificar_clientes(
        db: Session,
        id_repartodia: int,
        payload: PlanificarClientesIn,
        *,
        ignore_duplicates: bool = True,
    ) -> list[ClienteRepartoDia]:
        ClienteRepartoDiaService._get_reparto_or_404(db, id_repartodia)

        nuevos: list[ClienteRepartoDia] = []
        for item in payload.items:
            ya = db.get(ClienteRepartoDia, (id_repartodia, item.legajo))
            if ya:
                if ignore_duplicates:
                    continue
                raise HTTPException(
                    status_code=409,
                    detail=f"Cliente {item.legajo} ya planificado."
                )
            row = ClienteRepartoDia(
                id_repartodia=id_repartodia,
                legajo=item.legajo,
                turno_de_la_visita=item.turno_de_la_visita,
                observacion=item.observacion,
                estado_de_la_visita="pendiente",
                bidones_entregado=0,
                monto_abonado=Decimal("0.00"),
            )
            db.add(row)
            nuevos.append(row)

        db.commit()
        for r in nuevos:
            db.refresh(r)
        return nuevos

    @staticmethod
    def quitar_cliente(db: Session, id_repartodia: int, legajo: int) -> None:
        row = ClienteRepartoDiaService.get_or_404(db, id_repartodia, legajo)
        db.delete(row)
        db.commit()

    # -------------------------- Registrar resultado (PATCH) --------------------------

    @staticmethod
    def registrar_resultado(
        db: Session,
        *,
        id_repartodia: int,
        legajo: int,
        payload: ClienteRepartoDiaUpdate,
        actualizar_totales: bool = True,
        afectar_stock: bool = True,
        id_producto_bidon: int | None = None,
        medio_cobro: Literal["efectivo", "virtual"] | None = None,  # ← obligatorio si viene un cobro
    ) -> ClienteRepartoDia:
        entity = ClienteRepartoDiaService.get_or_404(db, id_repartodia, legajo)
        reparto = ClienteRepartoDiaService._get_reparto_or_404(db, id_repartodia)

        data = payload.model_dump(exclude_unset=True)

        # 1) Tomamos el monto como "incremento" de cobro y lo sacamos del patch normal
        monto_incremento = data.pop("monto_abonado", None)

        # 2) Aplicamos el resto del patch (estado, turno, observación, etc.)
        prev_bidones = entity.bidones_entregado or 0
        for campo, valor in data.items():
            setattr(entity, campo, valor)

        # Normalizaciones
        entity.bidones_entregado = int(entity.bidones_entregado or 0)
        entity.monto_abonado = (entity.monto_abonado or Decimal("0.00"))

        # 3) Si hay incremento de cobro, lo imputamos SIEMPRE al bucket elegido + total_recaudado
        if actualizar_totales and monto_incremento is not None and monto_incremento != 0:
            if monto_incremento < 0:
                raise HTTPException(status_code=400, detail="monto_abonado debe ser positivo (incremento).")
            if medio_cobro not in ("efectivo", "virtual"):
                raise HTTPException(
                    status_code=400,
                    detail="Debe indicar medio_cobro=efectivo|virtual para registrar el cobro.",
                )

            # Inicializar nulos
            reparto.total_recaudado = (reparto.total_recaudado or Decimal("0.00"))
            reparto.total_efectivo = (reparto.total_efectivo or Decimal("0.00"))
            reparto.total_virtual = (reparto.total_virtual or Decimal("0.00"))

            # Imputación incremental
            reparto.total_recaudado += monto_incremento
            if medio_cobro == "efectivo":
                reparto.total_efectivo += monto_incremento
            else:
                reparto.total_virtual += monto_incremento

            # También acumular en el cliente (total pagado por ese cliente en el día)
            entity.monto_abonado = (entity.monto_abonado or Decimal("0.00")) + monto_incremento

        # 4) Stock: seguimos calculando delta para bidones
        delta_bidones = entity.bidones_entregado - prev_bidones
        if afectar_stock and delta_bidones > 0:
            if not id_producto_bidon:
                raise HTTPException(status_code=400, detail="id_producto_bidon es requerido.")
            recorrido = ClienteRepartoDiaService._get_recorrido_por_reparto_or_404(db, id_repartodia)
            ClienteRepartoDiaService._registrar_mov_egreso(
                db,
                id_recorrido=recorrido.id_recorrido,
                id_producto_bidon=id_producto_bidon,
                cantidad=delta_bidones,
                id_repartodia=id_repartodia,
                legajo=legajo,
            )

        db.commit()
        db.refresh(entity)
        return entity
