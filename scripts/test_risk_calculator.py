from datetime import date

from stormwatch.transform.risk_calculator import (
    FloodRiskCalculator,
)


def main() -> None:
    calculator = FloodRiskCalculator()

    result = calculator.calculate(
        area_code="48",
        area_name="Đà Nẵng",
        forecast_date=date.today(),
        daily_rain_mm=135,
        max_3h_rain_mm=65,
        previous_48h_rain_mm=85,
    )

    print(result)


if __name__ == "__main__":
    main()
