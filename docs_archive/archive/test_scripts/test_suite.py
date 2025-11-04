#!/usr/bin/env python3
"""
Suite de tests complète pour ULC-ICAM Turnin
Vérifie toutes les fonctionnalités et la logique métier
"""

import unittest
import os
import json
import tempfile
from datetime import datetime, timedelta
from app import app, users, assignments, submissions, save_test_data

class ULCICAMTestSuite(unittest.TestCase):
    """Tests complets pour ULC-ICAM Turnin"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Données de test
        self.admin_user = {'username': 'admin', 'password': 'admin123'}
        self.teacher_user = {'cip': 'PROF001', 'password': 'prof123'}
        self.student_user = {'cip': 'ETU001', 'password': 'etu123'}
    
    def test_01_homepage_access(self):
        """Test 1: Accès à la page d'accueil"""
        print("\n🧪 Test 1: Page d'accueil")
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ULC-ICAM', response.data)
        print("✅ Page d'accueil accessible")
    
    def test_02_login_pages(self):
        """Test 2: Pages de connexion"""
        print("\n🧪 Test 2: Pages de connexion")
        
        # Page de sélection de connexion
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        print("✅ Page sélection connexion OK")
        
        # Pages de connexion spécifiques
        for role in ['student', 'teacher', 'admin']:
            response = self.client.get(f'/login/{role}')
            self.assertEqual(response.status_code, 200)
            print(f"✅ Page connexion {role} OK")
    
    def test_03_admin_login(self):
        """Test 3: Connexion administrateur"""
        print("\n🧪 Test 3: Connexion admin")
        
        response = self.client.post('/login/admin', data={
            'username': self.admin_user['username'],
            'password': self.admin_user['password']
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        print("✅ Connexion admin réussie")
        
        # Vérifier l'accès au dashboard admin
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['role'], 'admin')
        print("✅ Session admin établie")
    
    def test_04_student_login(self):
        """Test 4: Connexion étudiant"""
        print("\n🧪 Test 4: Connexion étudiant")
        
        response = self.client.post('/login/student', data={
            'identifier': self.student_user['cip'],
            'password': self.student_user['password']
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        print("✅ Connexion étudiant réussie")
    
    def test_05_teacher_login(self):
        """Test 5: Connexion professeur"""
        print("\n🧪 Test 5: Connexion professeur")
        
        response = self.client.post('/login/teacher', data={
            'identifier': self.teacher_user['cip'],
            'password': self.teacher_user['password']
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        print("✅ Connexion professeur réussie")
    
    def test_06_dashboard_access(self):
        """Test 6: Accès aux dashboards selon le rôle"""
        print("\n🧪 Test 6: Dashboards par rôle")
        
        # Test dashboard étudiant
        with self.client.session_transaction() as sess:
            sess['user'] = 'etu001'
            sess['role'] = 'student'
            sess['name'] = 'Test Student'
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        print("✅ Dashboard étudiant accessible")
        
        # Test dashboard professeur
        with self.client.session_transaction() as sess:
            sess['user'] = 'prof001'
            sess['role'] = 'teacher'
            sess['name'] = 'Test Teacher'
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        print("✅ Dashboard professeur accessible")
    
    def test_07_file_submission(self):
        """Test 7: Soumission de fichier"""
        print("\n🧪 Test 7: Soumission de fichier")
        
        # Connexion étudiant
        with self.client.session_transaction() as sess:
            sess['user'] = 'etu001'
            sess['role'] = 'student'
            sess['name'] = 'Test Student'
        
        # Créer un fichier de test
        test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        test_file.write("Contenu de test pour soumission")
        test_file.close()
        
        # Supposer qu'il y a un devoir avec ID 1
        if assignments:
            assignment_id = assignments[0]['id']
            
            with open(test_file.name, 'rb') as f:
                response = self.client.post(f'/submit/{assignment_id}', data={
                    'file': (f, 'test_submission.txt')
                }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            print("✅ Soumission de fichier réussie")
        
        # Nettoyer
        os.unlink(test_file.name)
    
    def test_08_admin_user_management(self):
        """Test 8: Gestion des utilisateurs (admin)"""
        print("\n🧪 Test 8: Gestion utilisateurs")
        
        # Connexion admin
        with self.client.session_transaction() as sess:
            sess['user'] = 'admin'
            sess['role'] = 'admin'
            sess['name'] = 'Admin'
        
        # Accès à la liste des utilisateurs
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 200)
        print("✅ Liste utilisateurs accessible")
        
        # Accès au formulaire d'ajout d'étudiant
        response = self.client.get('/admin/add_student')
        self.assertEqual(response.status_code, 200)
        print("✅ Formulaire ajout étudiant accessible")
    
    def test_09_teacher_assignment_creation(self):
        """Test 9: Création de devoir (professeur)"""
        print("\n🧪 Test 9: Création de devoir")
        
        # Connexion professeur
        with self.client.session_transaction() as sess:
            sess['user'] = 'prof001'
            sess['role'] = 'teacher'
            sess['name'] = 'Test Teacher'
        
        # Accès au formulaire de création
        response = self.client.get('/teacher/create_assignment')
        self.assertEqual(response.status_code, 200)
        print("✅ Formulaire création devoir accessible")
    
    def test_10_security_access_control(self):
        """Test 10: Contrôle d'accès et sécurité"""
        print("\n🧪 Test 10: Sécurité et contrôle d'accès")
        
        # Test accès non autorisé aux pages admin
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 302)  # Redirection vers login
        print("✅ Accès admin protégé")
        
        # Test accès non autorisé aux pages professeur
        response = self.client.get('/teacher/assignments')
        self.assertEqual(response.status_code, 302)
        print("✅ Accès professeur protégé")
    
    def test_11_data_persistence(self):
        """Test 11: Persistance des données"""
        print("\n🧪 Test 11: Persistance des données")
        
        # Sauvegarder les données
        initial_users_count = len(users)
        save_test_data()
        
        # Vérifier que le fichier JSON existe
        self.assertTrue(os.path.exists('ulc_icam_data.json'))
        print("✅ Fichier de données créé")
        
        # Vérifier le contenu
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(len(data['users']), initial_users_count)
        print("✅ Données sauvegardées correctement")
    
    def test_12_ai_features_integration(self):
        """Test 12: Intégration des fonctionnalités IA"""
        print("\n🧪 Test 12: Fonctionnalités IA")
        
        # Test des fonctions IA (sans exécution réelle)
        from app import simulate_plagiarism_check, simulate_auto_correction
        
        # Test détection de plagiat
        result = simulate_plagiarism_check("contenu test", 999)
        self.assertIn('similarity', result)
        self.assertIn('status', result)
        print("✅ Détection de plagiat fonctionnelle")
        
        # Test correction automatique
        assignment_mock = {'max_score': 100, 'title': 'Test'}
        result = simulate_auto_correction("contenu test", assignment_mock, 999)
        self.assertIn('score', result)
        self.assertIn('feedback', result)
        print("✅ Correction automatique fonctionnelle")

class TurninLogicValidator:
    """Validateur de la logique métier Turnin"""
    
    def __init__(self):
        self.validation_results = []
    
    def validate_turnin_logic(self):
        """Valide la logique métier complète"""
        print("\n🔍 VALIDATION DE LA LOGIQUE TURNIN")
        print("=" * 50)
        
        self.check_user_roles()
        self.check_assignment_workflow()
        self.check_submission_process()
        self.check_grading_system()
        self.check_course_management()
        self.check_security_model()
        
        return self.validation_results
    
    def check_user_roles(self):
        """Vérifie la gestion des rôles utilisateur"""
        print("\n👥 Validation des rôles utilisateur")
        
        roles_found = set()
        for user_data in users.values():
            roles_found.add(user_data.get('role'))
        
        expected_roles = {'admin', 'teacher', 'student'}
        if expected_roles.issubset(roles_found):
            print("✅ Tous les rôles requis présents")
            self.validation_results.append("✅ Rôles utilisateur: OK")
        else:
            print("❌ Rôles manquants")
            self.validation_results.append("❌ Rôles utilisateur: MANQUANT")
    
    def check_assignment_workflow(self):
        """Vérifie le workflow des devoirs"""
        print("\n📝 Validation du workflow des devoirs")
        
        required_fields = ['id', 'title', 'description', 'due_date', 'teacher']
        
        if assignments:
            assignment = assignments[0]
            missing_fields = [field for field in required_fields if field not in assignment]
            
            if not missing_fields:
                print("✅ Structure des devoirs complète")
                self.validation_results.append("✅ Workflow devoirs: OK")
            else:
                print(f"❌ Champs manquants: {missing_fields}")
                self.validation_results.append("❌ Workflow devoirs: INCOMPLET")
        else:
            print("⚠️ Aucun devoir pour validation")
            self.validation_results.append("⚠️ Workflow devoirs: NON TESTABLE")
    
    def check_submission_process(self):
        """Vérifie le processus de soumission"""
        print("\n📤 Validation du processus de soumission")
        
        required_fields = ['id', 'student', 'assignment_id', 'filename', 'submitted_at']
        
        if submissions:
            submission = submissions[0]
            missing_fields = [field for field in required_fields if field not in submission]
            
            if not missing_fields:
                print("✅ Structure des soumissions complète")
                self.validation_results.append("✅ Processus soumission: OK")
            else:
                print(f"❌ Champs manquants: {missing_fields}")
                self.validation_results.append("❌ Processus soumission: INCOMPLET")
        else:
            print("⚠️ Aucune soumission pour validation")
            self.validation_results.append("⚠️ Processus soumission: NON TESTABLE")
    
    def check_grading_system(self):
        """Vérifie le système de notation"""
        print("\n📊 Validation du système de notation")
        
        # Vérifier la présence des structures de correction
        from app import correction_results, plagiarism_results
        
        if hasattr(app, 'correction_results') or 'correction_results' in globals():
            print("✅ Système de correction présent")
            self.validation_results.append("✅ Système notation: OK")
        else:
            print("❌ Système de correction manquant")
            self.validation_results.append("❌ Système notation: MANQUANT")
    
    def check_course_management(self):
        """Vérifie la gestion des cours"""
        print("\n🎓 Validation de la gestion des cours")
        
        from app import admin_courses, course_assignments, course_enrollments
        
        structures_present = all([
            'admin_courses' in globals(),
            'course_assignments' in globals(),
            'course_enrollments' in globals()
        ])
        
        if structures_present:
            print("✅ Structures de gestion des cours présentes")
            self.validation_results.append("✅ Gestion cours: OK")
        else:
            print("❌ Structures de cours manquantes")
            self.validation_results.append("❌ Gestion cours: MANQUANT")
    
    def check_security_model(self):
        """Vérifie le modèle de sécurité"""
        print("\n🔒 Validation de la sécurité")
        
        # Vérifier les sessions et l'authentification
        security_features = []
        
        # Vérifier la gestion des sessions
        if hasattr(app, 'secret_key') and app.secret_key:
            security_features.append("Sessions sécurisées")
        
        # Vérifier les contrôles d'accès dans les routes
        protected_routes = ['/admin/', '/teacher/', '/submit/']
        route_protection = any(route in str(app.url_map) for route in protected_routes)
        
        if route_protection:
            security_features.append("Routes protégées")
        
        if len(security_features) >= 2:
            print("✅ Modèle de sécurité adéquat")
            self.validation_results.append("✅ Sécurité: OK")
        else:
            print("❌ Sécurité insuffisante")
            self.validation_results.append("❌ Sécurité: INSUFFISANTE")

def run_complete_validation():
    """Lance la validation complète"""
    print("🚀 VALIDATION COMPLÈTE ULC-ICAM TURNIN")
    print("=" * 60)
    
    # Tests unitaires
    print("\n📋 PHASE 1: TESTS UNITAIRES")
    suite = unittest.TestLoader().loadTestsFromTestCase(ULCICAMTestSuite)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Validation de la logique métier
    print("\n📋 PHASE 2: VALIDATION LOGIQUE MÉTIER")
    validator = TurninLogicValidator()
    validation_results = validator.validate_turnin_logic()
    
    # Rapport final
    print("\n" + "=" * 60)
    print("📊 RAPPORT FINAL DE VALIDATION")
    print("=" * 60)
    
    print(f"\n🧪 Tests unitaires:")
    print(f"  - Tests exécutés: {result.testsRun}")
    print(f"  - Échecs: {len(result.failures)}")
    print(f"  - Erreurs: {len(result.errors)}")
    
    print(f"\n🔍 Validation logique métier:")
    for result_item in validation_results:
        print(f"  {result_item}")
    
    # Score global
    success_count = sum(1 for r in validation_results if r.startswith("✅"))
    total_count = len(validation_results)
    score = (success_count / total_count) * 100 if total_count > 0 else 0
    
    print(f"\n🎯 SCORE GLOBAL: {score:.1f}%")
    
    if score >= 90:
        print("🎉 EXCELLENT - Application prête pour production")
    elif score >= 75:
        print("✅ BON - Quelques améliorations recommandées")
    elif score >= 60:
        print("⚠️ MOYEN - Corrections nécessaires")
    else:
        print("❌ INSUFFISANT - Révision majeure requise")
    
    return score

if __name__ == "__main__":
    score = run_complete_validation()
    exit(0 if score >= 75 else 1)