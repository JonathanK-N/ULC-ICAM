
def test_dashboard_access_student(client):
    client.post('/login/student', data={'identifier': 'ETUD001', 'password': 'etud123'})
    resp = client.get('/dashboard')
    assert resp.status_code == 200


codex/refactor-tests-to-use-app.test_client
def test_teacher_assignments_page(client):
    client.post('/login/teacher', data={'identifier': 'PROF001', 'password': 'prof123'})
    resp = client.get('/teacher/assignments')
    assert resp.status_code == 200

def create_test_file(filename, content):
    """Créer un fichier de test"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return filename

def test_student_submission():
    """Test de soumission par un étudiant"""
    print("🎓 === TEST SOUMISSION ÉTUDIANT ===")
    
    # Connexion étudiant
    login_data = {'username': 'etud001', 'password': 'etud1pass'}
    response = session.post(f"{BASE_URL}/login/student", data=login_data)
    
    if response.status_code != 200 or 'dashboard' not in response.url:
        print("❌ Échec connexion étudiant")
        return False
    
    print("✅ Connexion étudiant réussie")
    
    # Accéder au tableau de bord pour voir les devoirs
    response = session.get(f"{BASE_URL}/dashboard")
    if response.status_code == 200:
        print("✅ Accès tableau de bord étudiant")
        
        # Vérifier qu'il y a des devoirs affichés
        if 'devoir' in response.text.lower() or 'assignment' in response.text.lower():
            print("✅ Devoirs visibles sur le tableau de bord")
        else:
            print("⚠️  Aucun devoir visible")
    
    # Tenter d'accéder à une page de soumission (devoir ID 1)
    response = session.get(f"{BASE_URL}/submit/1")
    if response.status_code == 200:
        print("✅ Accès page de soumission")
        
        # Créer un fichier de test
        test_file = create_test_file("test_submission.txt", 
                                   f"Soumission de test par etud001\nDate: {datetime.now()}\nContenu du devoir...")
        # Additional workflow details: see test/fixtures/submission_workflow_full.txt
 deployement
