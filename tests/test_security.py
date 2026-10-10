"""
Tests unitaires - Sécurité ULC-ICAM Turnin System
Exécuter avec: python -m pytest tests/ -v
"""

import pytest
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestPasswordHashing:
    """Tests pour le hachage et la vérification des mots de passe."""

    def test_hash_is_not_plaintext(self):
        from werkzeug.security import generate_password_hash
        pwd = "MonMotDePasse123"
        hashed = generate_password_hash(pwd)
        assert hashed != pwd
        assert len(hashed) > 20

    def test_correct_password_verified(self):
        from app import _verify_password
        from werkzeug.security import generate_password_hash
        pwd = "MonMotDePasse123"
        hashed = generate_password_hash(pwd)
        assert _verify_password(pwd, hashed) is True

    def test_wrong_password_rejected(self):
        from app import _verify_password
        from werkzeug.security import generate_password_hash
        pwd = "MonMotDePasse123"
        hashed = generate_password_hash(pwd)
        assert _verify_password("MauvaisMotDePasse", hashed) is False

    def test_legacy_plaintext_migration(self):
        """Le fallback en clair doit fonctionner pour les anciens comptes."""
        from app import _verify_password
        assert _verify_password("admin123", "admin123") is True

    def test_legacy_plaintext_wrong(self):
        from app import _verify_password
        assert _verify_password("mauvais", "admin123") is False

    def test_empty_password_rejected(self):
        from app import _verify_password
        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash("secret")
        assert _verify_password("", hashed) is False

    def test_none_password_rejected(self):
        from app import _verify_password
        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash("secret")
        assert _verify_password(None, hashed) is False


class TestAppSecurity:
    """Tests d'intégration pour les routes sécurisées."""

    @pytest.fixture
    def client(self):
        from app import app
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Désactivé pour les tests
        with app.test_client() as c:
            yield c

    def test_dashboard_requires_auth(self, client):
        """Le dashboard doit rediriger si non connecté."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code in (302, 301)

    def test_admin_users_requires_auth(self, client):
        """La route admin doit rediriger si non connecté."""
        response = client.get('/admin/users', follow_redirects=False)
        assert response.status_code in (302, 301)

    def test_index_accessible(self, client):
        """La page d'accueil doit être accessible."""
        response = client.get('/')
        assert response.status_code == 200

    def test_login_page_accessible(self, client):
        """La page de login doit être accessible."""
        response = client.get('/login')
        assert response.status_code == 200

    def test_download_file_requires_auth(self, client):
        """Le téléchargement doit nécessiter une authentification."""
        response = client.get('/download_file/test.pdf', follow_redirects=False)
        assert response.status_code in (302, 301)

    def test_security_headers_present(self, client):
        """Les en-têtes de sécurité doivent être présents."""
        response = client.get('/')
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert 'X-Frame-Options' in response.headers

    def test_backup_excludes_passwords(self, client):
        """La sauvegarde ne doit jamais contenir les mots de passe."""
        with client.session_transaction() as sess:
            sess['user'] = 'admin'
            sess['role'] = 'admin'
            sess['name'] = 'Administrateur'
            sess['last_active'] = '2026-01-01T00:00:00'

        response = client.get('/admin/download_backup')
        if response.status_code == 200:
            import json
            data = json.loads(response.data)
            for username, udata in data.get('data', {}).get('users', {}).items():
                assert 'password' not in udata, \
                    f"Mot de passe trouvé dans le backup pour {username}"


class TestFileUploadSecurity:
    """Tests pour la sécurité des uploads de fichiers."""

    def test_secure_filename_strips_traversal(self):
        from werkzeug.utils import secure_filename
        dangerous = "../../../etc/passwd"
        safe = secure_filename(dangerous)
        assert '..' not in safe
        assert '/' not in safe

    def test_secure_filename_empty(self):
        from werkzeug.utils import secure_filename
        assert secure_filename("") == ""

    def test_secure_filename_normal(self):
        from werkzeug.utils import secure_filename
        assert secure_filename("document.pdf") == "document.pdf"


class TestCodeExecution:
    """Tests pour l'exécution sécurisée de code."""

    def test_unsupported_language(self):
        from code_execution import CodeExecutor
        executor = CodeExecutor()
        result = executor.execute_code('some code', 'cobol')
        assert result.get('success') is False


class TestDataIntegrity:
    """Tests pour l'intégrité des données."""

    def test_course_key_normalization(self):
        """La clé de cours doit toujours être une chaîne."""
        from app import _course_key
        assert _course_key(1) == '1'
        assert _course_key('1') == '1'
        assert _course_key(None) is None

    def test_temp_password_length(self):
        """Le mot de passe temporaire doit avoir la bonne longueur."""
        from app import generate_temp_password
        pwd = generate_temp_password()
        assert len(pwd) == 16
        assert pwd.isalnum()
