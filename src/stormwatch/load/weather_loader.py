from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Engine

from stormwatch.database.schema import (
    daily_weather_forecasts,
    weather_forecasts,
)
from stormwatch.models.daily_weather import (
    DailyWeatherSummary,
)
from stormwatch.models.weather_record import (
    WeatherForecastRecord,
)


class WeatherLoader:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def load_hourly(
        self,
        records: list[WeatherForecastRecord],
    ) -> int:

        rows = []

        for record in records:
            rows.append(
                {
                    "area_code": record.area_code,
                    "area_name": record.area_name,
                    "latitude": record.latitude,
                    "longitude": record.longitude,
                    "forecast_for": record.forecast_for,
                    "temperature_c": record.temperature_c,
                    "humidity_pct": record.humidity_pct,
                    "precipitation_mm": record.precipitation_mm,
                    "rain_mm": record.rain_mm,
                    "wind_speed_kmh": record.wind_speed_kmh,
                    "precipitation_probability_pct": (
                        record.precipitation_probability_pct
                    ),
                }
            )

        if not rows:
            return 0

        # Implement UPSERT
        with self.engine.begin() as connection:
            statement = insert(
                weather_forecasts
            ).values(rows)

            statement = statement.on_conflict_do_update(
                index_elements=[
                    "area_code",
                    "forecast_for",
                ],
                set_={
                    "area_name": statement.excluded.area_name,
                    "latitude": statement.excluded.latitude,
                    "longitude": statement.excluded.longitude,
                    "temperature_c": (
                        statement.excluded.temperature_c
                    ),
                    "humidity_pct": (
                        statement.excluded.humidity_pct
                    ),
                    "precipitation_mm": (
                        statement.excluded.precipitation_mm
                    ),
                    "rain_mm": statement.excluded.rain_mm,
                    "wind_speed_kmh": (
                        statement.excluded.wind_speed_kmh
                    ),
                    "precipitation_probability_pct": (
                        statement.excluded.precipitation_probability_pct
                    ),
                },
            )

            connection.execute(statement)
        
        return len(rows)

    def load_daily(
        self,
        summaries: list[DailyWeatherSummary],
    ) -> int:

        rows = []

        for summary in summaries:
            rows.append(
                {
                    "area_code": summary.area_code,
                    "area_name": summary.area_name,
                    "forecast_date": summary.forecast_date,
                    "total_rain_mm": summary.total_rain_mm,
                    "total_precipitation_mm": (
                        summary.total_precipitation_mm
                    ),
                    "min_temperature_c": (
                        summary.min_temperature_c
                    ),
                    "max_temperature_c": (
                        summary.max_temperature_c
                    ),
                    "max_wind_speed_kmh": (
                        summary.max_wind_speed_kmh
                    ),
                }
            )

        if not rows:
            return 0

        # Implement UPSERT
        with self.engine.begin() as connection:

            statement = insert(
                daily_weather_forecasts
            ).values(rows)

            statement = statement.on_conflict_do_update(
                index_elements=[
                    "area_code",
                    "forecast_date",
                ],
                set_={
                    "area_name": (
                        statement.excluded.area_name
                    ),
                    "total_rain_mm": (
                        statement.excluded.total_rain_mm
                    ),
                    "total_precipitation_mm": (
                        statement.excluded.total_precipitation_mm
                    ),
                    "min_temperature_c": (
                        statement.excluded.min_temperature_c
                    ),
                    "max_temperature_c": (
                        statement.excluded.max_temperature_c
                    ),
                    "max_wind_speed_kmh": (
                        statement.excluded.max_wind_speed_kmh
                    ),
                },
            )

            connection.execute(statement)

        return len(rows)
