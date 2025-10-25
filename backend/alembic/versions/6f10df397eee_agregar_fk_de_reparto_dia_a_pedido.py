"""Agregar fk de reparto_dia a pedido

Revision ID: 6f10df397eee
Revises: 75cace1a05ce
Create Date: 2025-10-25 16:09:52.630101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f10df397eee'
down_revision: Union[str, Sequence[str], None] = '75cace1a05ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = "soderia"

def upgrade() -> None:
    # 1) Columna nueva en pedido (nullable primero para no romper datos existentes)
    op.add_column(
        "pedido",
        sa.Column("id_repartodia", sa.Integer(), nullable=True),
        schema=SCHEMA,
    )

    # 2) Índice para joins
    op.create_index(
        "ix_pedido_id_repartodia",
        "pedido",
        ["id_repartodia"],
        unique=False,
        schema=SCHEMA,
    )

    # 3) FK → reparto_dia (elige el ondelete que prefieras)
    #    - CASCADE: si borrás un reparto_dia, borra sus pedidos
    #    - SET NULL: si borrás un reparto_dia, deja el pedido “huérfano”
    op.create_foreign_key(
        "fk_pedido_repartodia",
        source_table="pedido",
        referent_table="reparto_dia",
        local_cols=["id_repartodia"],
        remote_cols=["id_repartodia"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="CASCADE",   # o "SET NULL"
    )

    # (Opcional) si querés volverla NOT NULL:
    #  - acá primero harías un UPDATE para completar id_repartodia en los registros existentes
    # op.execute("UPDATE soderia.pedido SET id_repartodia = ...")
    # op.alter_column("pedido", "id_repartodia", nullable=False, schema=SCHEMA)


def downgrade() -> None:
    op.drop_constraint(
        "fk_pedido_repartodia",
        "pedido",
        type_="foreignkey",
        schema=SCHEMA,
    )
    op.drop_index("ix_pedido_id_repartodia", table_name="pedido", schema=SCHEMA)
    op.drop_column("pedido", "id_repartodia", schema=SCHEMA)

