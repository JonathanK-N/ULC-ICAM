"""Request transaction boundaries for the legacy Flask routes."""
from copy import deepcopy
from threading import RLock
from flask import g, request
from sqlalchemy import create_engine, event
from snapshot_repository import SnapshotRepository


def repository_from_environment(environment):
    mode = environment.get('COGNITO_STORAGE', 'json')
    if mode == 'json':
        return None
    if mode != 'relational':
        raise RuntimeError('Unsupported COGNITO_STORAGE')
    url = environment.get('DATABASE_URL')
    if not url:
        raise RuntimeError('DATABASE_URL is required for relational storage')
    if url.startswith(('postgres://', 'postgresql://')):
        url = 'postgresql+psycopg://' + url.split('://', 1)[1]
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name not in ('postgresql', 'sqlite'):
        raise RuntimeError('Only PostgreSQL and isolated SQLite are supported')
    if engine.dialect.name == 'sqlite':
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')
    return SnapshotRepository(engine)


def restore_globals(namespace, data):
    defaults = {'users': {}, 'admin_courses': [], 'course_assignments': {},
                'course_enrollments': {}, 'assignments': [], 'submissions': [],
                'next_course_admin_id': 1, 'next_assignment_id': 1,
                'course_content': {}, 'course_chapters': {}, 'next_chapter_id': 1,
                'group_assignments': {}, 'student_groups': {}, 'next_group_id': 1,
                'notifications': [], 'audit_logs': [], 'push_subscriptions': [],
                'courses': [], 'next_course_id': 1, 'email_jobs': [], 'generated_reports': []}
    if 'system_config' in data:
        defaults['system_config'] = {}
    integer_keys = {'course_content', 'course_chapters', 'group_assignments', 'student_groups'}
    for key, default in defaults.items():
        value = deepcopy(data.get(key, default))
        if key in integer_keys:
            value = {int(k): v for k, v in value.items()}
        namespace[key] = value
    for field in ('correction', 'plagiarism'):
        namespace[field + '_results'] = {s['id']: s[field] for s in namespace['submissions']
                                        if field in s}


def install_storage(app, repository, namespace, collect_snapshot):
    local_lock = RLock()

    def begin():
        if request.endpoint == 'static' or request.endpoint in ('core.service_worker', 'core.web_manifest', 'core.offline'):
            return
        local_lock.acquire()
        g.storage_lock = True
        transaction = repository.transaction()
        connection = transaction.__enter__()
        g.storage_transaction = transaction
        g.storage_connection = connection
        g.storage_snapshot = repository.load(connection)
        g.storage_dirty = False
        restore_globals(namespace, g.storage_snapshot)

    # Storage must be refreshed before role/session checks execute.
    app.before_request_funcs.setdefault(None, []).insert(0, begin)

    @app.after_request
    def finish(response):
        transaction = g.pop('storage_transaction', None)
        if transaction is None:
            return response
        try:
            if response.status_code < 400:
                data = dict(g.storage_snapshot)
                data.update(collect_snapshot())
                if g.storage_dirty or (request.method == 'POST' and data != g.storage_snapshot):
                    repository.save(g.storage_connection, data)
                transaction.__exit__(None, None, None)
            else:
                error = RuntimeError('Request rejected')
                transaction.__exit__(type(error), error, None)
        except BaseException as error:
            transaction.__exit__(type(error), error, error.__traceback__)
            raise
        finally:
            if g.pop('storage_lock', False):
                local_lock.release()
        return response

    @app.teardown_request
    def rollback(error):
        transaction = g.pop('storage_transaction', None)
        try:
            if transaction:
                failure = error or RuntimeError('Request did not complete')
                transaction.__exit__(type(failure), failure, failure.__traceback__)
        finally:
            if g.pop('storage_lock', False):
                local_lock.release()


def install_json_storage(app, namespace, collect_snapshot):
    """Serialize legacy requests until PostgreSQL activation is approved."""
    local_lock = namespace['_data_lock']
    def begin():
        if request.endpoint == 'static':
            return
        local_lock.acquire()
        g.json_lock = True
        g.json_snapshot = deepcopy(collect_snapshot())
    app.before_request_funcs.setdefault(None, []).insert(0, begin)

    @app.after_request
    def finish(response):
        if not g.get('json_lock'):
            return response
        current = collect_snapshot()
        if response.status_code >= 400:
            if current != g.json_snapshot:
                restore_globals(namespace, g.json_snapshot)
        elif request.method == 'POST' and current != g.get('json_saved_snapshot', g.json_snapshot):
            namespace['save_test_data']()
        return response

    @app.teardown_request
    def cleanup(error):
        if g.pop('json_lock', False):
            try:
                if error:
                    restore_globals(namespace, g.json_snapshot)
            finally:
                local_lock.release()

