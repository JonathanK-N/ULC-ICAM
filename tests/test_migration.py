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


def test_snapshot_transaction_round_trip_and_rollback(snapshot):
    from snapshot_repository import SnapshotRepository
    engine = isolated_engine('sqlite://')
    import_snapshot(snapshot[0], engine)
    repository = SnapshotRepository(engine)
    with repository.transaction() as connection:
        data = repository.load(connection)
        data['admin_courses'][0]['name'] = 'Updated'
        repository.save(connection, data)
    with pytest.raises(RuntimeError, match='rollback'):
        with repository.transaction() as connection:
            data = repository.load(connection)
            data['admin_courses'][0]['name'] = 'Lost'
            repository.save(connection, data)
            raise RuntimeError('rollback')
    with repository.transaction() as connection:
        data = repository.load(connection)
    assert data['admin_courses'][0]['name'] == 'Updated'
    assert data['submissions'][0]['correction']['score'] == 90
    assert data['course_content'] == snapshot[1]['course_content']
    assert data['group_assignments'] == snapshot[1]['group_assignments']
    engine.dispose()


def test_relational_rollback_export_is_consistent_and_never_overwrites(snapshot, tmp_path):
    from export_isolated import export_snapshot
    engine = isolated_engine('sqlite://')
    import_snapshot(snapshot[0], engine)
    output = tmp_path / 'rollback.json'
    result = export_snapshot(engine, output)
    loaded = json.loads(output.read_text(encoding='utf-8'))
    assert result['submissions'] == 1
    assert loaded['submissions'][0]['id'] == 30
    assert check_password_hash(loaded['users']['s']['password'], 'student-secret')
    before = output.read_bytes()
    with pytest.raises(FileExistsError):
        export_snapshot(engine, output)
    assert output.read_bytes() == before
    restored = isolated_engine('sqlite://')
    assert import_snapshot(output, restored)['counts']['submissions'] == 1
    restored.dispose()
    engine.dispose()


def test_worker_proposals_are_durable_idempotent_and_preserve_teacher_review(snapshot, tmp_path):
    from snapshot_repository import SnapshotRepository
    from submission_processor import SubmissionProcessor
    path, data = snapshot
    data['assignments'][0]['auto_correct'] = True
    data['submissions'][0].update(filename='answer.txt', processing_status='pending')
    path.write_text(json.dumps(data))
    (tmp_path / 'answer.txt').write_text('My academic work')
    engine = isolated_engine('sqlite://')
    import_snapshot(path, engine)
    repository = SnapshotRepository(engine)
    def grade(text, assignment):
        assert text == 'My academic work'
        # Simulate a teacher approving while the slow calculation is outside the lock.
        with repository.transaction() as connection:
            current = repository.load(connection)
            current['submissions'][0]['correction'] = {'score': 95, 'review_status': 'approved'}
            repository.save(connection, current)
        return {'score': 30, 'review_status': 'pending'}
    processor = SubmissionProcessor(repository, tmp_path, grader=grade)
    assert processor.process(30)['status'] == 'completed'
    assert processor.process(30)['status'] == 'already_processed'
    with repository.transaction() as connection:
        current = repository.load(connection)
    assert current['submissions'][0]['correction']['score'] == 95
    assert len(current['notifications']) == 1
    assert len(current['audit_logs']) == 1
    engine.dispose()


def test_push_delivery_removes_expired_device_and_hides_grades(snapshot, monkeypatch):
    from snapshot_repository import SnapshotRepository
    from push_service import deliver_notifications
    from tests.test_notifications import subscription
    path, data = snapshot
    data['notifications'] = [{'id': 'n', 'username': 't', 'message': 'Private grade 80'}]
    data['push_subscriptions'] = [{'id': 'device', 'username': 't', 'subscription': subscription()}]
    path.write_text(json.dumps(data))
    engine = isolated_engine('sqlite://')
    import_snapshot(path, engine)
    repository = SnapshotRepository(engine)
    for key in ('VAPID_PUBLIC_KEY', 'VAPID_PRIVATE_KEY', 'VAPID_SUBJECT'):
        monkeypatch.setenv(key, 'isolated-only')
    calls = []
    def sender(device, payload):
        calls.append(payload)
        return 'expired'
    assert deliver_notifications(repository, sender)['sent'] == 1
    assert '80' not in calls[0]['body']
    assert deliver_notifications(repository, sender)['sent'] == 0
    assert len(calls) == 1
    with repository.transaction() as connection:
        assert repository.load(connection)['push_subscriptions'] == []
    engine.dispose()


def test_durable_email_retry_is_bounded(snapshot, monkeypatch):
    from snapshot_repository import SnapshotRepository
    from email_service import deliver_emails
    path, data = snapshot
    data['email_jobs'] = [{'id': 'job', 'subject': 'Test', 'recipients': ['fake@example.test'],
                           'html': 'Test', 'status': 'pending'}]
    path.write_text(json.dumps(data))
    engine = isolated_engine('sqlite://')
    import_snapshot(path, engine)
    repository = SnapshotRepository(engine)
    monkeypatch.setenv('NOTIFICATIONS_ENABLED', 'true')
    calls = []
    def sender(job):
        calls.append(job['id'])
        raise RuntimeError('Simulated delivery failure')
    for _ in range(4):
        deliver_emails(repository, sender)
    assert calls == ['job', 'job', 'job']
    with repository.transaction() as connection:
        assert repository.load(connection)['email_jobs'][0]['status'] == 'failed'
    engine.dispose()


def test_flask_relational_startup_and_routes_without_json(snapshot, tmp_path, monkeypatch):
    import importlib.util
    import sys
    path, data = snapshot
    data['users']['a'] = {'role': 'admin', 'password': 'admin-secret', 'name': 'Admin'}
    data['users']['t']['name'] = 'Teacher'
    data['users']['s']['name'] = 'Student'
    data['assignments'][0].update(title='Exam', max_score=100, description='Review')
    path.write_text(json.dumps(data))
    url = 'sqlite:///' + (tmp_path / 'application.sqlite').as_posix()
    engine = isolated_engine(url)
    import_snapshot(path, engine)
    monkeypatch.setenv('COGNITO_STORAGE', 'relational')
    monkeypatch.setenv('DATABASE_URL', url)
    sentinel = tmp_path / 'must-not-create.json'
    monkeypatch.setenv('DATA_FILE', str(sentinel))
    spec = importlib.util.spec_from_file_location('relational_test_app', 'app.py')
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        assert client.post('/login/admin', data={'username': 'a', 'password': 'admin-secret'}).status_code == 302
        assert client.get('/admin/users').status_code == 200
        # Exercise an existing modifying route, then verify relational persistence.
        response = client.post('/admin/add_student', data={'username': 'new', 'name': 'New Student',
                                                          'email': 'new@example.test', 'cip': '1',
                                                          'nom': 'Student', 'postnom': '', 'prenom': 'New',
                                                          'sexe': 'M', 'date_naissance': '2000-01-01',
                                                          'promotion': 'L1', 'faculte': 'Science',
                                                          'departement': 'Maths', 'telephone': '', 'adresse': ''})
        assert response.status_code == 200
        assert client.get('/admin/users').status_code == 200
    from snapshot_repository import SnapshotRepository
    with SnapshotRepository(engine).transaction() as connection:
        loaded = SnapshotRepository(engine).load(connection)
    assert 'new' in loaded['users']
    assert not sentinel.exists()
    module.relational_repository.engine.dispose()
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
        from snapshot_repository import SnapshotRepository
        from concurrent.futures import ThreadPoolExecutor
        repository = SnapshotRepository(isolated)
        def increment():
            with repository.transaction() as connection:
                data = repository.load(connection)
                data['request_counter'] = data.get('request_counter', 0) + 1
                repository.save(connection, data)
        with ThreadPoolExecutor(max_workers=2) as workers:
            list(workers.map(lambda _: increment(), range(4)))
        with repository.transaction() as connection:
            assert repository.load(connection)['request_counter'] == 4
    finally:
        with engine.begin() as connection:
            connection.execute(text('DROP SCHEMA ' + schema_name + ' CASCADE'))
        engine.dispose()
