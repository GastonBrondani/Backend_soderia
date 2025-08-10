from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class MovimientoStock(Base):
    __tablename__ = "movimiento_stock"
    __table_args__ = (
        {'schema': 'soderia'},
        CheckConstraint(
            "tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE', 'TRASPASO')",
            name="movimiento_stock_tipo_movimiento_check"
        ),
    )

    id_movimiento_stock = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("soderia.producto.id_producto", ondelete="RESTRICT"), nullable=False)
    id_recorrido = Column(Integer, ForeignKey("soderia.recorrido.id_recorrido", ondelete="SET NULL"), nullable=True)
    id_pedido = Column(Integer, ForeignKey("soderia.pedido.id_pedido", ondelete="SET NULL"), nullable=True)
    fecha = Column(DateTime, nullable=False, server_default=func.now())
    tipo_movimiento = Column(String(20), nullable=False)
    cantidad = Column(Integer, nullable=False)
    observacion = Column(Text, nullable=True)

    producto = relationship("Producto", back_populates="movimientos_stock")
    recorrido = relationship("Recorrido", back_populates="movimientos_stock")
    pedido = relationship("Pedido", back_populates="movimientos_stock")
