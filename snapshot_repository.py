"""Compatibility repository for gradual replacement of Flask's JSON globals.

Requests share a database lock until commit. This favors correctness during the
transition; entity repositories can later shorten transaction boundaries.
"""
from contextlib import contextmanager
from copy import deepcopy
from sqlalchemy import select
import migration_schema as schema
from migrate_isolated import validate_snapshot, write_snapshot


class SnapshotRepository:
    def __init__(self, engine):
        self.engine = engine

    @contextmanager
    def transaction(self):
        with self.engine.begin() as connection:
            row = connection.execute(select(schema.roles.c.name).where(
                schema.roles.c.name == 'admin').with_for_update()).first()
            if row is None:
                raise RuntimeError('Import and verify the database before selecting relational storage')
            yield connection

    def load(self, connection):
        data = {row.key: deepcopy(row.payload) for row in
                connection.execute(select(schema.state))}
        data['users'] = {row.username: dict(row.payload, password=row.password_hash,
                                           role=row.role)
                         for row in connection.execute(select(schema.users))}
        for field, table in [('admin_courses', schema.courses),
                             ('assignments', schema.assignments),
                             ('submissions', schema.submissions)]:
            data[field] = [deepcopy(row.payload) for row in
                           connection.execute(select(table).order_by(table.c.id))]
        for field, table in [('course_assignments', schema.teachers),
                             ('course_enrollments', schema.enrollments)]:
            relations = {}
            for row in connection.execute(select(table)):
                relations.setdefault(str(row.course_id), []).append(row.username)
            data[field] = relations
        chapters = {}
        for row in connection.execute(select(schema.chapters).order_by(schema.chapters.c.id)):
            chapters.setdefault(str(row.course_id), []).append(deepcopy(row.payload))
        data['course_chapters'] = chapters
        by_id = {item['id']: item for item in data['submissions']}
        for field, table in [('correction', schema.grades), ('plagiarism', schema.plagiarism)]:
            for row in connection.execute(select(table)):
                by_id[row.submission_id][field] = deepcopy(row.payload)
        for field, table in [('notifications', schema.notifications), ('audit_logs', schema.audit_logs)]:
            records = [deepcopy(row.payload) for row in connection.execute(select(table))]
            data[field] = records or data.get(field, [])
        return data

    def save(self, connection, data):
        validate_snapshot(data)
        # Retain the lock row and import history throughout the transaction.
        for table in reversed(schema.metadata.sorted_tables):
            if table not in (schema.imports, schema.roles):
                connection.execute(table.delete())
        # The shared writer creates roles only for initial imports.
        write_snapshot(connection, data, include_roles=False)
