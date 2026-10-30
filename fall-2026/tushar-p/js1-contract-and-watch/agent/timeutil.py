"""Dates in America/New_York, as the contract's R2 requires."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")


def today() -> date:
    return datetime.now(NEW_YORK).date()


def stamp(moment: datetime) -> str:
    """Filename-safe timestamp, e.g. 2026-10-27T193012."""
    return moment.astimezone(NEW_YORK).strftime("%Y-%m-%dT%H%M%S")


def parse_calendar_date(value) -> date | None:
    """Calendar date in New York of an ISO 8601 timestamp, or None if missing/unparseable.

    A timestamp without an offset is read as New York time.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        moment = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=NEW_YORK)
    return moment.astimezone(NEW_YORK).date()
