#!/usr/bin/env python3
"""
Worker Celery pour traitement asynchrone
Lancer avec: python celery_worker.py
"""

import os
import sys
from app_optimized import create_app

# Créer l'application et Celery
app, celery = create_app()

if __name__ == '__main__':
    # Lancer le worker Celery
    celery.start()