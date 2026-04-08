# app/services/agenda_service.py

from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.clienteDiaSemana import ClienteDiaSemana


TEMP_ORDEN_BASE = 1_000_000


def _obtener_bucket(db: Session, id_dia: int, turno: str) -> list[ClienteDiaSemana]:
    return db.execute(
        select(ClienteDiaSemana)
        .where(
            ClienteDiaSemana.id_dia == id_dia,
            ClienteDiaSemana.turno_visita == turno,
        )
        .order_by(ClienteDiaSemana.orden, ClienteDiaSemana.id_cliente)
        .with_for_update()
    ).scalars().all()


def _reasignar_ordenes_sin_choque(
    db: Session,
    filas: list[ClienteDiaSemana],
) -> None:
    # Paso 1: mover todo a órdenes temporales para evitar choques de unique
    for i, fila in enumerate(filas, start=1):
        fila.orden = TEMP_ORDEN_BASE + i
        db.add(fila)
    db.flush()

    # Paso 2: asignar órdenes finales limpias
    for i, fila in enumerate(filas, start=1):
        fila.orden = i
        db.add(fila)
    db.flush()


def insertar_cliente_en_agenda(
    *,
    db: Session,
    id_cliente: int,
    id_dia: int,
    turno: str,
    posicion: str,
    despues_de_legajo: int | None,
):
    if not turno:
        raise HTTPException(400, "Falta turno")

    # Buscar si ya existe un registro para ese cliente en ese día
    # (aunque esté en otro turno)
    registro = db.execute(
        select(ClienteDiaSemana)
        .where(
            ClienteDiaSemana.id_cliente == id_cliente,
            ClienteDiaSemana.id_dia == id_dia,
        )
        .with_for_update()
    ).scalars().first()

    # Si ya existía en otro turno del mismo día, primero lo sacamos
    # de ese bucket para poder reordenar el origen sin choques.
    if registro and registro.turno_visita != turno:
        turno_origen = registro.turno_visita

        registro.turno_visita = turno
        registro.orden = TEMP_ORDEN_BASE * 10
        db.add(registro)
        db.flush()

        filas_origen = _obtener_bucket(db, id_dia, turno_origen)
        _reasignar_ordenes_sin_choque(db, filas_origen)

    # Traer bucket destino ya con lock
    filas = _obtener_bucket(db, id_dia, turno)

    if registro is None:
        registro = ClienteDiaSemana(
            id_cliente=id_cliente,
            id_dia=id_dia,
            turno_visita=turno,
        )
    else:
        # Si ya estaba en el bucket destino, lo quitamos para reinsertarlo
        filas = [f for f in filas if f.id_cliente != id_cliente]
        registro.id_dia = id_dia
        registro.turno_visita = turno

    # Calcular índice destino
    if posicion == "inicio":
        idx = 0

    elif posicion == "final":
        idx = len(filas)

    elif posicion == "despues":
        if not despues_de_legajo:
            raise HTTPException(400, "Falta despues_de_legajo")

        idx = None
        for i, f in enumerate(filas):
            if f.id_cliente == despues_de_legajo:
                idx = i + 1
                break

        if idx is None:
            raise HTTPException(404, "Cliente referencia no encontrado")

    else:
        raise HTTPException(400, "Posición inválida")

    # Insertar en memoria y reordenar sin choques
    filas.insert(idx, registro)
    _reasignar_ordenes_sin_choque(db, filas)