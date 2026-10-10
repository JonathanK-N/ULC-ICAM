"""Notification preferences and ownership-scoped subscription endpoints."""
import base64
import hashlib
import os
from urllib.parse import urlsplit
from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for


def validate_subscription(data):
    if not isinstance(data, dict):
        raise ValueError('Abonnement invalide')
    endpoint = data.get('endpoint', '')
    if not isinstance(endpoint, str) or len(endpoint) > 2048:
        raise ValueError('Adresse invalide')
    url = urlsplit(endpoint)
    host = url.hostname or ''
    allowed = host in ('fcm.googleapis.com', 'updates.push.services.mozilla.com', 'web.push.apple.com')
    allowed = allowed or host.endswith('.push.services.mozilla.com') or host.endswith('.notify.windows.com')
    if not allowed or url.scheme != 'https' or url.username or url.password or url.port not in (None, 443) or url.fragment:
        raise ValueError('Service de notifications non autorisé')
    keys = data.get('keys', {})
    if not isinstance(keys, dict):
        raise ValueError('Clés invalides')
    for key, size in [('p256dh', 65), ('auth', 16)]:
        value = keys.get(key)
        if not isinstance(value, str) or len(value) > 128:
            raise ValueError('Clé invalide')
        try:
            decoded = base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)
        except Exception as error:
            raise ValueError('Clé invalide') from error
        if len(decoded) != size or (key == 'p256dh' and decoded[0] != 4):
            raise ValueError('Clé invalide')
    return {'endpoint': endpoint, 'keys': {key: keys[key] for key in ('p256dh', 'auth')}}


def push_configured():
    return all(os.environ.get(key) for key in ('VAPID_PUBLIC_KEY', 'VAPID_PRIVATE_KEY', 'VAPID_SUBJECT'))


def create_notification_blueprint(state, save):
    blueprint = Blueprint('notifications', __name__)

    @blueprint.before_request
    def require_login():
        if 'user' not in session:
            return jsonify(error='Authentification requise'), 401

    @blueprint.get('/notifications')
    def preferences():
        items = [dict(item) for item in state('notifications') if item.get('username') == session['user']]
        for item in items:
            url = item.get('url', '')
            if not isinstance(url, str) or not url.startswith('/') or url.startswith('//') or '\\' in url:
                item['url'] = '/dashboard'
        return render_template('notifications.html', notifications=items[-100:][::-1],
                               push_enabled=push_configured())

    @blueprint.get('/api/notifications/push-config')
    def configuration():
        return jsonify(enabled=push_configured(), public_key=os.environ.get('VAPID_PUBLIC_KEY', '')
                       if push_configured() else '')

    @blueprint.post('/api/notifications/subscriptions')
    def subscribe():
        if not push_configured():
            return jsonify(error='Notifications navigateur non configurées'), 503
        try:
            subscription = validate_subscription(request.get_json(silent=True))
        except (ValueError, TypeError):
            return jsonify(error='Abonnement invalide'), 400
        subscriptions = state('push_subscriptions')
        identifier = hashlib.sha256(subscription['endpoint'].encode()).hexdigest()
        existing = next((item for item in subscriptions if item['id'] == identifier), None)
        if existing and existing['username'] != session['user']:
            return jsonify(error='Cet appareil est associé à un autre compte. Désabonnez-le d’abord.'), 409
        if existing:
            existing['subscription'] = subscription
        else:
            if sum(item['username'] == session['user'] for item in subscriptions) >= 10:
                return jsonify(error='Limite de dix appareils atteinte'), 409
            subscriptions.append({'id': identifier, 'username': session['user'], 'subscription': subscription})
        save()
        return jsonify(success=True, id=identifier), 201

    @blueprint.post('/api/notifications/subscriptions/remove')
    def unsubscribe():
        data = request.get_json(silent=True) or {}
        identifier = data.get('id')
        subscriptions = state('push_subscriptions')
        subscriptions[:] = [item for item in subscriptions if not
                             (item['id'] == identifier and item['username'] == session['user'])]
        save()
        return jsonify(success=True)

    @blueprint.post('/api/notifications/<identifier>/read')
    def mark_read(identifier):
        item = next((item for item in state('notifications') if item['id'] == identifier
                     and item.get('username') == session['user']), None)
        if item is None:
            return jsonify(error='Notification introuvable'), 404
        item['read'] = True
        save()
        if not request.is_json:
            return redirect(url_for('notifications.preferences'))
        return jsonify(success=True)

    return blueprint
