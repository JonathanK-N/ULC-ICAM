
def test_student_grades_page_accessible(client):
    client.post('/login/student', data={'identifier': 'ETUD001', 'password': 'etud123'})
    resp = client.get('/student/my_grades')
    assert resp.status_code == 200


def test_teacher_submissions_page_accessible(client):
    client.post('/login/teacher', data={'identifier': 'PROF001', 'password': 'prof123'})
    resp = client.get('/teacher/submissions')
    assert resp.status_code == 200
