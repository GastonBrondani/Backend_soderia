from typing import List
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.listaPrecioProducto import LPPOut, LPPUpsert
from app.services.listaPrecioProductoService import (
    upsert_precio as svc_upsert_precio,
    listar_productos_con_precio_por_lista as svc_listar_productos_con_precio_por_lista,
)
from app.schemas.producto import ProductoConPrecioOut
from app.schemas.listaDePrecios import (
    ListaDePreciosCreate,
    ListaDePreciosOut,
    ListaDePreciosUpdate,
)
from app.services.listaPrecioService import (
    crear_lista as svc_crear_lista,
    listar_listas as svc_listar_listas,
    obtener_lista as svc_obtener_lista,
    actualizar_lista as svc_actualizar_lista,
)
from app.schemas.listaPrecioCombo import (
    LPCOut as LPCOutCombo,
    LPCUpsert as LPCUpsertCombo,
)
from app.schemas.combo import ComboConPrecioOut
from app.services.listaPrecioComboService import (
    upsert_precio_combo as svc_upsert_precio_combo,
    listar_combos_con_precio_por_lista as svc_listar_combos_con_precio_por_lista,
)

from app.schemas.precioItem import PrecioItemOut
from app.services.listaPrecioItemService import (
    listar_items_con_precio as svc_listar_items_con_precio,
)

from app.schemas.listaPrecioServicio import LPSOut, LPSUpsert, LPSBasicOut
from app.services.listaPrecioServicioService import (
    listar_precios_de_lista_servicio as svc_listar_precios_de_lista_servicio,
    upsert_precio_servicio as svc_upsert_precio_servicio,
)

router = APIRouter(
    prefix="/listas-precios",
    tags=["ListaDePrecios"],
    dependencies=[Depends(get_current_user)],
)


@router.put("/{id_lista}/precios/{id_producto}", response_model=LPPOut)
def upsert_precio(
    id_lista: int,
    id_producto: int,
    payload: LPPUpsert,
    db: Session = Depends(get_db),
):
    payload.id_lista = id_lista
    payload.id_producto = id_producto
    return svc_upsert_precio(db, id_lista, payload)


@router.post("/", response_model=ListaDePreciosOut, status_code=201)
def crear_lista(payload: ListaDePreciosCreate, db: Session = Depends(get_db)):
    return svc_crear_lista(db, payload)


@router.get("/", response_model=list[ListaDePreciosOut])
def listar_listas(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    return svc_listar_listas(db, limit, offset)


@router.get("/{id_lista}", response_model=ListaDePreciosOut)
def obtener_lista(id_lista: int, db: Session = Depends(get_db)):
    return svc_obtener_lista(db, id_lista)


@router.put("/{id_lista}", response_model=ListaDePreciosOut)
def actualizar_lista(
    id_lista: int, payload: ListaDePreciosUpdate, db: Session = Depends(get_db)
):
    return svc_actualizar_lista(db, id_lista, payload)


@router.delete("/{id_lista}", response_model=ListaDePreciosOut)
def eliminar_lista(id_lista: int, db: Session = Depends(get_db)):
    payload = ListaDePreciosUpdate(estado="inactivo")
    return svc_actualizar_lista(db, id_lista, payload)


@router.get("/{id_lista}/productos", response_model=List[ProductoConPrecioOut])
def listar_productos_con_precio(
    id_lista: int,
    db: Session = Depends(get_db),
):
    return svc_listar_productos_con_precio_por_lista(db, id_lista)


@router.put("/{id_lista}/precios-combos/{id_combo}", response_model=LPCOutCombo)
def upsert_precio_combo(
    id_lista: int,
    id_combo: int,
    payload: LPCUpsertCombo,
    db: Session = Depends(get_db),
):
    payload.id_lista = id_lista
    payload.id_combo = id_combo
    return svc_upsert_precio_combo(db, id_lista, payload)


@router.get("/{id_lista}/combos", response_model=List[ComboConPrecioOut])
def listar_combos_con_precio(
    id_lista: int,
    db: Session = Depends(get_db),
):
    return svc_listar_combos_con_precio_por_lista(db, id_lista)


@router.get("/{id_lista}/precios-servicios", response_model=List[LPSBasicOut])
def listar_precios_de_lista_servicios(
    id_lista: int,
    db: Session = Depends(get_db),
    include_tipo: bool = Query(
        True, description="Incluye tipo de servicio (ALQUILER_DISPENSER)"
    ),
):
    return svc_listar_precios_de_lista_servicio(db, id_lista, include_tipo)


@router.put(
    "/{id_lista}/precios-servicios/{id_cliente_servicio}",
    response_model=LPSOut,
)
def upsert_precio_servicio(
    id_lista: int,
    id_cliente_servicio: int,
    payload: LPSUpsert,
    db: Session = Depends(get_db),
):
    payload.id_lista = id_lista
    payload.id_cliente_servicio = id_cliente_servicio
    return svc_upsert_precio_servicio(db, id_lista, payload)


@router.get("/{id_lista}/items", response_model=List[PrecioItemOut])
def listar_items_de_lista(
    id_lista: int,
    db: Session = Depends(get_db),
):
    return svc_listar_items_con_precio(db, id_lista=id_lista)