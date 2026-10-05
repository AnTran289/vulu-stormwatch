from math import isfinite

from stormwatch.models.risk_result import FloodRiskResult


class FloodRiskCalculator:

    DAILY_WEIGHT = 0.50
    INTENSITY_WEIGHT = 0.30
    PREVIOUS_RAIN_WEIGHT = 0.20

    @staticmethod
    def _safe_rainfall(value: float | None) -> float:
        """Return a usable, non-negative rainfall value for partial feeds."""
        if value is None:
            return 0.0

        try:
            rainfall = float(value)
        except (TypeError, ValueError):
            return 0.0

        if not isfinite(rainfall) or rainfall < 0:
            return 0.0

        return rainfall

    def calculate_daily_rain_score(
        self,
        rain_mm: float | None,
    ) -> float:
        rain_mm = self._safe_rainfall(rain_mm)
        if rain_mm < 30:
            return 0

        if rain_mm < 50:
            return 20

        if rain_mm < 100:
            return 40

        if rain_mm < 200:
            return 70

        if rain_mm < 400:
            return 90

        return 100

    def calculate_intensity_score(
        self,
        max_3h_rain_mm: float | None,
    ) -> float:
        max_3h_rain_mm = self._safe_rainfall(max_3h_rain_mm)
        if max_3h_rain_mm < 20:
            return 0

        if max_3h_rain_mm < 50:
            return 30

        if max_3h_rain_mm < 100:
            return 70

        return 100

    def calculate_previous_rain_score(
        self,
        previous_48h_rain_mm: float | None,
    ) -> float:
        previous_48h_rain_mm = self._safe_rainfall(previous_48h_rain_mm)
        if previous_48h_rain_mm < 30:
            return 0

        if previous_48h_rain_mm < 70:
            return 30

        if previous_48h_rain_mm < 150:
            return 60

        return 100

    def classify_risk(
        self,
        risk_score: float,
    ) -> str:
        if risk_score < 25:
            return "LOW"

        if risk_score < 50:
            return "MODERATE"

        if risk_score < 75:
            return "HIGH"

        return "VERY_HIGH"

    def calculate(
        self,
        *,
        area_code: str,
        area_name: str,
        forecast_date,
        daily_rain_mm: float | None,
        max_3h_rain_mm: float | None,
        previous_48h_rain_mm: float | None,
    ) -> FloodRiskResult:

        daily_rain_mm = self._safe_rainfall(daily_rain_mm)
        max_3h_rain_mm = self._safe_rainfall(max_3h_rain_mm)
        previous_48h_rain_mm = self._safe_rainfall(previous_48h_rain_mm)

        daily_score = self.calculate_daily_rain_score(
            daily_rain_mm
        )

        intensity_score = self.calculate_intensity_score(
            max_3h_rain_mm
        )

        previous_score = self.calculate_previous_rain_score(
            previous_48h_rain_mm
        )

        risk_score = (
            daily_score * self.DAILY_WEIGHT
            + intensity_score * self.INTENSITY_WEIGHT
            + previous_score * self.PREVIOUS_RAIN_WEIGHT
        )

        risk_score = round(
            risk_score,
            2,
        )

        return FloodRiskResult(
            area_code=area_code,
            area_name=area_name,
            forecast_date=forecast_date,
            daily_rain_mm=daily_rain_mm,
            max_3h_rain_mm=max_3h_rain_mm,
            previous_48h_rain_mm=previous_48h_rain_mm,
            daily_rain_score=daily_score,
            intensity_score=intensity_score,
            previous_rain_score=previous_score,
            risk_score=risk_score,
            risk_level=self.classify_risk(
                risk_score
            ),
        )
