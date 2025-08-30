#!/usr/bin/env python3
"""
ULC-ICAM TURNIN SYSTEM - PLANIFICATEUR BACKUP
Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
Tous droits réservés - Logiciel Propriétaire

Planificateur de tâches de backup pour ULC-ICAM

UTILISATION RESTREINTE - Voir LICENSE pour les conditions
"""
import sys
import argparse
from datetime import datetime, timedelta
from backup_manager import BackupManager
from backup_config import *

def daily_backup():
    """Backup quotidien (incrémentiel DB + fichiers)"""
    manager = BackupManager()
    
    try:
        # Backup incrémentiel de la DB
        db_backup = manager.backup_database('incremental')
        manager.upload_to_cloud(db_backup)
        
        # Backup des fichiers étudiants
        files_backup = manager.backup_files('uploads')
        if files_backup:
            manager.upload_to_cloud(files_backup)
        
        # Backup des rapports
        reports_backup = manager.backup_files('reports')
        if reports_backup:
            manager.upload_to_cloud(reports_backup)
        
        # Nettoyage des anciens backups
        manager.cleanup_old_backups()
        
        print("✅ Backup quotidien terminé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur backup quotidien: {e}")
        sys.exit(1)

def weekly_backup():
    """Backup hebdomadaire (complet DB + tous fichiers)"""
    manager = BackupManager()
    
    try:
        # Backup complet de la DB
        db_backup = manager.backup_database('full')
        manager.upload_to_cloud(db_backup)
        
        # Backup de tous les répertoires
        for path_key in BACKUP_PATHS.keys():
            backup_file = manager.backup_files(path_key)
            if backup_file:
                manager.upload_to_cloud(backup_file)
        
        print("✅ Backup hebdomadaire terminé avec succès")
        
    except Exception as e:
        print(f"❌ Erreur backup hebdomadaire: {e}")
        sys.exit(1)

def test_restore():
    """Test de restauration"""
    manager = BackupManager()
    
    try:
        # Trouver le backup le plus récent
        backup_dir = Path(BACKUP_BASE_DIR) / 'database'
        if not backup_dir.exists():
            print("❌ Aucun backup trouvé")
            return
            
        latest_backup = max(backup_dir.glob('*.enc'), key=os.path.getctime)
        
        # Tester la restauration
        if manager.test_restore(latest_backup):
            print("✅ Test de restauration réussi")
        else:
            print("❌ Test de restauration échoué")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur test restauration: {e}")
        sys.exit(1)

def restore_from_backup(backup_file):
    """Restauration depuis un fichier de backup"""
    manager = BackupManager()
    
    try:
        if not Path(backup_file).exists():
            print(f"❌ Fichier de backup introuvable: {backup_file}")
            sys.exit(1)
            
        # Confirmation
        response = input(f"⚠️  Confirmer la restauration depuis {backup_file}? (oui/non): ")
        if response.lower() != 'oui':
            print("Restauration annulée")
            return
            
        manager.restore_database(backup_file)
        print("✅ Restauration terminée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur restauration: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Gestionnaire de backup ULC-ICAM')
    parser.add_argument('action', choices=['daily', 'weekly', 'test', 'restore'], 
                       help='Action à exécuter')
    parser.add_argument('--file', help='Fichier de backup pour la restauration')
    
    args = parser.parse_args()
    
    if args.action == 'daily':
        daily_backup()
    elif args.action == 'weekly':
        weekly_backup()
    elif args.action == 'test':
        test_restore()
    elif args.action == 'restore':
        if not args.file:
            print("❌ Fichier de backup requis pour la restauration")
            sys.exit(1)
        restore_from_backup(args.file)

if __name__ == '__main__':
    main()