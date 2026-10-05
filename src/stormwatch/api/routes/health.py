from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from stormwatch.api.schemas.errors import ErrorResponse
from stormwatch.api.schemas.status import PipelineRunSummary, PipelineStatusResponse
from stormwatch.config.settings import STATUS_STALE_AFTER_SECONDS
from stormwatch.database.connection import create_database_engine
from stormwatch.repositories.pipeline_run_repository import PipelineRunRepository

router = APIRouter(tags=["health"])
repository = PipelineRunRepository(create_database_engine())


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


@router.get(
    "/status",
    response_model=PipelineStatusResponse,
    responses={
        503: {"model": ErrorResponse, "description": "Pipeline status unavailable"},
    },
)
def pipeline_status() -> PipelineStatusResponse:
    try:
        latest_row = repository.get_latest_run()
        successful_row = repository.get_latest_successful_run()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline status is temporarily unavailable.",
        ) from error

    latest_run = PipelineRunSummary(**latest_row) if latest_row else None
    latest_success = PipelineRunSummary(**successful_row) if successful_row else None
    last_update = latest_success.completed_at if latest_success else None
    age_seconds = (
        max(0, int((datetime.now(UTC) - _as_utc(last_update)).total_seconds()))
        if last_update
        else None
    )

    return PipelineStatusResponse(
        current_status=latest_run.status if latest_run else "NEVER_RUN",
        latest_run=latest_run,
        latest_successful_run=latest_success,
        last_update_time=last_update,
        failed_provinces_count=latest_run.locations_failed if latest_run else 0,
        data_age_seconds=age_seconds,
        stale_after_seconds=STATUS_STALE_AFTER_SECONDS,
        is_stale=age_seconds is None or age_seconds > STATUS_STALE_AFTER_SECONDS,
    )
