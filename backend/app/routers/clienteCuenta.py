from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_cliente_or_404_dep

from app.models.clienteCuenta import ClienteCuenta
from app.schemas.clienteCuenta import ClienteCuentaCreate, ClienteCuentaOut, ClienteCuentaUpdate


router = APIRouter(prefix="/clientes/{legajo}", tags=["ClienteCuenta"])

def _get_cuentas_by_legajo(db: Session, legajo: int) -> list[ClienteCuenta]:
    return db.execute(
        select(ClienteCuenta).where(ClienteCuenta.legajo == legajo)
    ).scalars().all()


@router.post("/cuentas", response_model=ClienteCuentaOut, status_code=201)
def create_cuenta(
    legajo: int,
    payload: ClienteCuentaCreate,
    db: Session = Depends(get_db),
):
    get_cliente_or_404_dep(legajo, db)

    cuenta = ClienteCuenta(legajo=legajo, **payload.model_dump(exclude_unset=True))
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta


@router.get("/cuenta", response_model=ClienteCuentaOut)
def obtener_cuenta(legajo:int, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)

    cuenta = _get_cuentas_by_legajo(db, legajo)
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no tiene cuenta asociada.")
    return cuenta

@router.put("/cuenta", response_model=ClienteCuentaOut)
def actualizar_cuenta_cliente(legajo: int, payload: ClienteCuentaUpdate, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)

    cuenta = _get_cuentas_by_legajo(db, legajo)
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no tiene cuenta creada.")

    updates = payload.model_dump(exclude_unset=True)
    for campo, valor in updates.items():
        setattr(cuenta, campo, valor)

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta