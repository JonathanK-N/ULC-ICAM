# ===============================================================================
# Lanceur de Tests Complets pour ULC-ICAM Turnin System
# Développeur: Jonathan Kakesa | Date: 19/12/2024
# Description: Script principal pour exécuter tous les tests et générer rapport
# ===============================================================================

import sys
import os
import time
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependencies():
    """Vérifier les dépendances nécessaires pour les tests"""
    print("🔍 Vérification des dépendances...")
    
    required_modules = [
        'flask', 'unittest', 'psutil', 'threading', 'tempfile'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Modules manquants: {', '.join(missing_modules)}")
        print("   Installez avec: pip install -r requirements.txt")
        return False
    
    print("✅ Toutes les dépendances sont disponibles")
    return True

def run_test_suite(test_name, test_function):
    """Exécute une suite de tests avec gestion d'erreurs"""
    print(f"\n{'='*60}")
    print(f"🧪 EXÉCUTION: {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        success = test_function()
        end_time = time.time()
        duration = end_time - start_time
        
        status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
        print(f"\n{status} - {test_name}")
        print(f"⏱️ Durée: {duration:.2f} secondes")
        
        return success, duration
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n💥 ERREUR - {test_name}")
        print(f"❌ Exception: {str(e)}")
        print(f"⏱️ Durée: {duration:.2f} secondes")
        
        return False, duration

def generate_test_report(results):
    """Génère un rapport de tests détaillé"""
    print(f"\n{'='*80}")
    print("📊 RAPPORT COMPLET DES TESTS ULC-ICAM")
    print(f"{'='*80}")
    
    # Informations générales
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️ Système: {os.name}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Résultats par suite
    print(f"\n📋 RÉSULTATS PAR SUITE:")
    print("-" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for success, _ in results.values() if success)
    total_duration = sum(duration for _, duration in results.values())
    
    for test_name, (success, duration) in results.items():
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name:<30} {duration:>8.2f}s")
    
    # Statistiques globales
    print(f"\n📈 STATISTIQUES GLOBALES:")
    print("-" * 30)
    print(f"Total des suites: {total_tests}")
    print(f"Succès: {passed_tests}")
    print(f"Échecs: {total_tests - passed_tests}")
    print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Durée totale: {total_duration:.2f} secondes")
    
    # Verdict final
    print(f"\n🎯 VERDICT FINAL:")
    print("-" * 20)
    
    if passed_tests == total_tests:
        print("🎉 EXCELLENT! Tous les tests sont passés")
        print("✅ Le système est prêt pour la production")
        print("🚀 Aucun bug critique détecté")
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ ACCEPTABLE avec quelques problèmes mineurs")
        print("🔧 Corrections recommandées avant production")
    else:
        print("🚨 CRITIQUE! Nombreux problèmes détectés")
        print("❌ NE PAS déployer en production")
        print("🛠️ Corrections majeures nécessaires")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    print("-" * 20)
    
    if 'Tests Complets' in results and not results['Tests Complets'][0]:
        print("• Corriger les problèmes de fonctionnalité de base")
    
    if 'Tests Performance' in results and not results['Tests Performance'][0]:
        print("• Optimiser les performances du système")
    
    if 'Tests Intégration' in results and not results['Tests Intégration'][0]:
        print("• Vérifier les workflows utilisateur")
    
    if passed_tests == total_tests:
        print("• Système prêt pour la mise en production")
        print("• Effectuer des tests utilisateur finaux")
        print("• Préparer la documentation de déploiement")
    
    return passed_tests == total_tests

def main():
    """Fonction principale d'exécution des tests"""
    print("🚀 SUITE COMPLÈTE DE TESTS ULC-ICAM TURNIN SYSTEM")
    print("Développeur: Jonathan Kakesa | Date: 2024-12-19")
    print("Institution: Université Libre du Congo - ICAM")
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Importer les modules de test
    try:
        from test_comprehensive import run_comprehensive_tests
        from test_performance import run_performance_tests
        from test_integration import run_integration_tests
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("Assurez-vous que tous les fichiers de test sont présents")
        sys.exit(1)
    
    # Définir les suites de tests
    test_suites = {
        'Tests Complets': run_comprehensive_tests,
        'Tests Performance': run_performance_tests,
        'Tests Intégration': run_integration_tests
    }
    
    # Exécuter toutes les suites
    results = {}
    
    for test_name, test_function in test_suites.items():
        success, duration = run_test_suite(test_name, test_function)
        results[test_name] = (success, duration)
    
    # Générer le rapport final
    all_passed = generate_test_report(results)
    
    # Code de sortie
    if all_passed:
        print(f"\n🎊 FÉLICITATIONS! Le système ULC-ICAM est prêt!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Des améliorations sont nécessaires avant la production")
        sys.exit(1)

if __name__ == '__main__':
    main()