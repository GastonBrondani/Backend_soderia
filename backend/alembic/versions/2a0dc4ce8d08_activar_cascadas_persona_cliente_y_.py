from alembic import op

# Usa tu baseline real si es distinto
revision = "2a0dc4ce8d08"
down_revision = "3696d56d07bb"
branch_labels = None
depends_on = None

SCHEMA = "soderia"

def upgrade():
    # 1) cliente.dni -> persona.dni : asegurar ON DELETE CASCADE
    # Drop de la FK actual (nombre desconocido) buscando por la columna 'dni'
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

    # Crear FK con CASCADE (nombre estable)
    op.create_foreign_key(
        "fk_cliente_persona_dni",
        source_table="cliente",
        referent_table="persona",
        local_cols=["dni"],
        remote_cols=["dni"],
        source_schema=SCHEMA,
        referent_schema=SCHEMA,
        ondelete="CASCADE",
    )

    # 2) Todas las FKs que apuntan a cliente(legajo) con ON DELETE CASCADE
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
