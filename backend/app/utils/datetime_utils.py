"""Datetime helper utilities used across services and the AI engine."""
from datetime import datetime, timedelta


def utcnow() -> datetime:
    """Return the current UTC datetime (naive, for consistent SQLite storage)."""
    return datetime.utcnow()


def minutes_ago(minutes: int) -> datetime:
    """Return a datetime `minutes` before now."""
    return utcnow() - timedelta(minutes=minutes)


def seconds_ago(seconds: int) -> datetime:
    """Return a datetime `seconds` before now."""
    return utcnow() - timedelta(seconds=seconds)


def format_iso(dt: datetime) -> str:
    """Format a datetime as an ISO-8601 string, safe for None."""
    if dt is None:
        return ""
    return dt.isoformat()


def humanize_delta(dt: datetime, reference: datetime = None) -> str:
    """Return a short human-readable delta like '7 minutes earlier'."""
    if dt is None:
        return "unknown time"
    reference = reference or utcnow()
    delta_seconds = (reference - dt).total_seconds()
    minutes = int(abs(delta_seconds) // 60)
    if minutes < 1:
        return "moments earlier" if delta_seconds >= 0 else "moments later"
    unit = "minute" if minutes == 1 else "minutes"
    suffix = "earlier" if delta_seconds >= 0 else "later"
    return f"{minutes} {unit} {suffix}"
