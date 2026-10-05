from datetime import UTC, date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from stormwatch.api.main import app
from stormwatch.api.routes.public_weather import get_engine
from stormwatch.database.schema import (
    daily_weather_forecasts,
    flood_risk_forecasts,
    locations,
    metadata,
    pipeline_runs,
    weather_forecasts,
)


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(locations.insert(), [
            {"area_code": "01", "area_name": "Ha Noi", "latitude": 21.0, "longitude": 105.8},
            {"area_code": "46", "area_name": "Hue", "latitude": 16.46, "longitude": 107.59},
        ])
        connection.execute(weather_forecasts.insert(), {
            "area_code": "01", "area_name": "Ha Noi", "latitude": 21.0,
            "longitude": 105.8, "forecast_for": datetime(2026, 8, 22, 1, tzinfo=UTC),
            "temperature_c": 29.1, "humidity_pct": 80, "precipitation_mm": 4.2,
            "rain_mm": 4.0, "wind_speed_kmh": 12,
            "precipitation_probability_pct": 82,
        })
        connection.execute(daily_weather_forecasts.insert(), {
            "area_code": "01", "area_name": "Ha Noi", "forecast_date": date(2026, 8, 22),
            "total_rain_mm": 8, "total_precipitation_mm": 9,
            "min_temperature_c": 25, "max_temperature_c": 31, "max_wind_speed_kmh": 14,
        })
        connection.execute(flood_risk_forecasts.insert(), {
            "area_code": "01", "forecast_date": date(2026, 8, 22), "daily_rain_mm": 8,
            "max_3h_rain_mm": 5, "previous_48h_rain_mm": 18, "daily_rain_score": 10,
            "intensity_score": 20, "previous_rain_score": 30, "risk_score": 32,
            "risk_level": "MODERATE",
        })
        connection.execute(pipeline_runs.insert(), {
            "run_id": "run-1", "pipeline_name": "weather", "status": "SUCCESS",
            "started_at": datetime(2026, 8, 22, tzinfo=UTC),
            "completed_at": datetime(2026, 8, 22, 0, 5, tzinfo=UTC),
            "locations_total": 2, "locations_successful": 1, "locations_failed": 1,
        })
    app.dependency_overrides[get_engine] = lambda: engine
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        metadata.drop_all(engine)


def test_recovered_province_endpoints(client):
    response = client.get("/api/weather/provinces")
    assert response.status_code == 200
    assert [item["area_code"] for item in response.json()] == ["01", "46"]
    assert response.json()[0]["risk_level"] == "MEDIUM"
    assert response.json()[1]["temperature_c"] is None

    detail = client.get("/api/weather/provinces/01")
    assert detail.status_code == 200
    assert detail.json()["temperature_c"] == 29.1
    assert client.get("/api/weather/provinces/99").status_code == 404


def test_recovered_forecast_risk_and_status_endpoints(client):
    daily = client.get("/api/weather/provinces/01/daily")
    assert daily.status_code == 200
    assert daily.json()[0]["name"] == "Ha Noi"
    assert daily.json()[0]["min_precipitation_probability_pct"] == 82
    assert daily.json()[0]["max_precipitation_probability_pct"] == 82

    hourly = client.get(
        "/api/weather/provinces/01/hourly", params={"forecast_date": "2026-08-22"}
    )
    assert hourly.status_code == 200
    assert hourly.json()[0]["forecast_for"].endswith("Z")
    assert hourly.json()[0]["precipitation_probability_pct"] == 82

    risk = client.get("/api/weather/risk", params={"risk_level": "MEDIUM"})
    assert risk.status_code == 200
    assert risk.json()[0]["area_code"] == "01"

    status = client.get("/api/weather/status")
    assert status.status_code == 200
    assert status.json()["current_status"] == "SUCCESS"
    assert status.json()["failed_provinces_count"] == 1


def test_naive_vietnam_forecast_time_is_serialized_as_utc() -> None:
    from stormwatch.api.schemas.public_weather import HourlyForecast

    forecast = HourlyForecast(
        area_code="92",
        name="Can Tho",
        forecast_for=datetime(2026, 9, 2, 11),
        temperature_c=29,
        humidity_pct=80,
        precipitation_mm=1.2,
        rain_mm=1.2,
        wind_speed_kmh=10,
        precipitation_probability_pct=82,
    )

    assert forecast.forecast_for == datetime(2026, 9, 2, 4, tzinfo=UTC)
