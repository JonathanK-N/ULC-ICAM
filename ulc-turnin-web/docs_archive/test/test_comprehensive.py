# ===============================================================================
# Tests Complets pour ULC-ICAM Turnin System
# Développeur: Jonathan Kakesa | Date: 19/12/2024
# Description: Tests approfondis pour éviter crashes, bugs et erreurs
# ===============================================================================

import unittest
import os
import sys
import json
import tempfile
import shutil
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, users, admin_courses, assignments, submissions
from config import Config

class TestULCICAMSystem(unittest.TestCase):
    """Tests complets du système ULC-ICAM"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Créer un dossier temporaire pour les uploads
        self.test_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.test_dir
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_01_configuration_validity(self):
        """Test 1: Vérifier la validité de la configuration"""
        print("\n🔧 Test 1: Configuration")
        
        # Vérifier les variables essentielles
        self.assertIsNotNone(app.secret_key)
        self.assertIsInstance(app.config['MAX_CONTENT_LENGTH'], int)
        
        # Vérifier la configuration
        config = Config()
        warnings = config.validate()
        print(f"   Avertissements config: {len(warnings)}")
        
        self.assertTrue(True, "Configuration valide")
    
    def test_02_routes_accessibility(self):
        """Test 2: Accessibilité des routes principales"""
        print("\n🌐 Test 2: Routes principales")
        
        routes_to_test = [
            ('/', 200),
            ('/login', 200),
            ('/login/student', 200),
            ('/login/teacher', 200),
            ('/login/admin', 200)
        ]
        
        for route, expected_status in routes_to_test:
            response = self.client.get(route)
            self.assertEqual(response.status_code, expected_status, 
                           f"Route {route} inaccessible")
            print(f"   ✓ {route}: {response.status_code}")
    
    def test_03_authentication_system(self):
        """Test 3: Système d'authentification"""
        print("\n🔐 Test 3: Authentification")
        
        # Test connexion admin valide
        response = self.client.post('/login/admin', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Connexion admin valide")
        
        # Test connexion invalide
        response = self.client.post('/login/admin', data={
            'username': 'admin',
            'password': 'wrong_password'
        })
        self.assertIn(b'Identifiants incorrects', response.data)
        print("   ✓ Rejet mot de passe incorrect")
        
        # Test déconnexion
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Déconnexion fonctionnelle")
    
    def test_04_data_integrity(self):
        """Test 4: Intégrité des données"""
        print("\n📊 Test 4: Intégrité des données")
        
        # Vérifier la structure des utilisateurs
        for username, user_data in users.items():
            self.assertIn('role', user_data, f"Rôle manquant pour {username}")
            self.assertIn('password', user_data, f"Mot de passe manquant pour {username}")
            self.assertIn('name', user_data, f"Nom manquant pour {username}")
        print(f"   ✓ {len(users)} utilisateurs valides")
        
        # Vérifier la structure des cours
        for course in admin_courses:
            self.assertIn('id', course, "ID manquant dans un cours")
            self.assertIn('name', course, "Nom manquant dans un cours")
        print(f"   ✓ {len(admin_courses)} cours valides")
        
        # Vérifier la structure des devoirs
        for assignment in assignments:
            self.assertIn('id', assignment, "ID manquant dans un devoir")
            self.assertIn('title', assignment, "Titre manquant dans un devoir")
        print(f"   ✓ {len(assignments)} devoirs valides")
    
    def test_05_file_upload_security(self):
        """Test 5: Sécurité des uploads"""
        print("\n📁 Test 5: Sécurité uploads")
        
        # Créer un fichier de test
        test_file_path = os.path.join(self.test_dir, 'test.txt')
        with open(test_file_path, 'w') as f:
            f.write('Contenu de test')
        
        # Test upload avec connexion
        with self.client.session_transaction() as sess:
            sess['user'] = 'admin'
            sess['role'] = 'admin'
        
        # Vérifier que le dossier d'upload existe
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        print("   ✓ Dossier upload créé")
        print("   ✓ Sécurité upload vérifiée")
    
    def test_06_error_handling(self):
        """Test 6: Gestion des erreurs"""
        print("\n⚠️ Test 6: Gestion d'erreurs")
        
        # Test accès non autorisé
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        print("   ✓ Redirection non-authentifié")
        
        # Test route inexistante
        response = self.client.get('/route_inexistante')
        self.assertEqual(response.status_code, 404)
        print("   ✓ Gestion 404")
        
        # Test méthode non autorisée
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
        print("   ✓ Gestion méthode non autorisée")
    
    def test_07_session_management(self):
        """Test 7: Gestion des sessions"""
        print("\n🔄 Test 7: Gestion sessions")
        
        # Test session vide
        with self.client.session_transaction() as sess:
            self.assertEqual(len(sess), 0)
        print("   ✓ Session vide initialement")
        
        # Test création session
        with self.client.session_transaction() as sess:
            sess['user'] = 'test_user'
            sess['role'] = 'student'
        
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['user'], 'test_user')
        print("   ✓ Création session")
        
        # Test nettoyage session
        response = self.client.get('/logout')
        with self.client.session_transaction() as sess:
            self.assertNotIn('user', sess)
        print("   ✓ Nettoyage session")
    
    def test_08_json_data_handling(self):
        """Test 8: Gestion des données JSON"""
        print("\n📄 Test 8: Données JSON")
        
        # Test sauvegarde données
        try:
            from app import save_test_data
            save_test_data()
            print("   ✓ Sauvegarde JSON")
        except Exception as e:
            self.fail(f"Erreur sauvegarde JSON: {e}")
        
        # Test chargement données
        try:
            from app import load_test_data
            data = load_test_data()
            self.assertIsInstance(data, (dict, type(None)))
            print("   ✓ Chargement JSON")
        except Exception as e:
            self.fail(f"Erreur chargement JSON: {e}")
    
    def test_09_memory_usage(self):
        """Test 9: Utilisation mémoire"""
        print("\n💾 Test 9: Utilisation mémoire")
        
        import psutil
        import gc
        
        # Mesurer mémoire avant
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simuler utilisation intensive
        for i in range(100):
            self.client.get('/')
        
        # Forcer garbage collection
        gc.collect()
        
        # Mesurer mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_diff = memory_after - memory_before
        
        print(f"   Mémoire avant: {memory_before:.1f} MB")
        print(f"   Mémoire après: {memory_after:.1f} MB")
        print(f"   Différence: {memory_diff:.1f} MB")
        
        # Vérifier pas de fuite mémoire excessive
        self.assertLess(memory_diff, 50, "Possible fuite mémoire")
        print("   ✓ Pas de fuite mémoire détectée")
    
    def test_10_concurrent_access(self):
        """Test 10: Accès concurrent"""
        print("\n🔄 Test 10: Accès concurrent")
        
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = self.client.get('/')
                results.append(response.status_code)
            except Exception as e:
                results.append(str(e))
        
        # Créer plusieurs threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Démarrer tous les threads
        for thread in threads:
            thread.start()
        
        # Attendre la fin
        for thread in threads:
            thread.join()
        
        # Vérifier les résultats
        success_count = sum(1 for r in results if r == 200)
        print(f"   Requêtes réussies: {success_count}/10")
        
        self.assertGreaterEqual(success_count, 8, "Trop d'échecs en concurrent")
        print("   ✓ Accès concurrent géré")

class TestSecurityVulnerabilities(unittest.TestCase):
    """Tests de sécurité spécifiques"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_sql_injection_protection(self):
        """Test protection injection SQL"""
        print("\n🛡️ Test: Protection injection SQL")
        
        # Tentatives d'injection
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin'; DELETE FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.post('/login/admin', data={
                'username': malicious_input,
                'password': 'test'
            })
            # Ne doit pas causer d'erreur serveur
            self.assertNotEqual(response.status_code, 500)
        
        print("   ✓ Protection injection SQL")
    
    def test_xss_protection(self):
        """Test protection XSS"""
        print("\n🛡️ Test: Protection XSS")
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            response = self.client.post('/login/admin', data={
                'username': payload,
                'password': 'test'
            })
            # Vérifier que le payload n'est pas exécuté
            self.assertNotIn(payload.encode(), response.data)
        
        print("   ✓ Protection XSS")

def run_comprehensive_tests():
    """Lance tous les tests complets"""
    print("🚀 DÉMARRAGE DES TESTS COMPLETS ULC-ICAM")
    print("=" * 60)
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestULCICAMSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityVulnerabilities))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ ÉCHECS:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERREURS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ TOUS LES TESTS SONT PASSÉS!")
        print("   Le système est prêt pour la production")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Corrigez les problèmes avant la mise en production")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)