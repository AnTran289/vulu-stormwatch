from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from stormwatch.database.schema import (
    flood_risk_forecasts,
)
from stormwatch.models.risk_result import (
    FloodRiskResult,
)


class RiskLoader:

    def __init__(
        self,
        engine: Engine,
    ) -> None:
        self.engine = engine

    def load(
        self,
        results: list[FloodRiskResult],
    ) -> int:

        rows = []

        for result in results:
            rows.append(
                {
                    "area_code": result.area_code,
                    "forecast_date": result.forecast_date,

                    "daily_rain_mm": result.daily_rain_mm,
                    "max_3h_rain_mm": result.max_3h_rain_mm,
                    "previous_48h_rain_mm": (
                        result.previous_48h_rain_mm
                    ),

                    "daily_rain_score": result.daily_rain_score,
                    "intensity_score": result.intensity_score,
                    "previous_rain_score": (
                        result.previous_rain_score
                    ),

                    "risk_score": result.risk_score,
                    "risk_level": result.risk_level,
                }
            )

        if not rows:
            return 0

        statement = insert(
            flood_risk_forecasts
        ).values(rows)

        statement = statement.on_conflict_do_update(
            index_elements=[
                "area_code",
                "forecast_date",
            ],
            set_={
                "daily_rain_mm": (
                    statement.excluded.daily_rain_mm
                ),
                "max_3h_rain_mm": (
                    statement.excluded.max_3h_rain_mm
                ),
                "previous_48h_rain_mm": (
                    statement.excluded.previous_48h_rain_mm
                ),
                "daily_rain_score": (
                    statement.excluded.daily_rain_score
                ),
                "intensity_score": (
                    statement.excluded.intensity_score
                ),
                "previous_rain_score": (
                    statement.excluded.previous_rain_score
                ),
                "risk_score": (
                    statement.excluded.risk_score
                ),
                "risk_level": (
                    statement.excluded.risk_level
                ),
            },
        )

        with self.engine.begin() as connection:
            connection.execute(statement)

        return len(rows)