from collections.abc import Callable
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from stormwatch.api.schemas.errors import ErrorResponse
from stormwatch.api.schemas.weather import DailyForecastItem, HourlyForecastItem, WeatherMapItem
from stormwatch.database.connection import create_database_engine
from stormwatch.repositories.weather_repository import WeatherRepository

router = APIRouter(prefix="/weather", tags=["weather"])
repository = WeatherRepository(create_database_engine())

ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Forecast data not found"},
    503: {"model": ErrorResponse, "description": "Weather data store unavailable"},
}


def _read_rows(operation: Callable[[], list[dict]]) -> list[dict]:
    try:
        rows = operation()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather data is temporarily unavailable.",
        ) from error
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No forecast data matched the request.",
        )
    return rows


@router.get("/map", response_model=list[WeatherMapItem], responses=ERROR_RESPONSES)
def get_weather_map(forecast_date: date) -> list[WeatherMapItem]:
    rows = _read_rows(lambda: repository.get_daily_forecasts(forecast_date))
    return [WeatherMapItem(**row) for row in rows]


@router.get(
    "/{area_code}/forecast",
    response_model=list[DailyForecastItem],
    responses=ERROR_RESPONSES,
)
def get_area_forecast(area_code: str) -> list[DailyForecastItem]:
    rows = _read_rows(lambda: repository.get_area_forecast(area_code))
    return [DailyForecastItem(**row) for row in rows]


@router.get(
    "/{area_code}/hourly",
    response_model=list[HourlyForecastItem],
    responses=ERROR_RESPONSES,
)
def get_hourly_forecast(area_code: str, forecast_date: date) -> list[HourlyForecastItem]:
    rows = _read_rows(lambda: repository.get_hourly_forecast(area_code, forecast_date))
    return [HourlyForecastItem(**row) for row in rows]
