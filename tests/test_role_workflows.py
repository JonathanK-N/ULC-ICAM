"""Exercise real login and representative pages with synthetic academic data."""
import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def academic_app(monkeypatch):
    import app as module
    password_hash = generate_password_hash('synthetic-login-password')
    users = {name: {'password': password_hash, 'role': role, 'name': name,
                    'cip': name, 'email': name + '@example.test', 'promotion': 'L1',
                    'faculte': 'Sciences', 'departement': 'Informatique'}
             for name, role in [('admin', 'admin'), ('teacher', 'teacher'), ('student', 'student')]}
    course = {'id': 1, 'name': 'Informatique', 'code': 'INFO1', 'credits': 3,
              'promotions': ['L1'], 'faculte': 'Sciences', 'departement': 'Informatique'}
    assignment = {'id': 1, 'title': 'Exercice', 'description': 'Travail synthétique',
                  'course_id': 1, 'teacher': 'teacher', 'teacher_name': 'teacher',
                  'due_date': '2030-10-09T12:00', 'max_score': 100, 'files': [],
                  'course': 'Informatique', 'results_published': False}
    for name, value in {'users': users, 'admin_courses': [course],
                        'course_assignments': {'1': ['teacher']}, 'course_enrollments': {'1': ['student']},
                        'assignments': [assignment], 'submissions': [], 'correction_results': {},
                        'plagiarism_results': {}, 'course_content': {1: {'description': 'Cours', 'documents': []}},
                        'course_chapters': {1: []}, 'group_assignments': {}, 'student_groups': {}}.items():
        monkeypatch.setattr(module, name, value)
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    module.limiter.reset()
    yield module.app
    module.limiter.reset()


@pytest.mark.parametrize('role,pages', [
    ('admin', ['/dashboard', '/admin/users', '/admin/courses', '/admin/assignments']),
    ('teacher', ['/dashboard', '/teacher/my_assigned_courses', '/teacher/assignments', '/teacher/assignment_results/1']),
    ('student', ['/dashboard', '/student/courses', '/student/course/1', '/student/my_grades', '/submit/1'])])
def test_real_login_and_academic_pages(academic_app, role, pages):
    with academic_app.test_client() as client:
        data = {'password': 'synthetic-login-password', 'username': role} if role == 'admin' else {'password': 'synthetic-login-password', 'identifier': role}
        response = client.post('/login/' + role, data=data)
        assert response.status_code == 302 and response.location.endswith('/dashboard')
        for page in pages:
            assert client.get(page).status_code == 200, page
        with client.session_transaction() as sess:
            assert sess['user'] == role and sess['role'] == role
