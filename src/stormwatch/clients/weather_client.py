# Request Open-Meteo weather data

from typing import Any

from stormwatch.clients.base_client import APIClient
from stormwatch.config.settings import OPEN_METEO_BASE_URL
from stormwatch.models.location import Location


class WeatherClient:
    def __init__(self) -> None:
        self.client = APIClient(OPEN_METEO_BASE_URL)

    def get_forecast(
        self,
        location: Location,
    ) -> dict[str, Any]:
        parameters = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "hourly": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "precipitation_probability,"
                "rain,"
                "wind_speed_10m"
            ),
            "forecast_days": 7,
            "past_days": 2,
            "timezone": "Asia/Ho_Chi_Minh",
        }

        response = self.client.get(params=parameters)

        if not isinstance(response, dict):
            raise ValueError("Weather API returned invalid data.")

        return response
