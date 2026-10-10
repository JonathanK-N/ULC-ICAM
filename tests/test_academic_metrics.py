from datetime import datetime, timezone
from academic_metrics import deadline_status


def test_deadlines_respect_date_end_and_imminent_window():
    now = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)
    assert deadline_status('2026-10-09', now)['label'] == 'Échéance passée'
    assert deadline_status('2026-10-10', now)['label'] == 'À remettre sous 48 h'
    assert deadline_status('2026-12-01', now)['label'] == 'À venir'
    assert deadline_status('invalid', now)['label'] == 'Date à confirmer'
