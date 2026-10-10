# ===============================================================================
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 19:05
# Description: Script de lancement pour ULC-ICAM Turnin System
# Fonctionnalités: Démarrage sécurisé, vérifications, info startup
# Nouvelles: Support compression, rapports, téléchargement lot
# ===============================================================================

import os
import sys
from app import app
from config import get_config

def check_requirements():
    """Vérifie que tous les prérequis sont satisfaits"""
    print("Vérification des prérequis...")
    
    # Vérifier Python version
    if sys.version_info < (3, 8):
        print("Python 3.8 ou supérieur requis")
        return False
    
    # Vérifier les dossiers nécessaires
    required_dirs = ['uploads', 'uploads/submissions', 'uploads/corrections', 'templates']
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"Création du dossier: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # Vérifier les fichiers essentiels
    required_files = ['ulc_icam_data.json', '.env']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Fichier manquant: {file}")
            return False
    
    print("Tous les prérequis sont satisfaits")
    return True

def display_startup_info():
    """Affiche les informations de démarrage"""
    print("\n" + "="*60)
    print("ULC-ICAM TURNIN SYSTEM")
    print("="*60)
    print("Développeur: Jonathan Kakesa")
    print("Date: 2024-12-19")
    print("Version: 1.0.0 - Avec notifications email")
    print("Institution: Université Libre du Congo - ICAM")
    print("="*60)
    
    # Afficher la configuration
    config = get_config()
    print(f"Mode: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {config.DEBUG}")
    print(f"Dossier uploads: {config.UPLOAD_FOLDER}")
    
    # Afficher les comptes de test
    print("\nCOMPTES DE TEST:")
    print("   Admin : identifiants configurés lors de l’initialisation")
    print("   Enseignant: prof_mukendi / prof123")
    print("   Étudiant: etudiant_marie / etud123")
    print("   Étudiant: etudiant_paul / etud123")
    
    print("\nACCÈS:")
    print("   URL: http://localhost:5000")
    print("   Ctrl+C pour arrêter le serveur")
    print("="*60 + "\n")

def main():
    """Fonction principale de lancement"""
    try:
        # Vérifier les prérequis
        if not check_requirements():
            print("Impossible de démarrer l'application")
            sys.exit(1)
        
        # Afficher les informations de démarrage
        display_startup_info()
        
        # Démarrer l'application
        print("Démarrage du serveur ULC-ICAM Turnin...")
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\nArrêt du serveur ULC-ICAM Turnin")
        print("Merci d'avoir utilisé notre système!")
        
    except Exception as e:
        print(f"\nErreur lors du démarrage: {e}")
        print("Consultez la documentation pour plus d'informations")
        sys.exit(1)

if __name__ == '__main__':
    main()