#!/usr/bin/env python3
"""
Script de réinitialisation complète du système ULC-ICAM
Efface toutes les données : utilisateurs, cours, devoirs, soumissions, etc.
"""

import json
import os
import shutil
from datetime import datetime

def reset_data_file():
    """Réinitialise le fichier de données JSON"""
    # Données par défaut avec seulement l'admin
    default_data = {
        'users': {
            'admin': {
                'password': 'admin123',
                'role': 'admin',
                'name': 'Administrateur ULC-ICAM'
            }
        },
        'admin_courses': [],
        'course_assignments': {},
        'course_enrollments': {},
        'assignments': [],
        'submissions': [],
        'next_course_admin_id': 1,
        'next_assignment_id': 1
    }
    
    # Sauvegarder les données réinitialisées
    with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    print("✅ Fichier de données réinitialisé")

def clean_upload_directories():
    """Nettoie tous les dossiers d'upload"""
    upload_dirs = [
        'uploads',
        'uploads/code_submissions',
        'uploads/submissions',
        'uploads/corrections',
        'uploads/assignments',
        'uploads/chapters',
        'uploads/syllabus',
        'uploads/analysis'
    ]
    
    for dir_path in upload_dirs:
        if os.path.exists(dir_path):
            # Supprimer tout le contenu du dossier
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Erreur suppression {file_path}: {e}")
            print(f"✅ Dossier {dir_path} nettoyé")
        else:
            # Créer le dossier s'il n'existe pas
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Dossier {dir_path} créé")

def main():
    """Fonction principale de réinitialisation"""
    print("🚨 RÉINITIALISATION COMPLÈTE DU SYSTÈME ULC-ICAM")
    print("=" * 60)
    
    # Confirmation
    response = input("⚠️  ATTENTION: Cette action supprimera TOUTES les données!\n"
                    "Tapez 'CONFIRMER' pour continuer: ")
    
    if response != 'CONFIRMER':
        print("❌ Réinitialisation annulée")
        return
    
    print("\n🔄 Début de la réinitialisation...")
    
    # Créer une sauvegarde avant réinitialisation
    if os.path.exists('ulc_icam_data.json'):
        backup_name = f"ulc_icam_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2('ulc_icam_data.json', backup_name)
        print(f"💾 Sauvegarde créée: {backup_name}")
    
    # Réinitialiser les données
    reset_data_file()
    
    # Nettoyer les dossiers d'upload
    clean_upload_directories()
    
    print("\n" + "=" * 60)
    print("✅ RÉINITIALISATION TERMINÉE")
    print("\n📋 État du système:")
    print("   - Utilisateurs: 1 (admin seulement)")
    print("   - Cours: 0")
    print("   - Devoirs: 0") 
    print("   - Soumissions: 0")
    print("   - Fichiers: supprimés")
    print("\n🔑 Compte administrateur:")
    print("   - Utilisateur: admin")
    print("   - Mot de passe: admin123")
    print("\n🚀 Le système est prêt pour une nouvelle utilisation!")

if __name__ == '__main__':
    main()