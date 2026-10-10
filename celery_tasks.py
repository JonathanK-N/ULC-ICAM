"""Pure worker tasks, registered on one Celery application."""
import os
from celery import Celery
from storage_bridge import repository_from_environment
from submission_processor import SubmissionProcessor, due_for_processing

celery = Celery('cognito')
BEAT_SCHEDULE = {'pending-submissions': {
    'task': 'celery_tasks.dispatch_pending_submissions', 'schedule': 30.0},
    'pending-notifications': {'task': 'celery_tasks.send_pending_notifications', 'schedule': 60.0},
    'pending-emails': {'task': 'celery_tasks.send_pending_emails', 'schedule': 60.0}}


def configure_celery():
    celery.conf.update(broker_url=os.environ.get('CELERY_BROKER_URL'),
                       result_backend=os.environ.get('CELERY_RESULT_BACKEND'),
                       task_serializer='json', result_serializer='json', accept_content=['json'],
                       timezone='UTC', enable_utc=True, task_track_started=True,
                       task_acks_late=True, worker_prefetch_multiplier=1,
                       task_soft_time_limit=180, task_time_limit=240,
                       result_expires=3600,
                       broker_connection_timeout=3, broker_transport_options={'socket_connect_timeout': 3,
                                                                            'socket_timeout': 3},
                       beat_schedule=BEAT_SCHEDULE)
    return celery


def make_celery(app):
    return configure_celery()


def worker_repository():
    repository = repository_from_environment(os.environ)
    if repository is None:
        raise RuntimeError('Worker persistence is disabled for JSON storage')
    if repository.engine.dialect.name != 'postgresql':
        repository.engine.dispose()
        raise RuntimeError('Concurrent workers require PostgreSQL')
    return repository


@celery.task(name='celery_tasks.process_submission')
def process_submission(submission_id):
    repository = worker_repository()
    try:
        return SubmissionProcessor(repository, os.environ.get('UPLOAD_FOLDER', 'uploads')).process(submission_id)
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.dispatch_pending_submissions')
def dispatch_pending_submissions():
    repository = worker_repository()
    try:
        with repository.transaction() as connection:
            snapshot = repository.load(connection)
        identifiers = [s['id'] for s in snapshot['submissions'] if due_for_processing(s)]
        for identifier in identifiers:
            process_submission.delay(identifier)
        return {'queued': len(identifiers)}
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.generate_statistics')
def generate_statistics():
    repository = worker_repository()
    try:
        with repository.transaction() as connection:
            data = repository.load(connection)
        return {'users_total': len(data['users']), 'assignments_total': len(data['assignments']),
                'submissions_total': len(data['submissions'])}
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.send_pending_notifications')
def send_pending_notifications():
    from push_service import deliver_notifications
    repository = worker_repository()
    try:
        return deliver_notifications(repository)
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.send_pending_emails')
def send_pending_emails():
    from email_service import deliver_emails
    repository = worker_repository()
    try:
        return deliver_emails(repository)
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.generate_assignment_report')
def generate_assignment_report(assignment_id, requested_by):
    from report_service import store_assignment_report
    repository = worker_repository()
    try:
        return store_assignment_report(repository, os.environ.get('UPLOAD_FOLDER', 'uploads'),
                                       assignment_id, requested_by)
    finally:
        repository.engine.dispose()


@celery.task(name='celery_tasks.cleanup_old_files')
def cleanup_old_files():
    return {'status': 'disabled', 'deleted': 0,
            'reason': 'An approved retention policy is required'}


def _save_plagiarism_result(submission_id, result):
    raise RuntimeError('Direct JSON worker writes are disabled')


def _save_correction_result(submission_id, result):
    raise RuntimeError('Direct JSON worker writes are disabled')
