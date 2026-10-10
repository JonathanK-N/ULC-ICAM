"""Web Push delivery with endpoint validation, bounded retries and revoked-device cleanup."""
import json
import os
import requests
import uuid
from datetime import datetime, timezone, timedelta
from notification_routes import validate_subscription, push_configured


class PushSession(requests.Session):
    def request(self, method, url, **kwargs):
        kwargs['allow_redirects'] = False
        kwargs['timeout'] = 10
        return super().request(method, url, **kwargs)


def send_push(subscription, payload):
    from pywebpush import webpush, WebPushException
    validate_subscription(subscription)
    with PushSession() as http:
        try:
            webpush(subscription_info=subscription, data=json.dumps(payload),
                    vapid_private_key=os.environ['VAPID_PRIVATE_KEY'],
                    vapid_claims={'sub': os.environ['VAPID_SUBJECT']},
                    timeout=10, ttl=3600, requests_session=http)
            return 'sent'
        except WebPushException as error:
            if error.response is not None and error.response.status_code in (404, 410):
                return 'expired'
            return 'retry'


def deliver_notifications(repository, sender=send_push):
    if not push_configured():
        return {'status': 'disabled', 'sent': 0}
    with repository.transaction() as connection:
        data = repository.load(connection)
        def available(item):
            if item.get('push_status') in ('sent', 'failed') or item.get('push_attempts', 0) >= 3:
                return False
            if item.get('push_status') == 'sending':
                try:
                    return datetime.now(timezone.utc) - datetime.fromisoformat(item['push_started']) > timedelta(minutes=10)
                except (KeyError, ValueError, TypeError):
                    return True
            return True
        pending = [item for item in data.get('notifications', [])
                   if available(item)][:1]
        for item in pending:
            item.update(push_status='sending', push_token=uuid.uuid4().hex,
                        push_started=datetime.now(timezone.utc).isoformat())
        subscriptions = data.get('push_subscriptions', [])
        repository.save(connection, data)
    outcomes = {}
    expired = set()
    for item in pending:
        devices = [device for device in subscriptions if device['username'] == item.get('username')]
        retry = False
        for device in devices:
            try:
                outcome = sender(device['subscription'], {
                    'title': 'Cognito Web', 'body': 'Une nouvelle information est disponible dans votre espace.',
                    'url': '/notifications', 'tag': item['id']})
            except Exception:
                outcome = 'retry'
            if outcome == 'expired':
                expired.add(device['id'])
            retry = retry or outcome == 'retry'
        outcomes[item['id']] = 'retry' if retry else 'sent'
    with repository.transaction() as connection:
        current = repository.load(connection)
        current['push_subscriptions'] = [device for device in current.get('push_subscriptions', [])
                                         if device['id'] not in expired]
        for item in current.get('notifications', []):
            claim = next((p for p in pending if p['id'] == item['id']), None)
            if item['id'] in outcomes and claim and item.get('push_token') == claim.get('push_token'):
                item['push_attempts'] = item.get('push_attempts', 0) + 1
                item['push_status'] = outcomes[item['id']]
                if item['push_status'] == 'retry' and item['push_attempts'] >= 3:
                    item['push_status'] = 'failed'
                item.pop('push_token', None)
        repository.save(connection, current)
    return {'status': 'completed', 'sent': sum(value == 'sent' for value in outcomes.values())}
