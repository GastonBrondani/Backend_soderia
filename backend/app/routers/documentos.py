from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.documentos import Documentos

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.get("/cliente/{legajo}")
def listar_documentos_cliente(
    legajo: int,
    db: Session = Depends(get_db),
):
    docs = db.execute(
        select(Documentos)
        .where(Documentos.legajo == legajo)
        .order_by(Documentos.fecha_carga.desc())
    ).scalars().all()

    return [
        {
            "id_documento": d.id_documento,
            "nombre_archivo": d.nombre_archivo,
            "tipo_archivo": d.tipo_archivo,
            "url": d.url_archivo,
            "fecha": d.fecha_carga,
            "observacion": d.observacion,
        }
        for d in docs
    ]
