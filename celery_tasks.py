"""
TÃ¢ches asynchrones Celery pour traitement IA
Correction: instance Celery initialisÃ©e correctement via make_celery()
"""

from celery import Celery
import os
import json
from datetime import datetime

# ---------------------------------------------------------------
# Factory : crÃ©e et configure l'instance Celery
# AppelÃ©e depuis app.py APRÃˆS la crÃ©ation de l'app Flask
# ---------------------------------------------------------------
def make_celery(app):
    """CrÃ©e une instance Celery liÃ©e Ã  l'application Flask."""
    celery_instance = Celery(
        app.import_name,
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )

    celery_instance.conf.update(
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='Africa/Kinshasa',
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        beat_schedule=BEAT_SCHEDULE,
    )

    class ContextTask(celery_instance.Task):
        """TÃ¢che qui s'exÃ©cute toujours dans le contexte Flask."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask
    return celery_instance


# ---------------------------------------------------------------
# Planning des tÃ¢ches pÃ©riodiques
# ---------------------------------------------------------------
from celery.schedules import crontab

BEAT_SCHEDULE = {
    'generate-stats': {
        'task': 'celery_tasks.generate_statistics',
        'schedule': crontab(minute=0),             # Toutes les heures
    },
}


# ---------------------------------------------------------------
# RÃ©fÃ©rence globale (remplie par app.py via make_celery)
# Usage : from celery_tasks import celery; @celery.task
# ---------------------------------------------------------------
celery = Celery(__name__)   # instance temporaire, remplacÃ©e dans app.py


# ---------------------------------------------------------------
# DÃ©claration des tÃ¢ches
# NOTE: Les tÃ¢ches utilisent 'celery' qui sera remplacÃ© par
#       l'instance rÃ©elle une fois make_celery() appelÃ©.
# ---------------------------------------------------------------

def _get_task_app():
    """RÃ©cupÃ¨re l'instance Celery active (aprÃ¨s initialisation)."""
    return celery


@celery.task(bind=True, name='celery_tasks.process_plagiarism_async')
def process_plagiarism_async(self, submission_id, file_path):
    """Traitement asynchrone de la dÃ©tection de plagiat."""
    try:
        from app import extract_text_from_file, check_plagiarism_local

        self.update_state(state='PROGRESS', meta={'status': 'Extraction du texte...'})
        text = extract_text_from_file(file_path)

        self.update_state(state='PROGRESS', meta={'status': 'Analyse de plagiat...'})
        result = check_plagiarism_local(text, submission_id)

        _save_plagiarism_result(submission_id, result)
        return {'status': 'completed', 'result': result}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@celery.task(bind=True, name='celery_tasks.process_correction_async')
def process_correction_async(self, submission_id, file_path, assignment_data):
    """Traitement asynchrone de la correction automatique."""
    try:
        from app import extract_text_from_file, ai_auto_correction

        self.update_state(state='PROGRESS', meta={'status': 'Extraction du texte...'})
        text = extract_text_from_file(file_path)

        self.update_state(state='PROGRESS', meta={'status': 'Correction IA en cours...'})
        result = ai_auto_correction(text, assignment_data, submission_id)

        _save_correction_result(submission_id, result)
        return {'status': 'completed', 'result': result}

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


@celery.task(name='celery_tasks.cleanup_old_files')
def cleanup_old_files():
    """Retain educational records until an approved retention policy exists."""
    return {'status': 'disabled', 'deleted': 0,
            'reason': 'Referenced uploads must not be deleted by age alone'}


@celery.task(name='celery_tasks.generate_statistics')
def generate_statistics():
    """GÃ©nÃ©ration des statistiques systÃ¨me (JSON)."""
    try:
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        users = data.get('users', {})
        stats = {
            'users_total': len(users),
            'students_total': sum(1 for u in users.values() if u.get('role') == 'student'),
            'teachers_total': sum(1 for u in users.values() if u.get('role') == 'teacher'),
            'assignments_total': len(data.get('assignments', [])),
            'submissions_total': len(data.get('submissions', [])),
            'generated_at': datetime.utcnow().isoformat(),
        }

        with open('stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        return stats

    except Exception as e:
        return {'error': str(e)}


# ---------------------------------------------------------------
# Helpers (sauvegarde des rÃ©sultats)
# ---------------------------------------------------------------

def _save_plagiarism_result(submission_id, result):
    raise RuntimeError('Worker persistence is disabled until relational storage is integrated')


def _save_correction_result(submission_id, result):
    raise RuntimeError('Worker persistence is disabled until relational storage is integrated')
