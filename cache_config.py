"""
Configuration du cache Redis/Flask-Caching
"""

from flask_caching import Cache
import os

def init_cache(app):
    """Initialise le système de cache"""
    
    # Configuration du cache
    if os.environ.get('REDIS_URL'):
        # Production avec Redis
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'ulc_icam:'
        }
    else:
        # Développement avec cache fichier
        cache_config = {
            'CACHE_TYPE': 'FileSystemCache',
            'CACHE_DIR': 'cache',
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_THRESHOLD': 1000
        }
    
    app.config.update(cache_config)
    cache = Cache(app)
    
    # Créer le dossier cache si nécessaire
    if cache_config['CACHE_TYPE'] == 'FileSystemCache':
        os.makedirs('cache', exist_ok=True)
    
    print(f"✅ Cache configuré: {cache_config['CACHE_TYPE']}")
    return cache

# Décorateurs de cache personnalisés
def cache_user_data(timeout=300):
    """Cache les données utilisateur"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            from flask import session
            if 'user' in session:
                cache_key = f"user_data:{session['user']}"
                # Implémentation du cache
            return f(*args, **kwargs)
        return wrapper
    return decorator

def cache_course_data(timeout=600):
    """Cache les données de cours"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # Implémentation du cache pour les cours
            return f(*args, **kwargs)
        return wrapper
    return decorator