import base64
from datetime import datetime
import pytest
from notification_routes import validate_subscription


def subscription(endpoint='https://fcm.googleapis.com/fcm/send/isolated'):
    return {'endpoint': endpoint, 'keys': {
        'p256dh': base64.urlsafe_b64encode(b'\x04' + b'x' * 64).decode().rstrip('='),
        'auth': base64.urlsafe_b64encode(b'x' * 16).decode().rstrip('=')}}


@pytest.mark.parametrize('endpoint', ['http://fcm.googleapis.com/x', 'https://127.0.0.1/x',
                                     'https://fcm.googleapis.com.evil.test/x',
                                     'https://user:pass@fcm.googleapis.com/x',
                                     'https://fcm.googleapis.com:8000/x'])
def test_push_rejects_untrusted_network_destinations(endpoint):
    with pytest.raises(ValueError):
        validate_subscription(subscription(endpoint))


def test_notifications_are_owned_and_subscriptions_are_idempotent(monkeypatch):
    import app as module
    monkeypatch.setattr(module, 'users', {'s': {'role': 'student', 'name': 'Student'}})
    monkeypatch.setattr(module, 'notifications', [{'id': 'mine', 'username': 's', 'message': 'Mine', 'url': '/dashboard'},
                                                {'id': 'other', 'username': 't', 'message': 'Private'}])
    monkeypatch.setattr(module, 'push_subscriptions', [])
    for key in ('VAPID_PUBLIC_KEY', 'VAPID_PRIVATE_KEY', 'VAPID_SUBJECT'):
        monkeypatch.setenv(key, 'isolated-test-only')
    module.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with module.app.test_client() as client:
        assert client.get('/api/notifications/push-config').status_code == 401
        with client.session_transaction() as sess:
            sess.update(user='s', role='student', name='Student', last_active=datetime.now().isoformat())
        response = client.get('/notifications')
        assert response.status_code == 200 and b'Private' not in response.data
        assert client.post('/api/notifications/other/read', json={}).status_code == 404
        assert client.post('/api/notifications/mine/read', json={}).status_code == 200
        assert client.post('/api/notifications/subscriptions', json=subscription()).status_code == 201
        assert client.post('/api/notifications/subscriptions', json=subscription()).status_code == 201
        assert len(module.push_subscriptions) == 1
        identifier = module.push_subscriptions[0]['id']
        assert client.post('/api/notifications/subscriptions/remove', json={'id': identifier}).status_code == 200
        assert module.push_subscriptions == []


def test_subscription_requires_csrf(monkeypatch):
    import app as module
    monkeypatch.setitem(module.app.config, 'WTF_CSRF_ENABLED', True)
    with module.app.test_client() as client:
        assert client.post('/api/notifications/subscriptions', json=subscription()).status_code == 400
