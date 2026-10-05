from datetime import UTC, date, datetime

import pytest

from stormwatch.utils.datetime_utils import vietnam_today


def test_vietnam_today_uses_vietnam_calendar_boundary() -> None:
    utc_evening = datetime(2026, 9, 6, 17, 30, tzinfo=UTC)

    assert vietnam_today(utc_evening) == date(2026, 9, 7)


def test_vietnam_today_rejects_naive_reference() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        vietnam_today(datetime(2026, 9, 6, 17, 30))
