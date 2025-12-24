"""add pago table

Revision ID: 8cce5e38f4cc
Revises: b1384d646dc5
Create Date: 2025-12-22 20:39:15.931575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cce5e38f4cc'
down_revision: Union[str, Sequence[str], None] = 'b1384d646dc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "pago",
        sa.Column("id_pago", sa.Integer(), primary_key=True),
        sa.Column("id_empresa", sa.Integer(), sa.ForeignKey("empresa.id_empresa", ondelete="CASCADE"), nullable=False),
        sa.Column("id_cuenta", sa.Integer(), sa.ForeignKey("cliente_cuenta.id_cuenta", ondelete="SET NULL"), nullable=True),
        sa.Column("id_pedido", sa.Integer(), sa.ForeignKey("pedido.id_pedido", ondelete="SET NULL"), nullable=True),
        sa.Column("id_medio_pago", sa.Integer(), sa.ForeignKey("medio_pago.id_medio_pago"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("monto", sa.Numeric(12, 2), nullable=False),
        sa.Column("tipo_pago", sa.String(length=30), nullable=False),
        sa.Column("observacion", sa.Text(), nullable=True),
    )
    op.create_index("ix_pago_empresa_fecha", "pago", ["id_empresa", "fecha"])
    op.create_index("ix_pago_pedido", "pago", ["id_pedido"])
    op.create_index("ix_pago_cuenta", "pago", ["id_cuenta"])

def downgrade():
    op.drop_index("ix_pago_cuenta", table_name="pago")
    op.drop_index("ix_pago_pedido", table_name="pago")
    op.drop_index("ix_pago_empresa_fecha", table_name="pago")
    op.drop_table("pago")