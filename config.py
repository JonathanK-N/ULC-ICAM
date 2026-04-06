# ===============================================================================
# Configuration centralisée - ULC-ICAM Turnin System
# ===============================================================================

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration principale."""

    # Clé secrète (OBLIGATOIRE en production via variable d'environnement)
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-only-change-in-production'

    DEBUG = os.environ.get('FLASK_ENV') == 'development'

    # Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'py', 'java', 'cpp', 'c', 'js', 'zip'}

    # Correction automatique
    AUTO_CORRECTION_ENABLED = True
    CORRECTION_TIMEOUT = 30

    # Détection plagiat
    PLAGIARISM_THRESHOLD = 30.0
    PLAGIARISM_ENABLED = True

    # Sécurité session
    SESSION_TIMEOUT = 3600          # 1 heure
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Données
    DATA_FILE = 'ulc_icam_data.json'
    BACKUP_ENABLED = True

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@ulc-icam.cd')
    NOTIFICATIONS_ENABLED = os.environ.get('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'

    # IA
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', '')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '')

    # Celery / Redis
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Compilateurs (Windows MSYS2 ou Linux PATH)
    C_COMPILER = os.environ.get('C_COMPILER', 'gcc')
    CPP_COMPILER = os.environ.get('CPP_COMPILER', 'g++')
    MSYS2_BIN = os.environ.get('MSYS2_BIN', r'C:\msys64\mingw64\bin')

    @classmethod
    def validate(cls):
        """Valide la configuration et retourne les avertissements."""
        warnings = []
        if cls.SECRET_KEY == 'dev-only-change-in-production':
            warnings.append("SECURITE: Définissez FLASK_SECRET_KEY en production")
        if not os.path.exists(cls.UPLOAD_FOLDER):
            warnings.append(f"INFO: Dossier '{cls.UPLOAD_FOLDER}' sera créé au démarrage")
        if not cls.OPENAI_API_KEY:
            warnings.append("INFO: OPENAI_API_KEY non définie — correction IA basique uniquement")
        return warnings


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

    # En production, la clé secrète DOIT être dans l'environnement
    @classmethod
    def validate(cls):
        warnings = super().validate()
        secret = os.environ.get('FLASK_SECRET_KEY', '')
        if not secret or secret == 'dev-only-change-in-production':
            raise ValueError(
                "ERREUR CRITIQUE: FLASK_SECRET_KEY n'est pas définie ou utilise "
                "la valeur par défaut en mode production. "
                "Définissez une clé aléatoire robuste (32+ caractères)."
            )
        return warnings


def get_config():
    """Retourne la classe de configuration selon l'environnement."""
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig
