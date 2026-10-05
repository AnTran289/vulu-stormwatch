import json
from pathlib import Path

from stormwatch.database.connection import (
    create_database_engine,
)
from stormwatch.load.weather_loader import (
    WeatherLoader,
)
from stormwatch.transform.daily_weather_aggregator import (
    DailyWeatherAggregator,
)
from stormwatch.transform.weather_transformer import (
    WeatherTransformer,
)


def main() -> None:

    raw_directory = Path(
        "data/raw/weather"
    )

    json_files = list(
        raw_directory.glob("*.json")
    )

    if not json_files:
        raise FileNotFoundError(
            "No raw weather files found."
        )

    raw_file = json_files[0]

    print(f"Reading: {raw_file}")

    with raw_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_data = json.load(file)

    # TRANSFORM

    transformer = WeatherTransformer()

    hourly_records = transformer.transform(
        raw_data
    )

    aggregator = DailyWeatherAggregator()

    daily_summaries = aggregator.aggregate(
        hourly_records
    )

    print(
        f"Hourly records: {len(hourly_records)}"
    )

    print(
        f"Daily summaries: {len(daily_summaries)}"
    )

    # LOAD

    engine = create_database_engine()

    loader = WeatherLoader(engine)

    hourly_loaded = loader.load_hourly(
        hourly_records
    )

    daily_loaded = loader.load_daily(
        daily_summaries
    )

    print(
        f"Loaded {hourly_loaded} hourly records."
    )

    print(
        f"Loaded {daily_loaded} daily summaries."
    )


if __name__ == "__main__":
    main()