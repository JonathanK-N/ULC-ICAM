"""Worker entry point reserved for the relational integration."""
raise RuntimeError(
    'Celery worker is disabled: the Flask application still uses JSON storage. '
    'Complete relational integration before enabling concurrent workers.'
)
