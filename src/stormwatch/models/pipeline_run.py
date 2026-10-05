from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PipelineRun:
    run_id: str
    pipeline_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    locations_total: int
    locations_successful: int
    locations_failed: int
    error_message: str | None = None