# ===============================================================================
# Tests de Performance pour ULC-ICAM Turnin System
# Développeur: Jonathan Kakesa | Date: 19/12/2024
# Description: Tests de charge et performance pour éviter les ralentissements
# ===============================================================================

import unittest
import time
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import psutil

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestPerformance(unittest.TestCase):
    """Tests de performance du système"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_response_time(self):
        """Test temps de réponse des pages principales"""
        print("\n⏱️ Test: Temps de réponse")
        
        routes = ['/', '/login', '/login/student', '/login/teacher', '/login/admin']
        
        for route in routes:
            start_time = time.time()
            response = self.client.get(route)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # en ms
            
            print(f"   {route}: {response_time:.2f}ms")
            self.assertLess(response_time, 1000, f"Route {route} trop lente")
        
        print("   ✓ Temps de réponse acceptables")
    
    def test_concurrent_users(self):
        """Test charge avec utilisateurs simultanés"""
        print("\n👥 Test: Utilisateurs simultanés")
        
        def simulate_user():
            """Simule un utilisateur"""
            try:
                # Navigation typique
                self.client.get('/')
                self.client.get('/login')
                self.client.post('/login/admin', data={
                    'username': 'admin',
                    'password': 'admin123'
                })
                return True
            except:
                return False
        
        # Test avec 20 utilisateurs simultanés
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(simulate_user) for _ in range(20)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        success_rate = sum(results) / len(results) * 100
        total_time = end_time - start_time
        
        print(f"   Utilisateurs: 20")
        print(f"   Succès: {success_rate:.1f}%")
        print(f"   Temps total: {total_time:.2f}s")
        
        self.assertGreater(success_rate, 80, "Taux de succès trop faible")
        self.assertLess(total_time, 10, "Temps de traitement trop long")
        
        print("   ✓ Charge simultanée gérée")
    
    def test_memory_efficiency(self):
        """Test efficacité mémoire"""
        print("\n💾 Test: Efficacité mémoire")
        
        process = psutil.Process()
        
        # Mémoire initiale
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Simulation d'utilisation intensive
        for i in range(100):
            self.client.get('/')
            if i % 20 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"   Requête {i}: {current_memory:.1f} MB")
        
        # Mémoire finale
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        print(f"   Mémoire initiale: {initial_memory:.1f} MB")
        print(f"   Mémoire finale: {final_memory:.1f} MB")
        print(f"   Augmentation: {memory_increase:.1f} MB")
        
        # Vérifier pas d'augmentation excessive
        self.assertLess(memory_increase, 50, "Augmentation mémoire excessive")
        
        print("   ✓ Utilisation mémoire efficace")

def run_performance_tests():
    """Lance les tests de performance"""
    print("🚀 TESTS DE PERFORMANCE ULC-ICAM")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPerformance)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS PERFORMANCE")
    print("=" * 50)
    
    if result.wasSuccessful():
        print("✅ PERFORMANCE OPTIMALE")
        print("   Le système peut gérer la charge attendue")
    else:
        print("⚠️ PROBLÈMES DE PERFORMANCE DÉTECTÉS")
        print("   Optimisation nécessaire")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_performance_tests()