#!/usr/bin/env python3
"""
Moniteur de performance en temps réel
"""

import time
import psutil
import threading
from datetime import datetime
from flask import g, request
import functools

class PerformanceMonitor:
    """Moniteur de performance"""
    
    def __init__(self):
        self.metrics = {
            'requests': 0,
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'errors': 0
        }
        self.start_time = time.time()
    
    def track_request(self, func):
        """Décorateur pour tracker les requêtes"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                self.metrics['requests'] += 1
                
                # Temps de réponse
                response_time = time.time() - start_time
                self.metrics['response_times'].append(response_time)
                
                # Garder seulement les 100 dernières mesures
                if len(self.metrics['response_times']) > 100:
                    self.metrics['response_times'] = self.metrics['response_times'][-100:]
                
                return result
                
            except Exception as e:
                self.metrics['errors'] += 1
                raise e
        
        return wrapper
    
    def collect_system_metrics(self):
        """Collecte les métriques système"""
        def collect():
            while True:
                # Mémoire
                memory = psutil.virtual_memory()
                self.metrics['memory_usage'].append(memory.percent)
                
                # CPU
                cpu = psutil.cpu_percent(interval=1)
                self.metrics['cpu_usage'].append(cpu)
                
                # Garder seulement les 60 dernières mesures (1 minute)
                if len(self.metrics['memory_usage']) > 60:
                    self.metrics['memory_usage'] = self.metrics['memory_usage'][-60:]
                    self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-60:]
                
                time.sleep(1)
        
        thread = threading.Thread(target=collect, daemon=True)
        thread.start()
    
    def get_stats(self):
        """Retourne les statistiques actuelles"""
        uptime = time.time() - self.start_time
        
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times'])
        
        return {
            'uptime': uptime,
            'requests_total': self.metrics['requests'],
            'avg_response_time': round(avg_response_time * 1000, 2),  # en ms
            'current_memory': psutil.virtual_memory().percent,
            'current_cpu': psutil.cpu_percent(),
            'errors_total': self.metrics['errors'],
            'requests_per_minute': round(self.metrics['requests'] / (uptime / 60), 2) if uptime > 0 else 0
        }

# Instance globale
monitor = PerformanceMonitor()

def init_monitoring(app):
    """Initialise le monitoring pour Flask"""
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            monitor.metrics['response_times'].append(response_time)
            monitor.metrics['requests'] += 1
            
            # Garder seulement les 100 dernières mesures
            if len(monitor.metrics['response_times']) > 100:
                monitor.metrics['response_times'] = monitor.metrics['response_times'][-100:]
        
        return response
    
    @app.route('/admin/performance')
    def performance_dashboard():
        """Dashboard de performance (admin seulement)"""
        from flask import session, render_template_string
        
        if 'user' not in session or session.get('role') != 'admin':
            return "Accès non autorisé", 403
        
        stats = monitor.get_stats()
        
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Dashboard - ULC-ICAM</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .good { border-left: 5px solid #4CAF50; }
                .warning { border-left: 5px solid #FF9800; }
                .critical { border-left: 5px solid #F44336; }
                .value { font-size: 24px; font-weight: bold; color: #333; }
                .label { color: #666; font-size: 14px; }
            </style>
        </head>
        <body>
            <h1>📊 Performance Dashboard ULC-ICAM</h1>
            <p>Mise à jour automatique toutes les 5 secondes</p>
            
            <div class="metric good">
                <div class="value">{{ "%.1f"|format(stats.uptime/3600) }}h</div>
                <div class="label">Temps de fonctionnement</div>
            </div>
            
            <div class="metric {{ 'good' if stats.requests_per_minute < 10 else 'warning' if stats.requests_per_minute < 50 else 'critical' }}">
                <div class="value">{{ stats.requests_per_minute }}</div>
                <div class="label">Requêtes par minute</div>
            </div>
            
            <div class="metric {{ 'good' if stats.avg_response_time < 500 else 'warning' if stats.avg_response_time < 1000 else 'critical' }}">
                <div class="value">{{ stats.avg_response_time }}ms</div>
                <div class="label">Temps de réponse moyen</div>
            </div>
            
            <div class="metric {{ 'good' if stats.current_memory < 70 else 'warning' if stats.current_memory < 85 else 'critical' }}">
                <div class="value">{{ stats.current_memory }}%</div>
                <div class="label">Utilisation mémoire</div>
            </div>
            
            <div class="metric {{ 'good' if stats.current_cpu < 50 else 'warning' if stats.current_cpu < 80 else 'critical' }}">
                <div class="value">{{ stats.current_cpu }}%</div>
                <div class="label">Utilisation CPU</div>
            </div>
            
            <div class="metric {{ 'good' if stats.errors_total == 0 else 'critical' }}">
                <div class="value">{{ stats.errors_total }}</div>
                <div class="label">Erreurs totales</div>
            </div>
            
            <div class="metric good">
                <div class="value">{{ stats.requests_total }}</div>
                <div class="label">Requêtes totales</div>
            </div>
            
            <p><a href="/admin/dashboard">← Retour au dashboard admin</a></p>
        </body>
        </html>
        """
        
        return render_template_string(template, stats=stats)
    
    # Démarrer la collecte des métriques système
    monitor.collect_system_metrics()

if __name__ == "__main__":
    # Test du moniteur
    print("Test du moniteur de performance...")
    stats = monitor.get_stats()
    print(f"Stats: {stats}")