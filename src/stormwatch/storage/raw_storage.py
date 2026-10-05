from pathlib import Path
from typing import Any, Protocol


class RawStorage(Protocol):
    def save_json(
        self,
        source: str,
        data: dict[str, Any] | list[Any],
    ) -> Path | str: ...
