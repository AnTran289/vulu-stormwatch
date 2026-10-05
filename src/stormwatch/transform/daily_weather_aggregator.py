from collections import defaultdict

from stormwatch.models.daily_weather import (
    DailyWeatherSummary,
)
from stormwatch.models.weather_record import (
    WeatherForecastRecord,
)


class DailyWeatherAggregator:

    def aggregate(
        self,
        records: list[WeatherForecastRecord],
    ) -> list[DailyWeatherSummary]:

        grouped_records = defaultdict(list)

        for record in records:
            forecast_date = record.forecast_for.date()

            grouped_records[forecast_date].append(record)

        summaries = []

        for forecast_date, daily_records in grouped_records.items():

            rain_values = [
                record.rain_mm
                for record in daily_records
                if record.rain_mm is not None
            ]

            precipitation_values = [
                record.precipitation_mm
                for record in daily_records
                if record.precipitation_mm is not None
            ]

            temperature_values = [
                record.temperature_c
                for record in daily_records
                if record.temperature_c is not None
            ]

            wind_values = [
                record.wind_speed_kmh
                for record in daily_records
                if record.wind_speed_kmh is not None
            ]

            summary = DailyWeatherSummary(
                area_code=daily_records[0].area_code,
                area_name=daily_records[0].area_name,
                forecast_date=forecast_date,

                total_rain_mm=sum(rain_values),

                total_precipitation_mm=sum(
                    precipitation_values
                ),

                min_temperature_c=(
                    min(temperature_values)
                    if temperature_values
                    else None
                ),

                max_temperature_c=(
                    max(temperature_values)
                    if temperature_values
                    else None
                ),

                max_wind_speed_kmh=(
                    max(wind_values)
                    if wind_values
                    else None
                ),
            )

            summaries.append(summary)

        return summaries