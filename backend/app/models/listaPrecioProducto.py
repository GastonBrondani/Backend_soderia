from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .listaDePrecios import ListaDePrecios
    from .producto import Producto

from sqlalchemy import Integer, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

SCHEMA = "soderia"


class ListaPrecioProducto(Base):
    __tablename__ = "lista_precio_producto"
    __table_args__ = ({"schema": SCHEMA},)

    # PK compuesta: (id_lista, id_producto)
    id_lista: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.lista_de_precios.id_lista", name="fk_listaprecio_lista"),
        primary_key=True,
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(f"{SCHEMA}.producto.id_producto", name="fk_listaprecio_producto"),
        primary_key=True,
        nullable=False,
    )

    # Campos
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # --------- RELATIONSHIPS (completas) ---------
    # many-to-one -> ListaDePrecios
    lista: Mapped["ListaDePrecios"] = relationship(
        "ListaDePrecios",
        back_populates="productos",
        lazy="selectin",
    )

    # many-to-one -> Producto
    producto: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="listas_precios",  # en Producto: listas_precios = relationship("ListaPrecioProducto", back_populates="producto")
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ListaPrecioProducto lista={self.id_lista} producto={self.id_producto} precio={self.precio}>"
