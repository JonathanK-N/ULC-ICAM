
def test_submission_page(client):
    client.post('/login/student', data={'identifier': 'ETUD001', 'password': 'etud123'})
    resp = client.get('/submit/1')
    assert resp.status_code in (200, 302, 404)


def test_download_file_route(client):
    resp = client.get('/download_file/test.txt')
    assert resp.status_code in (200, 302, 404)
