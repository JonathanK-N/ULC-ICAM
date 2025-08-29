#!/usr/bin/env python3
"""
Plan d'optimisation ULC-ICAM Turnin
Analyse et recommandations pour améliorer les performances
"""

import os
import time
import psutil
import json
from datetime import datetime

class OptimizationAnalyzer:
    """Analyseur de performance et optimisation"""
    
    def __init__(self):
        self.recommendations = []
        self.metrics = {}
    
    def analyze_current_state(self):
        """Analyse l'état actuel de l'application"""
        print("ANALYSE DE PERFORMANCE ULC-ICAM")
        print("=" * 50)
        
        # 1. Analyse des fichiers
        self._analyze_file_structure()
        
        # 2. Analyse de la mémoire
        self._analyze_memory_usage()
        
        # 3. Analyse du code
        self._analyze_code_structure()
        
        # 4. Recommandations
        self._generate_recommendations()
        
        return self.recommendations
    
    def _analyze_file_structure(self):
        """Analyse la structure des fichiers"""
        print("\nSTRUCTURE DES FICHIERS")
        
        # Taille des uploads
        uploads_size = self._get_directory_size('uploads')
        print(f"Taille uploads: {uploads_size:.2f} MB")
        
        # Nombre de fichiers JSON
        json_files = [f for f in os.listdir('.') if f.endswith('.json')]
        print(f"Fichiers JSON: {len(json_files)}")
        
        if uploads_size > 100:
            self.recommendations.append({
                'type': 'storage',
                'priority': 'high',
                'issue': 'Dossier uploads volumineux',
                'solution': 'Implémenter nettoyage automatique des anciens fichiers'
            })
    
    def _analyze_memory_usage(self):
        """Analyse l'utilisation mémoire"""
        print("\nUTILISATION MEMOIRE")
        
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"Mémoire utilisée: {memory_mb:.2f} MB")
        
        if memory_mb > 200:
            self.recommendations.append({
                'type': 'memory',
                'priority': 'medium',
                'issue': 'Consommation mémoire élevée',
                'solution': 'Optimiser le chargement des données'
            })
    
    def _analyze_code_structure(self):
        """Analyse la structure du code"""
        print("\nSTRUCTURE DU CODE")
        
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Lignes de code: {len(lines)}")
        
        # Détection des variables globales
        global_vars = [line for line in lines if line.strip().startswith(('users =', 'assignments =', 'submissions ='))]
        print(f"Variables globales: {len(global_vars)}")
        
        if len(lines) > 2000:
            self.recommendations.append({
                'type': 'architecture',
                'priority': 'high',
                'issue': 'Fichier app.py trop volumineux',
                'solution': 'Diviser en modules séparés'
            })
    
    def _get_directory_size(self, directory):
        """Calcule la taille d'un dossier en MB"""
        if not os.path.exists(directory):
            return 0
        
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
        return total_size / (1024 * 1024)
    
    def _generate_recommendations(self):
        """Génère les recommandations d'optimisation"""
        print("\n" + "=" * 50)
        print("RECOMMANDATIONS D'OPTIMISATION")
        
        # Recommandations de base
        base_recommendations = [
            {
                'type': 'database',
                'priority': 'critical',
                'issue': 'Stockage JSON non scalable',
                'solution': 'Migration vers SQLite/PostgreSQL'
            },
            {
                'type': 'caching',
                'priority': 'high',
                'issue': 'Pas de mise en cache',
                'solution': 'Implémenter Redis/Flask-Caching'
            },
            {
                'type': 'async',
                'priority': 'high',
                'issue': 'Traitement IA synchrone',
                'solution': 'Queue asynchrone avec Celery'
            },
            {
                'type': 'security',
                'priority': 'high',
                'issue': 'Authentification basique',
                'solution': 'JWT tokens + rate limiting'
            },
            {
                'type': 'monitoring',
                'priority': 'medium',
                'issue': 'Pas de monitoring',
                'solution': 'Logs structurés + métriques'
            }
        ]
        
        self.recommendations.extend(base_recommendations)
        
        # Affichage des recommandations
        for i, rec in enumerate(self.recommendations, 1):
            priority_icon = {
                'critical': '[CRITICAL]',
                'high': '[HIGH]',
                'medium': '[MEDIUM]',
                'low': '[LOW]'
            }.get(rec['priority'], '[INFO]')
            
            print(f"\n{i}. {priority_icon} [{rec['priority'].upper()}] {rec['type'].upper()}")
            print(f"   Problème: {rec['issue']}")
            print(f"   Solution: {rec['solution']}")

def main():
    """Fonction principale"""
    analyzer = OptimizationAnalyzer()
    recommendations = analyzer.analyze_current_state()
    
    # Sauvegarde du rapport
    report = {
        'timestamp': datetime.now().isoformat(),
        'recommendations': recommendations
    }
    
    with open('optimization_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nRapport sauvegarde: optimization_report.json")
    print(f"Analyse effectuee le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()