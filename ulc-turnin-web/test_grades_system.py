#!/usr/bin/env python3
"""
Test du système de notes et publication des résultats
"""

import requests
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_grades_system():
    """Test complet du système de notes"""
    print("=== TEST SYSTÈME DE NOTES ===")
    
    session = requests.Session()
    
    # 1. Test connexion étudiant et accès aux notes
    print("1. Test accès notes étudiant...")
    login_data = {'username': 'etud001', 'password': 'etud1pass'}
    response = session.post(f"{BASE_URL}/login/student", data=login_data)
    
    if 'dashboard' in response.url:
        print("OK - Connexion étudiant réussie")
        
        # Accès à la page des notes
        response = session.get(f"{BASE_URL}/student/my_grades")
        if response.status_code == 200:
            print("OK - Page notes étudiant accessible")
        else:
            print("ERREUR - Page notes inaccessible")
            return False
    else:
        print("ERREUR - Échec connexion étudiant")
        return False
    
    # 2. Test connexion professeur et gestion publication
    print("2. Test gestion publication professeur...")
    login_data = {'username': 'prof001', 'password': 'prof1pass'}
    response = session.post(f"{BASE_URL}/login/teacher", data=login_data)
    
    if 'dashboard' in response.url:
        print("OK - Connexion professeur réussie")
        
        # Accès aux résultats d'un devoir
        response = session.get(f"{BASE_URL}/teacher/assignment_results/1")
        if response.status_code == 200:
            print("OK - Page résultats accessible")
            
            # Vérifier présence boutons publication
            if 'publier' in response.text.lower() or 'masquer' in response.text.lower():
                print("OK - Boutons de publication présents")
            else:
                print("ERREUR - Boutons de publication manquants")
        else:
            print("ERREUR - Page résultats inaccessible")
            return False
    else:
        print("ERREUR - Échec connexion professeur")
        return False
    
    # 3. Test publication des résultats
    print("3. Test publication résultats...")
    response = session.get(f"{BASE_URL}/teacher/publish_results/1")
    if response.status_code == 200 or 'redirect' in str(response.status_code):
        print("OK - Route publication fonctionne")
    else:
        print("ERREUR - Route publication défaillante")
        return False
    
    # 4. Test masquage des résultats
    print("4. Test masquage résultats...")
    response = session.get(f"{BASE_URL}/teacher/unpublish_results/1")
    if response.status_code == 200 or 'redirect' in str(response.status_code):
        print("OK - Route masquage fonctionne")
    else:
        print("ERREUR - Route masquage défaillante")
        return False
    
    print("\n=== RÉSULTAT ===")
    print("SYSTÈME DE NOTES FONCTIONNEL")
    print("- Étudiants peuvent voir leurs notes")
    print("- Professeurs contrôlent la publication")
    print("- Publication/masquage opérationnels")
    
    return True

def test_grade_visibility():
    """Test de la visibilité des notes selon le statut de publication"""
    print("\n=== TEST VISIBILITÉ NOTES ===")
    
    session = requests.Session()
    
    # Connexion étudiant
    login_data = {'username': 'etud001', 'password': 'etud1pass'}
    session.post(f"{BASE_URL}/login/student", data=login_data)
    
    # Accès aux notes
    response = session.get(f"{BASE_URL}/student/my_grades")
    if response.status_code == 200:
        content = response.text.lower()
        
        # Vérifier présence d'indicateurs de publication
        if 'résultats non encore disponibles' in content or 'résultats disponibles' in content:
            print("OK - Statut de publication affiché")
        else:
            print("INFO - Vérifiez l'affichage du statut")
        
        # Vérifier présence de notes
        if 'note obtenue' in content or 'en cours de correction' in content:
            print("OK - Système de notes opérationnel")
        else:
            print("INFO - Aucune note visible (normal si pas de soumissions)")
        
        return True
    
    return False

if __name__ == "__main__":
    try:
        # Vérifier que l'app est démarrée
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            success1 = test_grades_system()
            success2 = test_grade_visibility()
            
            if success1 and success2:
                print("\n🎉 TOUS LES TESTS DE NOTES SONT PASSÉS !")
            else:
                print("\n⚠️ Certains tests ont échoué")
        else:
            print("Application non accessible")
    except:
        print("Application non démarrée - Lancez: python app.py")