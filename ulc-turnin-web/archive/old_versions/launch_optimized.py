#!/usr/bin/env python3
"""
Lanceur simple pour l'application optimisée ULC-ICAM
Sans migration automatique pour éviter les conflits
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_compress import Compress
from flask_caching import Cache
import os
from datetime import datetime

# Import de l'app originale pour compatibilité
from app import *

def create_optimized_app():
    """Crée une version optimisée de l'app existante"""
    
    # Utiliser l'app existante comme base
    global app
    
    # Ajouter les optimisations
    Compress(app)
    
    # Configuration cache
    cache_config = {
        'CACHE_TYPE': 'FileSystemCache',
        'CACHE_DIR': 'cache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD': 1000
    }
    app.config.update(cache_config)
    
    # Créer dossier cache
    os.makedirs('cache', exist_ok=True)
    
    # Initialiser le cache
    cache = Cache(app)
    
    # Optimiser la route index avec cache
    original_index = app.view_functions['index']
    
    @cache.cached(timeout=300)
    def cached_index():
        return original_index()
    
    app.view_functions['index'] = cached_index
    
    # Ajouter route de monitoring
    @app.route('/admin/performance')
    def performance_dashboard():
        if session.get('role') != 'admin':
            return "Accès non autorisé", 403
        
        import psutil
        
        stats = {
            'memory': psutil.virtual_memory().percent,
            'cpu': psutil.cpu_percent(),
            'users_count': len(users),
            'assignments_count': len(assignments),
            'submissions_count': len(submissions)
        }
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance - ULC-ICAM</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .value { font-size: 24px; font-weight: bold; color: #333; }
                .label { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>Performance Dashboard ULC-ICAM</h1>
            <div class="metric">
                <div class="value">{{ stats.memory }}%</div>
                <div class="label">Utilisation mémoire</div>
            </div>
            <div class="metric">
                <div class="value">{{ stats.cpu }}%</div>
                <div class="label">Utilisation CPU</div>
            </div>
            <div class="metric">
                <div class="value">{{ stats.users_count }}</div>
                <div class="label">Utilisateurs</div>
            </div>
            <div class="metric">
                <div class="value">{{ stats.assignments_count }}</div>
                <div class="label">Devoirs</div>
            </div>
            <div class="metric">
                <div class="value">{{ stats.submissions_count }}</div>
                <div class="label">Soumissions</div>
            </div>
            <p><a href="/admin/dashboard">← Retour</a></p>
        </body>
        </html>
        """
        
        from flask import render_template_string
        return render_template_string(template, stats=stats)
    
    print("Optimisations appliquees:")
    print("  - Compression des réponses")
    print("  - Cache FileSystem")
    print("  - Dashboard performance")
    print("  - Monitoring système")
    
    return app

if __name__ == '__main__':
    # Créer l'app optimisée
    optimized_app = create_optimized_app()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("ULC-ICAM OPTIMISE DEMARRE")
    print(f"Port: {port}")
    print(f"Cache: FileSystem")
    print(f"Performance: /admin/performance")
    print(f"URL: http://localhost:{port}")
    
    optimized_app.run(host='0.0.0.0', port=port, debug=debug)