# defines what one clean hourly weather row should look like.

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class WeatherForecastRecord:
    area_code: str
    area_name: str

    latitude: float
    longitude: float

    forecast_for: datetime

    temperature_c: float | None
    humidity_pct: float | None
    precipitation_mm: float | None
    rain_mm: float | None
    wind_speed_kmh: float | None
    precipitation_probability_pct: int | None = None
