from datetime import datetime
import io
import json
import pytest


@pytest.fixture
def academic_client(monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'users', {'student': {'role': 'student', 'name': 'Student', 'password': 'hash'},
                                       'teacher': {'role': 'teacher', 'name': 'Teacher'},
                                       'admin': {'role': 'admin', 'name': 'Admin', 'password': 'hash'}})
    monkeypatch.setattr(module, 'assignments', [{'id': 1, 'teacher': 'teacher', 'course_id': 1, 'files': ['exam.pdf'], 'is_mixed_assignment': True}])
    monkeypatch.setattr(module, 'course_enrollments', {'1': []})
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.update(user='student', role='student', name='Student', last_active=datetime.now().isoformat())
        yield module, client


def test_analysis_requires_enrollment_before_upload(academic_client):
    _, client = academic_client
    response = client.post('/upload_analysis_files/1', data={'analysis_files': (io.BytesIO(b'test'), 'answer.pdf')})
    assert response.status_code == 403


def test_assignment_file_requires_enrollment(academic_client):
    _, client = academic_client
    assert client.get('/download_assignment_file/exam.pdf').status_code == 403


@pytest.mark.parametrize('timestamp', ['invalid', 42, '2026-01-01T00:00:00+00:00',
                                     '2999-01-01T00:00:00'])
def test_invalid_session_timestamp_requires_login(academic_client, timestamp):
    _, client = academic_client
    with client.session_transaction() as sess:
        sess['last_active'] = timestamp
    assert client.get('/dashboard').status_code == 302
    with client.session_transaction() as sess:
        assert 'user' not in sess


def test_file_ai_submission_does_not_publish_assignment(academic_client, monkeypatch, tmp_path):
    module, client = academic_client
    assignment = module.assignments[0]
    assignment['auto_correct'] = True
    monkeypatch.setattr(module, 'course_enrollments', {'1': ['student']})
    monkeypatch.setattr(module, 'submissions', [])
    monkeypatch.setattr(module, 'save_test_data', lambda: None)
    monkeypatch.setattr(module, 'process_submission_async', lambda *args: None)
    monkeypatch.setitem(module.app.config, 'UPLOAD_FOLDER', str(tmp_path))
    response = client.post('/submit/1', data={'file': (io.BytesIO(b'answer'), 'answer.txt')})
    assert response.status_code == 302
    assert len(module.submissions) == 1
    assert module.submissions[0]['results_available'] is False
    assert not assignment.get('results_published')


def test_admin_export_excludes_credentials(academic_client):
    _, client = academic_client
    with client.session_transaction() as sess:
        sess.update(user='admin', role='admin')
    response = client.get('/admin/export_all_data')
    assert response.status_code == 200
    for user in json.loads(response.data)['users'].values():
        assert 'password' not in user and 'temp_password' not in user
    assert response.headers['Cache-Control'] == 'no-store'


@pytest.mark.parametrize('path', ['/teacher/enroll_student/1/student', '/teacher/unenroll_student/1/student',
                                 '/admin/unassign_teacher/1/teacher', '/admin/check_all_plagiarism', '/admin/recheck_plagiarism/1'])
def test_other_mutations_reject_get(academic_client, path):
    _, client = academic_client
    assert client.get(path).status_code == 405


def test_login_brute_force_limited(academic_client):
    module, client = academic_client
    module.limiter.reset()
    try:
        responses = [client.post('/login/admin', data={'username': 'absent', 'password': 'wrong'}) for _ in range(6)]
        assert responses[-1].status_code == 429
    finally:
        module.limiter.reset()


def test_sandbox_failure_has_retryable_http_response(academic_client, monkeypatch):
    _, client = academic_client
    import code_execution
    monkeypatch.setattr(code_execution, 'JUDGE0_API_KEY', '')
    response = client.post('/test_submit', data={'code_content': 'print(1)', 'language': 'python'})
    assert response.status_code == 503
    assert response.json['execution_result']['retryable']
    assert 'score' not in response.json['execution_result']


def test_demo_bootstrap_refuses_production_and_known_defaults(monkeypatch):
    from bootstrap_credentials import isolated_admin_hash
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('BOOTSTRAP_ADMIN_PASSWORD', 'long-isolated-secret')
    with pytest.raises(RuntimeError):
        isolated_admin_hash()
    monkeypatch.setenv('FLASK_ENV', 'development')
    monkeypatch.delenv('BOOTSTRAP_ADMIN_PASSWORD')
    with pytest.raises(RuntimeError):
        isolated_admin_hash()


def test_corrupt_storage_never_replaced_by_empty_defaults(monkeypatch, tmp_path):
    import runpy
    path = tmp_path / 'broken.json'
    original = b'{incomplete'
    path.write_bytes(original)
    monkeypatch.setenv('DATA_FILE', str(path))
    with pytest.raises(RuntimeError, match='Données illisibles'):
        runpy.run_path('app.py', run_name='isolated_corrupt_storage_test')
    assert path.read_bytes() == original
