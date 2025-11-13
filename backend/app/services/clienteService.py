""" from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException


from app.models.cliente import Cliente
from app.schemas.clienteDetalle import ClienteDetalleOut


class ClienteService:

    # Muestro todo lo detallado al cliente.
    @staticmethod
    def get_detalle_cliente(db: Session, legajo: int) -> ClienteDetalleOut:
        stmt = (
            select(Cliente)
            .options(
                joinedload(Cliente.persona),
                selectinload(Cliente.direcciones),
                selectinload(Cliente.telefonos),
                selectinload(Cliente.emails),
                selectinload(Cliente.productos),
                selectinload(Cliente.cuentas),
                selectinload(Cliente.dias_semanas),
            )
            .where(Cliente.legajo == legajo)
        )
        cliente = db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        return ClienteDetalleOut.model_validate(cliente)
 """





# Emma
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException

from app.models.cliente import Cliente
from app.schemas.clienteDetalle import ClienteDetalleOut
from app.models.historico import Historico
from app.models.pedido import Pedido      # (opcional si querés tipar)



class ClienteService:
    @staticmethod
    def get_detalle_cliente(db: Session, legajo: int) -> ClienteDetalleOut:
        stmt = (
            select(Cliente)
            .options(
                joinedload(Cliente.persona),
                selectinload(Cliente.direcciones),
                selectinload(Cliente.telefonos),
                selectinload(Cliente.emails),
                selectinload(Cliente.productos),
                selectinload(Cliente.cuentas),
                selectinload(Cliente.dias_semanas),
                # ❌ podemos sacar:
                # selectinload(Cliente.pedidos),
                # selectinload(Cliente.historicos).selectinload(Historico.evento),
            )
            .where(Cliente.legajo == legajo)
        )
        cliente = db.execute(stmt).scalars().first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # ClienteDetalleOut tiene pedidos/historicos con default_factory=list,
        # así que van como listas vacías por ahora
        return ClienteDetalleOut.model_validate(cliente)

