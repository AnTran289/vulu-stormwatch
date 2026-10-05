# Orchestrator

import logging
from pathlib import Path

import pandas as pd

from stormwatch.clients.weather_client import WeatherClient
from stormwatch.extract.weather_extractor import WeatherExtractor
from stormwatch.models.extraction_result import ExtractionResult
from stormwatch.models.location import Location
from stormwatch.storage.raw_file_storage import RawFileStorage

logger = logging.getLogger(__name__)


def load_locations(csv_path: Path) -> list[Location]:
    dataframe = pd.read_csv(csv_path)

    locations = []

    for row in dataframe.itertuples(index=False):
        locations.append(
            Location(
                area_code=str(row.area_code),
                area_name=row.area_name,
                latitude=float(row.latitude),
                longitude=float(row.longitude),
            )
        )

    return locations


def run_extraction(
    locations_path: Path,
    raw_directory: Path,
) -> list[ExtractionResult]:
    locations = load_locations(locations_path)

    weather_client = WeatherClient()
    raw_storage = RawFileStorage(raw_directory)

    extractor = WeatherExtractor(
        client=weather_client,
        storage=raw_storage,
    )

    results = []

    for location in locations:
        result = extractor.extract_location(location)
        results.append(result)

    successful = sum(result.success for result in results)
    failed = len(results) - successful

    logger.info(
        "Extraction completed: %s successful, %s failed",
        successful,
        failed,
    )

    return results