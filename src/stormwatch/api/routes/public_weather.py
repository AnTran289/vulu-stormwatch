import logging
from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from stormwatch.api.schemas.public_weather import (
    DailyForecast,
    ErrorResponse,
    FloodRisk,
    HourlyForecast,
    PipelineStatus,
    ProvinceMapMarker,
    ProvinceSummary,
    RiskLevel,
)
from stormwatch.config.settings import (
    STATUS_SLIGHTLY_STALE_AFTER_SECONDS,
    STATUS_STALE_AFTER_SECONDS,
)
from stormwatch.database.connection import create_database_engine
from stormwatch.repositories.pipeline_run_repository import PipelineRunRepository
from stormwatch.repositories.weather_repository import WeatherRepository

PUBLIC_TO_STORED_RISK_LEVEL = {
    RiskLevel.LOW: "LOW", RiskLevel.MEDIUM: "MODERATE",
    RiskLevel.HIGH: "HIGH", RiskLevel.SEVERE: "VERY_HIGH",
}
logger = logging.getLogger("stormwatch.api.weather")
router = APIRouter(prefix="/api/weather", tags=["weather"])
engine = create_database_engine()
AreaCode = Annotated[str, Path(min_length=1, max_length=16, pattern=r"^[0-9]+$")]
ERRORS: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Province not found"},
    422: {"model": ErrorResponse, "description": "Invalid query or path parameter"},
    500: {"model": ErrorResponse, "description": "Weather data query failed"},
}


def get_engine() -> Engine:
    return engine


def get_repository(engine: Engine = Depends(get_engine)) -> WeatherRepository:
    return WeatherRepository(engine)


def execute(operation, operation_name: str):
    try:
        return operation()
    except SQLAlchemyError as exc:
        logger.error("StormWatch database query failed", extra={
            "event": "weather_db_query_failure", "operation": operation_name,
            "error_type": type(exc).__name__,
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Weather data is temporarily unavailable.") from exc


def require_province(repository: WeatherRepository, area_code: str) -> dict:
    province = execute(lambda: repository.get_province(area_code), "get_province")
    if province is None:
        logger.warning("Weather province was not found", extra={
            "event": "weather_province_missing", "area_code": area_code,
        })
        raise HTTPException(status_code=404, detail="Province not found.")
    return province


@router.get("/provinces", response_model=list[ProvinceMapMarker], responses=ERRORS)
def list_provinces(
    risk_level: RiskLevel | None = None,
    order_by: Literal["province", "risk"] = "province",
    repository: WeatherRepository = Depends(get_repository),
) -> list[dict]:
    return execute(lambda: repository.list_provinces(
        risk_level=PUBLIC_TO_STORED_RISK_LEVEL[risk_level] if risk_level else None,
        order_by=order_by,
    ), "list_provinces")


@router.get("/provinces/{area_code}", response_model=ProvinceSummary, responses=ERRORS)
def get_province(area_code: AreaCode,
                 repository: WeatherRepository = Depends(get_repository)) -> dict:
    return require_province(repository, area_code)


@router.get("/provinces/{area_code}/daily", response_model=list[DailyForecast], responses=ERRORS)
def get_daily(area_code: AreaCode,
              repository: WeatherRepository = Depends(get_repository)) -> list[dict]:
    require_province(repository, area_code)
    return execute(lambda: repository.list_daily(area_code), "list_daily")


@router.get("/provinces/{area_code}/hourly", response_model=list[HourlyForecast], responses=ERRORS)
def get_hourly(
    area_code: AreaCode, forecast_date: date | None = None,
    repository: WeatherRepository = Depends(get_repository),
) -> list[dict]:
    require_province(repository, area_code)
    return execute(lambda: repository.list_hourly(area_code, forecast_date), "list_hourly")


@router.get("/risk", response_model=list[FloodRisk], responses=ERRORS)
def list_risk(
    risk_level: RiskLevel | None = None, latest_snapshot: bool = True,
    repository: WeatherRepository = Depends(get_repository),
) -> list[dict]:
    return execute(lambda: repository.list_risk(
        risk_level=PUBLIC_TO_STORED_RISK_LEVEL[risk_level] if risk_level else None,
        latest=latest_snapshot,
    ), "list_risk")


@router.get("/risk/{area_code}", response_model=list[FloodRisk], responses=ERRORS)
def get_risk(
    area_code: AreaCode, latest_snapshot: bool = True,
    repository: WeatherRepository = Depends(get_repository),
) -> list[dict]:
    require_province(repository, area_code)
    return execute(lambda: repository.list_risk(area_code=area_code, latest=latest_snapshot),
                   "list_risk_by_province")


@router.get("/status", response_model=PipelineStatus, responses={500: ERRORS[500]})
def get_pipeline_status(engine: Engine = Depends(get_engine)) -> dict:
    repository = PipelineRunRepository(engine)
    latest_row = execute(repository.get_latest_run, "get_latest_run")
    success_row = execute(repository.get_latest_successful_run, "get_latest_successful_run")
    last_update = success_row["completed_at"] if success_row else None
    if last_update is None:
        data_age_seconds = None
    else:
        last_update_utc = (last_update.replace(tzinfo=UTC) if last_update.tzinfo is None
                           else last_update.astimezone(UTC))
        data_age_seconds = max(0, int((datetime.now(UTC) - last_update_utc).total_seconds()))
    if data_age_seconds is None:
        freshness_level = "UNKNOWN"
    elif data_age_seconds < STATUS_SLIGHTLY_STALE_AFTER_SECONDS:
        freshness_level = "FRESH"
    elif data_age_seconds <= STATUS_STALE_AFTER_SECONDS:
        freshness_level = "SLIGHTLY_STALE"
    else:
        freshness_level = "STALE"
    return {
        "current_status": latest_row["status"] if latest_row else "NEVER_RUN",
        "latest_run": latest_row, "latest_successful_run": success_row,
        "last_update_time": last_update,
        "failed_provinces_count": latest_row["locations_failed"] if latest_row else 0,
        "data_age_seconds": data_age_seconds,
        "slightly_stale_after_seconds": STATUS_SLIGHTLY_STALE_AFTER_SECONDS,
        "stale_after_seconds": STATUS_STALE_AFTER_SECONDS,
        "freshness_level": freshness_level,
        "is_stale": freshness_level in {"STALE", "UNKNOWN"},
    }
