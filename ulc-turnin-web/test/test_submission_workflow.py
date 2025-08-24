#!/usr/bin/env python3
"""
Test spécifique du workflow de soumission et récupération des fichiers
"""

import requests
import os
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
session = requests.Session()

def create_test_file(filename, content):
    """Créer un fichier de test"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def test_student_submission():
    """Test de soumission par un étudiant"""
    print("🎓 === TEST SOUMISSION ÉTUDIANT ===")
    
    # Connexion étudiant
    login_data = {'username': 'etud001', 'password': 'etud1pass'}
    response = session.post(f"{BASE_URL}/login/student", data=login_data)
    
    if response.status_code != 200 or 'dashboard' not in response.url:
        print("❌ Échec connexion étudiant")
        return False
    
    print("✅ Connexion étudiant réussie")
    
    # Accéder au tableau de bord pour voir les devoirs
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Accès tableau de bord étudiant")
        
        # Vérifier qu'il y a des devoirs affichés
        if 'devoir' in response.text.lower() or 'assignment' in response.text.lower():
            print("✅ Devoirs visibles sur le tableau de bord")
        else:
            print("⚠️  Aucun devoir visible")
    
    # Tenter d'accéder à une page de soumission (devoir ID 1)
    response = session.get(f"{BASE_URL}/submit/1")
    if response.status_code == 200:
        print("✅ Accès page de soumission")
        
        # Créer un fichier de test
        test_file = create_test_file("test_submission.txt", 
                                   f"Soumission de test par etud001\nDate: {datetime.now()}\nContenu du devoir...")
        # Additional workflow details: see test/fixtures/submission_workflow_full.txt
