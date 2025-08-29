#!/usr/bin/env python3
"""
Script d'optimisation automatique ULC-ICAM
Applique les optimisations critiques
"""

import os
import shutil
import json
from datetime import datetime, timedelta

class AutoOptimizer:
    """Optimiseur automatique"""
    
    def __init__(self):
        self.optimizations_applied = []
    
    def run_optimizations(self):
        """Lance toutes les optimisations"""
        print("🚀 OPTIMISATION AUTOMATIQUE ULC-ICAM")
        print("=" * 50)
        
        # 1. Nettoyage des fichiers
        self._cleanup_old_files()
        
        # 2. Optimisation JSON
        self._optimize_json_storage()
        
        # 3. Compression des uploads
        self._compress_old_uploads()
        
        # 4. Création des index
        self._create_indexes()
        
        # 5. Configuration cache
        self._setup_caching()
        
        self._print_summary()
    
    def _cleanup_old_files(self):
        """Nettoie les anciens fichiers"""
        print("\n🧹 NETTOYAGE DES FICHIERS")
        
        cleaned = 0
        
        # Nettoyer les logs anciens
        for file in os.listdir('.'):
            if file.endswith('.log'):
                file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file))
                if file_age.days > 7:
                    os.remove(file)
                    cleaned += 1
        
        # Nettoyer uploads anciens (>30 jours)
        if os.path.exists('uploads'):
            for root, dirs, files in os.walk('uploads'):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_age.days > 30:
                            os.remove(filepath)
                            cleaned += 1
                    except:
                        pass
        
        print(f"✅ {cleaned} fichiers nettoyés")
        self.optimizations_applied.append(f"Nettoyage: {cleaned} fichiers supprimés")
    
    def _optimize_json_storage(self):
        """Optimise le stockage JSON"""
        print("\n📊 OPTIMISATION JSON")
        
        if os.path.exists('ulc_icam_data.json'):
            # Backup
            shutil.copy('ulc_icam_data.json', f'ulc_icam_data_backup_{datetime.now().strftime("%Y%m%d")}.json')
            
            # Compresser le JSON
            with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Sauvegarder sans indentation
            with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            
            print("✅ JSON optimisé et sauvegardé")
            self.optimizations_applied.append("JSON compressé")
    
    def _compress_old_uploads(self):
        """Compresse les anciens uploads"""
        print("\n🗜️ COMPRESSION DES UPLOADS")
        
        if not os.path.exists('uploads'):
            return
        
        import zipfile
        
        # Créer archive des fichiers > 7 jours
        archive_name = f'old_uploads_{datetime.now().strftime("%Y%m%d")}.zip'
        archived_count = 0
        
        with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('uploads'):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_age.days > 7:
                            zipf.write(filepath)
                            os.remove(filepath)
                            archived_count += 1
                    except:
                        pass
        
        if archived_count == 0:
            os.remove(archive_name)
        else:
            print(f"✅ {archived_count} fichiers archivés dans {archive_name}")
            self.optimizations_applied.append(f"Archive: {archived_count} fichiers")
    
    def _create_indexes(self):
        """Crée des index pour accélération"""
        print("\n📇 CRÉATION D'INDEX")
        
        # Index des utilisateurs par CIP/email
        if os.path.exists('ulc_icam_data.json'):
            with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Index utilisateurs
            user_index = {}
            for username, user_data in data.get('users', {}).items():
                if user_data.get('cip'):
                    user_index[user_data['cip']] = username
                if user_data.get('email'):
                    user_index[user_data['email']] = username
            
            # Index soumissions par étudiant
            submission_index = {}
            for submission in data.get('submissions', []):
                student = submission.get('student')
                if student not in submission_index:
                    submission_index[student] = []
                submission_index[student].append(submission['id'])
            
            # Sauvegarder les index
            indexes = {
                'users': user_index,
                'submissions': submission_index,
                'created_at': datetime.now().isoformat()
            }
            
            with open('indexes.json', 'w', encoding='utf-8') as f:
                json.dump(indexes, f, ensure_ascii=False)
            
            print("✅ Index créés")
            self.optimizations_applied.append("Index de recherche créés")
    
    def _setup_caching(self):
        """Configure le système de cache"""
        print("\n⚡ CONFIGURATION CACHE")
        
        # Créer dossier cache
        os.makedirs('cache', exist_ok=True)
        
        # Configuration cache simple
        cache_config = {
            'CACHE_TYPE': 'filesystem',
            'CACHE_DIR': 'cache',
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_THRESHOLD': 1000
        }
        
        with open('cache_config.json', 'w', encoding='utf-8') as f:
            json.dump(cache_config, f, indent=2)
        
        print("✅ Configuration cache créée")
        self.optimizations_applied.append("Cache configuré")
    
    def _print_summary(self):
        """Affiche le résumé des optimisations"""
        print("\n" + "=" * 50)
        print("📈 RÉSUMÉ DES OPTIMISATIONS")
        
        for i, optimization in enumerate(self.optimizations_applied, 1):
            print(f"{i}. ✅ {optimization}")
        
        print(f"\n🎯 {len(self.optimizations_applied)} optimisations appliquées")
        print(f"📅 Optimisation effectuée le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Fonction principale"""
    optimizer = AutoOptimizer()
    optimizer.run_optimizations()

if __name__ == "__main__":
    main()