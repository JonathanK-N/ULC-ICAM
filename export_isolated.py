"""Export a relational staging snapshot for consistency and rollback tests."""
import argparse
import hashlib
import json
from pathlib import Path
from migrate_isolated import isolated_engine, validate_snapshot
from snapshot_repository import SnapshotRepository


def export_snapshot(engine, destination):
    repository = SnapshotRepository(engine)
    with repository.transaction() as connection:
        data = repository.load(connection)
    validate_snapshot(data)
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    with Path(destination).open('xb') as stream:
        stream.write(raw)
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'users': len(data['users']),
            'submissions': len(data['submissions'])}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database-url', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--confirm-isolated', action='store_true')
    args = parser.parse_args()
    if not args.confirm_isolated:
        parser.error('Explicit isolated confirmation is required')
    engine = isolated_engine(args.database_url)
    try:
        print(json.dumps(export_snapshot(engine, args.output)))
    finally:
        engine.dispose()
