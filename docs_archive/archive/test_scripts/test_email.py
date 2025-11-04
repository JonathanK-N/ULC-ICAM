#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
                    TEST NOTIFICATIONS EMAIL ULC-ICAM
=============================================================================

Script de test pour vérifier la configuration des notifications email
du système ULC-ICAM Turnin.

Fonctionnalités testées:
- Configuration des variables d'environnement email
- Présence des données utilisateurs avec emails
- Validation de la configuration complète

Auteur: Jonathan Kakesa
Date: Décembre 2024
Version: 1.0

=============================================================================
"""

# Test simple des notifications email

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_config():
    print("=== TEST CONFIGURATION EMAIL ===")
    print(f"MAIL_SERVER: {os.environ.get('MAIL_SERVER', 'Non configuré')}")
    print(f"MAIL_PORT: {os.environ.get('MAIL_PORT', 'Non configuré')}")
    print(f"MAIL_USERNAME: {os.environ.get('MAIL_USERNAME', 'Non configuré')}")
    print(f"MAIL_PASSWORD: {'Configuré' if os.environ.get('MAIL_PASSWORD') else 'Non configuré'}")
    print(f"NOTIFICATIONS_ENABLED: {os.environ.get('NOTIFICATIONS_ENABLED', 'false')}")
    
    if os.environ.get('NOTIFICATIONS_ENABLED', 'false').lower() == 'true':
        print("\nNotifications activees")
        if os.environ.get('MAIL_USERNAME') and os.environ.get('MAIL_PASSWORD'):
            print("Configuration email complete")
            return True
        else:
            print("Configuration email incomplete")
            return False
    else:
        print("\nNotifications desactivees")
        return False

def test_data():
    print("\n=== TEST DONNÉES ===")
    try:
        import json
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        users = data.get('users', {})
        enrollments = data.get('course_enrollments', {})
        
        # Compter les étudiants avec email
        students_with_email = 0
        for username, user in users.items():
            if user.get('role') == 'student' and user.get('email'):
                students_with_email += 1
                print(f"  Étudiant: {user.get('name')} - {user.get('email')}")
        
        print(f"\n{students_with_email} etudiants avec email trouves")
        print(f"{len(enrollments)} cours avec inscriptions")
        
        return students_with_email > 0
        
    except Exception as e:
        print(f"Erreur lecture donnees: {e}")
        return False

if __name__ == '__main__':
    print("TEST SYSTÈME DE NOTIFICATIONS ULC-ICAM")
    print("=" * 50)
    
    config_ok = test_config()
    data_ok = test_data()
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Configuration: {'OK' if config_ok else 'ERREUR'}")
    print(f"Donnees: {'OK' if data_ok else 'ERREUR'}")
    
    if config_ok and data_ok:
        print("\nSysteme pret pour les notifications!")
        print("Pour tester:")
        print("1. Démarrez l'application: python app.py")
        print("2. Connectez-vous comme enseignant")
        print("3. Créez un nouveau devoir")
        print("4. Vérifiez les logs pour l'envoi d'email")
    else:
        print("\nConfiguration requise:")
        if not config_ok:
            print("- Configurez MAIL_USERNAME et MAIL_PASSWORD dans .env")
        if not data_ok:
            print("- Vérifiez les données dans ulc_icam_data.json")