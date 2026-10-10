"""Deadline labels shared by student and teacher dashboards."""
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
import os


def deadline_status(value, now=None):
    try:
        zone = ZoneInfo(os.environ.get('ACADEMIC_TIMEZONE', 'Africa/Kinshasa'))
        due = datetime.fromisoformat(value)
        if len(value) == 10:
            due = datetime.combine(due.date(), time(23, 59, 59))
        if due.tzinfo is None:
            due = due.replace(tzinfo=zone)
        current = now or datetime.now(timezone.utc)
        seconds = (due - current).total_seconds()
        if seconds < 0:
            return {'label': 'Échéance passée', 'class': 'bg-secondary'}
        if seconds <= 48 * 3600:
            return {'label': 'À remettre sous 48 h', 'class': 'bg-warning text-dark'}
        return {'label': 'À venir', 'class': 'bg-info text-dark'}
    except (ValueError, TypeError, KeyError):
        return {'label': 'Date à confirmer', 'class': 'bg-secondary'}
