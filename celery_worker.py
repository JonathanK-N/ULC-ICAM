"""Dedicated relational worker; importing this module never imports Flask."""
import os
from celery_tasks import celery, configure_celery

if os.environ.get('COGNITO_STORAGE') != 'relational':
    raise RuntimeError('Celery worker requires relational storage; Flask still uses JSON otherwise')
if not os.environ.get('DATABASE_URL') or not os.environ.get('CELERY_BROKER_URL'):
    raise RuntimeError('DATABASE_URL and CELERY_BROKER_URL are required')
configure_celery()

if __name__ == '__main__':
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=2'])
