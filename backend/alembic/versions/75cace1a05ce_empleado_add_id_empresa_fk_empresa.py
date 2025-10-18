"""empleado: add id_empresa FK -> empresa

Revision ID: 75cace1a05ce
Revises: 488d96e09c64
Create Date: 2025-09-20 19:46:17.602694
"""

from alembic import op
import sqlalchemy as sa

# --- Alembic identifiers ---
revision = "75cace1a05ce"
down_revision = "488d96e09c64"
branch_labels = None
depends_on = None

# --- Constantes de esquema/tablas ---
SCHEMA = "soderia"
EMP_TABLE = "empleado"
EMP_COL = "id_empresa"
EMP_PK = "legajo"
EMP_FK_NAME = "empleado_id_empresa_fkey"
EMPRESA_TABLE = "empresa"
EMPRESA_PK = "id_empresa"   # ⚠️ Verificá que sea la PK real; si es "id", cambiala aquí.

# --- Helpers idempotentes ---
def _index_exists(conn, schema, table, index_name):
    sql = """
    SELECT 1
    FROM pg_indexes
    WHERE schemaname = %s AND tablename = %s AND indexname = %s
    """
    return conn.exec_driver_sql(sql, (schema, table, index_name)).first() is not None

def _fk_exists(conn, schema, table, fk_name):
    sql = """
    SELECT 1
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE c.contype = 'f'
      AND n.nspname = %s
      AND t.relname = %s
      AND c.conname = %s
    """
    return conn.exec_driver_sql(sql, (schema, table, fk_name)).first() is not None


def upgrade():
    conn = op.get_bind()

    # 1) Columna: agregar solo si no existe
    op.execute(
        f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" ADD COLUMN IF NOT EXISTS "{EMP_COL}" INTEGER;'
    )

    # 2) Backfill (solo si hay NULLs) — ajustá el valor si tu empresa por defecto no es 1
    op.execute(
        sa.text(
            f'UPDATE "{SCHEMA}"."{EMP_TABLE}" '
            f'SET "{EMP_COL}" = 1 '
            f'WHERE "{EMP_COL}" IS NULL'
        )
    )

    # 3) NOT NULL (comentá esta línea si te falla por datos existentes sin empresa)
    op.execute(
        f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" ALTER COLUMN "{EMP_COL}" SET NOT NULL;'
    )

    # 4) Índice: crear solo si no existe
    ix_name = f"ix_{EMP_TABLE}_{EMP_COL}"
    if not _index_exists(conn, SCHEMA, EMP_TABLE, ix_name):
        op.create_index(ix_name, EMP_TABLE, [EMP_COL], unique=False, schema=SCHEMA)

    # 5) FK: borrar si existe y crear si falta (nombre estable)
    op.execute(
        f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" DROP CONSTRAINT IF EXISTS "{EMP_FK_NAME}";'
    )
    if not _fk_exists(conn, SCHEMA, EMP_TABLE, EMP_FK_NAME):
        # on delete policy: RESTRICT (cambiá a CASCADE o SET NULL si tu modelo lo requiere)
        op.execute(
            f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" '
            f'ADD CONSTRAINT "{EMP_FK_NAME}" '
            f'FOREIGN KEY ("{EMP_COL}") '
            f'REFERENCES "{SCHEMA}"."{EMPRESA_TABLE}" ("{EMPRESA_PK}") '
            f'ON DELETE RESTRICT;'
        )


def downgrade():
    conn = op.get_bind()

    # FK: drop si existe
    op.execute(
        f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" DROP CONSTRAINT IF EXISTS "{EMP_FK_NAME}";'
    )

    # Índice: drop si existe
    ix_name = f"ix_{EMP_TABLE}_{EMP_COL}"
    if _index_exists(conn, SCHEMA, EMP_TABLE, ix_name):
        op.drop_index(ix_name, table_name=EMP_TABLE, schema=SCHEMA)

    # Columna: drop si existe
    op.execute(
        f'ALTER TABLE "{SCHEMA}"."{EMP_TABLE}" DROP COLUMN IF EXISTS "{EMP_COL}";'
    )
