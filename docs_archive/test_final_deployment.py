#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Final de Déploiement - ULC-ICAM Turnin System
Teste toutes les fonctionnalités critiques avant déploiement
"""

import requests
import json
import os
import time
from datetime import datetime

class ULCTestSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        status = "PASS" if success else "FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        print(f"{status} - {test_name}: {message}")
    
    def test_homepage(self):
        """Test de la page d'accueil"""
        try:
            response = self.session.get(self.base_url)
            success = response.status_code == 200 and "ULC-ICAM" in response.text
            self.log_test("Page d'accueil", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Page d'accueil", False, str(e))
    
    def test_login_pages(self):
        """Test des pages de connexion"""
        login_pages = [
            ("/login", "Sélection de connexion"),
            ("/login/admin", "Connexion admin"),
            ("/login/teacher", "Connexion professeur"),
            ("/login/student", "Connexion étudiant")
        ]
        
        for url, name in login_pages:
            try:
                response = self.session.get(self.base_url + url)
                success = response.status_code == 200
                self.log_test(f"Page {name}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Page {name}", False, str(e))
    
    def test_admin_login(self):
        """Test de connexion administrateur"""
        try:
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            response = self.session.post(self.base_url + "/login/admin", data=login_data)
            success = response.status_code == 302 or "dashboard" in response.url
            self.log_test("Connexion admin", success, "Redirection vers dashboard")
            return success
        except Exception as e:
            self.log_test("Connexion admin", False, str(e))
            return False
    
    def test_admin_dashboard(self):
        """Test du tableau de bord admin"""
        try:
            response = self.session.get(self.base_url + "/dashboard")
            success = response.status_code == 200 and "administrateur" in response.text.lower()
            self.log_test("Dashboard admin", success, "Accès au tableau de bord")
        except Exception as e:
            self.log_test("Dashboard admin", False, str(e))
    
    def test_admin_pages(self):
        """Test des pages d'administration"""
        admin_pages = [
            ("/admin/users", "Gestion utilisateurs"),
            ("/admin/courses", "Gestion cours"),
            ("/admin/assignments", "Gestion devoirs"),
            ("/admin/submissions", "Gestion soumissions"),
            ("/admin/students", "Liste étudiants"),
            ("/admin/teachers", "Liste professeurs")
        ]
        
        for url, name in admin_pages:
            try:
                response = self.session.get(self.base_url + url)
                success = response.status_code == 200
                self.log_test(f"Page {name}", success, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Page {name}", False, str(e))
    
    def test_file_structure(self):
        """Test de la structure des fichiers"""
        required_dirs = [
            "uploads",
            "uploads/code_submissions",
            "uploads/submissions", 
            "uploads/corrections",
            "uploads/assignments",
            "uploads/chapters",
            "uploads/syllabus",
            "uploads/analysis"
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join("c:\\Users\\Lenovo\\OneDrive - USherbrooke\\Bureau\\ULC-ICAM\\ulc-turnin-web", dir_path)
            exists = os.path.exists(full_path)
            self.log_test(f"Dossier {dir_path}", exists, "Existe" if exists else "Manquant")
    
    def test_data_file(self):
        """Test du fichier de données"""
        try:
            data_file = "c:\\Users\\Lenovo\\OneDrive - USherbrooke\\Bureau\\ULC-ICAM\\ulc-turnin-web\\ulc_icam_data.json"
            exists = os.path.exists(data_file)
            if exists:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    has_users = 'users' in data and len(data['users']) > 0
                    has_admin = 'admin' in data.get('users', {})
                    self.log_test("Fichier données", has_users and has_admin, 
                                f"Utilisateurs: {len(data.get('users', {}))}")
            else:
                self.log_test("Fichier données", False, "Fichier manquant")
        except Exception as e:
            self.log_test("Fichier données", False, str(e))
    
    def test_plagiarism_detection(self):
        """Test de la détection de plagiat"""
        try:
            response = self.session.get(self.base_url + "/admin/check_all_plagiarism")
            # Même si redirection, la route doit exister
            success = response.status_code in [200, 302, 403]
            self.log_test("Détection plagiat", success, "Route accessible")
        except Exception as e:
            self.log_test("Détection plagiat", False, str(e))
    
    def test_code_execution(self):
        """Test de l'exécution de code"""
        try:
            # Test simple de la route de test
            test_data = {
                'code_content': 'print("Hello World")',
                'language': 'python'
            }
            response = self.session.post(self.base_url + "/test_submit", data=test_data)
            success = response.status_code == 200
            self.log_test("Exécution code", success, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Exécution code", False, str(e))
    
    def logout(self):
        """Déconnexion"""
        try:
            response = self.session.get(self.base_url + "/logout")
            success = response.status_code == 302
            self.log_test("Déconnexion", success, "Redirection vers accueil")
        except Exception as e:
            self.log_test("Déconnexion", False, str(e))
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("DEBUT DES TESTS DE DEPLOIEMENT ULC-ICAM")
        print("=" * 50)
        
        # Tests de base
        self.test_homepage()
        self.test_login_pages()
        
        # Tests admin
        if self.test_admin_login():
            self.test_admin_dashboard()
            self.test_admin_pages()
            self.test_plagiarism_detection()
            self.test_code_execution()
            self.logout()
        
        # Tests système
        self.test_file_structure()
        self.test_data_file()
        
        # Résumé
        self.print_summary()
    
    def print_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "=" * 50)
        print("RESUME DES TESTS")
        print("=" * 50)
        
        passed = sum(1 for test in self.test_results if "PASS" in test['status'])
        failed = sum(1 for test in self.test_results if "FAIL" in test['status'])
        total = len(self.test_results)
        
        print(f"Total: {total} tests")
        print(f"Reussis: {passed}")
        print(f"Echoues: {failed}")
        print(f"Taux de réussite: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\nTESTS ECHOUES:")
            for test in self.test_results:
                if "FAIL" in test['status']:
                    print(f"  - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 50)
        if failed == 0:
            print("TOUS LES TESTS SONT PASSES - PRET POUR LE DEPLOIEMENT!")
        else:
            print("CERTAINS TESTS ONT ECHOUE - VERIFIEZ AVANT LE DEPLOIEMENT")
        print("=" * 50)

if __name__ == "__main__":
    # Lancer les tests
    tester = ULCTestSuite()
    tester.run_all_tests()
    
    # Sauvegarder le rapport
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"test_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(tester.test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nRapport sauvegarde: {report_file}")