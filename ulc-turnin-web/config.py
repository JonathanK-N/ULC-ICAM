"""
Configuration centralisée pour toutes les clés API et paramètres
ULC-ICAM Turnin System
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

class Config:
    """Configuration principale de l'application"""
    
    # === FLASK CONFIGURATION ===
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # === UPLOAD CONFIGURATION ===
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'py', 'java', 'cpp', 'c', 'js', 'html', 'css', 'md'}
    
    # === AI SERVICES API KEYS ===
    
    # OpenAI (GPT-3.5/4) - Pour correction automatique avancée
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', '500'))
    
    # Google Custom Search - Pour détection de plagiat web
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
    
    # Hugging Face - Pour modèles locaux
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')  # Optionnel
    HUGGINGFACE_MODEL = os.environ.get('HUGGINGFACE_MODEL', 'nlptown/bert-base-multilingual-uncased-sentiment')
    
    # === PLAGIARISM DETECTION SETTINGS ===
    PLAGIARISM_THRESHOLD_SUSPECT = float(os.environ.get('PLAGIARISM_THRESHOLD_SUSPECT', '50.0'))
    PLAGIARISM_THRESHOLD_ATTENTION = float(os.environ.get('PLAGIARISM_THRESHOLD_ATTENTION', '30.0'))
    PLAGIARISM_MAX_SOURCES = int(os.environ.get('PLAGIARISM_MAX_SOURCES', '5'))
    
    # === AUTO CORRECTION SETTINGS ===
    AUTO_CORRECTION_ENABLED = os.environ.get('AUTO_CORRECTION_ENABLED', 'true').lower() == 'true'
    CORRECTION_TIMEOUT = int(os.environ.get('CORRECTION_TIMEOUT', '30'))  # secondes
    
    # === DATABASE CONFIGURATION ===
    # Pour future migration vers vraie DB
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # === EMAIL CONFIGURATION ===
    # Pour notifications futures
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    
    # === SECURITY SETTINGS ===
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 heure
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    
    # === LOGGING CONFIGURATION ===
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'ulc_icam.log')
    
    @classmethod
    def validate_config(cls):
        """Valide la configuration et affiche les warnings"""
        warnings = []
        
        if not cls.OPENAI_API_KEY:
            warnings.append("⚠️  OpenAI API key manquante - correction basique utilisée")
        
        if not cls.GOOGLE_API_KEY:
            warnings.append("⚠️  Google API key manquante - détection plagiat locale uniquement")
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production' and cls.FLASK_ENV == 'production':
            warnings.append("🚨 ATTENTION: Changez la clé secrète en production!")
        
        return warnings

# Configuration pour différents environnements
class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    FLASK_ENV = 'production'
    
class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    DEBUG = True

# Sélection automatique de la configuration
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retourne la configuration selon l'environnement"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])