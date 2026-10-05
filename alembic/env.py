from logging.config import fileConfig

from sqlalchemy import text

from alembic import context
from stormwatch.config.settings import DB_SCHEMA
from stormwatch.database.connection import create_migration_engine, get_database_url
from stormwatch.database.schema import metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata
owned_tables = set(metadata.tables)


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "table":
        return name in owned_tables

    table = getattr(object_, "table", None)
    return table is None or table.name in owned_tables


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url().render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,
        version_table_schema=DB_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_migration_engine()
    try:
        with connectable.connect() as connection:
            if DB_SCHEMA != "public":
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"'))
                connection.commit()

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                include_object=include_object,
                version_table_schema=DB_SCHEMA,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
