# Create a province model.

from dataclasses import dataclass


@dataclass(frozen=True)
class Province:
    code: str
    name: str
    administrative_unit: str | None = None