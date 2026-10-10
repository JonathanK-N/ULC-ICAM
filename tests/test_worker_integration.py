"""Real PostgreSQL/Redis workflow, enabled only by explicit isolated test URLs."""
import importlib.util
import io
import json
import os
import sys
import uuid
from urllib.parse import urlsplit
import pytest
from sqlalchemy import text
from migrate_isolated import isolated_engine, import_snapshot
from snapshot_repository import SnapshotRepository


def test_real_postgres_redis_flask_submission_and_teacher_review(tmp_path, monkeypatch):
    pg_url = os.environ.get('TEST_POSTGRES_URL')
    redis_url = os.environ.get('TEST_REDIS_URL')
    if not pg_url or not redis_url:
        pytest.skip('Explicit isolated PostgreSQL and Redis required')
    assert urlsplit(redis_url).hostname in ('localhost', '127.0.0.1', '::1')
    from celery.contrib.testing.worker import start_worker
    from celery_tasks import celery, process_submission, configure_celery
    engine = isolated_engine(pg_url)
    schema_name = 'cognito_worker_' + uuid.uuid4().hex
    queue_name = 'test_' + uuid.uuid4().hex
    with engine.begin() as connection:
        connection.execute(text('CREATE SCHEMA ' + schema_name))
    isolated = engine.execution_options(schema_translate_map={None: schema_name})
    application_url = engine.url.update_query_dict({'options': '-csearch_path=' + schema_name}).render_as_string(hide_password=False)
    module = None
    prior_conf = {key: celery.conf[key] for key in ('broker_url', 'result_backend', 'task_always_eager')}
    try:
        data = {'users': {
            's': {'role': 'student', 'password': 'student-secret', 'name': 'Student', 'cip': 'S'},
            't': {'role': 'teacher', 'password': 'teacher-secret', 'name': 'Teacher', 'cip': 'T'}},
            'admin_courses': [{'id': 5, 'name': 'Maths'}],
            'course_assignments': {'5': ['t']}, 'course_enrollments': {'5': ['s']},
            'assignments': [{'id': 20, 'teacher': 't', 'course_id': 5, 'title': 'Exam',
                             'description': 'Explain your answer', 'max_score': 100,
                             'due_date': '2030-01-01', 'auto_correct': True}], 'submissions': []}
        source = tmp_path / 'isolated.json'
        source.write_text(json.dumps(data))
        before = source.read_bytes()
        import_snapshot(source, isolated)
        monkeypatch.setenv('COGNITO_STORAGE', 'relational')
        monkeypatch.setenv('DATABASE_URL', application_url)
        monkeypatch.setenv('CELERY_BROKER_URL', redis_url)
        monkeypatch.setenv('CELERY_RESULT_BACKEND', redis_url)
        uploads = tmp_path / 'uploads'
        uploads.mkdir()
        monkeypatch.setenv('UPLOAD_FOLDER', str(uploads))
        sentinel = tmp_path / 'must-not-create.json'
        monkeypatch.setenv('DATA_FILE', str(sentinel))
        monkeypatch.delenv('OPENAI_API_KEY', raising=False)
        monkeypatch.delenv('OPENAI_MODEL', raising=False)
        spec = importlib.util.spec_from_file_location('isolated_postgres_app', 'app.py')
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, spec.name, module)
        spec.loader.exec_module(module)
        module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        configure_celery()
        celery.conf.task_always_eager = False
        with module.app.test_client() as client:
            assert client.post('/login/student', data={'identifier': 'S', 'password': 'student-secret'}).status_code == 302
            assert client.post('/submit/20', data={'file': (io.BytesIO(b'Academic answer'), 'answer.txt')}).status_code == 302
            repository = SnapshotRepository(isolated)
            with repository.transaction() as connection:
                submitted = repository.load(connection)['submissions'][0]
            assert submitted['processing_status'] == 'pending'
            with start_worker(celery, pool='solo', queues=[queue_name], perform_ping_check=False):
                result = process_submission.apply_async(args=[submitted['id']], queue=queue_name)
                assert result.get(timeout=30)['status'] == 'completed'
                result.forget()
            with repository.transaction() as connection:
                proposal = repository.load(connection)['submissions'][0]
            assert proposal['correction']['score'] is None
            assert not proposal['results_available']
            assert client.post('/login/teacher', data={'identifier': 'T', 'password': 'teacher-secret'}).status_code == 302
            assert client.get('/teacher/assignment_results/20').status_code == 200
            assert client.post('/teacher/grade_submission/' + str(submitted['id']),
                               data={'score': '80', 'max_score': '100', 'feedback': 'Verified'}).status_code == 302
            assert client.post('/teacher/publish_submissions/20').status_code == 302
            assert client.post('/login/student', data={'identifier': 'S', 'password': 'student-secret'}).status_code == 302
            assert client.get('/student/my_grades').status_code == 200
            with repository.transaction() as connection:
                approved = repository.load(connection)['submissions'][0]
            assert approved['correction']['review_status'] == 'approved' and approved['results_available']
        assert not sentinel.exists() and source.read_bytes() == before
    finally:
        celery.conf.update(prior_conf)
        if module:
            module.relational_repository.engine.dispose()
        with engine.begin() as connection:
            connection.execute(text('DROP SCHEMA ' + schema_name + ' CASCADE'))
        engine.dispose()
