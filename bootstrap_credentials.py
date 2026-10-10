"""Credentials for explicitly isolated administration scripts."""
import os
from werkzeug.security import generate_password_hash


def isolated_admin_hash():
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError('Administration de démonstration interdite en production')
    password = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD')
    if not password or len(password) < 16:
        raise RuntimeError('BOOTSTRAP_ADMIN_PASSWORD de 16 caractères minimum requis')
    return generate_password_hash(password)
