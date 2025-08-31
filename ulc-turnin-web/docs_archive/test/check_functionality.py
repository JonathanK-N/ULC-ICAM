import os
from app import users


def test_required_files_exist():
    required_files = [
        'app.py',
        'templates/base.html',
        'templates/index.html',
    ]
    for path in required_files:
        assert os.path.exists(path), f"{path} manquant"


def test_users_loaded():
    assert len(users) > 0


def test_routes_defined(client):
    routes = ['/', '/login', '/dashboard']
    defined = [rule.rule for rule in client.application.url_map.iter_rules()]
    for route in routes:
        assert any(route in r for r in defined)
