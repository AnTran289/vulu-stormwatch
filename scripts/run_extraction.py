from datetime import UTC, datetime

from stormwatch.config.settings import (
    BASE_DIR,
    RAW_DATA_DIR,
)
from stormwatch.extract.extraction_pipeline import run_extraction
from stormwatch.utils.logging_config import configure_logging


def main() -> None:
    log_filename = datetime.now(UTC).strftime(
        "extraction_%Y%m%d_%H%M%S.log"
    )

    configure_logging(
        BASE_DIR / "logs" / log_filename
    )

    run_extraction(
        locations_path=(
            BASE_DIR
            / "data"
            / "reference"
            / "province_coordinates.csv"
        ),
        raw_directory=RAW_DATA_DIR,
    )


if __name__ == "__main__":
    main()