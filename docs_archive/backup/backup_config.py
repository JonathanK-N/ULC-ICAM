#!/usr/bin/env python3
"""
ULC-ICAM TURNIN SYSTEM - CONFIGURATION BACKUP
Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
Tous droits réservés - Logiciel Propriétaire

Configuration centralisée pour le système de backup ULC-ICAM

UTILISATION RESTREINTE - Voir LICENSE pour les conditions
"""
import os
from datetime import datetime, timedelta

# Configuration générale
BACKUP_BASE_DIR = os.environ.get('BACKUP_BASE_DIR', '/opt/ulc-icam/backups')
ENCRYPTION_KEY = os.environ.get('BACKUP_ENCRYPTION_KEY', 'ulc-icam-backup-key-2024')
RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))

# Configuration base de données
DB_CONFIG = {
    'type': os.environ.get('DB_TYPE', 'postgresql'),  # postgresql, mysql
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'ulc_icam_db'),
    'username': os.environ.get('DB_USER', 'ulc_admin'),
    'password': os.environ.get('DB_PASSWORD', ''),
}

# Configuration stockage cloud
CLOUD_CONFIG = {
    'provider': os.environ.get('CLOUD_PROVIDER', 's3'),  # s3, azure, gcp
    'bucket': os.environ.get('CLOUD_BUCKET', 'ulc-icam-backups'),
    'region': os.environ.get('CLOUD_REGION', 'us-east-1'),
    'access_key': os.environ.get('CLOUD_ACCESS_KEY', ''),
    'secret_key': os.environ.get('CLOUD_SECRET_KEY', ''),
}

# Répertoires à sauvegarder
BACKUP_PATHS = {
    'uploads': os.environ.get('UPLOADS_DIR', '/opt/ulc-icam/uploads'),
    'reports': os.environ.get('REPORTS_DIR', '/opt/ulc-icam/reports'),
    'logs': os.environ.get('LOGS_DIR', '/opt/ulc-icam/logs'),
    'config': os.environ.get('CONFIG_DIR', '/opt/ulc-icam/config'),
}

# Notifications
NOTIFICATION_CONFIG = {
    'email': os.environ.get('BACKUP_NOTIFICATION_EMAIL', 'admin@ulc-icam.cd'),
    'webhook': os.environ.get('BACKUP_WEBHOOK_URL', ''),
}

def get_backup_filename(backup_type, date=None):
    """Génère un nom de fichier de backup standardisé"""
    if date is None:
        date = datetime.now()
    return f"ulc-icam-{backup_type}-{date.strftime('%Y%m%d_%H%M%S')}"