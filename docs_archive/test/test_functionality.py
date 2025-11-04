def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200


def test_login_pages(client):
    for page in ['/login', '/login/student', '/login/teacher', '/login/admin']:
        assert client.get(page).status_code == 200


def test_admin_login(client):
    resp = client.post('/login/admin', data={'username': 'admin', 'password': 'admin123'})
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']
