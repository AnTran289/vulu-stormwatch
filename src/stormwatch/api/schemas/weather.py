# defines what the frontend is allowed to receive
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

VIETNAM_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


class WeatherMapItem(BaseModel):

    area_code: str
    area_name: str

    latitude: float
    longitude: float

    forecast_date: date

    total_rain_mm: float
    total_precipitation_mm: float

    min_temperature_c: float | None
    max_temperature_c: float | None

    max_wind_speed_kmh: float | None


class DailyForecastItem(BaseModel):
    area_code: str
    area_name: str
    forecast_date: date
    total_rain_mm: float
    total_precipitation_mm: float
    min_temperature_c: float | None
    max_temperature_c: float | None
    max_wind_speed_kmh: float | None


class HourlyForecastItem(BaseModel):
    area_code: str
    area_name: str
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
