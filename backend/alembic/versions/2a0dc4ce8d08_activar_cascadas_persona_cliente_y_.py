

from alembic import op
import sqlalchemy as sa

SCHEMA = "soderia"

def fk_exists(conn, schema, table, fk_name):
    sql = """
    SELECT 1
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = t.relnamespace
    WHERE c.contype='f'
      AND n.nspname=%s AND t.relname=%s AND c.conname=%s
    """
    return conn.exec_driver_sql(sql, (schema, table, fk_name)).first() is not None

def drop_fk_if_exists(conn, schema, table, fk_name):
    conn.exec_driver_sql(
        f'ALTER TABLE "{schema}"."{table}" DROP CONSTRAINT IF EXISTS "{fk_name}";'
    )

def create_fk_if_missing(conn, schema, table, fk_name, cols, ref_schema, ref_table, ref_cols, ondelete=None):
    if not fk_exists(conn, schema, table, fk_name):
        ondel = f" ON DELETE {ondelete}" if ondelete else ""
        cols_sql = ", ".join(f'"{c}"' for c in cols)
        ref_cols_sql = ", ".join(f'"{c}"' for c in ref_cols)
        conn.exec_driver_sql(
            f'ALTER TABLE "{schema}"."{table}" '
            f'ADD CONSTRAINT "{fk_name}" FOREIGN KEY ({cols_sql}) '
            f'REFERENCES "{ref_schema}"."{ref_table}" ({ref_cols_sql}){ondel};'
        )


# Usa tu baseline real si es distinto
revision = "2a0dc4ce8d08"
down_revision = "3696d56d07bb"
branch_labels = None
depends_on = None

SCHEMA = "soderia"

def upgrade():
    conn = op.get_bind()

    # 1) cliente.dni -> persona.dni con ON DELETE CASCADE
    #   - dropeamos la FK que haya sobre cliente(dni) si existe (sin asumir nombre)
    op.execute(f"""
    DO $$
    DECLARE
        fkname text;
    BEGIN
        SELECT c.conname INTO fkname
        FROM pg_constraint c
        JOIN pg_class r ON r.oid = c.conrelid
        JOIN pg_namespace n ON n.oid = r.relnamespace
        JOIN pg_attribute a ON a.attrelid = r.oid AND a.attnum = ANY(c.conkey)
        WHERE n.nspname = '{SCHEMA}'
          AND r.relname = 'cliente'
          AND c.contype = 'f'
          AND a.attname = 'dni';
        IF fkname IS NOT NULL THEN
            EXECUTE format('ALTER TABLE {SCHEMA}.cliente DROP CONSTRAINT %I', fkname);
        END IF;
    END$$;
    """)

    # Creamos la FK con nombre estable si no existe
    create_fk_if_missing(
        conn,
        SCHEMA, "cliente", "fk_cliente_persona_dni", ["dni"],
        SCHEMA, "persona", ["dni"],
        ondelete="CASCADE"
    )

    # 2) FKs que apuntan a cliente(legajo) con ON DELETE CASCADE
    # ATENCIÓN: verificá que las columnas locales coincidan con tu modelo real.
    # En tu lista usás "legajo_cliente" en usuario; si en tus modelos se llama distinto, cambiá aquí.
    pairs = [
        ("cliente_cuenta_legajo_fkey",         "cliente_cuenta",      ["legajo"]),
        ("cliente_dia_semana_id_cliente_fkey", "cliente_dia_semana",  ["id_cliente"]),
        ("cliente_reparto_dia_legajo_fkey",    "cliente_reparto_dia", ["legajo"]),
        ("direccion_cliente_legajo_fkey",      "direccion_cliente",   ["legajo"]),
        ("documentos_legajo_fkey",             "documentos",          ["legajo"]),
        ("fk_usuario_cliente",                 "usuario",             ["legajo_cliente"]),
        ("historico_legajo_fkey",              "historico",           ["legajo"]),
        ("mail_cliente_legajo_fkey",           "mail_cliente",        ["legajo"]),
        ("pedido_legajo_fkey",                 "pedido",              ["legajo"]),
        ("producto_cliente_legajo_fkey",       "producto_cliente",    ["legajo"]),
        ("telefono_cliente_legajo_fkey",       "telefono_cliente",    ["legajo"]),
    ]

    for fk_name, table, local_cols in pairs:
        # dropear si existe
        drop_fk_if_exists(conn, SCHEMA, table, fk_name)
        # crear si falta
        create_fk_if_missing(
            conn,
            SCHEMA, table, fk_name, local_cols,
            SCHEMA, "cliente", ["legajo"],
            ondelete="CASCADE",
        )


def downgrade():
    # Revertir cliente.dni -> persona.dni sin CASCADE
    op.drop_constraint("fk_cliente_persona_dni", "cliente", type_="foreignkey", schema=SCHEMA)
    op.create_foreign_key(
        "fk_cliente_persona_dni",
        source_table="cliente",
        referent_table="persona",
        local_cols=["dni"],
        remote_cols=["dni"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        # sin ondelete
    )

    # Revertir FKs hacia cliente(legajo) sin CASCADE
    pairs = [
        ("cliente_cuenta_legajo_fkey",         "cliente_cuenta",      ["legajo"]),
        ("cliente_dia_semana_id_cliente_fkey", "cliente_dia_semana",  ["id_cliente"]),
        ("cliente_reparto_dia_legajo_fkey",    "cliente_reparto_dia", ["legajo"]),
        ("direccion_cliente_legajo_fkey",      "direccion_cliente",   ["legajo"]),
        ("documentos_legajo_fkey",             "documentos",          ["legajo"]),
        ("fk_usuario_cliente",                 "usuario",             ["legajo_cliente"]),
        ("historico_legajo_fkey",              "historico",           ["legajo"]),
        ("mail_cliente_legajo_fkey",           "mail_cliente",        ["legajo"]),
        ("pedido_legajo_fkey",                 "pedido",              ["legajo"]),
        ("producto_cliente_legajo_fkey",       "producto_cliente",    ["legajo"]),
        ("telefono_cliente_legajo_fkey",       "telefono_cliente",    ["legajo"]),
    ]
    for fk_name, table, local_cols in pairs:
        op.drop_constraint(fk_name, table, type_="foreignkey", schema=SCHEMA)
        op.create_foreign_key(
            fk_name,
            source_table=table,
            referent_table="cliente",
            local_cols=local_cols,
            remote_cols=["legajo"],
            source_schema=SCHEMA,
            referent_schema=SCHEMA,
            # sin ondelete
        )
