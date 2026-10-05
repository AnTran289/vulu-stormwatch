from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.engine import Engine

from stormwatch.database.schema import pipeline_failures, pipeline_runs


class PipelineRunRepository:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create_run(
        self,
        run_id: str,
        pipeline_name: str,
        locations_total: int,
    ) -> None:

        row = {
            "run_id": run_id,
            "pipeline_name": pipeline_name,
            "status": "RUNNING",
            "started_at": datetime.now(UTC),
            "locations_total": locations_total,
            "locations_successful": 0,
            "locations_failed": 0,
        }

        with self.engine.begin() as connection:
            connection.execute(
                pipeline_runs.insert(),
                row,
            )

    def get_latest_run(self) -> dict | None:
        statement = (
            select(pipeline_runs)
            .order_by(pipeline_runs.c.started_at.desc())
            .limit(1)
        )
        with self.engine.connect() as connection:
            row = connection.execute(statement).mappings().first()
        return dict(row) if row else None

    def get_latest_successful_run(self) -> dict | None:
        statement = (
            select(pipeline_runs)
            .where(pipeline_runs.c.status == "SUCCESS")
            .order_by(pipeline_runs.c.completed_at.desc())
            .limit(1)
        )
        with self.engine.connect() as connection:
            row = connection.execute(statement).mappings().first()
        return dict(row) if row else None

    # finish function
    def record_failure(
        self,
        *,
        run_id: str,
        area_code: str,
        area_name: str,
        stage: str,
        error_message: str,
        attempt: int,
    ) -> None:
        row = {
            "run_id": run_id,
            "area_code": area_code,
            "area_name": area_name,
            "stage": stage,
            "error_message": error_message,
            "attempt": attempt,
            "created_at": datetime.now(UTC),
        }
        with self.engine.begin() as connection:
            connection.execute(pipeline_failures.insert(), row)

    def finish_run(
        self,
        run_id: str,
        status: str,
        locations_successful: int,
        locations_failed: int,
        error_message: str | None = None,
    ) -> None:

        statement = (
            update(pipeline_runs)
            .where(
                pipeline_runs.c.run_id == run_id
            )
            .values(
                status=status,
                completed_at=datetime.now(UTC),
                locations_successful=locations_successful,
                locations_failed=locations_failed,
                error_message=error_message,
            )
        )

        with self.engine.begin() as connection:
            connection.execute(statement)
