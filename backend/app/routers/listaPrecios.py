from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.listaPrecioProducto import LPPOut, LPPUpsert, LPPBasicOut
from app.services.listaPrecioProductoService import (
    listar_precios_de_lista as svc_listar_precios_de_lista,
    upsert_precio as svc_upsert_precio,
    #upsert_precios_bulk as svc_upsert_precios_bulk,
)
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