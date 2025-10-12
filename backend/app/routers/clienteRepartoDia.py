# app/routers/cliente_reparto_dia.py
from __future__ import annotations

from typing import List, Optional,Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

# Ajustá este import según tu proyecto (sé que en tu repo usás core.database)
from app.core.database import get_db

from app.schemas.clienteRepartoDia import (
    ClienteRepartoDiaCreate,
    PlanificarClientesIn,
    ClienteRepartoDiaUpdate,
    ClienteRepartoDiaOut,
)
from app.services.clienteRepartoDiaService import ClienteRepartoDiaService

router = APIRouter(prefix="/repartos-dia/{id_repartodia}/clientes", tags=["RepartoDia - Clientes"],)


# ---------------------- Planificar UNO ----------------------
@router.post(
    "/",
    response_model=ClienteRepartoDiaOut,
    status_code=status.HTTP_201_CREATED,
)
def planificar_cliente(
    id_repartodia: int,
    payload: ClienteRepartoDiaCreate,
    db: Session = Depends(get_db),
):
    """
    Planifica un cliente dentro del reparto del día indicado.
    """
    entity = ClienteRepartoDiaService.planificar_cliente(db, id_repartodia, payload)
    return entity


# ---------------------- Planificar BULK ----------------------
@router.post(
    "/bulk",
    response_model=List[ClienteRepartoDiaOut],
    status_code=status.HTTP_201_CREATED,
)
def planificar_clientes_bulk(
    id_repartodia: int,
    payload: PlanificarClientesIn,
    ignore_duplicates: bool = Query(
        True, description="Si True, ignora clientes ya planificados."
    ),
    db: Session = Depends(get_db),
):
    """
    Planifica varios clientes de una sola vez.
    """
    rows = ClienteRepartoDiaService.planificar_clientes(
        db, id_repartodia, payload, ignore_duplicates=ignore_duplicates
    )
    return rows


# ---------------------- Listar por reparto ----------------------
@router.get(
    "/",
    response_model=List[ClienteRepartoDiaOut],
)
def listar_clientes_de_reparto(
    id_repartodia: int,
    db: Session = Depends(get_db),
):
    """
    Lista todas las filas cliente_reparto_dia de un reparto.
    """
    rows = ClienteRepartoDiaService.listar_por_reparto(db, id_repartodia)
    return rows


# ---------------------- Detalle (PK compuesta) ----------------------
@router.get(
    "/{legajo}",
    response_model=ClienteRepartoDiaOut,
)
def obtener_detalle_cliente_en_reparto(
    id_repartodia: int,
    legajo: int,
    db: Session = Depends(get_db),
):
    """
    Obtiene el registro de planificación/resultado de un cliente en un reparto.
    """
    row = ClienteRepartoDiaService.get_or_404(db, id_repartodia, legajo)
    return row


# ---------------------- Registrar resultado (PATCH) ----------------------
@router.patch(
    "/{legajo}",
    response_model=ClienteRepartoDiaOut,
)
def registrar_resultado_visita(
    id_repartodia: int,
    legajo: int,
    payload: ClienteRepartoDiaUpdate,
    # Flags para side-effects mínimos y controlables desde la UI
    afectar_stock: bool = Query(
        True,
        description="Si True, registra EGRESO en movimiento_stock por el delta de bidones.",
    ),
    actualizar_totales: bool = Query(
        True,
        description="Si True, suma el delta de monto_abonado al total_recaudado del reparto.",
    ),
    id_producto_bidon: Optional[int] = Query(
        None,
        description="Producto 'bidón' para generar movimiento de stock cuando afectar_stock=True.",
    ),
    medio_cobro: Optional[Literal["efectivo", "virtual"]] = Query(
        None,
        description="A qué subtotal sumar el delta de monto_abonado."
    ),
    db: Session = Depends(get_db),
):
    """
    Aplica el resultado de la visita. Calcula deltas y, si corresponde:
    - EGRESO en movimiento_stock (vinculado al recorrido del reparto).
    - Suma al total_recaudado del reparto.
    """
    row = ClienteRepartoDiaService.registrar_resultado(
        db,
        id_repartodia=id_repartodia,
        legajo=legajo,
        payload=payload,
        actualizar_totales=actualizar_totales,
        afectar_stock=afectar_stock,
        id_producto_bidon=id_producto_bidon,
        medio_cobro=medio_cobro,
    )
    return row


# ---------------------- Quitar de la planificación ----------------------
@router.delete(
    "/{legajo}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def quitar_cliente_de_reparto(
    id_repartodia: int,
    legajo: int,
    db: Session = Depends(get_db),
):
    """
    Elimina la fila (id_repartodia, legajo).
    """
    ClienteRepartoDiaService.quitar_cliente(db, id_repartodia, legajo)
    return None
