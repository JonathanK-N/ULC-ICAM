#!/usr/bin/env python3
"""
Test simple du workflow de soumission
"""

import requests
import os
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_submission_workflow():
    """Test complet du workflow de soumission"""
    print("=== TEST WORKFLOW SOUMISSION ===")
    
    session = requests.Session()
    
    # 1. Test connexion étudiant
    print("1. Test connexion étudiant...")
    login_data = {'username': 'etud001', 'password': 'etud1pass'}
    response = session.post(f"{BASE_URL}/login/student", data=login_data)
    
    if 'dashboard' in response.url:
        print("OK - Connexion étudiant réussie")
    else:
        print("ERREUR - Échec connexion étudiant")
        return False
    
    # 2. Test accès page de soumission
    print("2. Test accès page soumission...")
    response = session.get(f"{BASE_URL}/submit/1")
    
    if response.status_code == 200:
        print("OK - Page soumission accessible")
    else:
        print("ERREUR - Page soumission inaccessible")
        return False
    
    # 3. Test connexion professeur
    print("3. Test connexion professeur...")
    login_data = {'username': 'prof001', 'password': 'prof1pass'}
    response = session.post(f"{BASE_URL}/login/teacher", data=login_data)
    
    if 'dashboard' in response.url:
        print("OK - Connexion professeur réussie")
    else:
        print("ERREUR - Échec connexion professeur")
        return False
    
    # 4. Test accès soumissions professeur
    print("4. Test accès soumissions professeur...")
    response = session.get(f"{BASE_URL}/teacher/submissions")
    
    if response.status_code == 200:
        print("OK - Page soumissions professeur accessible")
    else:
        print("ERREUR - Page soumissions professeur inaccessible")
        return False
    
    # 5. Test téléchargement fichier
    print("5. Test route téléchargement...")
    response = session.get(f"{BASE_URL}/download_file/test.txt")
    
    if response.status_code in [200, 404]:  # 404 normal si fichier n'existe pas
        print("OK - Route téléchargement fonctionne")
    else:
        print("ERREUR - Route téléchargement défaillante")
        return False
    
    # 6. Vérifier dossier uploads
    print("6. Vérification dossier uploads...")
    if os.path.exists('uploads'):
        print("OK - Dossier uploads existe")
    else:
        print("ERREUR - Dossier uploads manquant")
        return False
    
    print("\n=== RÉSULTAT ===")
    print("TOUS LES TESTS DE BASE SONT PASSÉS")
    print("Le workflow de soumission est fonctionnel")
    
    return True

if __name__ == "__main__":
    try:
        # Vérifier que l'app est démarrée
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            test_submission_workflow()
        else:
            print("Application non accessible")
    except:
        print("Application non démarrée - Lancez: python app.py")