#!/usr/bin/env python3
"""
Worker Celery pour traitement asynchrone ULC-ICAM
Lancer avec: celery -A celery_worker.celery worker --loglevel=info
Ou:          python celery_worker.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Importer l'application Flask réelle (app.py)
from app import app
from celery_tasks import make_celery

# Créer l'instance Celery liée à l'app Flask
celery = make_celery(app)

# Rendre les tâches disponibles dans ce module pour que Celery
# puisse les découvrir automatiquement
import celery_tasks
celery_tasks.celery = celery

if __name__ == '__main__':
    # Lancer le worker directement
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=2'])
