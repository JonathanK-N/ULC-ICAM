import importlib
import os
import time

import pytest
from sqlalchemy import select, Table, Column, Integer

import celery_tasks
import migration_schema as schema
from migrate_isolated import isolated_engine, import_snapshot
from submission_repository import SubmissionRepository


def test_cleanup_retains_old_course_files(tmp_path, monkeypatch):
    upload = tmp_path / 'course.pdf'
    upload.write_bytes(b'course')
    old = time.time() - 60 * 86400
    os.utime(upload, (old, old))
    monkeypatch.setenv('UPLOAD_FOLDER', str(tmp_path))
    assert celery_tasks.cleanup_old_files.run()['deleted'] == 0
    assert upload.read_bytes() == b'course'
    assert all(item['task'] != 'celery_tasks.cleanup_old_files'
               for item in celery_tasks.BEAT_SCHEDULE.values())


def test_worker_rejects_json_storage():
    with pytest.raises(RuntimeError, match='still uses JSON'):
        importlib.import_module('celery_worker')


@pytest.mark.parametrize('save', [celery_tasks._save_correction_result,
                                 celery_tasks._save_plagiarism_result])
def test_worker_helpers_cannot_rewrite_json(save, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = tmp_path / 'ulc_icam_data.json'
    data.write_text('{"submissions": []}')
    before = data.read_bytes()
    with pytest.raises(RuntimeError, match='disabled'):
        save(1, {'score': 100})
    assert data.read_bytes() == before


def test_alembic_revision_is_independent_of_future_models(tmp_path, monkeypatch):
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    future = Table('future_model', schema.metadata, Column('id', Integer, primary_key=True))
    url = 'sqlite:///' + (tmp_path / 'frozen.sqlite').as_posix()
    monkeypatch.setenv('ISOLATED_DATABASE_URL', url)
    try:
        command.upgrade(Config('alembic.ini'), 'head')
        engine = isolated_engine(url)
        assert 'future_model' not in inspect(engine).get_table_names()
        engine.dispose()
    finally:
        schema.metadata.remove(future)
