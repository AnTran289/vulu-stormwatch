from datetime import date, datetime

from stormwatch.models.weather_record import WeatherForecastRecord
from stormwatch.transform.risk_input_builder import RiskInputBuilder


def record(hour: datetime, rain: float | None) -> WeatherForecastRecord:
    return WeatherForecastRecord(
        area_code="01",
        area_name="Ha Noi",
        latitude=21.0,
        longitude=105.8,
        forecast_for=hour,
        temperature_c=25,
        humidity_pct=80,
        precipitation_mm=rain,
        rain_mm=rain,
        wind_speed_kmh=5,
    )


def test_builds_daily_intensity_and_previous_48_hour_inputs() -> None:
    records = [
        record(datetime(2026, 8, 16, 12), 4),
        record(datetime(2026, 8, 17, 12), 6),
        record(datetime(2026, 8, 18, 0), 1),
        record(datetime(2026, 8, 18, 1), 2),
        record(datetime(2026, 8, 18, 2), 3),
        record(datetime(2026, 8, 18, 3), 1),
    ]

    result = RiskInputBuilder().build_for_date(
        records=records,
        forecast_date=date(2026, 8, 18),
    )

    assert result == {
        "daily_rain_mm": 7,
        "max_3h_rain_mm": 6,
        "previous_48h_rain_mm": 10,
    }


def test_sanitizes_missing_invalid_and_negative_rainfall() -> None:
    records = [
        record(datetime(2026, 8, 18, 0), None),
        record(datetime(2026, 8, 18, 1), -2),
        record(datetime(2026, 8, 18, 2), float("nan")),
    ]

    result = RiskInputBuilder().build_for_date(
        records=records,
        forecast_date=date(2026, 8, 18),
    )

    assert result == {
        "daily_rain_mm": 0,
        "max_3h_rain_mm": 0,
        "previous_48h_rain_mm": 0,
    }
