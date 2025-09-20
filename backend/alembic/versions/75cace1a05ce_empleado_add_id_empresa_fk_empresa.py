"""empleado: add id_empresa FK -> empresa

Revision ID: 75cace1a05ce
Revises: 488d96e09c64
Create Date: 2025-09-20 19:46:17.602694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75cace1a05ce'
down_revision: Union[str, Sequence[str], None] = '488d96e09c64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SCHEMA = "soderia"
EMP_TABLE = "empleado"
EMP_COL = "id_empresa"
EMP_PK = "legajo"
EMP_FK_NAME = "empleado_id_empresa_fkey"
EMPRESA_TABLE = "empresa"
EMPRESA_PK = "id_empresa"

def upgrade():
    # 1) Agregar columna nullable (paso seguro para datos existentes)
    op.add_column(
        EMP_TABLE,
        sa.Column(EMP_COL, sa.Integer(), nullable=True),
        schema=SCHEMA,
    )

    # 2) Backfill: asignar empresa por defecto (usamos 1 porque en tu proyecto
    #    ya existe y la usás como empresa única)
    op.execute(
        sa.text(f'UPDATE "{SCHEMA}"."{EMP_TABLE}" SET "{EMP_COL}" = 1 WHERE "{EMP_COL}" IS NULL')
    )

    # 3) Hacer NOT NULL
    op.alter_column(
        EMP_TABLE,
        EMP_COL,
        existing_type=sa.Integer(),
        nullable=False,
        schema=SCHEMA,
    )

    # 4) (Opcional) Índice para mejorar consultas por empresa
    op.create_index(
        f"ix_{EMP_TABLE}_{EMP_COL}",
        EMP_TABLE,
        [EMP_COL],
        unique=False,
        schema=SCHEMA,
    )

    # 5) FK hacia empresa(id_empresa)
    #    Por defecto es RESTRICT (no CASCADE). Es más seguro para no borrar empleados
    #    si se borra una empresa por accidente. Si querés CASCADE, agregá ondelete="CASCADE".
    op.create_foreign_key(
        EMP_FK_NAME,
        source_table=EMP_TABLE,
        referent_table=EMPRESA_TABLE,
        local_cols=[EMP_COL],
        remote_cols=[EMPRESA_PK],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete=None,  # cambiar a "CASCADE" si así lo deseás
        initially=None,
        deferrable=None,
        use_alter=True,
    )


def downgrade():
    # El orden inverso: primero soltar FK e índice, luego la columna
    op.drop_constraint(EMP_FK_NAME, EMP_TABLE, type_="foreignkey", schema=SCHEMA)
    op.drop_index(f"ix_{EMP_TABLE}_{EMP_COL}", table_name=EMP_TABLE, schema=SCHEMA)
    op.drop_column(EMP_TABLE, EMP_COL, schema=SCHEMA)
