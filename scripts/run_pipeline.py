import logging
import time
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.engine import Engine

from stormwatch.config.settings import (
    BASE_DIR,
    PIPELINE_ADVISORY_LOCK_ID,
    PIPELINE_LOCATION_MAX_ATTEMPTS,
    PIPELINE_RETRY_BACKOFF_SECONDS,
    PROVINCE_COORDINATES_FILE,
    RAW_DATA_DIR,
    RAW_S3_BUCKET,
)
from stormwatch.database.connection import (
    create_database_engine,
)
from stormwatch.database.run_lock import pipeline_advisory_lock
from stormwatch.load.location_loader import LocationLoader
from stormwatch.pipeline.weather_pipeline import (
    WeatherPipeline,
)
from stormwatch.repositories.pipeline_run_repository import (
    PipelineRunRepository,
)
from stormwatch.storage.raw_file_storage import (
    RawFileStorage,
)
from stormwatch.storage.raw_storage import RawStorage
from stormwatch.storage.s3_raw_storage import S3RawStorage
from stormwatch.utils.location_loader import (
    load_locations,
)
from stormwatch.utils.logging_config import (
    configure_logging,
)

logger = logging.getLogger("stormwatch.pipeline_runner")

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
PIPELINE_EXIT_CODES = {
    "SUCCESS": EXIT_SUCCESS,
    "PARTIAL_SUCCESS": EXIT_SUCCESS,
    "FAILED": EXIT_FAILURE,
}


def pipeline_exit_code(status: str) -> int:
    try:
        return PIPELINE_EXIT_CODES[status]
    except KeyError as error:
        raise ValueError(f"Unknown pipeline status: {status}") from error


def create_raw_storage() -> RawStorage:
    if RAW_S3_BUCKET:
        logger.info("Using S3 raw storage bucket %s.", RAW_S3_BUCKET)
        return S3RawStorage(RAW_S3_BUCKET)

    logger.info("Using local raw storage directory %s.", RAW_DATA_DIR)
    return RawFileStorage(RAW_DATA_DIR)


def _run_pipeline(engine: Engine) -> int:
    raw_storage = create_raw_storage()

    pipeline = WeatherPipeline(
        raw_storage=raw_storage
    )

    locations = load_locations(
        PROVINCE_COORDINATES_FILE
    )

    location_loader = LocationLoader(
        engine
    )

    location_loader.load(
        locations
    )

    print(
        f"Loaded {len(locations)} locations."
    )

    run_id = str(uuid4())

    run_repository = PipelineRunRepository(
        engine=engine
    )

    run_repository.create_run(
        run_id=run_id,
        pipeline_name="weather_forecast",
        locations_total=len(locations),
    )

    successful_codes: set[str] = set()
    pending_locations = locations

    try:
        for attempt in range(1, PIPELINE_LOCATION_MAX_ATTEMPTS + 1):
            still_failed = []
            for location in pending_locations:
                result = pipeline.run_location(location)
                if result.success:
                    successful_codes.add(location.area_code)
                    continue

                run_repository.record_failure(
                    run_id=run_id,
                    area_code=result.area_code,
                    area_name=result.area_name,
                    stage=result.stage.value,
                    error_message=result.error_message or "Unknown pipeline error",
                    attempt=attempt,
                )
                still_failed.append(location)

            pending_locations = still_failed
            if not pending_locations:
                break

            if attempt < PIPELINE_LOCATION_MAX_ATTEMPTS:
                delay = PIPELINE_RETRY_BACKOFF_SECONDS * (2 ** (attempt - 1))
                print(
                    f"Retrying {len(pending_locations)} failed location(s) "
                    f"in {delay:g} seconds (attempt {attempt + 1}/"
                    f"{PIPELINE_LOCATION_MAX_ATTEMPTS})."
                )
                time.sleep(delay)

        successful = len(successful_codes)
        failed = len(pending_locations)
        status = (
            "SUCCESS" if failed == 0
            else "FAILED" if successful == 0
            else "PARTIAL_SUCCESS"
        )
        run_repository.finish_run(
            run_id=run_id,
            status=status,
            locations_successful=successful,
            locations_failed=failed,
        )
    except Exception as error:
        run_repository.finish_run(
            run_id=run_id,
            status="FAILED",
            locations_successful=len(successful_codes),
            locations_failed=len(locations) - len(successful_codes),
            error_message=str(error),
        )
        raise

    print(f"Pipeline run {run_id} completed with status: {status}.")
    if status == "PARTIAL_SUCCESS":
        logger.warning(
            "Pipeline completed with degraded status: %s location(s) failed.",
            failed,
        )
    return pipeline_exit_code(status)


def main() -> int:
    log_filename = datetime.now(UTC).strftime(
        "pipeline_%Y%m%d_%H%M%S.log"
    )
    configure_logging(BASE_DIR / "logs" / log_filename)

    engine = create_database_engine()
    with pipeline_advisory_lock(engine, PIPELINE_ADVISORY_LOCK_ID) as acquired:
        if not acquired:
            logger.warning(
                "Pipeline skipped because another run holds advisory lock %s.",
                PIPELINE_ADVISORY_LOCK_ID,
            )
            return EXIT_SUCCESS
        return _run_pipeline(engine)

if __name__ == "__main__":
    raise SystemExit(main())
