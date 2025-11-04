# ===============================================================================
# Tests d'Intégration pour ULC-ICAM Turnin System
# Développeur: Jonathan Kakesa | Date: 19/12/2024
# Description: Tests de flux complets utilisateur pour éviter les bugs workflow
# ===============================================================================

import unittest
import os
import sys
import tempfile
import shutil
from io import BytesIO

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, users, admin_courses, assignments, submissions

class TestIntegrationWorkflows(unittest.TestCase):
    """Tests d'intégration des workflows complets"""
    
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        
        # Créer dossier temporaire
        self.test_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.test_dir
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def login_as_admin(self):
        """Connexion en tant qu'admin"""
        return self.client.post('/login/admin', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
    
    def login_as_teacher(self):
        """Connexion en tant qu'enseignant"""
        # Utiliser un enseignant existant ou créer un compte test
        if 'prof_test' not in users:
            users['prof_test'] = {
                'password': 'test123',
                'role': 'teacher',
                'name': 'Professeur Test',
                'cip': 'prof_test',
                'email': 'prof@test.com'
            }
        
        return self.client.post('/login/teacher', data={
            'identifier': 'prof_test',
            'password': 'test123'
        }, follow_redirects=True)
    
    def login_as_student(self):
        """Connexion en tant qu'étudiant"""
        # Utiliser un étudiant existant ou créer un compte test
        if 'etud_test' not in users:
            users['etud_test'] = {
                'password': 'test123',
                'role': 'student',
                'name': 'Étudiant Test',
                'cip': 'etud_test',
                'email': 'etudiant@test.com'
            }
        
        return self.client.post('/login/student', data={
            'identifier': 'etud_test',
            'password': 'test123'
        }, follow_redirects=True)
    
    def test_complete_admin_workflow(self):
        """Test workflow complet administrateur"""
        print("\n👨‍💼 Test: Workflow Admin Complet")
        
        # 1. Connexion admin
        response = self.login_as_admin()
        self.assertEqual(response.status_code, 200)
        print("   ✓ Connexion admin")
        
        # 2. Accès dashboard admin
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'admin', response.data)
        print("   ✓ Dashboard admin accessible")
        
        # 3. Gestion utilisateurs
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Liste utilisateurs")
        
        # 4. Ajout étudiant
        response = self.client.post('/admin/add_student', data={
            'username': 'test_student_new',
            'password': 'password123',
            'cip': 'test_cip_new',
            'nom': 'Test',
            'postnom': 'Student',
            'prenom': 'New',
            'sexe': 'M',
            'date_naissance': '2000-01-01',
            'promotion': 'L1',
            'faculte': 'Sciences',
            'telephone': '123456789',
            'email': 'test@student.com',
            'adresse': 'Test Address'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Ajout étudiant")
        
        # 5. Gestion cours
        response = self.client.get('/admin/courses')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Gestion cours")
        
        # 6. Déconnexion
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Déconnexion admin")
    
    def test_complete_teacher_workflow(self):
        """Test workflow complet enseignant"""
        print("\n👨‍🏫 Test: Workflow Enseignant Complet")
        
        # 1. Connexion enseignant
        response = self.login_as_teacher()
        self.assertEqual(response.status_code, 200)
        print("   ✓ Connexion enseignant")
        
        # 2. Dashboard enseignant
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Dashboard enseignant")
        
        # 3. Voir cours assignés
        response = self.client.get('/teacher/my_assigned_courses')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Cours assignés")
        
        # 4. Voir devoirs
        response = self.client.get('/teacher/assignments')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Liste devoirs")
        
        # 5. Voir soumissions
        response = self.client.get('/teacher/submissions')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Soumissions")
        
        # 6. Déconnexion
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Déconnexion enseignant")
    
    def test_complete_student_workflow(self):
        """Test workflow complet étudiant"""
        print("\n👨‍🎓 Test: Workflow Étudiant Complet")
        
        # 1. Connexion étudiant
        response = self.login_as_student()
        self.assertEqual(response.status_code, 200)
        print("   ✓ Connexion étudiant")
        
        # 2. Dashboard étudiant
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Dashboard étudiant")
        
        # 3. Voir cours
        response = self.client.get('/student/courses')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Cours étudiants")
        
        # 4. Voir notes
        response = self.client.get('/student/my_grades')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Notes étudiant")
        
        # 5. Déconnexion
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        print("   ✓ Déconnexion étudiant")
    
    def test_assignment_submission_workflow(self):
        """Test workflow soumission de devoir"""
        print("\n📝 Test: Workflow Soumission Devoir")
        
        # Préparer un devoir test
        if not assignments:
            assignments.append({
                'id': 999,
                'title': 'Devoir Test',
                'description': 'Test assignment',
                'course_id': 1,
                'teacher': 'prof_test',
                'created_at': '2024-12-19'
            })
        
        # 1. Connexion étudiant
        response = self.login_as_student()
        self.assertEqual(response.status_code, 200)
        print("   ✓ Connexion étudiant")
        
        # 2. Accéder à la page de soumission
        assignment_id = 999
        response = self.client.get(f'/submit/{assignment_id}')
        # Peut être redirigé si pas inscrit au cours
        self.assertIn(response.status_code, [200, 302])
        print("   ✓ Page soumission accessible")
        
        # 3. Créer un fichier test
        test_content = b'Contenu du devoir test'
        
        # 4. Soumettre le fichier (si autorisé)
        response = self.client.post(f'/submit/{assignment_id}', data={
            'file': (BytesIO(test_content), 'test_submission.txt')
        }, follow_redirects=True)
        
        # Vérifier que la soumission ne cause pas d'erreur
        self.assertNotEqual(response.status_code, 500)
        print("   ✓ Soumission traitée")
        
        # 5. Déconnexion
        response = self.client.get('/logout')
        print("   ✓ Workflow soumission terminé")
    
    def test_error_recovery_workflow(self):
        """Test récupération d'erreurs"""
        print("\n🔧 Test: Récupération d'Erreurs")
        
        # 1. Test accès non autorisé
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 302)  # Redirection
        print("   ✓ Redirection accès non autorisé")
        
        # 2. Test données manquantes
        response = self.client.post('/login/admin', data={})
        self.assertNotEqual(response.status_code, 500)
        print("   ✓ Gestion données manquantes")
        
        # 3. Test route inexistante
        response = self.client.get('/route/inexistante')
        self.assertEqual(response.status_code, 404)
        print("   ✓ Gestion route inexistante")
        
        # 4. Test méthode incorrecte
        response = self.client.delete('/')
        self.assertEqual(response.status_code, 405)
        print("   ✓ Gestion méthode incorrecte")
    
    def test_session_persistence(self):
        """Test persistance des sessions"""
        print("\n🔐 Test: Persistance Sessions")
        
        # 1. Connexion
        response = self.login_as_admin()
        self.assertEqual(response.status_code, 200)
        
        # 2. Vérifier session active
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        print("   ✓ Session active")
        
        # 3. Navigation multiple
        pages = ['/admin/users', '/admin/courses', '/admin/assignments']
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200)
        print("   ✓ Session persistante")
        
        # 4. Déconnexion
        response = self.client.get('/logout')
        
        # 5. Vérifier session fermée
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirection
        print("   ✓ Session fermée correctement")

def run_integration_tests():
    """Lance les tests d'intégration"""
    print("🚀 TESTS D'INTÉGRATION ULC-ICAM")
    print("=" * 50)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIntegrationWorkflows)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS INTÉGRATION")
    print("=" * 50)
    
    if result.wasSuccessful():
        print("✅ TOUS LES WORKFLOWS FONCTIONNENT")
        print("   L'intégration est complète et fonctionnelle")
    else:
        print("⚠️ PROBLÈMES D'INTÉGRATION DÉTECTÉS")
        for test, error in result.failures + result.errors:
            print(f"   ❌ {test}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_integration_tests()