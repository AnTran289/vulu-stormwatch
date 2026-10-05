# SQLAlchemy's current Core API uses select() to construct SELECT statements and executes them through a connection.
from datetime import date, datetime, time, timedelta

from sqlalchemy import Select, and_, asc, desc, func, select
from sqlalchemy.engine import Engine

from stormwatch.database.schema import (
    daily_weather_forecasts,
    locations,
    weather_forecasts,
)


class WeatherRepository:

    def __init__(
        self,
        engine: Engine,
    ) -> None:
        self.engine = engine

    def _rows(self, statement: Select) -> list[dict]:
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings().all()]

    @staticmethod
    def _public_risk(rows: list[dict]) -> list[dict]:
        mapping = {
            "LOW": "LOW", "MODERATE": "MEDIUM", "MEDIUM": "MEDIUM",
            "HIGH": "HIGH", "VERY_HIGH": "SEVERE", "SEVERE": "SEVERE",
        }
        for row in rows:
            if row.get("risk_level") is not None:
                row["risk_level"] = mapping.get(row["risk_level"], row["risk_level"])
        return rows

    def get_province(self, area_code: str) -> dict | None:
        rows = self.list_provinces(area_code=area_code)
        return rows[0] if rows else None

    def list_provinces(
        self,
        *,
        area_code: str | None = None,
        risk_level: str | None = None,
        order_by: str = "province",
    ) -> list[dict]:
        from stormwatch.database.schema import flood_risk_forecasts, pipeline_runs

        latest_risk_date = select(func.max(flood_risk_forecasts.c.forecast_date)).scalar_subquery()
        next_hourly = (
            select(func.min(weather_forecasts.c.forecast_for))
            .where(weather_forecasts.c.forecast_for >= func.now())
            .scalar_subquery()
        )
        latest_hourly = select(func.max(weather_forecasts.c.forecast_for)).scalar_subquery()
        current_hourly = func.coalesce(next_hourly, latest_hourly)
        latest_update = (
            select(pipeline_runs.c.completed_at)
            .where(pipeline_runs.c.status == "SUCCESS")
            .order_by(pipeline_runs.c.completed_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        statement = (
            select(
                locations.c.area_code,
                locations.c.area_name.label("name"),
                locations.c.latitude,
                locations.c.longitude,
                weather_forecasts.c.temperature_c,
                weather_forecasts.c.precipitation_mm,
                flood_risk_forecasts.c.risk_score,
                flood_risk_forecasts.c.risk_level,
                latest_update.label("forecast_updated_at"),
            )
            .outerjoin(
                weather_forecasts,
                and_(
                    weather_forecasts.c.area_code == locations.c.area_code,
                    weather_forecasts.c.forecast_for == current_hourly,
                ),
            )
            .outerjoin(
                flood_risk_forecasts,
                and_(
                    flood_risk_forecasts.c.area_code == locations.c.area_code,
                    flood_risk_forecasts.c.forecast_date == latest_risk_date,
                ),
            )
        )
        if area_code:
            statement = statement.where(locations.c.area_code == area_code)
        if risk_level:
            statement = statement.where(flood_risk_forecasts.c.risk_level == risk_level)
        ordering = {
            "province": asc(locations.c.area_name),
            "risk": desc(flood_risk_forecasts.c.risk_score).nulls_last(),
        }
        return self._public_risk(
            self._rows(statement.order_by(ordering[order_by], locations.c.area_code))
        )

    def list_daily(self, area_code: str) -> list[dict]:
        daily_min_probability = (
            select(func.min(weather_forecasts.c.precipitation_probability_pct))
            .where(
                weather_forecasts.c.area_code == daily_weather_forecasts.c.area_code,
                func.date(weather_forecasts.c.forecast_for)
                == daily_weather_forecasts.c.forecast_date,
            )
            .correlate(daily_weather_forecasts)
            .scalar_subquery()
        )
        daily_max_probability = (
            select(func.max(weather_forecasts.c.precipitation_probability_pct))
            .where(
                weather_forecasts.c.area_code == daily_weather_forecasts.c.area_code,
                func.date(weather_forecasts.c.forecast_for)
                == daily_weather_forecasts.c.forecast_date,
            )
            .correlate(daily_weather_forecasts)
            .scalar_subquery()
        )
        statement = select(
            daily_weather_forecasts.c.area_code,
            daily_weather_forecasts.c.area_name.label("name"),
            daily_weather_forecasts.c.forecast_date,
            daily_weather_forecasts.c.total_rain_mm,
            daily_weather_forecasts.c.total_precipitation_mm,
            daily_weather_forecasts.c.min_temperature_c,
            daily_weather_forecasts.c.max_temperature_c,
            daily_weather_forecasts.c.max_wind_speed_kmh,
            daily_min_probability.label("min_precipitation_probability_pct"),
            daily_max_probability.label("max_precipitation_probability_pct"),
        ).where(daily_weather_forecasts.c.area_code == area_code)
        return self._rows(statement.order_by(daily_weather_forecasts.c.forecast_date))

    def list_hourly(self, area_code: str, forecast_date: date | None = None) -> list[dict]:
        statement = select(
            weather_forecasts.c.area_code,
            weather_forecasts.c.area_name.label("name"),
            weather_forecasts.c.forecast_for,
            weather_forecasts.c.temperature_c,
            weather_forecasts.c.humidity_pct,
            weather_forecasts.c.precipitation_mm,
            weather_forecasts.c.rain_mm,
            weather_forecasts.c.wind_speed_kmh,
            weather_forecasts.c.precipitation_probability_pct,
        ).where(weather_forecasts.c.area_code == area_code)
        if forecast_date:
            # weather_forecasts stores Open-Meteo Asia/Ho_Chi_Minh wall time
            # as a naive timestamp. Filter with the same convention; the API
            # schema converts these values to UTC for transport.
            day_start = datetime.combine(forecast_date, time.min)
            statement = statement.where(
                weather_forecasts.c.forecast_for >= day_start,
                weather_forecasts.c.forecast_for < day_start + timedelta(days=1),
            )
        return self._rows(statement.order_by(weather_forecasts.c.forecast_for))

    def list_risk(
        self,
        *,
        area_code: str | None = None,
        risk_level: str | None = None,
        latest: bool = True,
    ) -> list[dict]:
        from stormwatch.database.schema import flood_risk_forecasts

        statement = select(
            flood_risk_forecasts.c.area_code,
            locations.c.area_name.label("name"),
            locations.c.latitude,
            locations.c.longitude,
            flood_risk_forecasts.c.forecast_date,
            flood_risk_forecasts.c.daily_rain_mm,
            flood_risk_forecasts.c.max_3h_rain_mm,
            flood_risk_forecasts.c.previous_48h_rain_mm,
            flood_risk_forecasts.c.risk_score,
            flood_risk_forecasts.c.risk_level,
        ).join(locations, locations.c.area_code == flood_risk_forecasts.c.area_code)
        if latest:
            latest_date = select(func.max(flood_risk_forecasts.c.forecast_date)).scalar_subquery()
            statement = statement.where(flood_risk_forecasts.c.forecast_date == latest_date)
        if area_code:
            statement = statement.where(flood_risk_forecasts.c.area_code == area_code)
        if risk_level:
            statement = statement.where(flood_risk_forecasts.c.risk_level == risk_level)
        return self._public_risk(self._rows(statement.order_by(
            flood_risk_forecasts.c.forecast_date.desc(),
            flood_risk_forecasts.c.risk_score.desc(),
            locations.c.area_name,
        )))

    def get_daily_forecasts(
        self,
        forecast_date: date,
    ) -> list[dict]:

        statement = (
            select(
                daily_weather_forecasts.c.area_code,
                locations.c.area_name,
                locations.c.latitude,
                locations.c.longitude,
                daily_weather_forecasts.c.forecast_date,
                daily_weather_forecasts.c.total_rain_mm,
                daily_weather_forecasts.c.total_precipitation_mm,
                daily_weather_forecasts.c.min_temperature_c,
                daily_weather_forecasts.c.max_temperature_c,
                daily_weather_forecasts.c.max_wind_speed_kmh,
            )
            .join(
                locations,
                daily_weather_forecasts.c.area_code
                == locations.c.area_code,
            )
            .where(
                daily_weather_forecasts.c.forecast_date
                == forecast_date
            )       
            .order_by(
                locations.c.area_name
            )
        )

        with self.engine.connect() as connection:
            result = connection.execute(
                statement
            )

            rows = result.mappings().all()

        return [
            dict(row)
            for row in rows
        ]

    def get_area_forecast(self, area_code: str) -> list[dict]:
        statement = (
            select(daily_weather_forecasts)
            .where(daily_weather_forecasts.c.area_code == area_code)
            .order_by(daily_weather_forecasts.c.forecast_date)
        )

        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        return [dict(row) for row in rows]

    def get_hourly_forecast(
        self,
        area_code: str,
        forecast_date: date,
    ) -> list[dict]:
        day_start = datetime.combine(forecast_date, time.min)
        day_end = day_start + timedelta(days=1)
        statement = (
            select(weather_forecasts)
            .where(
                weather_forecasts.c.area_code == area_code,
                weather_forecasts.c.forecast_for >= day_start,
                weather_forecasts.c.forecast_for < day_end,
            )
            .order_by(weather_forecasts.c.forecast_for)
        )

        with self.engine.connect() as connection:
            rows = connection.execute(statement).mappings().all()

        return [dict(row) for row in rows]
