"""
Tâches asynchrones Celery pour traitement IA
Correction: instance Celery initialisée correctement via make_celery()
"""

from celery import Celery
import os
import json
from datetime import datetime

# ---------------------------------------------------------------
# Factory : crée et configure l'instance Celery
# Appelée depuis app.py APRÈS la création de l'app Flask
# ---------------------------------------------------------------
def make_celery(app):
    """Crée une instance Celery liée à l'application Flask."""
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
        """Tâche qui s'exécute toujours dans le contexte Flask."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_instance.Task = ContextTask
    return celery_instance


# ---------------------------------------------------------------
# Planning des tâches périodiques
# ---------------------------------------------------------------
from celery.schedules import crontab

BEAT_SCHEDULE = {
    'cleanup-files': {
        'task': 'celery_tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),   # Tous les jours à 2h
    },
    'generate-stats': {
        'task': 'celery_tasks.generate_statistics',
        'schedule': crontab(minute=0),             # Toutes les heures
    },
}


# ---------------------------------------------------------------
# Référence globale (remplie par app.py via make_celery)
# Usage : from celery_tasks import celery; @celery.task
# ---------------------------------------------------------------
celery = Celery(__name__)   # instance temporaire, remplacée dans app.py


# ---------------------------------------------------------------
# Déclaration des tâches
# NOTE: Les tâches utilisent 'celery' qui sera remplacé par
#       l'instance réelle une fois make_celery() appelé.
# ---------------------------------------------------------------

def _get_task_app():
    """Récupère l'instance Celery active (après initialisation)."""
    return celery


@celery.task(bind=True, name='celery_tasks.process_plagiarism_async')
def process_plagiarism_async(self, submission_id, file_path):
    """Traitement asynchrone de la détection de plagiat."""
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
    """Nettoyage automatique des anciens fichiers (> 30 jours)."""
    import time

    cleaned = 0
    uploads_dir = os.environ.get('UPLOAD_FOLDER', 'uploads')

    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    if time.time() - os.path.getmtime(filepath) > 30 * 24 * 3600:
                        os.remove(filepath)
                        cleaned += 1
                except OSError:
                    pass

    return f"Nettoyage terminé: {cleaned} fichiers supprimés"


@celery.task(name='celery_tasks.generate_statistics')
def generate_statistics():
    """Génération des statistiques système (JSON)."""
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
# Helpers (sauvegarde des résultats)
# ---------------------------------------------------------------

def _save_plagiarism_result(submission_id, result):
    """Sauvegarde le résultat de plagiat dans le fichier JSON."""
    try:
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for sub in data.get('submissions', []):
            if sub['id'] == submission_id:
                sub['plagiarism'] = result
                break

        with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[Celery] Erreur sauvegarde plagiat: {e}")


def _save_correction_result(submission_id, result):
    """Sauvegarde le résultat de correction dans le fichier JSON."""
    try:
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for sub in data.get('submissions', []):
            if sub['id'] == submission_id:
                sub['correction'] = result
                break

        with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[Celery] Erreur sauvegarde correction: {e}")
