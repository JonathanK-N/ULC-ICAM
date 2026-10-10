"""Explicit isolated schema management; no production URL fallback."""
import os
from alembic import context
from migrate_isolated import isolated_engine
from migration_schema import metadata

url = os.environ.get('ISOLATED_DATABASE_URL')
if not url:
    raise RuntimeError('ISOLATED_DATABASE_URL is required')
engine = isolated_engine(url)
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():
        context.run_migrations()
