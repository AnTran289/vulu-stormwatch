from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from stormwatch.api.main import app
from stormwatch.api.routes import health, risk, weather
from stormwatch.database.schema import (
    daily_weather_forecasts,
    flood_risk_forecasts,
    locations,
    metadata,
    pipeline_runs,
)
from stormwatch.repositories.pipeline_run_repository import PipelineRunRepository
from stormwatch.repositories.risk_repository import RiskRepository
from stormwatch.repositories.weather_repository import WeatherRepository


def test_map_repositories_flow_through_api() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    forecast_date = date(2026, 8, 18)
    completed_at = datetime.now(UTC) - timedelta(minutes=18)
    with engine.begin() as connection:
        connection.execute(
            locations.insert(),
            {"area_code": "01", "area_name": "Ha Noi", "latitude": 21.0, "longitude": 105.8},
        )
        connection.execute(
            daily_weather_forecasts.insert(),
            {
                "area_code": "01", "area_name": "Ha Noi", "forecast_date": forecast_date,
                "total_rain_mm": 12, "total_precipitation_mm": 13,
                "min_temperature_c": 22, "max_temperature_c": 30, "max_wind_speed_kmh": 15,
            },
        )
        connection.execute(
            flood_risk_forecasts.insert(),
            {
                "area_code": "01", "forecast_date": forecast_date,
                "daily_rain_mm": 12, "max_3h_rain_mm": 7, "previous_48h_rain_mm": 20,
                "daily_rain_score": 0, "intensity_score": 0, "previous_rain_score": 0,
                "risk_score": 0, "risk_level": "LOW",
            },
        )
        connection.execute(
            pipeline_runs.insert(),
            {
                "run_id": "run-1",
                "pipeline_name": "weather_forecast",
                "status": "SUCCESS",
                "started_at": completed_at - timedelta(minutes=2),
                "completed_at": completed_at,
                "locations_total": 34,
                "locations_successful": 34,
                "locations_failed": 0,
            },
        )

    original_weather = weather.repository
    original_risk = risk.repository
    original_status = health.repository
    weather.repository = WeatherRepository(engine)
    risk.repository = RiskRepository(engine)
    health.repository = PipelineRunRepository(engine)
    try:
        client = TestClient(app)
        weather_response = client.get("/weather/map?forecast_date=2026-08-18")
        risk_response = client.get("/risk/map?forecast_date=2026-08-18")
        missing_response = client.get("/weather/99/forecast")
        status_response = client.get("/status")
    finally:
        weather.repository = original_weather
        risk.repository = original_risk
        health.repository = original_status

    assert weather_response.status_code == 200
    assert weather_response.json()[0]["area_code"] == "01"
    assert risk_response.status_code == 200
    assert risk_response.json()[0]["risk_level"] == "LOW"
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "No forecast data matched the request."}
    assert status_response.status_code == 200
    assert status_response.json()["current_status"] == "SUCCESS"
    assert status_response.json()["failed_provinces_count"] == 0
    assert status_response.json()["is_stale"] is False
    assert 1_070 <= status_response.json()["data_age_seconds"] <= 1_090
