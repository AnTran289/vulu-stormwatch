from unittest.mock import MagicMock

from stormwatch.database.run_lock import pipeline_advisory_lock


def lock_engine(acquired: bool) -> tuple[MagicMock, MagicMock]:
    engine = MagicMock()
    connection = engine.connect.return_value.__enter__.return_value
    connection.execute.return_value.scalar_one.return_value = acquired
    return engine, connection


def test_holds_and_releases_advisory_lock() -> None:
    engine, connection = lock_engine(True)

    with pipeline_advisory_lock(engine, 123) as acquired:
        assert acquired is True
        assert connection.execute.call_count == 1

    assert connection.execute.call_count == 2
    assert "pg_try_advisory_lock" in str(connection.execute.call_args_list[0].args[0])
    assert "pg_advisory_unlock" in str(connection.execute.call_args_list[1].args[0])
    assert connection.commit.call_count == 2


def test_does_not_unlock_when_lock_is_unavailable() -> None:
    engine, connection = lock_engine(False)

    with pipeline_advisory_lock(engine, 123) as acquired:
        assert acquired is False

    assert connection.execute.call_count == 1
    assert connection.commit.call_count == 1


def test_releases_lock_when_pipeline_body_raises() -> None:
    engine, connection = lock_engine(True)

    try:
        with pipeline_advisory_lock(engine, 123):
            raise RuntimeError("pipeline failed")
    except RuntimeError:
        pass

    assert connection.execute.call_count == 2
    assert "pg_advisory_unlock" in str(connection.execute.call_args_list[1].args[0])
    assert connection.commit.call_count == 2
