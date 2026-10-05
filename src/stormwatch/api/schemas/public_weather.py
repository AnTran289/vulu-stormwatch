from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

VIETNAM_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class PipelineRunStatus(StrEnum):
    NEVER_RUN = "NEVER_RUN"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class AwareTimestamps(BaseModel):
    @field_validator(
        "forecast_updated_at", "started_at", "completed_at", "last_update_time",
        check_fields=False,
    )
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)


class ProvinceMapMarker(AwareTimestamps):
    area_code: str
    name: str
    latitude: float
    longitude: float
    temperature_c: float | None
    precipitation_mm: float | None
    risk_score: float | None
    risk_level: RiskLevel | None
    forecast_updated_at: datetime | None


class ProvinceSummary(ProvinceMapMarker):
    pass


class DailyForecast(BaseModel):
    area_code: str
    name: str
    forecast_date: date
    total_rain_mm: float
    total_precipitation_mm: float
    min_temperature_c: float | None
    max_temperature_c: float | None
    max_wind_speed_kmh: float | None
    min_precipitation_probability_pct: int | None
    max_precipitation_probability_pct: int | None


class HourlyForecast(AwareTimestamps):
    area_code: str
    name: str
    forecast_for: datetime
    temperature_c: float | None
    humidity_pct: float | None
    precipitation_mm: float | None
    rain_mm: float | None
    wind_speed_kmh: float | None
    precipitation_probability_pct: int | None

    @field_validator("forecast_for")
    @classmethod
    def ensure_forecast_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=VIETNAM_TIMEZONE)
        return value.astimezone(UTC)


class FloodRisk(BaseModel):
    area_code: str
    name: str
    latitude: float
    longitude: float
    forecast_date: date
    daily_rain_mm: float
    max_3h_rain_mm: float
    previous_48h_rain_mm: float
    risk_score: float
    risk_level: RiskLevel


class PipelineRun(AwareTimestamps):
    run_id: str
    pipeline_name: str
    status: PipelineRunStatus
    started_at: datetime
    completed_at: datetime | None
    locations_total: int
    locations_successful: int
    locations_failed: int


class PipelineStatus(AwareTimestamps):
    current_status: PipelineRunStatus
    latest_run: PipelineRun | None
    latest_successful_run: PipelineRun | None
    last_update_time: datetime | None
    failed_provinces_count: int
    data_age_seconds: int | None
    slightly_stale_after_seconds: int
    stale_after_seconds: int
    freshness_level: Literal["FRESH", "SLIGHTLY_STALE", "STALE", "UNKNOWN"]
    is_stale: bool


class ErrorResponse(BaseModel):
    detail: str
