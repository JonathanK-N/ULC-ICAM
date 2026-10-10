from unittest.mock import Mock
import pytest
import requests
import code_execution as engine


@pytest.fixture
def executor(monkeypatch):
    monkeypatch.setattr(engine, 'JUDGE0_API_KEY', 'test-key')
    monkeypatch.setattr(engine, 'JUDGE0_URL', 'https://sandbox.example')
    return engine.CodeExecutor()


def test_no_key_never_executes_locally(executor, monkeypatch, tmp_path):
    monkeypatch.setattr(engine, 'JUDGE0_API_KEY', '')
    marker = tmp_path / 'executed'
    result = executor.execute_code(f"open({str(marker)!r}, 'w').write('unsafe')", 'python')
    assert result['error_code'] == 'execution_unavailable'
    assert not marker.exists()
    assert not hasattr(executor, '_execute_locally')


@pytest.mark.parametrize('url', ['http://sandbox.example', 'https://user:pass@host', 'https://host?key=secret'])
def test_insecure_endpoint_rejected(executor, monkeypatch, url):
    monkeypatch.setattr(engine, 'JUDGE0_URL', url)
    assert executor.execute_code('print(1)', 'python')['retryable']


def test_network_failure_is_sanitized(executor, monkeypatch):
    def fail(*args, **kwargs):
        assert kwargs['timeout'] == (3, 5)
        assert kwargs['allow_redirects'] is False
        assert kwargs['json']['enable_network'] is False
        raise requests.Timeout('secret-key')
    monkeypatch.setattr(engine.requests, 'post', fail)
    result = executor.execute_code('print(1)', 'python')
    assert result['error_code'] == 'execution_unavailable'
    assert 'secret-key' not in str(result)


def test_remote_result_normalizes_nulls(executor, monkeypatch):
    monkeypatch.setattr(engine.requests, 'post', Mock(return_value=Mock(status_code=201, json=lambda: {'token': 'abc'})))
    monkeypatch.setattr(engine.requests, 'get', Mock(return_value=Mock(status_code=200, json=lambda: {
        'status': {'id': 3, 'description': 'Accepted'}, 'stdout': 'Hello', 'stderr': None, 'compile_output': None})))
    result = executor.execute_code('print("Hello")', 'python')
    assert result['success'] and result['stdout'] == 'Hello'
    assert result['stderr'] == result['compile_output'] == ''


def test_failed_remote_test_cannot_pass(executor, monkeypatch):
    monkeypatch.setattr(engine.requests, 'post', Mock(return_value=Mock(status_code=201, json=lambda: {'token': 'abc'})))
    results = iter([{'status_id': 3, 'success': True}, {'success': False, 'stdout': ''}])
    monkeypatch.setattr(executor, '_wait_for_result', lambda token: next(results))
    result = executor.execute_code('print(1)', 'python', test_cases=[{'input': '', 'expected_output': ''}])
    assert not result['success']
    assert not result['test_results'][0]['passed']


def test_missing_bootstrap_has_no_default_admin():
    from app import _build_default_data
    assert _build_default_data()['users'] == {}


def test_test_submit_requires_existing_account():
    from app import app
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        assert client.post('/test_submit', data={'code_content': 'print(1)'}).status_code == 401
        with client.session_transaction() as sess:
            sess['user'] = 'deleted-account'
            sess['role'] = 'admin'
        assert client.post('/test_submit').status_code == 401


def test_test_submit_csrf_enforced():
    from app import app
    app.config['WTF_CSRF_ENABLED'] = True
    try:
        with app.test_client() as client:
            assert client.post('/test_submit').status_code == 400
    finally:
        app.config['WTF_CSRF_ENABLED'] = False


def test_submission_storage_uses_configured_folder_and_safe_unique_paths(monkeypatch, tmp_path):
    monkeypatch.setenv('UPLOAD_FOLDER', str(tmp_path))
    first = engine.save_code_submission('../../outsider', 1, 'print(1)', 'python', {'success': True})
    second = engine.save_code_submission('../../outsider', 1, 'print(2)', 'python', {'success': True})
    assert first['code_file'] != second['code_file']
    for key in ('code_file', 'result_file'):
        assert '/' not in first[key] and '\\' not in first[key]
        assert (tmp_path / 'code_submissions' / first[key]).is_file()
    assert (tmp_path / 'code_submissions' / first['code_file']).read_text() == 'print(1)'
