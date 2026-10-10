import json
import pytest
from sqlalchemy import select, func
from werkzeug.security import check_password_hash
from migrate_isolated import import_snapshot, isolated_engine, MigrationError
import migration_schema as schema


@pytest.fixture
def snapshot(tmp_path):
    data = {
        'users': {'t': {'role': 'teacher', 'password': 'teacher-secret'},
                  's': {'role': 'student', 'password': 'student-secret', 'temp_password': 'clear-secret'}},
        'admin_courses': [{'id': 5, 'name': 'Maths', 'custom_field': 'preserve'}],
        'course_assignments': {'5': ['t']}, 'course_enrollments': {'5': ['s']},
        'course_chapters': {'5': [{'id': 10, 'documents': [{'filename': 'lesson.pdf'}]}]},
        'assignments': [{'id': 20, 'teacher': 't', 'course_id': 5}],
        'submissions': [{'id': 30, 'assignment_id': 20, 'student': 's', 'filename': 'answer.pdf',
                         'correction': {'score': 90}, 'plagiarism': {'similarity': 12}}],
        'group_assignments': {'20': {'groups': [['s']], 'type': 'manual'}},
        'course_content': {'5': {'description': 'Preserved'}}, 'next_assignment_id': 21}
    path = tmp_path / 'snapshot.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return path, data


def test_import_preserves_ids_and_fields_and_is_idempotent(snapshot):
    path, _ = snapshot
    before = path.read_bytes()
    engine = isolated_engine('sqlite://')
    first = import_snapshot(path, engine)
    second = import_snapshot(path, engine)
    assert not first['already_imported'] and second['already_imported']
    assert first['counts'] == second['counts']
    with engine.connect() as conn:
        assert conn.execute(select(schema.courses.c.id)).scalar_one() == 5
        assert conn.execute(select(schema.courses.c.payload)).scalar_one()['custom_field'] == 'preserve'
        user = conn.execute(select(schema.users).where(schema.users.c.username == 's')).mappings().one()
        assert check_password_hash(user['password_hash'], 'student-secret')
        assert 'temp_password' not in user['payload'] and 'password' not in user['payload']
        assert conn.execute(select(schema.grades.c.payload)).scalar_one()['score'] == 90
        assert conn.execute(select(schema.plagiarism.c.payload)).scalar_one()['similarity'] == 12
        assert conn.execute(select(schema.group_members.c.username)).scalar_one() == 's'
        assert conn.execute(select(schema.state.c.payload).where(schema.state.c.key == 'next_assignment_id')).scalar_one() == 21
    assert path.read_bytes() == before


def test_orphan_rejected_before_import(snapshot):
    path, data = snapshot
    data['submissions'][0]['assignment_id'] = 999
    path.write_text(json.dumps(data))
    engine = isolated_engine('sqlite://')
    with pytest.raises(MigrationError):
        import_snapshot(path, engine)
    from sqlalchemy import inspect
    assert inspect(engine).get_table_names() == []


def test_changed_snapshot_cannot_overwrite_existing(snapshot):
    path, data = snapshot
    engine = isolated_engine('sqlite://')
    import_snapshot(path, engine)
    data['admin_courses'][0]['name'] = 'Changed'
    path.write_text(json.dumps(data))
    with pytest.raises(MigrationError, match='Destination must be empty'):
        import_snapshot(path, engine)
    with engine.connect() as conn:
        assert conn.execute(select(schema.courses.c.payload)).scalar_one()['name'] == 'Maths'


def test_remote_database_rejected():
    with pytest.raises(MigrationError):
        isolated_engine('postgresql+psycopg://user:password@production.example/db')


def test_transactional_results_preserve_submissions_and_teacher_approval(snapshot):
    from submission_repository import SubmissionRepository
    engine = isolated_engine('sqlite://')
    import_snapshot(snapshot[0], engine)
    repository = SubmissionRepository(engine)
    proposal = {'score': 65, 'review_status': 'approved'}
    assert repository.save_proposal(30, proposal)
    assert proposal['review_status'] == 'approved'
    assert repository.save_similarity(30, {'similarity': 15})
    result = repository.get(30)
    assert result['filename'] == 'answer.pdf'
    assert result['correction']['review_status'] == 'pending'
    assert result['plagiarism']['requires_human_review'] is True
    with engine.begin() as connection:
        connection.execute(schema.grades.update().where(schema.grades.c.submission_id == 30)
                           .values(payload={'score': 80, 'review_status': 'approved'}))
    assert not repository.save_proposal(30, {'score': 25})
    assert repository.get(30)['correction']['score'] == 80
    with pytest.raises(KeyError):
        repository.save_proposal(999, {'score': 0})
    assert repository.get(30)['correction']['score'] == 80
    engine.dispose()


def test_alembic_upgrade_and_rollback_in_isolation(tmp_path, monkeypatch):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    url = 'sqlite:///' + (tmp_path / 'alembic.sqlite').as_posix()
    monkeypatch.setenv('ISOLATED_DATABASE_URL', url)
    config = Config('alembic.ini')
    command.upgrade(config, 'head')
    engine = isolated_engine(url)
    assert set(schema.metadata.tables).issubset(inspect(engine).get_table_names())
    engine.dispose()

    command.downgrade(config, 'base')
    engine = isolated_engine(url)
    assert not set(schema.metadata.tables).intersection(inspect(engine).get_table_names())
    engine.dispose()


def test_postgresql_round_trip_when_available(snapshot):
    import os
    import uuid
    from sqlalchemy import text
    url = os.environ.get('TEST_POSTGRES_URL')
    if not url:
        pytest.skip('No isolated PostgreSQL configured; SQLite is not PostgreSQL validation')
    engine = isolated_engine(url)
    schema_name = 'cognito_test_' + uuid.uuid4().hex
    with engine.begin() as connection:
        connection.execute(text('CREATE SCHEMA ' + schema_name))
    isolated = engine.execution_options(schema_translate_map={None: schema_name})
    try:
        first = import_snapshot(snapshot[0], isolated)
        second = import_snapshot(snapshot[0], isolated)
        assert first['counts'] == second['counts'] and second['already_imported']
        from submission_repository import SubmissionRepository
        repository = SubmissionRepository(isolated)
        assert repository.save_proposal(30, {'score': 85})
        assert repository.save_similarity(30, {'similarity': 5})
        assert repository.get(30)['correction']['review_status'] == 'pending'
        with isolated.connect() as connection:
            assert connection.execute(select(schema.submissions.c.id)).scalar_one() == 30
            assert connection.execute(select(schema.grades.c.payload)).scalar_one()['score'] == 85
    finally:
        with engine.begin() as connection:
            connection.execute(text('DROP SCHEMA ' + schema_name + ' CASCADE'))
        engine.dispose()
