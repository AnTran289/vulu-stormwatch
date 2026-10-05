import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from stormwatch.transform.risk_calculator import (
    FloodRiskCalculator,
)
from stormwatch.transform.risk_input_builder import (
    RiskInputBuilder,
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

    with raw_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        raw_data = json.load(file)

    transformer = WeatherTransformer()

    records = transformer.transform(
        raw_data
    )

    today = datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    ).date()

    historical_records = [
        record
        for record in records
        if record.forecast_for.date() < today
    ]

    forecast_records = [
        record
        for record in records
        if record.forecast_for.date() >= today
    ]

    if not forecast_records:
        raise ValueError(
            "Weather data contains no current or future records."
        )

    forecast_date = today

    input_builder = RiskInputBuilder()

    inputs = input_builder.build_for_date(
        records=records,
        forecast_date=forecast_date,
    )

    calculator = FloodRiskCalculator()

    result = calculator.calculate(
        area_code=records[0].area_code,
        area_name=records[0].area_name,
        forecast_date=forecast_date,
        daily_rain_mm=inputs[
            "daily_rain_mm"
        ],
        max_3h_rain_mm=inputs[
            "max_3h_rain_mm"
        ],
        previous_48h_rain_mm=inputs[
            "previous_48h_rain_mm"
        ],
    )

    print(
        f"Historical records: {len(historical_records)}"
    )
    print(
        f"Forecast records: {len(forecast_records)}"
    )
    print(result)


if __name__ == "__main__":
    main()
