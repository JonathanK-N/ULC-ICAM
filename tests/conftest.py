"""Run tests against disposable storage; never import production data."""
import os
import tempfile
from pathlib import Path

_storage = tempfile.TemporaryDirectory(prefix='cognito-tests-')
os.environ['DATA_FILE'] = str(Path(_storage.name) / 'data.json')
os.environ['UPLOAD_FOLDER'] = str(Path(_storage.name) / 'uploads')
os.environ['FLASK_SECRET_KEY'] = 'isolated-test-session-key'
os.environ.pop('BOOTSTRAP_ADMIN_PASSWORD', None)
os.environ.pop('REDIS_URL', None)
for _key in ('COGNITO_STORAGE', 'DATABASE_URL', 'VAPID_PUBLIC_KEY', 'VAPID_PRIVATE_KEY', 'VAPID_SUBJECT'):
    os.environ.pop(_key, None)
