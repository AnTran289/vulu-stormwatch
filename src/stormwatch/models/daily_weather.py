from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DailyWeatherSummary:
    area_code: str
    area_name: str
    forecast_date: date

    total_rain_mm: float
    total_precipitation_mm: float

    min_temperature_c: float | None
    max_temperature_c: float | None

    max_wind_speed_kmh: float | None