from sqlalchemy.pool import NullPool

from stormwatch.config.settings import DB_MAX_OVERFLOW, DB_POOL_SIZE
from stormwatch.database.connection import (
    create_database_engine,
    create_migration_engine,
)


def test_application_engine_is_shared_and_bounded() -> None:
    create_database_engine.cache_clear()
    first = create_database_engine()
    second = create_database_engine()

    try:
        assert first is second
        assert first.pool.size() == DB_POOL_SIZE
        assert first.pool._max_overflow == DB_MAX_OVERFLOW
    finally:
        first.dispose()
        create_database_engine.cache_clear()


def test_migration_engine_does_not_retain_connections() -> None:
    engine = create_migration_engine()
    try:
        assert isinstance(engine.pool, NullPool)
    finally:
        engine.dispose()
