from datetime import date

from pydantic import BaseModel


class RiskMapItem(BaseModel):
    area_code: str
    area_name: str

    latitude: float
    longitude: float

    forecast_date: date

    daily_rain_mm: float
    max_3h_rain_mm: float
    previous_48h_rain_mm: float

    risk_score: float
    risk_level: str