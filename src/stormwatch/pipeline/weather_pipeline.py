import logging

from stormwatch.clients.weather_client import WeatherClient
from stormwatch.database.connection import create_database_engine
from stormwatch.extract.weather_extractor import WeatherExtractor
from stormwatch.load.risk_loader import RiskLoader
from stormwatch.load.weather_loader import WeatherLoader
from stormwatch.models.extraction_result import ExtractionResult
from stormwatch.models.location import Location
from stormwatch.models.pipeline_result import (
    LocationPipelineResult,
    PipelineStage,
)
from stormwatch.storage.raw_storage import RawStorage
from stormwatch.transform.daily_weather_aggregator import (
    DailyWeatherAggregator,
)
from stormwatch.transform.risk_calculator import (
    FloodRiskCalculator,
)
from stormwatch.transform.risk_input_builder import (
    RiskInputBuilder,
)
from stormwatch.transform.weather_transformer import (
    WeatherTransformer,
)
from stormwatch.utils.datetime_utils import vietnam_today

logger = logging.getLogger(__name__)


class WeatherPipeline:

    # assembling all the components
    def __init__(
        self,
        raw_storage: RawStorage,
    ) -> None:

        self.extractor = WeatherExtractor(
            client=WeatherClient(),
            storage=raw_storage,
        )

        self.transformer = WeatherTransformer()

        self.aggregator = DailyWeatherAggregator()

        self.risk_input_builder = RiskInputBuilder()

        self.risk_calculator = FloodRiskCalculator()

        self.loader = WeatherLoader(
            create_database_engine()
        )

        self.risk_loader = RiskLoader(
            create_database_engine()
        )

    def run_location(
        self,
        location: Location,
    ) -> LocationPipelineResult:

        logger.info(
            "Starting pipeline for %s",
            location.area_name,
        )

        stage = PipelineStage.EXTRACT

        # -------------------------
        # EXTRACT
        # -------------------------
        try:
            extraction_result: ExtractionResult = (
                self.extractor.extract_location(location)
            )

            if not extraction_result.success:
                logger.error(
                    "Extraction failed for %s: %s",
                    location.area_name,
                    extraction_result.error_message,
                )

                return LocationPipelineResult(
                    area_code=location.area_code,
                    area_name=location.area_name,
                    success=False,
                    stage=PipelineStage.EXTRACT,
                    error_message=extraction_result.error_message,
                )

            logger.info(
                "Extraction completed for %s",
                location.area_name,
            )

            raw_data = extraction_result.raw_data

            if raw_data is None:
                raise RuntimeError(
                    "Extraction succeeded but returned no raw data."
                )

            # -------------------------
            # TRANSFORM
            # -------------------------
            stage = PipelineStage.TRANSFORM
            hourly_records = self.transformer.transform(
                raw_data
            )

            today = vietnam_today()

            historical_records = [
                record
                for record in hourly_records
                if record.forecast_for.date() < today
            ]

            forecast_records = [
                record
                for record in hourly_records
                if record.forecast_for.date() >= today
            ]

            logger.info(
                (
                    "Transformation completed for %s: %d historical "
                    "and %d forecast hourly records"
                ),
                location.area_name,
                len(historical_records),
                len(forecast_records),
            )

            #-------------------------
            # AGGREGATE
            #-------------------------
            daily_summaries = self.aggregator.aggregate(
                forecast_records
            )

            risk_results = []
            stage = PipelineStage.RISK

            for summary in daily_summaries:
                inputs = self.risk_input_builder.build_for_date(
                    records=hourly_records,
                    forecast_date=summary.forecast_date,
                )

                risk = self.risk_calculator.calculate(
                    area_code=summary.area_code,
                    area_name=summary.area_name,
                    forecast_date=summary.forecast_date,
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

                risk_results.append(risk)

            logger.info(
                "Created %d daily summaries and %d risk results.",
                len(daily_summaries),
                len(risk_results),
            )

            for risk in risk_results:
                logger.info(
                    "Risk for %s on %s: score=%s level=%s",
                    risk.area_name,
                    risk.forecast_date,
                    risk.risk_score,
                    risk.risk_level,
                )

            # -------------------------
            # LOAD
            # -------------------------
            stage = PipelineStage.LOAD
            hourly_loaded = self.loader.load_hourly(
                hourly_records
            )

            daily_loaded = self.loader.load_daily(
                daily_summaries
            )

            risk_loaded = self.risk_loader.load(
                risk_results
            )

            logger.info(
                "Load %s hourly records.",
                hourly_loaded,
            )

            logger.info(
                "Load %s daily summaries.",
                daily_loaded,
            )

            logger.info(
                "Loaded %s flood risk records.",
                risk_loaded,
            )

            logger.info(
                "Pipeline completed for %s",
                location.area_name,
            )
            return LocationPipelineResult(
                area_code=location.area_code,
                area_name=location.area_name,
                success=True,
                stage=PipelineStage.COMPLETE,
            )

        except Exception as error:
            logger.exception(
                "Pipeline failed for %s during %s",
                location.area_name,
                stage.value,
            )
            return LocationPipelineResult(
                area_code=location.area_code,
                area_name=location.area_name,
                success=False,
                stage=stage,
                error_message=str(error),
            )
