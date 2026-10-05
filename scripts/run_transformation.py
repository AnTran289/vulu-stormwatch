import json
from pathlib import Path

from stormwatch.transform.daily_weather_aggregator import (
    DailyWeatherAggregator,
)
from stormwatch.transform.weather_transformer import (
    WeatherTransformer,
)


def main() -> None:

    raw_directory = Path("data/raw/weather")

    json_files = list(
        raw_directory.glob("*.json")
    )

    if not json_files:
        raise FileNotFoundError(
            "No raw weather JSON files found."
        )

    raw_file = json_files[0]

    print(f"Reading: {raw_file}")

    with raw_file.open(
        mode="r",
        encoding="utf-8",
    ) as file:
        raw_data = json.load(file)

    transformer = WeatherTransformer()

    records = transformer.transform(raw_data)

    aggregator = DailyWeatherAggregator()

    daily_summaries = aggregator.aggregate(records)

    print("\nDaily summaries:")

    for summary in daily_summaries:
        print(summary)

    print(
        f"Transformed {len(records)} weather records."
    )

    for record in records[:5]:
        print(record)


if __name__ == "__main__":
    main()