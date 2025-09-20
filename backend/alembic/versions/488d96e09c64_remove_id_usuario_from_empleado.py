"""remove id_usuario from empleado

Revision ID: 488d96e09c64
Revises: 2a0dc4ce8d08
Create Date: 2025-09-20 19:22:26.740346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '488d96e09c64'
down_revision: Union[str, Sequence[str], None] = '2a0dc4ce8d08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("empleado", "id_usuario",schema="soderia")


def downgrade() -> None:
    op.add_column("empleado",sa.Column('id_usuario', sa.Integer(), nullable=True),schema="soderia")
