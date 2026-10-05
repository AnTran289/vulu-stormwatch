import logging
import sys
from pathlib import Path
from typing import Any


def configure_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Make Windows terminal output support Vietnamese characters
    stdout: Any = sys.stdout
    stdout.reconfigure(encoding="utf-8")

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_file,
                encoding="utf-8",
            ),
        ],
    )
