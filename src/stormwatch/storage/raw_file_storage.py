# Save original API data before transforming it.

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class RawFileStorage:
    def __init__(self, base_directory: Path) -> None:
        self.base_directory = base_directory

    def save_json(
        self,
        source: str,
        data: dict[str, Any] | list[Any],
    ) -> Path:
        extracted_at = datetime.now(UTC)

        source_directory = self.base_directory / source
        source_directory.mkdir(parents=True, exist_ok=True)

        filename = extracted_at.strftime(
            "%Y%m%d_%H%M%S_%f.json"
        )

        file_path = source_directory / filename

        with file_path.open(
            mode="w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return file_path