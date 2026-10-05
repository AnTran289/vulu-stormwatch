from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FloodRiskResult:
    area_code: str
    area_name: str
    forecast_date: date

    daily_rain_mm: float
    max_3h_rain_mm: float
    previous_48h_rain_mm: float

    daily_rain_score: float
    intensity_score: float
    previous_rain_score: float

    risk_score: float
    risk_level: str
