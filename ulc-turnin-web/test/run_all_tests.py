#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 21:00
Description: Script principal pour exécuter tous les tests du système
Fonctionnalités: Orchestration de tous les tests, rapport final
===============================================================================
"""

import sys
import os
import time
import json
from datetime import datetime
import subprocess

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports des modules de test
try:
    from test_complete_system import TestULCICAMSystem
    from test_user_management import TestUserManagement
    from test_course_assignment import TestCourseAssignment
    from test_submission_workflow import TestSubmissionWorkflow
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Assurez-vous que tous les fichiers de test sont présents")
    sys.exit(1)

class TestOrchestrator:
    """Orchestrateur principal des tests"""
    
    def __init__(self):
        self.test_results = {
            'start_time': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {}
        }
        self.base_url = "http://localhost:5000"
    
    def check_server_status(self):
        """Vérifie si le serveur est en cours d'exécution"""
        try:
            import requests
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_server_if_needed(self):
        """Démarre le serveur si nécessaire"""
        if not self.check_server_status():
            print("🚀 Démarrage du serveur ULC-ICAM Turnin...")
            try:
                # Essayer de démarrer le serveur en arrière-plan
                app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
                if os.path.exists(app_path):
                    subprocess.Popen([sys.executable, app_path], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    time.sleep(5)  # Attendre que le serveur démarre
                    
                    if self.check_server_status():
                        print("✅ Serveur démarré avec succès")
                        return True
                    else:
                        print("❌ Échec du démarrage automatique du serveur")
                        return False
                else:
                    print("❌ Fichier app.py non trouvé")
                    return False
            except Exception as e:
                print(f"❌ Erreur lors du démarrage du serveur: {e}")
                return False
        else:
            print("✅ Serveur déjà en cours d'exécution")
            return True
    
    def run_test_suite(self, suite_name, test_class):
        """Exécute une suite de tests"""
        print(f"\n{'='*60}")
        print(f"EXÉCUTION DE LA SUITE: {suite_name}")
        print(f"{'='*60}")
        
        try:
            tester = test_class(self.base_url)
            passed, failed = tester.run_all_tests()
            
            self.test_results['test_suites'][suite_name] = {
                'passed': passed,
                'failed': failed,
                'total': passed + failed,
                'success_rate': (passed / (passed + failed) * 100) if (passed + failed) > 0 else 0,
                'status': 'SUCCESS' if failed == 0 else 'PARTIAL' if passed > 0 else 'FAILED'
            }
            
            return passed, failed
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de {suite_name}: {e}")
            self.test_results['test_suites'][suite_name] = {
                'passed': 0,
                'failed': 1,
                'total': 1,
                'success_rate': 0,
                'status': 'ERROR',
                'error': str(e)
            }
            return 0, 1
    
    def run_all_tests(self):
        """Exécute toutes les suites de tests"""
        print("🧪 DÉBUT DES TESTS COMPLETS DU SYSTÈME ULC-ICAM TURNIN")
        print("=" * 80)
        print(f"Heure de début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Vérifier et démarrer le serveur si nécessaire
        if not self.start_server_if_needed():
            print("❌ Impossible de démarrer le serveur. Tests annulés.")
            print("\n📋 INSTRUCTIONS POUR DÉMARRER LE SERVEUR MANUELLEMENT:")
            print("1. Ouvrez un terminal dans le répertoire du projet")
            print("2. Exécutez: python app.py")
            print("3. Attendez que le serveur démarre sur http://localhost:5000")
            print("4. Relancez ce script de test")
            return False
        
        # Définir les suites de tests
        test_suites = [
            ("Tests Système Complets", TestULCICAMSystem),
            ("Tests Gestion Utilisateurs", TestUserManagement),
            ("Tests Gestion Cours", TestCourseAssignment),
            ("Tests Workflow Soumission", TestSubmissionWorkflow)
        ]
        
        total_passed = 0
        total_failed = 0
        
        # Exécuter chaque suite de tests
        for suite_name, test_class in test_suites:
            passed, failed = self.run_test_suite(suite_name, test_class)
            total_passed += passed
            total_failed += failed
            
            # Pause entre les suites
            time.sleep(2)
        
        # Calculer les statistiques finales
        self.test_results['end_time'] = datetime.now().isoformat()
        self.test_results['summary'] = {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_tests': total_passed + total_failed,
            'overall_success_rate': (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0,
            'overall_status': 'SUCCESS' if total_failed == 0 else 'PARTIAL' if total_passed > 0 else 'FAILED'
        }
        
        # Afficher le rapport final
        self.display_final_report()
        
        # Sauvegarder les résultats
        self.save_results()
        
        return total_failed == 0
    
    def display_final_report(self):
        """Affiche le rapport final des tests"""
        print("\n" + "=" * 80)
        print("📊 RAPPORT FINAL DES TESTS")
        print("=" * 80)
        
        summary = self.test_results['summary']
        
        # Statistiques globales
        print(f"🎯 Tests totaux: {summary['total_tests']}")
        print(f"✅ Tests réussis: {summary['total_passed']}")
        print(f"❌ Tests échoués: {summary['total_failed']}")
        print(f"📈 Taux de réussite global: {summary['overall_success_rate']:.1f}%")
        print(f"🏆 Statut global: {summary['overall_status']}")
        
        # Détail par suite
        print(f"\n📋 DÉTAIL PAR SUITE DE TESTS:")
        print("-" * 80)
        
        for suite_name, results in self.test_results['test_suites'].items():
            status_emoji = {
                'SUCCESS': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'ERROR': '💥'
            }.get(results['status'], '❓')
            
            print(f"{status_emoji} {suite_name}")
            print(f"   Réussis: {results['passed']}, Échoués: {results['failed']}, "
                  f"Taux: {results['success_rate']:.1f}%")
            
            if 'error' in results:
                print(f"   Erreur: {results['error']}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        print("-" * 80)
        
        if summary['overall_status'] == 'SUCCESS':
            print("🎉 Excellent! Tous les tests sont passés avec succès.")
            print("   Le système ULC-ICAM Turnin est prêt pour la production.")
        elif summary['overall_status'] == 'PARTIAL':
            print("⚠️  Certains tests ont échoué. Vérifiez les points suivants:")
            print("   - Configuration du serveur")
            print("   - Permissions des fichiers")
            print("   - Connexions à la base de données")
            print("   - Configuration des services externes (email, IA)")
        else:
            print("❌ Plusieurs tests ont échoué. Actions recommandées:")
            print("   - Vérifiez que le serveur fonctionne correctement")
            print("   - Contrôlez les logs d'erreur")
            print("   - Vérifiez la configuration système")
            print("   - Testez manuellement les fonctionnalités de base")
        
        # Informations de performance
        start_time = datetime.fromisoformat(self.test_results['start_time'])
        end_time = datetime.fromisoformat(self.test_results['end_time'])
        duration = end_time - start_time
        
        print(f"\n⏱️  INFORMATIONS DE PERFORMANCE:")
        print("-" * 80)
        print(f"Heure de début: {start_time.strftime('%H:%M:%S')}")
        print(f"Heure de fin: {end_time.strftime('%H:%M:%S')}")
        print(f"Durée totale: {duration.total_seconds():.1f} secondes")
        print(f"Vitesse moyenne: {summary['total_tests'] / duration.total_seconds():.1f} tests/seconde")
    
    def save_results(self):
        """Sauvegarde les résultats des tests"""
        try:
            results_dir = os.path.dirname(__file__)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = os.path.join(results_dir, f'test_results_{timestamp}.json')
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Résultats sauvegardés dans: {results_file}")
            
            # Créer aussi un fichier de résumé en texte
            summary_file = os.path.join(results_dir, f'test_summary_{timestamp}.txt')
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("RAPPORT DE TESTS ULC-ICAM TURNIN SYSTEM\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tests totaux: {self.test_results['summary']['total_tests']}\n")
                f.write(f"Tests réussis: {self.test_results['summary']['total_passed']}\n")
                f.write(f"Tests échoués: {self.test_results['summary']['total_failed']}\n")
                f.write(f"Taux de réussite: {self.test_results['summary']['overall_success_rate']:.1f}%\n")
                f.write(f"Statut: {self.test_results['summary']['overall_status']}\n\n")
                
                f.write("DÉTAIL PAR SUITE:\n")
                f.write("-" * 30 + "\n")
                for suite_name, results in self.test_results['test_suites'].items():
                    f.write(f"{suite_name}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)\n")
            
            print(f"📄 Résumé sauvegardé dans: {summary_file}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")

def main():
    """Fonction principale"""
    print("🏛️  UNIVERSITÉ LOYOLA DU CONGO - INSTITUT CATHOLIQUE D'ART ET MÉTIER")
    print("🎓 SYSTÈME ULC-ICAM TURNIN - SUITE DE TESTS COMPLÈTE")
    print("👨‍💻 Développé par: Jonathan Kakesa")
    print("📅 Date: 19 décembre 2024")
    print()
    
    orchestrator = TestOrchestrator()
    success = orchestrator.run_all_tests()
    
    if success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("✅ Le système ULC-ICAM Turnin est prêt pour la production.")
        return 0
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Consultez le rapport détaillé ci-dessus pour les corrections nécessaires.")
        return 1

if __name__ == "__main__":
    exit(main())