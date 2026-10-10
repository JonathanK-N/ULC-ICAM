from datetime import datetime
import pytest


@pytest.fixture
def state(monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'users', {
        't1': {'role': 'teacher', 'name': 'Teacher'},
        's1': {'role': 'student', 'name': 'Student'}})
    monkeypatch.setattr(module, 'assignments', [{'id': 1, 'teacher': 't1'}, {'id': 2, 'teacher': 't2'}])
    monkeypatch.setattr(module, 'submissions', [{'id': 1, 'assignment_id': 1}, {'id': 2, 'assignment_id': 2}])
    module._test_real_save = module.save_test_data
    monkeypatch.setattr(module, 'save_test_data', lambda: None)
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.update(user='t1', role='teacher', name='Teacher', last_active=datetime.now().isoformat())
        yield module, client


@pytest.mark.parametrize('action', ['publish_submissions', 'unpublish_submissions', 'publish_results', 'unpublish_results'])
def test_publication_requires_post_and_ownership(state, action):
    module, client = state
    assert client.get(f'/teacher/{action}/1').status_code == 405
    assert client.post(f'/teacher/{action}/2').status_code == 403
    assert 'results_available' not in module.submissions[1]
    assert client.post(f'/teacher/{action}/1').status_code == 302


def test_delete_user_get_disallowed(state):
    _, client = state
    assert client.get('/admin/delete_user/s1').status_code == 405


def test_syllabus_requires_course_membership_and_matching_record(state, monkeypatch, tmp_path):
    module, client = state
    monkeypatch.setattr(module, 'course_assignments', {'1': ['t1']})
    monkeypatch.setattr(module, 'course_content', {1: {'syllabus_file': 'plan.pdf'}})
    module.app.config['UPLOAD_FOLDER'] = str(tmp_path)
    (tmp_path / 'syllabus').mkdir()
    (tmp_path / 'syllabus' / 'plan.pdf').write_bytes(b'%PDF-test')
    assert client.get('/download_syllabus/2/plan.pdf').status_code == 403
    assert client.get('/download_syllabus/1/other.pdf').status_code == 404
    assert client.get('/download_syllabus/1/plan.pdf').status_code == 200


def test_plaintext_temporary_password_not_saved(state, monkeypatch, tmp_path):
    module, _ = state
    import json
    monkeypatch.setattr(module, 'DATA_FILE', str(tmp_path / 'data.json'))
    monkeypatch.setattr(module, 'DATA_FILE_TMP', str(tmp_path / 'data.tmp'))
    module.users['s1']['temp_password'] = 'secret'
    module.users['s1']['password'] = 'hashed-value'
    module._test_real_save()
    stored = json.loads((tmp_path / 'data.json').read_text(encoding='utf-8'))
    assert 'temp_password' not in stored['users']['s1']
    assert stored['users']['s1']['password'] == 'hashed-value'
