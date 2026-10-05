from datetime import datetime
from math import isfinite
from typing import Any

from stormwatch.models.weather_record import WeatherForecastRecord


class WeatherTransformer:

    @staticmethod
    def _precipitation_probability(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(
                "Weather payload contains a non-numeric "
                "'precipitation_probability' value."
            )
        if not isfinite(value) or not float(value).is_integer():
            raise ValueError(
                "Weather payload contains an invalid "
                "'precipitation_probability' value."
            )

        probability = int(value)
        if not 0 <= probability <= 100:
            raise ValueError(
                "Weather payload contains an out-of-range "
                "'precipitation_probability' value."
            )
        return probability

    def transform(
        self,
        raw_data: dict[str, Any],
    ) -> list[WeatherForecastRecord]:

        if "area" not in raw_data:
            raise ValueError(
                "Raw weather data is missing 'area'."
            )

        if "payload" not in raw_data:
            raise ValueError(
                "Raw weather data is missing 'payload'."
            )

        area = raw_data["area"]
        payload = raw_data["payload"]

        if "hourly" not in payload:
            raise ValueError(
                "Weather payload is missing hourly data."
            )

        hourly = payload["hourly"]

        required_fields = [
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "precipitation_probability",
            "rain",
            "wind_speed_10m",
        ]

        for field in required_fields:
            if field not in hourly:
                raise ValueError(
                    f"Weather payload is missing '{field}'."
                )

        times = hourly["time"]
        if not isinstance(times, list):
            raise ValueError("Weather payload field 'time' must be an array.")

        for field in required_fields:
            values = hourly[field]
            if not isinstance(values, list):
                raise ValueError(
                    f"Weather payload field '{field}' must be an array."
                )
            if len(values) != len(times):
                raise ValueError(
                    f"Weather payload field '{field}' is not aligned with 'time'."
                )

        records = []

        for index, time_value in enumerate(times):

            record = WeatherForecastRecord(
                area_code=str(area["code"]),
                area_name=area["name"],
                latitude=float(area["latitude"]),
                longitude=float(area["longitude"]),
                forecast_for=datetime.fromisoformat(
                    time_value
                ),
                temperature_c=hourly[
                    "temperature_2m"
                ][index],
                humidity_pct=hourly[
                    "relative_humidity_2m"
                ][index],
                precipitation_mm=hourly[
                    "precipitation"
                ][index],
                rain_mm=hourly["rain"][index],
                wind_speed_kmh=hourly[
                    "wind_speed_10m"
                ][index],
                precipitation_probability_pct=(
                    self._precipitation_probability(
                        hourly["precipitation_probability"][index]
                    )
                ),
            )

            records.append(record)

        return records
