"""
Tâches asynchrones Celery pour traitement IA
"""

from celery import Celery
import os
import json
from datetime import datetime

# Configuration Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Instance Celery (sera initialisée dans app.py)
celery = None

@celery.task(bind=True)
def process_plagiarism_async(self, submission_id, file_path):
    """Traitement asynchrone de la détection de plagiat"""
    try:
        from app import extract_text_from_file, check_plagiarism_local
        
        # Mise à jour du statut
        self.update_state(state='PROGRESS', meta={'status': 'Extraction du texte...'})
        
        text = extract_text_from_file(file_path)
        
        self.update_state(state='PROGRESS', meta={'status': 'Analyse de plagiat...'})
        
        result = check_plagiarism_local(text, submission_id)
        
        # Sauvegarder le résultat
        save_plagiarism_result(submission_id, result)
        
        return {'status': 'completed', 'result': result}
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery.task(bind=True)
def process_correction_async(self, submission_id, file_path, assignment_data):
    """Traitement asynchrone de la correction automatique"""
    try:
        from app import extract_text_from_file, ai_auto_correction
        
        self.update_state(state='PROGRESS', meta={'status': 'Extraction du texte...'})
        
        text = extract_text_from_file(file_path)
        
        self.update_state(state='PROGRESS', meta={'status': 'Correction IA en cours...'})
        
        result = ai_auto_correction(text, assignment_data, submission_id)
        
        # Sauvegarder le résultat
        save_correction_result(submission_id, result)
        
        return {'status': 'completed', 'result': result}
        
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise

@celery.task
def cleanup_old_files():
    """Nettoyage automatique des anciens fichiers"""
    import os
    import time
    
    cleaned = 0
    uploads_dir = 'uploads'
    
    if os.path.exists(uploads_dir):
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    # Supprimer les fichiers > 30 jours
                    if time.time() - os.path.getmtime(filepath) > 30 * 24 * 3600:
                        os.remove(filepath)
                        cleaned += 1
                except:
                    pass
    
    return f"Nettoyage terminé: {cleaned} fichiers supprimés"

@celery.task
def generate_statistics():
    """Génération des statistiques système"""
    from models import db, User, Assignment, Submission
    
    stats = {
        'users_total': User.query.count(),
        'students_total': User.query.filter_by(role='student').count(),
        'teachers_total': User.query.filter_by(role='teacher').count(),
        'assignments_total': Assignment.query.count(),
        'submissions_total': Submission.query.count(),
        'generated_at': datetime.utcnow().isoformat()
    }
    
    # Sauvegarder les stats
    with open('stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

def save_plagiarism_result(submission_id, result):
    """Sauvegarde le résultat de plagiat"""
    from models import db, PlagiarismResult
    
    plagiarism = PlagiarismResult(
        submission_id=submission_id,
        similarity=result.get('similarity', 0),
        sources=json.dumps(result.get('sources', [])),
        status=result.get('status', 'acceptable')
    )
    
    db.session.add(plagiarism)
    db.session.commit()

def save_correction_result(submission_id, result):
    """Sauvegarde le résultat de correction"""
    from models import db, CorrectionResult
    
    correction = CorrectionResult(
        submission_id=submission_id,
        score=result.get('score', 0),
        max_score=result.get('max_score', 100),
        feedback=json.dumps(result.get('feedback', [])),
        feedback_file=result.get('feedback_file'),
        auto_generated=result.get('auto_generated', True),
        ai_model=result.get('ai_model', 'Unknown')
    )
    
    db.session.add(correction)
    db.session.commit()

# Configuration des tâches périodiques
from celery.schedules import crontab

celery_beat_schedule = {
    'cleanup-files': {
        'task': 'celery_tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # Tous les jours à 2h
    },
    'generate-stats': {
        'task': 'celery_tasks.generate_statistics',
        'schedule': crontab(minute=0),  # Toutes les heures
    },
}