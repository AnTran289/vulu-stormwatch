from datetime import date

from sqlalchemy import select
from sqlalchemy.engine import Engine

from stormwatch.database.schema import (
    flood_risk_forecasts,
    locations,
)


class RiskRepository:

    def __init__(
        self,
        engine: Engine,
    ) -> None:
        self.engine = engine

    def get_risk_map(
        self,
        forecast_date: date,
    ) -> list[dict]:

        statement = (
            select(
                flood_risk_forecasts.c.area_code,
                locations.c.area_name,
                locations.c.latitude,
                locations.c.longitude,
                flood_risk_forecasts.c.forecast_date,
                flood_risk_forecasts.c.daily_rain_mm,
                flood_risk_forecasts.c.max_3h_rain_mm,
                flood_risk_forecasts.c.previous_48h_rain_mm,
                flood_risk_forecasts.c.risk_score,
                flood_risk_forecasts.c.risk_level,
            )
            .join(
                locations,
                flood_risk_forecasts.c.area_code
                == locations.c.area_code,
            )
            .where(
                flood_risk_forecasts.c.forecast_date
                == forecast_date
            )
            .order_by(
                locations.c.area_name
            )
        )

        with self.engine.connect() as connection:
            rows = connection.execute(
                statement
            ).mappings().all()

        return [
            dict(row)
            for row in rows
        ]