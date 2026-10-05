from copy import deepcopy

import pytest

from stormwatch.transform.weather_transformer import WeatherTransformer


@pytest.fixture()
def raw_weather() -> dict:
    return {
        "area": {
            "code": "46",
            "name": "Hue",
            "latitude": 16.46,
            "longitude": 107.59,
        },
        "payload": {
            "hourly": {
                "time": ["2026-09-02T10:00", "2026-09-02T11:00"],
                "temperature_2m": [28.0, 29.0],
                "relative_humidity_2m": [88, 84],
                "precipitation": [0.0, 3.2],
                "precipitation_probability": [0, 82],
                "rain": [0.0, 3.2],
                "wind_speed_10m": [8.0, 10.0],
            }
        },
    }


def test_maps_precipitation_probability_to_matching_hour(raw_weather: dict) -> None:
    records = WeatherTransformer().transform(raw_weather)

    assert [record.precipitation_probability_pct for record in records] == [0, 82]
    # Open-Meteo was requested in Asia/Ho_Chi_Minh, so the internal naive
    # timestamp intentionally represents Vietnam wall time.
    assert records[1].forecast_for.isoformat() == "2026-09-02T11:00:00"


def test_accepts_null_and_one_hundred_percent(raw_weather: dict) -> None:
    raw_weather["payload"]["hourly"]["precipitation_probability"] = [None, 100]

    records = WeatherTransformer().transform(raw_weather)

    assert [record.precipitation_probability_pct for record in records] == [None, 100]


@pytest.mark.parametrize("value", [-1, 101, 40.5, float("nan"), "80", True])
def test_rejects_invalid_precipitation_probability(
    raw_weather: dict,
    value: object,
) -> None:
    raw_weather["payload"]["hourly"]["precipitation_probability"][0] = value

    with pytest.raises(ValueError, match="precipitation_probability"):
        WeatherTransformer().transform(raw_weather)


def test_rejects_hourly_array_that_is_not_aligned(raw_weather: dict) -> None:
    misaligned = deepcopy(raw_weather)
    misaligned["payload"]["hourly"]["precipitation_probability"] = [82]

    with pytest.raises(ValueError, match="not aligned with 'time'"):
        WeatherTransformer().transform(misaligned)
