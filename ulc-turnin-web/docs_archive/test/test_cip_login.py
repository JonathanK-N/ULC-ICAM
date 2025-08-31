def test_student_login_with_cip(client):
    resp = client.post('/login/student', data={'identifier': 'ETUD001', 'password': 'etud123'})
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']


def test_teacher_login_with_cip(client):
    resp = client.post('/login/teacher', data={'identifier': 'PROF001', 'password': 'prof123'})
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']


def test_login_invalid_identifier(client):
    resp = client.post('/login/student', data={'identifier': 'WRONG123', 'password': 'wrong'})
    assert resp.status_code == 200
