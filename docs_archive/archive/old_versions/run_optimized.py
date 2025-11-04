#!/usr/bin/env python3
"""
Script de lancement de l'application optimisée
"""

import os
import sys
import subprocess
import time
from app_optimized import create_app

def check_redis():
    """Vérifie si Redis est disponible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def start_redis():
    """Démarre Redis si nécessaire"""
    if not check_redis():
        print("⚠️  Redis non disponible - utilisation du cache fichier")
        return False
    else:
        print("✅ Redis disponible")
        return True

def start_celery_worker():
    """Démarre le worker Celery en arrière-plan"""
    if check_redis():
        try:
            subprocess.Popen([
                sys.executable, '-m', 'celery', '-A', 'celery_tasks', 
                'worker', '--loglevel=info'
            ])
            print("✅ Worker Celery démarré")
            return True
        except Exception as e:
            print(f"⚠️  Impossible de démarrer Celery: {e}")
            return False
    return False

def main():
    """Fonction principale"""
    print("🚀 DÉMARRAGE ULC-ICAM OPTIMISÉ")
    print("=" * 50)
    
    # Vérifications préalables
    redis_available = start_redis()
    celery_started = start_celery_worker() if redis_available else False
    
    # Créer l'application
    app, celery_app = create_app()
    
    # Configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("\n📊 CONFIGURATION")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Cache: {app.config.get('CACHE_TYPE', 'FileSystem')}")
    print(f"Redis: {'✅' if redis_available else '❌'}")
    print(f"Celery: {'✅' if celery_started else '❌'}")
    
    print("\n🎯 FONCTIONNALITÉS ACTIVÉES")
    print("✅ Base de données SQLite")
    print("✅ Cache intelligent")
    print("✅ Authentification JWT")
    print("✅ Rate limiting")
    print("✅ Compression des réponses")
    print("✅ Monitoring de performance")
    print("✅ Traitement IA asynchrone" if celery_started else "⚠️  Traitement IA synchrone")
    
    print(f"\n🌐 Application disponible sur: http://localhost:{port}")
    print("📈 Dashboard performance: http://localhost:{port}/admin/performance")
    
    if celery_started:
        print("🌸 Monitoring Celery: http://localhost:5555 (si Flower installé)")
    
    print("\n" + "=" * 50)
    
    # Démarrer l'application
    try:
        if debug:
            app.run(host='0.0.0.0', port=port, debug=True)
        else:
            # Production avec Gunicorn
            os.system(f"gunicorn --bind 0.0.0.0:{port} --workers 4 --timeout 120 app_optimized:create_app()")
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'application")

if __name__ == "__main__":
    main()