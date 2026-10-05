from datetime import date, datetime
from zoneinfo import ZoneInfo

VIETNAM_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def vietnam_today(reference: datetime | None = None) -> date:
    """Return the Vietnam calendar date for now or an aware reference instant."""
    if reference is None:
        return datetime.now(VIETNAM_TIMEZONE).date()
    if reference.tzinfo is None:
        raise ValueError("reference must be timezone-aware")
    return reference.astimezone(VIETNAM_TIMEZONE).date()
