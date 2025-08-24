
def test_dashboard_access_student(client):
    client.post('/login/student', data={'identifier': 'ETUD001', 'password': 'etud123'})
    resp = client.get('/dashboard')
    assert resp.status_code == 200


def test_teacher_assignments_page(client):
    client.post('/login/teacher', data={'identifier': 'PROF001', 'password': 'prof123'})
    resp = client.get('/teacher/assignments')
    assert resp.status_code == 200
