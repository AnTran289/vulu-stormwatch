from datetime import date, timedelta
from math import isfinite

from stormwatch.models.weather_record import (
    WeatherForecastRecord,
)


class RiskInputBuilder:

    @staticmethod
    def _safe_rainfall(value: float | None) -> float:
        if value is None:
            return 0.0

        try:
            rainfall = float(value)
        except (TypeError, ValueError):
            return 0.0

        return rainfall if isfinite(rainfall) and rainfall >= 0 else 0.0

    def build_for_date(
        self,
        *,
        records: list[WeatherForecastRecord],
        forecast_date: date,
    ) -> dict[str, float]:
        target_records = [
            record
            for record in records
            if record.forecast_for.date() == forecast_date
        ]

        daily_rain_mm = sum(
            self._safe_rainfall(record.rain_mm)
            for record in target_records
        )

        max_3h_rain_mm = self._calculate_max_3h_rain(
            target_records
        )

        previous_48h_rain_mm = (
            self._calculate_previous_48h_rain(
                records=records,
                forecast_date=forecast_date,
            )
        )

        return {
            "daily_rain_mm": daily_rain_mm,
            "max_3h_rain_mm": max_3h_rain_mm,
            "previous_48h_rain_mm": previous_48h_rain_mm,
        }

    def _calculate_max_3h_rain(
        self,
        records: list[WeatherForecastRecord],
    ) -> float:
        sorted_records = sorted(
            records,
            key=lambda record: record.forecast_for,
        )

        rain_values = [
            self._safe_rainfall(record.rain_mm)
            for record in sorted_records
        ]

        if not rain_values:
            return 0.0

        max_3h = 0.0

        for index in range(len(rain_values)):
            window = rain_values[index:index + 3]

            total = sum(window)

            max_3h = max(
                max_3h,
                total,
            )

        return max_3h

    def _calculate_previous_48h_rain(
        self,
        *,
        records: list[WeatherForecastRecord],
        forecast_date: date,
    ) -> float:
        start_time = (
            forecast_date
            - timedelta(days=2)
        )

        previous_records = [
            record
            for record in records
            if (
                start_time
                <= record.forecast_for.date()
                < forecast_date
            )
        ]

        return sum(
            self._safe_rainfall(record.rain_mm)
            for record in previous_records
        )
