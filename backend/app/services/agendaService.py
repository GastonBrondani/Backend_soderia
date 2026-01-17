# app/services/agenda_service.py

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.clienteDiaSemana import ClienteDiaSemana


def insertar_cliente_en_agenda(
    *,
    db: Session,
    id_cliente: int,
    id_dia: int,
    turno: str,
    posicion: str,
    despues_de_legajo: int | None,
):
    # 🔒 Lock del conjunto
    filas = db.execute(
        select(ClienteDiaSemana)
        .where(
            ClienteDiaSemana.id_dia == id_dia,
            ClienteDiaSemana.turno_visita == turno,
        )
        .order_by(ClienteDiaSemana.orden)
        .with_for_update()
    ).scalars().all()

    # Quitar si ya estaba
    filas = [f for f in filas if f.id_cliente != id_cliente]

    # Calcular índice destino
    if posicion == "inicio":
        idx = 0
    elif posicion == "final":
        idx = len(filas)
    elif posicion == "despues":
        if not despues_de_legajo:
            raise HTTPException(400, "Falta despues_de_legajo")

        for i, f in enumerate(filas):
            if f.id_cliente == despues_de_legajo:
                idx = i + 1
                break
        else:
            raise HTTPException(404, "Cliente referencia no encontrado")
    else:
        raise HTTPException(400, "Posición inválida")

    # Insertar virtualmente
    nuevo = ClienteDiaSemana(
        id_cliente=id_cliente,
        id_dia=id_dia,
        turno_visita=turno,
    )
    filas.insert(idx, nuevo)

    # 🔁 Reasignar órdenes limpias
    for i, f in enumerate(filas, start=1):
        f.orden = i
        db.add(f)

