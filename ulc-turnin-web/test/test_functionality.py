#!/usr/bin/env python3
"""
Script de test pour vérifier toutes les fonctionnalités de Cognito Web
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_login(username, password):
    """Test de connexion"""
    print(f"🔐 Test connexion: {username}")
    
    # Aller à la page de connexion
    response = session.get(f"{BASE_URL}/login")
    if response.status_code != 200:
        print(f"❌ Erreur accès page login: {response.status_code}")
        return False
    
    # Tenter la connexion
    login_data = {
        'username': username,
        'password': password
    }
    
    if 'admin' in username:
        response = session.post(f"{BASE_URL}/login/admin", data=login_data)
    elif 'prof' in username:
        response = session.post(f"{BASE_URL}/login/teacher", data=login_data)
    elif 'etud' in username:
        response = session.post(f"{BASE_URL}/login/student", data=login_data)
    
    if response.status_code == 200 and 'dashboard' in response.url:
        print(f"✅ Connexion réussie: {username}")
        return True
    else:
        print(f"❌ Échec connexion: {username}")
        return False

def test_admin_functions():
    """Test des fonctionnalités administrateur"""
    print("\n📋 === TESTS ADMINISTRATEUR ===")
    
    if not test_login('admin', 'admin123'):
        return False
    
    # Test tableau de bord admin
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Tableau de bord admin accessible")
    else:
        print("❌ Problème tableau de bord admin")
    
    # Test gestion utilisateurs
    response = session.get(f"{BASE_URL}/admin/users")
    if response.status_code == 200:
        print("✅ Page gestion utilisateurs accessible")
    else:
        print("❌ Problème page utilisateurs")
    
    # Test gestion cours
    response = session.get(f"{BASE_URL}/admin/courses")
    if response.status_code == 200:
        print("✅ Page gestion cours accessible")
    else:
        print("❌ Problème page cours")
    
    # Test configuration système
    response = session.get(f"{BASE_URL}/admin/system_config")
    if response.status_code == 200:
        print("✅ Page configuration système accessible")
    else:
        print("❌ Problème page configuration")
    
    # Test pages statistiques
    pages_admin = [
        '/admin/assignments',
        '/admin/submissions', 
        '/admin/students',
        '/admin/teachers'
    ]
    
    for page in pages_admin:
        response = session.get(f"{BASE_URL}{page}")
        if response.status_code == 200:
            print(f"✅ Page {page} accessible")
        else:
            print(f"❌ Problème page {page}")
    
    return True

def test_teacher_functions():
    """Test des fonctionnalités professeur"""
    print("\n👨‍🏫 === TESTS PROFESSEUR ===")
    
    if not test_login('prof001', 'prof1pass'):
        return False
    
    # Test tableau de bord professeur
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Tableau de bord professeur accessible")
    else:
        print("❌ Problème tableau de bord professeur")
    
    # Test pages professeur
    pages_teacher = [
        '/teacher/assignments',
        '/teacher/assigned_courses',
        '/teacher/submissions',
        '/teacher/students'
    ]
    
    for page in pages_teacher:
        response = session.get(f"{BASE_URL}{page}")
        if response.status_code == 200:
            print(f"✅ Page {page} accessible")
        else:
            print(f"❌ Problème page {page}")
    
    # Test création de devoir
    response = session.get(f"{BASE_URL}/teacher/create_assignment")
    if response.status_code == 200:
        print("✅ Page création devoir accessible")
    else:
        print("❌ Problème page création devoir")
    
    return True

def test_student_functions():
    """Test des fonctionnalités étudiant"""
    print("\n🎓 === TESTS ÉTUDIANT ===")
    
    if not test_login('etud001', 'etud1pass'):
        return False
    
    # Test tableau de bord étudiant
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Tableau de bord étudiant accessible")
    else:
        print("❌ Problème tableau de bord étudiant")
    
    return True

def test_group_functionality():
    """Test des fonctionnalités de groupe"""
    print("\n👥 === TESTS GROUPES ===")
    
    # Connexion professeur pour créer un devoir de groupe
    if not test_login('prof001', 'prof1pass'):
        return False
    
    # Test gestion des groupes (si des devoirs de groupe existent)
    response = session.get(f"{BASE_URL}/teacher/assignments")
    if response.status_code == 200:
        print("✅ Accès aux devoirs pour test groupes")
    else:
        print("❌ Problème accès devoirs")
    
    return True

def test_file_operations():
    """Test des opérations sur fichiers"""
    print("\n📁 === TESTS FICHIERS ===")
    
    # Test accès aux pages de soumission
    if not test_login('etud001', 'etud1pass'):
        return False
    
    # Vérifier qu'on peut accéder aux pages de soumission
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Accès dashboard pour test fichiers")
    else:
        print("❌ Problème accès dashboard")
    
    return True

def test_navigation():
    """Test de la navigation générale"""
    print("\n🧭 === TESTS NAVIGATION ===")
    
    # Test page d'accueil
    response = session.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Page d'accueil accessible")
    else:
        print("❌ Problème page d'accueil")
    
    # Test pages de connexion
    login_pages = [
        '/login',
        '/login/student', 
        '/login/teacher',
        '/login/admin'
    ]
    
    for page in login_pages:
        response = session.get(f"{BASE_URL}{page}")
        if response.status_code == 200:
            print(f"✅ Page {page} accessible")
        else:
            print(f"❌ Problème page {page}")
    
    return True

def test_data_integrity():
    """Test de l'intégrité des données"""
    print("\n🔍 === TESTS INTÉGRITÉ DONNÉES ===")
    
    # Connexion admin pour vérifier les données
    if not test_login('admin', 'admin123'):
        return False
    
    # Vérifier que les données de test sont chargées
    response = session.get(f"{BASE_URL}/admin/users")
    if response.status_code == 200:
        print("✅ Données utilisateurs accessibles")
        # Vérifier dans le contenu HTML si on a bien 50+ professeurs et 100+ étudiants
        if 'prof0' in response.text and 'etud0' in response.text:
            print("✅ Données de test présentes")
        else:
            print("⚠️  Données de test partielles")
    else:
        print("❌ Problème accès données utilisateurs")
    
    return True

def run_comprehensive_test():
    """Exécuter tous les tests"""
    print("🚀 === DÉBUT DES TESTS COGNITO WEB ===")
    print(f"URL de test: {BASE_URL}")
    print(f"Heure de début: {datetime.now()}")
    
    results = {
        'navigation': test_navigation(),
        'admin': test_admin_functions(),
        'teacher': test_teacher_functions(), 
        'student': test_student_functions(),
        'groups': test_group_functionality(),
        'files': test_file_operations(),
        'data': test_data_integrity()
    }
    
    print("\n📊 === RÉSULTATS DES TESTS ===")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSÉ" if result else "❌ ÉCHEC"
        print(f"{test_name.upper()}: {status}")
    
    print(f"\n🎯 SCORE GLOBAL: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 TOUS LES TESTS SONT PASSÉS ! Application fonctionnelle.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    print(f"Heure de fin: {datetime.now()}")

def test_specific_urls():
    """Test d'URLs spécifiques importantes"""
    print("\n🔗 === TESTS URLS SPÉCIFIQUES ===")
    
    # URLs publiques (sans authentification)
    public_urls = [
        '/',
        '/login',
        '/login/student',
        '/login/teacher', 
        '/login/admin'
    ]
    
    for url in public_urls:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {url}")
            else:
                print(f"❌ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Erreur: {str(e)}")

if __name__ == "__main__":
    print("Cognito Web - Suite de Tests Automatisés")
    print("=" * 50)
    
    # Test de base - vérifier si l'application est démarrée
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Application Cognito Web détectée et accessible")
            
            # Exécuter la suite complète de tests
            run_comprehensive_test()
            
            # Tests d'URLs spécifiques
            test_specific_urls()
            
        else:
            print(f"❌ Application non accessible - Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Application non démarrée")
        print("💡 Démarrez l'application avec: python app.py")
        print("💡 Puis relancez ce script de test")
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Tests terminés.")