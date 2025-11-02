from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException

from app.models.cliente import Cliente
from app.schemas.clienteDetalle import ClienteDetalleOut 


class ClienteService:

    #Muestro todo lo detallado al cliente.
    @staticmethod
    def get_detalle_cliente(db:Session,legajo:int) ->ClienteDetalleOut:
        stmt = (select(Cliente).options(joinedload(Cliente.persona),
                                        selectinload(Cliente.direcciones),
                                        selectinload(Cliente.telefonos),
                                        selectinload(Cliente.emails),
                                        selectinload(Cliente.productos),
                                        selectinload(Cliente.cuentas))
                                        .where(Cliente.legajo == legajo))
        cliente=db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return ClienteDetalleOut.model_validate(cliente)