from datetime import datetime

from pydantic import BaseModel


class PipelineRunSummary(BaseModel):
    run_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    locations_total: int
    locations_successful: int
    locations_failed: int


class PipelineStatusResponse(BaseModel):
    current_status: str
    latest_run: PipelineRunSummary | None
    latest_successful_run: PipelineRunSummary | None
    last_update_time: datetime | None
    failed_provinces_count: int
    data_age_seconds: int | None
    stale_after_seconds: int
    is_stale: bool
