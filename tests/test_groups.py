from datetime import datetime
import json
import pytest


@pytest.fixture
def group_client(monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'users', {name: {'role': 'student', 'name': name} for name in ['s1', 's2', 'outsider']})
    monkeypatch.setattr(module, 'assignments', [{'id': 1, 'course_id': 1, 'is_group_work': True, 'group_size': 2}])
    monkeypatch.setattr(module, 'course_enrollments', {'1': ['s1', 's2']})
    monkeypatch.setattr(module, 'group_assignments', {})
    monkeypatch.setattr(module, 'student_groups', {})
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.update(user='s1', role='student', name='s1', last_active=datetime.now().isoformat())
        yield module, client


def test_group_rejects_outsider_and_duplicate_members(group_client):
    module, client = group_client
    assert client.post('/student/join_group/1', data={'group_members': 'outsider'}).status_code == 403
    assert client.post('/student/join_group/1', data={'group_members': 's1'}).status_code == 400
    assert module.group_assignments == {}


def test_group_is_saved_and_cannot_be_created_twice(group_client, monkeypatch, tmp_path):
    module, client = group_client
    monkeypatch.setattr(module, 'DATA_FILE', str(tmp_path / 'data.json'))
    monkeypatch.setattr(module, 'DATA_FILE_TMP', str(tmp_path / 'data.tmp'))
    assert client.post('/student/join_group/1', data={'group_members': 's2'}).status_code == 302
    data = json.loads((tmp_path / 'data.json').read_text(encoding='utf-8'))
    assert data['group_assignments']['1']['groups'] == [['s2', 's1']]
    assert data['student_groups']['1'] == {'s2': 0, 's1': 0}
    assert client.post('/student/join_group/1', data={'group_members': 's2'}).status_code == 409


def test_session_role_is_verified_against_existing_account(group_client):
    _, client = group_client
    with client.session_transaction() as sess:
        sess['role'] = 'admin'
    assert client.get('/admin/users').status_code == 302
