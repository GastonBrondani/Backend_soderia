from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_cliente_or_404_dep

from app.models.clienteCuenta import ClienteCuenta
from app.schemas.clienteCuenta import ClienteCuentaCreate, ClienteCuentaOut, ClienteCuentaUpdate


router = APIRouter(prefix="/clientes/{legajo}", tags=["ClienteCuenta"])

def _get_cuenta_by_legajo(db: Session, legajo: int) -> ClienteCuenta | None:
    return db.execute(
        select(ClienteCuenta).where(ClienteCuenta.legajo == legajo)
    ).scalars().first()

@router.post("/cuenta", response_model=ClienteCuentaOut, status_code=status.HTTP_201_CREATED)
def create_cuenta(legajo: int,payLoad: ClienteCuentaCreate, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)

    existe =  _get_cuenta_by_legajo(db, legajo)
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,detail="El cliente ya tiene una cuenta creada.")
    

    data = payLoad.model_dump(exclude_unset=True)
    cuenta = ClienteCuenta(legajo=legajo, **data)
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta

@router.get("/cuenta", response_model=ClienteCuentaOut)
def obtener_cuenta(legajo:int, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)

    cuenta = _get_cuenta_by_legajo(db, legajo)
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no tiene cuenta asociada.")
    return cuenta

@router.put("/cuenta", response_model=ClienteCuentaOut)
def actualizar_cuenta_cliente(legajo: int, payload: ClienteCuentaUpdate, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)

    cuenta = _get_cuenta_by_legajo(db, legajo)
    if not cuenta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no tiene cuenta creada.")

    updates = payload.model_dump(exclude_unset=True)
    for campo, valor in updates.items():
        setattr(cuenta, campo, valor)

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta