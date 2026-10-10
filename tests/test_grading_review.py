from datetime import datetime
import pytest
from grading_service import parse_ai_response


@pytest.mark.parametrize('text', ['No grade', 'NOTE: -5/100', 'NOTE: 101/100', 'NOTE: 80/20', None])
def test_invalid_ai_response_has_no_invented_score(text):
    assert parse_ai_response(text, 100)[0] is None


def test_decimal_grade_and_feedback():
    assert parse_ai_response('NOTE: 82,5/100\n- Justifiez votre raisonnement.', 100) == (82.5, ['Justifiez votre raisonnement.'])


def test_fallback_is_pending_without_numeric_grade(monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'correction_results', {})
    result = module.fallback_correction({'max_score': 100}, 1)
    assert result['score'] is None and result['review_status'] == 'pending'
    assert module.correction_results[1] == result


@pytest.mark.parametrize('action', ['publish_submissions', 'publish_results'])
def test_pending_ai_grade_cannot_be_published(monkeypatch, action):
    import app as module
    monkeypatch.setattr(module, 'users', {'teacher': {'role': 'teacher'}})
    monkeypatch.setattr(module, 'assignments', [{'id': 1, 'teacher': 'teacher'}])
    monkeypatch.setattr(module, 'submissions', [{'id': 1, 'assignment_id': 1,
                                              'correction': {'score': 80, 'review_status': 'pending'}}])
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.update(user='teacher', role='teacher', last_active=datetime.now().isoformat())
        assert client.post('/teacher/' + action + '/1').status_code == 409
    assert 'results_available' not in module.submissions[0]


def test_teacher_can_review_draft_and_then_publish(monkeypatch):
    import app as module
    draft = {'score': None, 'max_score': 100, 'review_status': 'pending', 'feedback': ['Correction requise'], 'auto_generated': True}
    submission = {'id': 1, 'assignment_id': 1, 'student': 'student', 'filename': 'answer.pdf',
                  'submitted_at': '2026-10-09 12:00:00', 'correction': draft}
    monkeypatch.setattr(module, 'users', {'teacher': {'role': 'teacher', 'name': 'Teacher'}})
    monkeypatch.setattr(module, 'assignments', [{'id': 1, 'teacher': 'teacher', 'title': 'Exam', 'max_score': 100}])
    monkeypatch.setattr(module, 'submissions', [submission])
    monkeypatch.setattr(module, 'correction_results', {1: draft})
    monkeypatch.setattr(module, 'save_test_data', lambda: None)
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        with client.session_transaction() as sess:
            sess.update(user='teacher', role='teacher', name='Teacher', last_active=datetime.now().isoformat())
        assert client.get('/teacher/assignment_results/1').status_code == 200
        assert client.post('/teacher/grade_submission/1', data={'score': '-1', 'max_score': '100'}).status_code == 400
        assert client.post('/teacher/grade_submission/1', data={'score': '80', 'max_score': '100', 'feedback': 'Validé'}).status_code == 302
        assert submission['correction']['review_status'] == 'approved'
        assert client.post('/teacher/publish_submissions/1').status_code == 302
        assert submission['results_available']
