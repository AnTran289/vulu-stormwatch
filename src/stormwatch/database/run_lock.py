from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.engine import Engine


@contextmanager
def pipeline_advisory_lock(engine: Engine, lock_id: int) -> Iterator[bool]:
    """Hold a PostgreSQL session advisory lock for one pipeline execution."""
    with engine.connect() as connection:
        acquired = bool(
            connection.execute(
                text("SELECT pg_try_advisory_lock(:lock_id)"),
                {"lock_id": lock_id},
            ).scalar_one()
        )
        connection.commit()

        if not acquired:
            yield False
            return

        try:
            yield True
        finally:
            connection.execute(
                text("SELECT pg_advisory_unlock(:lock_id)"),
                {"lock_id": lock_id},
            )
            connection.commit()
