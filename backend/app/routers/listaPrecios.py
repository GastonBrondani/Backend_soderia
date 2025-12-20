from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.listaPrecioProducto import LPPOut, LPPUpsert, LPPBasicOut
from app.services.listaPrecioProductoService import (
    listar_precios_de_lista as svc_listar_precios_de_lista,
    upsert_precio as svc_upsert_precio,
    listar_productos_con_precio_por_lista as svc_listar_productos_con_precio_por_lista,
    #upsert_precios_bulk as svc_upsert_precios_bulk,
)
from app.schemas.producto import ProductoConPrecioOut
from app.schemas.listaDePrecios import (
    ListaDePreciosCreate, ListaDePreciosOut
)
from app.services.listaPrecioService import (
    crear_lista as svc_crear_lista,
    listar_listas as svc_listar_listas,
    #obtener_lista as svc_obtener_lista,
    #actualizar_lista as svc_actualizar_lista,
    #eliminar_lista as svc_eliminar_lista
)
from app.schemas.listaPrecioCombo import LPCOut as LPCOutCombo, LPCUpsert as LPCUpsertCombo, LPCBasicOut as LPCBasicOutCombo
from app.schemas.combo import ComboConPrecioOut
from app.services.listaPrecioComboService import (
    listar_precios_de_lista_combo as svc_listar_precios_de_lista_combo,
    upsert_precio_combo as svc_upsert_precio_combo,
    listar_combos_con_precio_por_lista as svc_listar_combos_con_precio_por_lista,
)
#Estos son los nuevos que hay que utilizar, ver como integrarlos con los viejos
from app.schemas.precioItem import PrecioItemUpsert, PrecioItemOut, TipoItemPrecio
from app.services.listaPrecioItemService import upsert_precio_item as svc_upsert_precio_item
from app.services.listaPrecioItemService import listar_items_con_precio as svc_listar_items_con_precio

router = APIRouter(prefix="/listas-precios", tags=["ListaDePrecios"])

@router.get("/{id_lista}/precios", response_model=List[LPPBasicOut])
def listar_precios_de_lista(
    id_lista: int,
    db: Session = Depends(get_db),
    include_producto: bool = Query(True, description="Incluye nombre del producto (optimiza para UI)"),
):
    return svc_listar_precios_de_lista(db, id_lista, include_producto)

@router.put("/{id_lista}/precios/{id_producto}", response_model=LPPOut)
def upsert_precio(
    id_lista: int,
    id_producto: int,
    payload: LPPUpsert,
    db: Session = Depends(get_db),
):
    # normalizo body con ids del path para evitar inconsistencias
    payload.id_lista = id_lista
    payload.id_producto = id_producto
    return svc_upsert_precio(db, id_lista, payload)

@router.post("/", response_model=ListaDePreciosOut, status_code=201)
def crear_lista(payload: ListaDePreciosCreate, db: Session = Depends(get_db)):
    return svc_crear_lista(db, payload)


@router.get("/", response_model=list[ListaDePreciosOut])
def listar_listas(db: Session = Depends(get_db), limit: int = 50, offset: int = 0):
    return svc_listar_listas(db, limit, offset)

#Devuelve todos los productos que tienen precio cargado en la lista indicada, junto con ese precio.
@router.get("/{id_lista}/productos", response_model=List[ProductoConPrecioOut])
def listar_productos_con_precio(
    id_lista: int,
    db: Session = Depends(get_db),
):
    """
    Devuelve todos los productos que tienen precio cargado
    en la lista indicada, junto con ese precio.
    """
    return svc_listar_productos_con_precio_por_lista(db, id_lista)


@router.get("/{id_lista}/precios-combos", response_model=List[LPCBasicOutCombo])
def listar_precios_de_lista_combos(
    id_lista: int,
    db: Session = Depends(get_db),
    include_combo: bool = Query(True, description="Incluye nombre del combo (optimiza para UI)"),
):
    return svc_listar_precios_de_lista_combo(db, id_lista, include_combo)


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

@router.put("/{id_lista}/precios/{tipo}/{id_item}", response_model=PrecioItemOut)
def upsert_precio_global(
    id_lista: int,
    tipo: TipoItemPrecio,   # "producto" | "combo"
    id_item: int,
    payload: PrecioItemUpsert,
    db: Session = Depends(get_db),
):
    return svc_upsert_precio_item(
        db,
        id_lista=id_lista,
        tipo=tipo,
        id_item=id_item,
        precio=payload.precio,
    )


@router.get("/{id_lista}/items", response_model=List[PrecioItemOut])
def listar_items_de_lista(
    id_lista: int,
    db: Session = Depends(get_db),
):
    return svc_listar_items_con_precio(db, id_lista=id_lista)

#--- TODOO LO COMENTADO ANDA, PERO DE MOMENTO NO SE USA, LO DEJO PARA MAS ADELANTE ---

#@router.put("/{id_lista}/precios", response_model=List[LPPOut])
#def upsert_precios_bulk(
#    id_lista: int,
#    items: List[LPPUpsert],
#    db: Session = Depends(get_db),
#):
#    return svc_upsert_precios_bulk(db, id_lista, items)


#@router.get("/{id_lista}", response_model=ListaDePreciosOut)
#def obtener_lista(id_lista: int, db: Session = Depends(get_db)):
#    return svc_obtener_lista(db, id_lista)

#@router.put("/{id_lista}", response_model=ListaDePreciosOut)
#def actualizar_lista(id_lista: int, payload: ListaDePreciosUpdate, db: Session = Depends(get_db)):
#    return svc_actualizar_lista(db, id_lista, payload)

#Mas adelante capaz se habilite
# --- DELETE lista de precios ---
#@router.delete("/{id_lista}", status_code=204)
#def eliminar_lista(
#    id_lista: int,
#    cascade: bool = Query(True, description="Si es true, borra también los precios de esta lista"),
#    db: Session = Depends(get_db),
#):
#    svc_eliminar_lista(db, id_lista, cascade)
#    return Response(status_code=204)