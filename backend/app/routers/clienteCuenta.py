from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_cliente_or_404_dep
from app.models.clienteCuenta import ClienteCuenta
from app.schemas.clienteCuenta import ClienteCuentaCreate, ClienteCuentaOut, ClienteCuentaUpdate

router = APIRouter(prefix="/clientes/{legajo}", tags=["ClienteCuenta"])

def _get_cuenta_or_404(db: Session, legajo: int, id_cuenta: int) -> ClienteCuenta:
    cuenta = db.execute(
        select(ClienteCuenta).where(
            ClienteCuenta.legajo == legajo,
            ClienteCuenta.id_cuenta == id_cuenta,
        )
    ).scalar_one_or_none()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada.")
    return cuenta

@router.post("/cuentas", response_model=ClienteCuentaOut, status_code=201)
def create_cuenta(legajo: int, payload: ClienteCuentaCreate, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)
    cuenta = ClienteCuenta(legajo=legajo, **payload.model_dump(exclude_unset=True))
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta

@router.get("/cuentas", response_model=list[ClienteCuentaOut])
def listar_cuentas(legajo: int, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)
    return db.execute(
        select(ClienteCuenta).where(ClienteCuenta.legajo == legajo)
    ).scalars().all()

@router.get("/cuentas/{id_cuenta}", response_model=ClienteCuentaOut)
def obtener_cuenta(legajo: int, id_cuenta: int, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)
    return _get_cuenta_or_404(db, legajo, id_cuenta)

@router.put("/cuentas/{id_cuenta}", response_model=ClienteCuentaOut)
def actualizar_cuenta(legajo: int, id_cuenta: int, payload: ClienteCuentaUpdate, db: Session = Depends(get_db)):
    get_cliente_or_404_dep(legajo, db)
    cuenta = _get_cuenta_or_404(db, legajo, id_cuenta)

    updates = payload.model_dump(exclude_unset=True, exclude={"id_cuenta"})
    for campo, valor in updates.items():
        setattr(cuenta, campo, valor)

    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta
