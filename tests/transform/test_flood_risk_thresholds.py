from datetime import date

import pytest

from stormwatch.transform.risk_calculator import FloodRiskCalculator


@pytest.fixture
def calculator() -> FloodRiskCalculator:
    return FloodRiskCalculator()


@pytest.mark.parametrize(
    ("rainfall", "expected"),
    [
        (0, 0), (29.99, 0), (30, 20), (49.99, 20), (50, 40),
        (99.99, 40), (100, 70), (199.99, 70), (200, 90),
        (399.99, 90), (400, 100),
    ],
)
def test_daily_rain_thresholds(calculator, rainfall, expected):
    assert calculator.calculate_daily_rain_score(rainfall) == expected


@pytest.mark.parametrize(
    ("rainfall", "expected"),
    [(0, 0), (19.99, 0), (20, 30), (49.99, 30), (50, 70),
     (99.99, 70), (100, 100)],
)
def test_intensity_thresholds(calculator, rainfall, expected):
    assert calculator.calculate_intensity_score(rainfall) == expected


@pytest.mark.parametrize(
    ("rainfall", "expected"),
    [(0, 0), (29.99, 0), (30, 30), (69.99, 30), (70, 60),
     (149.99, 60), (150, 100)],
)
def test_previous_rain_thresholds(calculator, rainfall, expected):
    assert calculator.calculate_previous_rain_score(rainfall) == expected


@pytest.mark.parametrize(
    ("score", "expected"),
    [(0, "LOW"), (24.99, "LOW"), (25, "MODERATE"),
     (49.99, "MODERATE"), (50, "HIGH"), (74.99, "HIGH"),
     (75, "VERY_HIGH"), (100, "VERY_HIGH")],
)
def test_risk_level_boundaries(calculator, score, expected):
    assert calculator.classify_risk(score) == expected


def test_weighted_risk_result(calculator):
    result = calculator.calculate(
        area_code="01",
        area_name="Ha Noi",
        forecast_date=date(2026, 8, 14),
        daily_rain_mm=100,
        max_3h_rain_mm=50,
        previous_48h_rain_mm=70,
    )

    assert result.risk_score == 68.0
    assert result.risk_level == "HIGH"


@pytest.mark.parametrize("missing", [None, float("nan"), float("inf"), -1])
def test_incomplete_rainfall_is_safe(calculator, missing):
    result = calculator.calculate(
        area_code="01",
        area_name="Ha Noi",
        forecast_date=date(2026, 8, 14),
        daily_rain_mm=missing,
        max_3h_rain_mm=missing,
        previous_48h_rain_mm=missing,
    )

    assert result.daily_rain_mm == 0
    assert result.max_3h_rain_mm == 0
    assert result.previous_48h_rain_mm == 0
    assert result.risk_score == 0
    assert result.risk_level == "LOW"
