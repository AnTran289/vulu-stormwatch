# Connect the weather client to raw file storage

import logging

from stormwatch.clients.weather_client import WeatherClient
from stormwatch.models.extraction_result import ExtractionResult
from stormwatch.models.location import Location
from stormwatch.storage.raw_storage import RawStorage

logger = logging.getLogger(__name__)


class WeatherExtractor:
    def __init__(
        self,
        client: WeatherClient,
        storage: RawStorage,
    ) -> None:
        self.client = client
        self.storage = storage

    def extract_location(
        self,
        location: Location,
    ) -> ExtractionResult:
        logger.info(
            "Extracting weather for %s",
            location.area_name,
        )

        try:
            weather_data = self.client.get_forecast(location)

            raw_record = {
                "source": "open_meteo",
                "area": {
                    "code": location.area_code,
                    "name": location.area_name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                },
                "payload": weather_data,
            }

            file_path = self.storage.save_json(
                source="weather",
                data=raw_record,
            )

            logger.info(
                "Weather extraction completed for %s",
                location.area_name,
            )

            return ExtractionResult(
                source="open_meteo",
                area_code=location.area_code,
                area_name=location.area_name,
                success=True,
                file_path=file_path,
                raw_data=raw_record,
            )

        except Exception as error:
            logger.exception(
                "Weather extraction failed for %s",
                location.area_name,
            )

            return ExtractionResult(
                source="open_meteo",
                area_code=location.area_code,
                area_name=location.area_name,
                success=False,
                error_message=str(error),
            )
