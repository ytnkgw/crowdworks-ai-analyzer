import re
from datetime import date, datetime
from zoneinfo import ZoneInfo

_JST = ZoneInfo("Asia/Tokyo")


def get_today_jst(now: datetime | None = None) -> date:
    current = now if now is not None else datetime.now(_JST)
    if current.tzinfo is None:
        current = current.replace(tzinfo=_JST)
    else:
        current = current.astimezone(_JST)
    return current.date()


def parse_application_deadline(value: str | None) -> date | None:
    if not value:
        return None

    text = value.strip()
    if not text:
        return None

    patterns = [
        r"(?P<y>\d{4})年\s*(?P<m>\d{1,2})月\s*(?P<d>\d{1,2})日",
        r"(?P<y>\d{4})/(?P<m>\d{1,2})/(?P<d>\d{1,2})",
        r"(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue

        try:
            return date(
                int(match.group("y")),
                int(match.group("m")),
                int(match.group("d")),
            )
        except ValueError:
            return None

    return None


def should_exclude_by_deadline(
    application_deadline: str | None,
    today: date | None = None,
) -> bool:
    deadline_date = parse_application_deadline(application_deadline)
    if deadline_date is None:
        return False

    base = today if today is not None else get_today_jst()
    return deadline_date < base


def filter_expired_jobs(
    items: list[dict], today: date | None = None
) -> tuple[list[dict], int]:
    filtered: list[dict] = []
    skipped = 0

    for item in items:
        job = item.get("job") if isinstance(item, dict) else None
        deadline = job.get("application_deadline") if isinstance(job, dict) else None

        if should_exclude_by_deadline(deadline, today=today):
            skipped += 1
            continue

        filtered.append(item)

    return filtered, skipped
