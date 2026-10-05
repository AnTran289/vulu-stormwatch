# Create the connection
import re
from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, Engine
from sqlalchemy.pool import NullPool

from stormwatch.config.settings import (
    DB_HOST,
    DB_MAX_OVERFLOW,
    DB_NAME,
    DB_PASSWORD,
    DB_POOL_RECYCLE_SECONDS,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT_SECONDS,
    DB_PORT,
    DB_SCHEMA,
    DB_USER,
)

POSTGRES_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def get_database_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )


def get_database_schema() -> str:
    if not POSTGRES_IDENTIFIER.fullmatch(DB_SCHEMA):
        raise ValueError("DB_SCHEMA must be a valid unquoted PostgreSQL identifier.")
    return DB_SCHEMA


def _set_search_path(
    dbapi_connection: Any,
    _connection_record: Any,
    _connection_proxy: Any,
) -> None:
    schema = get_database_schema()
    with dbapi_connection.cursor() as cursor:
        cursor.execute(f'SET search_path TO "{schema}", public')


def _configure_search_path(engine: Engine) -> Engine:
    event.listen(engine.pool, "checkout", _set_search_path)
    return engine


@lru_cache(maxsize=1)
def create_database_engine() -> Engine:
    """Return the single bounded application engine for this process."""
    return _configure_search_path(
        create_engine(
            get_database_url(),
            pool_size=DB_POOL_SIZE,
            max_overflow=DB_MAX_OVERFLOW,
            pool_timeout=DB_POOL_TIMEOUT_SECONDS,
            pool_recycle=DB_POOL_RECYCLE_SECONDS,
            pool_pre_ping=True,
        )
    )


def create_migration_engine() -> Engine:
    """Create a disposable engine that never retains migration connections."""
    return _configure_search_path(
        create_engine(get_database_url(), poolclass=NullPool)
    )
