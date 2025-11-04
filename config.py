# ===============================================================================
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 18:55
# Description: Configuration centralisée pour ULC-ICAM Turnin System
# Fonctionnalités: Paramètres app, email, uploads, sécurité, environnements
# Nouvelles: Support compression, rapports, téléchargement lot
# ===============================================================================

import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

class Config:
    """Configuration principale de l'application ULC-ICAM"""
    
    # Configuration Flask de base
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'ulc-icam-secret-key-2024'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Configuration des clés API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    
    # Configuration des uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB maximum
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'py', 'java', 'cpp', 'c'}
    
    # Configuration de la correction automatique
    AUTO_CORRECTION_ENABLED = True
    CORRECTION_TIMEOUT = 30  # secondes
    
    # Configuration de la détection de plagiat
    PLAGIARISM_THRESHOLD = 30.0  # Pourcentage de similarité
    PLAGIARISM_ENABLED = True
    
    # Configuration de sécurité
    SESSION_TIMEOUT = 3600  # 1 heure
    MAX_LOGIN_ATTEMPTS = 5
    
    # Configuration des données
    DATA_FILE = 'data.json'
    BACKUP_ENABLED = True
    
    # Configuration email pour notifications
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@ulc-icam.cd')
    
    # Configuration des notifications
    NOTIFICATIONS_ENABLED = os.environ.get('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
    NOTIFICATION_TYPES = {
        'new_assignment': True,
        'grades_published': True,
        'assignment_reminder': True
    }
    
    @classmethod
    def validate(cls):
        """Valide la configuration et retourne les avertissements"""
        warnings = []
        
        if cls.SECRET_KEY == 'ulc-icam-secret-key-2024':
            warnings.append("⚠️ Changez la clé secrète en production")
        
        if not os.path.exists(cls.UPLOAD_FOLDER):
            warnings.append(f"📁 Dossier {cls.UPLOAD_FOLDER} sera créé")
        
        return warnings

# Configuration pour différents environnements
class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'CHANGE-ME-IN-PRODUCTION'

# Sélection automatique de la configuration
def get_config():
    """Retourne la configuration selon l'environnement"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig