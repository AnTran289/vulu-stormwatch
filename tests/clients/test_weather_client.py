from unittest.mock import Mock

from stormwatch.clients.weather_client import WeatherClient
from stormwatch.models.location import Location


def test_requests_hourly_precipitation_probability() -> None:
    client = WeatherClient()
    client.client = Mock()
    client.client.get.return_value = {"hourly": {}}
    location = Location(
        area_code="46",
        area_name="Hue",
        latitude=16.46,
        longitude=107.59,
    )

    assert client.get_forecast(location) == {"hourly": {}}

    parameters = client.client.get.call_args.kwargs["params"]
    assert "precipitation_probability" in parameters["hourly"].split(",")
    assert parameters["timezone"] == "Asia/Ho_Chi_Minh"
