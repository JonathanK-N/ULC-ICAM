"""Validate and import a JSON snapshot into an isolated relational staging database.

Never imported by Flask. Does not change the original JSON or switch application storage.
"""
import argparse
import hashlib
import json
from pathlib import Path
from sqlalchemy import create_engine, select, func, event
from sqlalchemy.engine import make_url
from werkzeug.security import generate_password_hash
import migration_schema as schema


class MigrationError(ValueError):
    pass


def isolated_engine(url):
    parsed = make_url(url)
    if parsed.get_backend_name() not in ('sqlite', 'postgresql'):
        raise MigrationError('Only SQLite and PostgreSQL are supported')
    if parsed.get_backend_name() == 'postgresql' and parsed.host not in ('localhost', '127.0.0.1', '::1'):
        raise MigrationError('Only a local isolated PostgreSQL server is allowed')
    engine = create_engine(url)
    if parsed.get_backend_name() == 'sqlite':
        @event.listens_for(engine, 'connect')
        def enforce_foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    return engine


def validate_snapshot(data):
    """Validate references before opening a write transaction."""
    users = data.get('users', {})
    if not isinstance(users, dict):
        raise MigrationError('users must be an object')
    course_ids = [c['id'] for c in data.get('admin_courses', [])]
    assignment_ids = [a['id'] for a in data.get('assignments', [])]
    submission_ids = [s['id'] for s in data.get('submissions', [])]
    for ids in (course_ids, assignment_ids, submission_ids):
        if any(not isinstance(i, int) or isinstance(i, bool) or i < 1 for i in ids) or len(set(ids)) != len(ids):
            raise MigrationError('Duplicate or invalid identifiers')
    for user in users.values():
        if user.get('role') not in ('admin', 'teacher', 'student') or not user.get('password'):
            raise MigrationError('Invalid role or missing credential')
    for field, role in [('course_assignments', 'teacher'), ('course_enrollments', 'student')]:
        for cid, names in data.get(field, {}).items():
            if int(cid) not in course_ids or len(set(names)) != len(names):
                raise MigrationError(f'Invalid {field} relation')
            for name in names:
                if name not in users or users[name]['role'] != role:
                    raise MigrationError(f'Invalid {field} user')
    for assignment in data.get('assignments', []):
        if users.get(assignment.get('teacher'), {}).get('role') != 'teacher':
            raise MigrationError('Assignment references an invalid teacher')
        if assignment.get('course_id') is not None and assignment['course_id'] not in course_ids:
            raise MigrationError('Assignment references a missing course')
    for submission in data.get('submissions', []):
        if submission['assignment_id'] not in assignment_ids or users.get(submission.get('student'), {}).get('role') != 'student':
            raise MigrationError('Submission references a missing assignment or student')
    chapter_ids = []
    for cid, chapters in data.get('course_chapters', {}).items():
        if int(cid) not in course_ids:
            raise MigrationError('Chapter references a missing course')
        chapter_ids.extend(c['id'] for c in chapters)
    if len(set(chapter_ids)) != len(chapter_ids):
        raise MigrationError('Duplicate chapter identifiers')
    for aid, definition in data.get('group_assignments', {}).items():
        if int(aid) not in assignment_ids:
            raise MigrationError('Group references a missing assignment')
        seen = set()
        for members in definition.get('groups', []):
            for name in members:
                if users.get(name, {}).get('role') != 'student' or name in seen:
                    raise MigrationError('Invalid or duplicate group member')
                seen.add(name)
    return data


def import_snapshot(path, engine):
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    data = validate_snapshot(json.loads(raw))
    schema.metadata.create_all(engine)
    with engine.begin() as connection:
        existing = connection.execute(select(schema.imports.c.counts).where(schema.imports.c.source_sha256 == digest)).scalar_one_or_none()
        if existing is not None:
            actual = {table.name: connection.execute(select(func.count()).select_from(table)).scalar()
                      for table in schema.metadata.sorted_tables if table is not schema.imports}
            if actual != existing:
                raise MigrationError('Destination counts changed after import; consistency check failed')
            return dict(source_sha256=digest, counts=existing, already_imported=True)
        if any(connection.execute(select(func.count()).select_from(t)).scalar() for t in schema.metadata.sorted_tables):
            raise MigrationError('Destination must be empty or contain this exact snapshot; no merge or overwrite')
        for role in ('admin', 'teacher', 'student'):
            connection.execute(schema.roles.insert().values(name=role))
        for name, user in data.get('users', {}).items():
            password = user['password']
            if not (password.startswith(('pbkdf2:', 'scrypt:')) or ':' in password):
                password = generate_password_hash(password)
            payload = {k: v for k, v in user.items() if k not in ('password', 'temp_password')}
            connection.execute(schema.users.insert().values(username=name, role=user['role'], password_hash=password, payload=payload))
        for course in data.get('admin_courses', []):
            connection.execute(schema.courses.insert().values(id=course['id'], payload=course))
        for field, table in [('course_assignments', schema.teachers), ('course_enrollments', schema.enrollments)]:
            for cid, names in data.get(field, {}).items():
                for name in names:
                    connection.execute(table.insert().values(course_id=int(cid), username=name))
        for cid, chapters in data.get('course_chapters', {}).items():
            for chapter in chapters:
                connection.execute(schema.chapters.insert().values(id=chapter['id'], course_id=int(cid), payload=chapter))
        for assignment in data.get('assignments', []):
            connection.execute(schema.assignments.insert().values(id=assignment['id'], course_id=assignment.get('course_id'), teacher=assignment['teacher'], payload=assignment))
        for submission in data.get('submissions', []):
            payload = {k: v for k, v in submission.items() if k not in ('correction', 'plagiarism')}
            connection.execute(schema.submissions.insert().values(id=submission['id'], assignment_id=submission['assignment_id'], student=submission['student'], payload=payload))
            for field, table in [('correction', schema.grades), ('plagiarism', schema.plagiarism)]:
                value = submission.get(field, data.get(field + '_results', {}).get(str(submission['id'])))
                if value is not None:
                    connection.execute(table.insert().values(submission_id=submission['id'], payload=value))
        for aid, definition in data.get('group_assignments', {}).items():
            for gid, members in enumerate(definition.get('groups', [])):
                connection.execute(schema.groups.insert().values(assignment_id=int(aid), group_id=str(gid), payload={'members': members, 'type': definition.get('type')}))
                for name in members:
                    connection.execute(schema.group_members.insert().values(assignment_id=int(aid), group_id=str(gid), username=name))
        # Preserve all fields not yet mapped without activating them in the live application.
        mapped = {'users', 'admin_courses', 'course_assignments', 'course_enrollments', 'course_chapters', 'assignments', 'submissions'}
        for key, value in data.items():
            if key not in mapped:
                connection.execute(schema.state.insert().values(key=key, payload=value))
        counts = {table.name: connection.execute(select(func.count()).select_from(table)).scalar() for table in schema.metadata.sorted_tables if table is not schema.imports}
        connection.execute(schema.imports.insert().values(source_sha256=digest, counts=counts))
    return dict(source_sha256=digest, counts=counts, already_imported=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot')
    parser.add_argument('--database-url', required=True)
    parser.add_argument('--confirm-isolated', action='store_true')
    args = parser.parse_args()
    if not args.confirm_isolated:
        parser.error('Explicit --confirm-isolated is required; production migration is prohibited')
    print(json.dumps(import_snapshot(args.snapshot, isolated_engine(args.database_url)), indent=2))
