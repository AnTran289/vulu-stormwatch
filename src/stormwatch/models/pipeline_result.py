from dataclasses import dataclass
from enum import StrEnum


class PipelineStage(StrEnum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    RISK = "risk"
    LOAD = "load"
    COMPLETE = "complete"


@dataclass(frozen=True)
class LocationPipelineResult:
    area_code: str
    area_name: str
    success: bool
    stage: PipelineStage
    error_message: str | None = None
