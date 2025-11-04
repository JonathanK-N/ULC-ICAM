# ===============================================================================
# Test de Démarrage Rapide pour ULC-ICAM Turnin System
# Développeur: Jonathan Kakesa | Date: 19/12/2024
# Description: Test rapide pour vérifier que l'application démarre correctement
# ===============================================================================

import sys
import os
import unittest
import tempfile
import shutil

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStartup(unittest.TestCase):
    """Tests de démarrage rapide"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_imports(self):
        """Test que tous les imports fonctionnent"""
        print("\nTest: Imports des modules")
        
        try:
            from app import app
            print("   OK Import app.py reussi")
        except Exception as e:
            self.fail(f"Erreur import app.py: {e}")
        
        try:
            from config import Config
            print("   OK Import config.py reussi")
        except Exception as e:
            self.fail(f"Erreur import config.py: {e}")
        
        try:
            from models import User
            print("   OK Import models.py reussi")
        except Exception as e:
            self.fail(f"Erreur import models.py: {e}")
    
    def test_app_creation(self):
        """Test creation de l'application Flask"""
        print("\nTest: Creation application Flask")
        
        try:
            from app import app
            self.assertIsNotNone(app)
            self.assertEqual(app.name, 'app')
            print("   OK Application Flask creee")
        except Exception as e:
            self.fail(f"Erreur création app: {e}")
    
    def test_basic_routes(self):
        """Test accessibilite des routes de base"""
        print("\nTest: Routes de base")
        
        try:
            from app import app
            app.config['TESTING'] = True
            client = app.test_client()
            
            # Test route principale
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            print("   OK Route / accessible")
            
            # Test route login
            response = client.get('/login')
            self.assertEqual(response.status_code, 200)
            print("   OK Route /login accessible")
            
        except Exception as e:
            self.fail(f"Erreur test routes: {e}")
    
    def test_data_structure(self):
        """Test structure des donnees"""
        print("\nTest: Structure des donnees")
        
        try:
            from app import users, admin_courses, assignments
            
            self.assertIsInstance(users, dict)
            print("   OK Structure users valide")
            
            self.assertIsInstance(admin_courses, list)
            print("   OK Structure admin_courses valide")
            
            self.assertIsInstance(assignments, list)
            print("   OK Structure assignments valide")
            
        except Exception as e:
            self.fail(f"Erreur structure données: {e}")

def run_startup_test():
    """Lance le test de démarrage rapide"""
    print("TEST DE DEMARRAGE RAPIDE ULC-ICAM")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestStartup)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("DEMARRAGE REUSSI!")
        print("   L'application est prete a fonctionner")
    else:
        print("PROBLEMES DE DEMARRAGE")
        for test, error in result.failures + result.errors:
            print(f"   • {error}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_startup_test()
    sys.exit(0 if success else 1)