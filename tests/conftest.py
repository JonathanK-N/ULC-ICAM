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
