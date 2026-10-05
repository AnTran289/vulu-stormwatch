# Represent whether each extraction succeeded or failed.

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExtractionResult:
    source: str
    area_code: str
    area_name: str
    success: bool
    file_path: Path | str | None = None
    raw_data: dict[str, Any] | None = None
    error_message: str | None = None
