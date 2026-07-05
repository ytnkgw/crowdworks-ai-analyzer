from datetime import date, datetime

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from job_filter import (  # noqa: E402
    get_today_jst,
    parse_application_deadline,
    should_exclude_by_deadline,
)


def test_should_exclude_when_deadline_is_yesterday() -> None:
    assert should_exclude_by_deadline("2026年07月01日", today=date(2026, 7, 2)) is True


def test_should_not_exclude_when_deadline_is_today() -> None:
    assert should_exclude_by_deadline("2026年07月02日", today=date(2026, 7, 2)) is False


def test_should_not_exclude_when_deadline_is_tomorrow() -> None:
    assert should_exclude_by_deadline("2026年07月03日", today=date(2026, 7, 2)) is False


def test_should_not_exclude_when_deadline_missing_or_unparseable() -> None:
    assert should_exclude_by_deadline(None, today=date(2026, 7, 2)) is False
    assert should_exclude_by_deadline("応募期限未定", today=date(2026, 7, 2)) is False


def test_parse_application_deadline_accepts_common_formats() -> None:
    assert parse_application_deadline("2026年7月2日") == date(2026, 7, 2)
    assert parse_application_deadline("2026/07/02 23:59") == date(2026, 7, 2)
    assert parse_application_deadline("2026-07-02") == date(2026, 7, 2)


def test_get_today_jst_uses_asia_tokyo() -> None:
    utc_time = datetime.fromisoformat("2026-07-01T15:30:00+00:00")
    assert get_today_jst(now=utc_time) == date(2026, 7, 2)
