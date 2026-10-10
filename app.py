# ===============================================================================
# ULC-ICAM TURNIN SYSTEM - PROPRIÉTÉ INTELLECTUELLE
# Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
# Tous droits réservés - Logiciel Propriétaire
# 
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 18:30
# Description: Application Flask principale pour ULC-ICAM Turnin System
# Fonctionnalités: Gestion académique, devoirs, plagiat, notifications email
# Nouvelles: Compression fichiers, téléchargement lot, rapports avancés
# 
# UTILISATION RESTREINTE - Voir LICENSE pour les conditions d'utilisation
# ===============================================================================

from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash, session, jsonify, send_from_directory, make_response, g
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import secrets
import string
import random
import requests
import hashlib
import logging
import threading
import re
from difflib import SequenceMatcher
from pathlib import Path
from functools import wraps
from grading_service import parse_ai_response, requires_review
from security_policy import can_access_course, owns_assignment
from code_execution import CodeExecutor, save_code_submission
# Imports optionnels pour traitement de fichiers
try:
    import docx2txt
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("docx2txt non installé - lecture DOCX désactivée")

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PyPDF2 non installé - lecture PDF désactivée")

# Nouveaux imports pour fonctionnalités avancées
import zipfile
import io
import csv
# Imports optionnels pour PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab non installé - génération PDF désactivée")
# Ajout pour les notifications email
try:
    from flask_mail import Mail, Message
    from dotenv import load_dotenv
    load_dotenv()
    MAIL_AVAILABLE = True
except ImportError:
    MAIL_AVAILABLE = False
    print("Flask-Mail non installé - notifications désactivées")

PWA_MANIFEST = {
    "name": "ULC-ICAM Turnin",
    "short_name": "ULC-ICAM Turnin",
    "description": "Plateforme ULC-ICAM Turnin pour la gestion des devoirs et du suivi académique.",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#2563eb",
    "orientation": "portrait-primary",
    "scope": "/",
    "lang": "fr",
    "categories": ["education", "productivity"],
    "icons": [
        {
            "src": "/static/images/pwa-icon-192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/images/pwa-icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any"
        },
        {
            "src": "/static/images/pwa-icon-512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable"
        }
    ],
    "shortcuts": [
        {
            "name": "Tableau de Bord",
            "short_name": "Dashboard",
            "description": "Accéder au tableau de bord principal",
            "url": "/dashboard",
            "icons": [{"src": "/static/images/pwa-icon-192.png", "sizes": "192x192"}]
        },
        {
            "name": "Soumettre Devoir",
            "short_name": "Soumettre",
            "description": "Soumettre un nouveau devoir",
            "url": "/submit",
            "icons": [{"src": "/static/images/pwa-icon-192.png", "sizes": "192x192"}]
        },
        {
            "name": "Mes Notes",
            "short_name": "Notes",
            "description": "Consulter mes notes",
            "url": "/student/my_grades",
            "icons": [{"src": "/static/images/pwa-icon-192.png", "sizes": "192x192"}]
        }
    ]
}


app = Flask(__name__)

# -----------------------------------------------------------------------
# Clé secrète robuste : toujours depuis l'environnement en production
# -----------------------------------------------------------------------
_secret = os.environ.get("FLASK_SECRET_KEY")
if not _secret and os.environ.get('FLASK_ENV') == 'production':
    raise RuntimeError('FLASK_SECRET_KEY obligatoire en production')
if not _secret:
    _secret = secrets.token_hex(32)
    logging.warning("FLASK_SECRET_KEY non définie — clé aléatoire générée. "
                    "Les sessions seront invalidées au redémarrage.")
app.secret_key = _secret

# -----------------------------------------------------------------------
# Configuration de base
# -----------------------------------------------------------------------
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')

app.config.setdefault('PREFERRED_URL_SCHEME', 'https')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Sessions sécurisées
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# WTF CSRF
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 heure

# -----------------------------------------------------------------------
# CSRF Protection (Flask-WTF)
# -----------------------------------------------------------------------
try:
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    csrf = CSRFProtect(app)
    CSRF_AVAILABLE = True

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    @app.after_request
    def auto_inject_csrf(response):
        """Injecte automatiquement le token CSRF dans tous les formulaires HTML."""
        try:
            if 'text/html' in response.content_type:
                token = generate_csrf()
                html = response.get_data(as_text=True)
                hidden = f'<input type="hidden" name="csrf_token" value="{token}">'
                html = re.sub(r'(<form\b[^>]*>)', r'\1' + hidden, html, flags=re.IGNORECASE)
                meta = f'<meta name="csrf-token" content="{token}">'
                html = html.replace('</head>', meta + '\n</head>', 1)
                response.set_data(html)
        except Exception:
            pass
        return response

except Exception as _e:
    CSRF_AVAILABLE = False
    if os.environ.get('FLASK_ENV') == 'production':
        raise RuntimeError('Protection CSRF indisponible') from _e
    logging.warning(f"Flask-WTF désactivé : {_e}")

# -----------------------------------------------------------------------
# Rate Limiting (Flask-Limiter)
# -----------------------------------------------------------------------
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get("REDIS_URL", "memory://"),
    )
    LIMITER_AVAILABLE = True
except Exception as _e:
    LIMITER_AVAILABLE = False
    logging.warning(f"Flask-Limiter désactivé : {_e}")

# -----------------------------------------------------------------------
# Configuration email
# -----------------------------------------------------------------------
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@ulc-icam.cd')
app.config['NOTIFICATIONS_ENABLED'] = os.environ.get('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'

# Initialiser Flask-Mail
if MAIL_AVAILABLE:
    mail = Mail(app)

# -----------------------------------------------------------------------
# Logging structuré
# -----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ulc_icam')

# -----------------------------------------------------------------------
# Verrou thread-safe pour les données partagées
# -----------------------------------------------------------------------
_data_lock = threading.RLock()

# -----------------------------------------------------------------------
# Chemin du fichier de données (configurable via DATA_FILE env var)
# -----------------------------------------------------------------------
DATA_FILE = os.environ.get('DATA_FILE', 'ulc_icam_data.json')
DATA_FILE_TMP = DATA_FILE + '.tmp'
from storage_bridge import repository_from_environment, install_storage, install_json_storage
relational_repository = repository_from_environment(os.environ)

def read_storage_snapshot():
    if relational_repository is not None:
        with relational_repository.transaction() as connection:
            return relational_repository.load(connection)
    with open(DATA_FILE, 'r', encoding='utf-8') as stream:
        return json.load(stream)

# -----------------------------------------------------------------------
# Créer le dossier uploads
# -----------------------------------------------------------------------
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

# -----------------------------------------------------------------------
# En-têtes de sécurité sur toutes les réponses
# -----------------------------------------------------------------------
@app.after_request
def add_security_headers(response):
    if 'user' in session or request.endpoint in ('add_student', 'add_teacher', 'import_csv'):
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    if os.environ.get('FLASK_ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# -----------------------------------------------------------------------
# Vérification de session expirée
# -----------------------------------------------------------------------
@app.before_request
def check_session_timeout():
    if 'user' in session:
        account = users.get(session['user'])
        if not account or account.get('disabled'):
            session.clear()
            if request.method == 'POST':
                return jsonify(success=False, error='Authentification requise'), 401
            return redirect(url_for('login'))
        session['role'] = account.get('role')
        last_active = session.get('last_active')
        if last_active is not None:
            try:
                elapsed = (datetime.now() - datetime.fromisoformat(last_active)).total_seconds()
            except (ValueError, TypeError):
                elapsed = 3601
            if elapsed > 3600 or elapsed < 0:  # 1 heure
                session.clear()
                flash('Votre session a expiré. Veuillez vous reconnecter.')
                return redirect(url_for('login'))
        session['last_active'] = datetime.now().isoformat()





def load_test_data():
    """Charge les données depuis le fichier JSON"""
    try:
        return read_storage_snapshot()
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None

def collect_storage_snapshot():
    data = {
        'users': {name: {k: v for k, v in user.items() if k != 'temp_password'}
                  for name, user in globals().get('users', {}).items()},
        'admin_courses': globals().get('admin_courses', []),
        'course_assignments': {str(k): v for k, v in globals().get('course_assignments', {}).items()},
        'course_enrollments': {str(k): v for k, v in globals().get('course_enrollments', {}).items()},
        'assignments': globals().get('assignments', []),
        'submissions': globals().get('submissions', []),
        'next_course_admin_id': globals().get('next_course_admin_id', 1),
        'next_assignment_id': globals().get('next_assignment_id', 1),
        'course_content': {str(k): v for k, v in globals().get('course_content', {}).items()},
        'course_chapters': {str(k): v for k, v in globals().get('course_chapters', {}).items()},
        'next_chapter_id': globals().get('next_chapter_id', 1),
        'group_assignments': globals().get('group_assignments', {}),
        'student_groups': globals().get('student_groups', {}),
        'next_group_id': globals().get('next_group_id', 1),
        'notifications': globals().get('notifications', []),
        'audit_logs': globals().get('audit_logs', []),
        'push_subscriptions': globals().get('push_subscriptions', []),
        'system_config': globals().get('system_config', {}),
        'courses': globals().get('courses', []),
        'next_course_id': globals().get('next_course_id', 1),
        'email_jobs': globals().get('email_jobs', []),
        'generated_reports': globals().get('generated_reports', []),
    }
    return data


def save_test_data():
    """Sauvegarde les données actuelles dans le fichier JSON (thread-safe)."""
    if relational_repository is not None:
        if not getattr(g, 'storage_connection', None):
            raise RuntimeError('Relational writes require a request transaction')
        g.storage_dirty = True
        return
    with _data_lock:
        try:
            data = collect_storage_snapshot()
            # Écriture atomique via fichier temporaire
            tmp_path = DATA_FILE_TMP
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, DATA_FILE)
            from flask import has_request_context
            if has_request_context():
                from copy import deepcopy
                g.json_saved_snapshot = deepcopy(data)
        except Exception as e:
            logger.error('Erreur lors de l’enregistrement des données')
            raise

# -----------------------------------------------------------------------
# Chargement des données depuis le fichier JSON
# -----------------------------------------------------------------------
_DEFAULT_ADMIN_PASSWORD = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD')

def _build_default_data():
    """Crée le jeu de données initial avec un admin dont le mot de passe est hashé."""
    return {
        'users': ({
            'admin': {
                'password': generate_password_hash(_DEFAULT_ADMIN_PASSWORD),
                'role': 'admin',
                'name': 'Administrateur ULC-ICAM',
                'email': ''
            }
        } if _DEFAULT_ADMIN_PASSWORD else {}),
        'admin_courses': [],
        'course_assignments': {},
        'course_enrollments': {},
        'assignments': [],
        'submissions': [],
        'next_course_admin_id': 1,
        'next_assignment_id': 1
    }

print("=== CHARGEMENT DES DONNÉES ===")
try:
    data = read_storage_snapshot()
    users                = data.get('users', {})
    admin_courses        = data.get('admin_courses', [])
    course_assignments   = {str(k): v for k, v in data.get('course_assignments', {}).items()}
    course_enrollments   = {str(k): v for k, v in data.get('course_enrollments', {}).items()}
    assignments          = data.get('assignments', [])
    submissions          = data.get('submissions', [])
    next_course_admin_id = data.get('next_course_admin_id', 1)
    next_assignment_id   = data.get('next_assignment_id', 1)
    course_content       = {int(k): v for k, v in data.get('course_content', {}).items()}
    course_chapters      = {int(k): v for k, v in data.get('course_chapters', {}).items()}
    next_chapter_id      = data.get('next_chapter_id', 1)

    # Migrer les anciens mots de passe en clair vers werkzeug hash
    _migrated = 0
    for _uname, _udata in users.items():
        _pwd = _udata.get('password', '')
        if _pwd and not _pwd.startswith('pbkdf2:') and not _pwd.startswith('scrypt:') and ':' not in _pwd:
            _udata['password'] = generate_password_hash(_pwd)
            _migrated += 1
    if _migrated:
        logger.info('Anciens mots de passe hashés en mémoire ; aucune réécriture au démarrage')

    if not users:
        _default = _build_default_data()
        users = _default['users']
        logger.warning(f"Aucun utilisateur trouvé — compte admin créé. "
                       "Initialisation via BOOTSTRAP_ADMIN_PASSWORD uniquement.")

    print("Données chargées depuis ulc_icam_data.json")

except FileNotFoundError:
    logger.warning("ulc_icam_data.json introuvable — création du fichier avec données par défaut")
    _default = _build_default_data()
    users                = _default['users']
    admin_courses        = []
    course_assignments   = {}
    course_enrollments   = {}
    assignments          = []
    submissions          = []
    next_course_admin_id = 1
    next_assignment_id   = 1
    course_content       = {}
    course_chapters      = {}
    next_chapter_id      = 1
    # Créer le fichier tout de suite
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as _f:
            json.dump(_default, _f, ensure_ascii=False, indent=2)
        logger.info(f"ulc_icam_data.json créé. Compte admin initial — "
                    "Initialisation administrateur configurée par environnement.")
    except Exception as _e:
        logger.error(f"Impossible de créer ulc_icam_data.json : {_e}")

except Exception as e:
    logger.critical('Chargement des données impossible ; démarrage interrompu pour éviter leur écrasement')
    raise RuntimeError('Données illisibles : restaurer ou corriger une copie vérifiée') from e

for _user_data in users.values():
    _user_data.pop('temp_password', None)

# Résultats de correction et plagiat
correction_results = {}  # {submission_id: {'score': 85, 'feedback': 'Bon travail'}}
plagiarism_results = {}  # {submission_id: {'similarity': 15, 'sources': []}}

print(f"Utilisateurs chargés: {len(users)}")
print(f"Cours chargés: {len(admin_courses)}")
print(f"Devoirs chargés: {len(assignments)}")
print(f"Soumissions chargées: {len(submissions)}")
print(f"Résultats de correction: {len(correction_results)}")
print(f"Résultats de plagiat: {len(plagiarism_results)}")
print("=== CHARGEMENT TERMINÉ ===")

# Charger les corrections existantes depuis les soumissions
for sub in submissions:
    if 'correction' in sub:
        correction_results[sub['id']] = sub['correction']
    if 'plagiarism' in sub:
        plagiarism_results[sub['id']] = sub['plagiarism']

# Gestion des groupes pour les devoirs
group_assignments = {int(k): v for k, v in globals().get('data', {}).get('group_assignments', {}).items()}  # {assignment_id: {'groups': [[student1, student2], [student3, student4]], 'type': 'manual/auto'}}
student_groups = {int(k): v for k, v in globals().get('data', {}).get('student_groups', {}).items()}  # {assignment_id: {student_username: group_id}}
next_group_id = globals().get('data', {}).get('next_group_id', 1)

notifications = data.get('notifications', []) if 'data' in globals() else []
audit_logs = data.get('audit_logs', []) if 'data' in globals() else []
push_subscriptions = data.get('push_subscriptions', []) if 'data' in globals() else []
email_jobs = data.get('email_jobs', []) if 'data' in globals() else []
generated_reports = data.get('generated_reports', []) if 'data' in globals() else []

# Gestion des cours
courses = data.get('courses', []) if 'data' in globals() else []
next_course_id = data.get('next_course_id', 1) if 'data' in globals() else 1

# -----------------------------------------------------------------------
# Helpers sécurité mots de passe
# -----------------------------------------------------------------------

def _verify_password(plain: str, stored: str) -> bool:
    """
    Vérifie un mot de passe contre le hash stocké.
    Supporte la migration transparente :
      - hash werkzeug (pbkdf2:sha256:...)  → vérification normale
      - hash legacy auth_jwt (salt:hex)    → vérification PBKDF2 custom
      - texte en clair (anciens comptes)   → comparaison directe + migration auto
    """
    if not plain or not stored:
        return False

    # Format werkzeug (nouveau, recommandé)
    if stored.startswith('pbkdf2:') or stored.startswith('scrypt:'):
        return check_password_hash(stored, plain)

    # Format legacy auth_jwt : "salt:hex_hash"
    if ':' in stored:
        try:
            salt, pwd_hash = stored.split(':', 1)
            import hashlib as _hl
            computed = _hl.pbkdf2_hmac(
                'sha256', plain.encode('utf-8'), salt.encode('utf-8'), 100000
            ).hex()
            return computed == pwd_hash
        except Exception:
            pass

    # Fallback texte en clair (migration automatique)
    if plain == stored:
        return True

    return False


def _course_key(course_id):
    """Normalise l'identifiant de cours en chaîne."""
    return str(course_id) if course_id is not None else None

def get_assigned_teachers(course_id):
    """Retourne la liste des enseignants assignés à un cours."""
    return course_assignments.get(_course_key(course_id), [])

def ensure_course_assignment(course_id):
    """Crée si nécessaire la liste des enseignants pour un cours."""
    return course_assignments.setdefault(_course_key(course_id), [])

def get_enrolled_students(course_id):
    """Retourne la liste des étudiants inscrits à un cours."""
    return course_enrollments.get(_course_key(course_id), [])

def ensure_course_enrollments(course_id):
    """Crée si nécessaire la liste des inscriptions pour un cours."""
    return course_enrollments.setdefault(_course_key(course_id), [])

# Harmoniser les clés existantes éventuelles en chaînes
course_assignments = { _course_key(k): v for k, v in course_assignments.items() }
course_enrollments = { _course_key(k): v for k, v in course_enrollments.items() }

# Inscriptions des étudiants aux cours chargées depuis le fichier JSON ci-dessus

# Configuration système (modifiable par l'admin)
# Démarrage avec uniquement la Faculté des Sciences et Technologies (ULC-ICAM)
system_config = {
    'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'],
    'facultes': ['Faculté des Sciences et Technologies (ULC-ICAM)'],
    'departements': [
        'Mathématiques & Informatique',
        'Génie Mécanique', 
        'Génie Électrique',
        'Physique & Chimie',
        'Génie Informatique',
        'Maintenance & Génie Industriels',
        'Énergie/Environnement/Matériaux',
        'Polytechnique Générale'
    ],
    'grades': ['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']
}

# Les cours sont maintenant chargés depuis le fichier JSON ci-dessus

# course_content, course_chapters et next_chapter_id sont chargés depuis le JSON ci-dessus

# Fonctions de notification email
if 'data' in globals() and 'system_config' in data:
    system_config.update(data['system_config'])

def send_email_notification(subject, recipients, html_body):
    """Envoie une notification email"""
    if relational_repository is not None:
        if recipients and os.environ.get('NOTIFICATIONS_ENABLED', '').lower() in ('true', '1', 'yes'):
            email_jobs.append({'id': secrets.token_hex(16), 'subject': '[ULC-ICAM] ' + subject,
                               'recipients': recipients, 'html': html_body, 'status': 'pending'})
            save_test_data()
        return
    if not MAIL_AVAILABLE or not app.config.get('NOTIFICATIONS_ENABLED'):
        print(f"Notification désactivée: {subject}")
        return
    
    if not recipients:
        return
    
    try:
        msg = Message(
            subject=f"[ULC-ICAM] {subject}",
            recipients=recipients,
            html=html_body
        )
        
        def send_async():
            with app.app_context():
                try:
                    mail.send(msg)
                    print(f"Email envoyé: {subject}")
                except Exception as e:
                    print(f"Erreur envoi email: {e}")
        
        thread = threading.Thread(target=send_async)
        thread.start()
        
    except Exception as e:
        print(f"Erreur création email: {e}")

def generate_temp_password():
    """Génère un mot de passe temporaire"""
    length = 16
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_student_emails_for_course(course_id):
    """Récupère les emails des étudiants inscrits à un cours"""
    emails = []
    enrolled_students = get_enrolled_students(course_id)
    
    for student_username in enrolled_students:
        if student_username in users:
            student = users[student_username]
            if student.get('email') and student.get('role') == 'student':
                emails.append(student['email'])
    
    return emails

# ===============================================================================
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 18:35
# Description: Fonctionnalités avancées - Compression et téléchargement
# Fonctionnalités: Compression ZIP, téléchargement en lot, rapports PDF/CSV
# ===============================================================================

def create_zip_archive(files_data, archive_name):
    """Crée une archive ZIP avec les fichiers fournis"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, file_name in files_data:
            if os.path.exists(file_path):
                zip_file.write(file_path, file_name)
    zip_buffer.seek(0)
    return zip_buffer

def generate_assignment_report_pdf(assignment_id):
    """Génère un rapport PDF pour un devoir"""
    if not REPORTLAB_AVAILABLE:
        print("ReportLab non disponible - génération PDF impossible")
        return None
        
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Trouver le devoir
        assignment = next((a for a in assignments if a['id'] == assignment_id), None)
        if not assignment:
            return None
        
        # Titre du rapport
        title = Paragraph(f"Rapport - {assignment['title']}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Informations du devoir
        info_data = [
            ['Devoir:', assignment['title']],
            ['Date limite:', assignment.get('due_date', 'Non définie')],
            ['Note max:', str(assignment.get('max_score', 100))]
        ]
        info_table = Table(info_data)
        story.append(info_table)
        story.append(Spacer(1, 12))
        
        # Statistiques des soumissions
        assignment_submissions = [s for s in submissions if s['assignment_id'] == assignment_id]
        stats_data = [
            ['Soumissions totales:', str(len(assignment_submissions))],
            ['Corrigées:', str(sum(1 for s in assignment_submissions if s['id'] in correction_results))]
        ]
        stats_table = Table(stats_data)
        story.append(stats_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Erreur génération PDF: {e}")
        return None

def generate_course_report_csv(course_id):
    """Génère un rapport CSV pour un cours"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes
    writer.writerow(['Étudiant', 'Email', 'Devoirs soumis', 'Note moyenne'])
    
    # Données des étudiants
    enrolled_students = get_enrolled_students(course_id)
    for student_username in enrolled_students:
        if student_username in users:
            student = users[student_username]
            student_submissions = [s for s in submissions if s['student'] == student_username]
            avg_score = 0
            if student_submissions:
                scores = [correction_results.get(s['id'], {}).get('score', 0) for s in student_submissions]
                scores = [score for score in scores if isinstance(score, (int, float))]
                avg_score = sum(scores) / len(scores) if scores else 0
            
            writer.writerow([
                student.get('name', student_username),
                student.get('email', ''),
                len(student_submissions),
                f"{avg_score:.1f}"
            ])
    
    output.seek(0)
    return output.getvalue()































































def extract_text_from_file(file_path):
    """Extrait le texte d'un fichier selon son extension"""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.docx' and DOCX_AVAILABLE:
            return docx2txt.process(file_path)
        elif ext == '.pdf' and PDF_AVAILABLE:
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        print(f"Erreur extraction texte: {e}")
        return ""

# ============================================================
# MOTEUR DE DÉTECTION DE PLAGIAT — VERSION AMÉLIORÉE
# Trois niveaux de comparaison :
#   1. Exact   : SequenceMatcher sur lignes normalisées
#   2. Structurel : SequenceMatcher après remplacement des
#                   noms de variables par des tokens génériques
#   3. Web     : Google Custom Search API (si clé configurée)
# ============================================================

# Mots-clés à ignorer lors de la tokenisation des variables
from plagiarism_service import (normalize_code_line, _strip_comments, _normalize_lines,
                                _tokenize_variables, _text_to_token_lines,
                                _sequence_similarity, check_web_plagiarism, check_similarity)


def check_plagiarism_local(text, submission_id):
    result = check_similarity(text, submission_id, submissions, app.config['UPLOAD_FOLDER'],
                              extract_text_from_file, check_web_plagiarism)
    plagiarism_results[submission_id] = result
    return result


from ai_service import propose_correction, manual_proposal


def ai_auto_correction(text, assignment, submission_id):
    result = propose_correction(text, assignment)
    correction_results[submission_id] = result
    return result


def openai_correction(text, assignment, submission_id):
    return ai_auto_correction(text, assignment, submission_id)


def huggingface_correction(text, assignment, submission_id):
    return fallback_correction(assignment, submission_id)


def fallback_correction(assignment, submission_id):
    result = manual_proposal(assignment)
    correction_results[submission_id] = result
    return result


def process_submission_async(file_path, assignment, submission_id):
    target = next(s for s in submissions if s['id'] == submission_id)
    if relational_repository is not None:
        target['processing_status'] = 'pending'
        return
    # JSON compatibility mode stays in the request until the relational worker is enabled.
    text = extract_text_from_file(file_path)
    if assignment.get('plagiarism_check'):
        target['plagiarism'] = check_plagiarism_local(text, submission_id)
    if assignment.get('auto_correct'):
        target['correction'] = ai_auto_correction(text, assignment, submission_id)
    target['processing_status'] = 'completed'


def generate_automatic_groups(assignment_id, course_id, group_size):
    """Générer automatiquement des groupes pour un devoir"""
    global group_assignments, student_groups
    if not course_id:
        return
    
    enrolled_students = list(get_enrolled_students(course_id))
    if not enrolled_students:
        return
    import random
    random.shuffle(enrolled_students)
    
    groups = []
    for i in range(0, len(enrolled_students), group_size):
        group = enrolled_students[i:i+group_size]
        if group:  # Ajouter le groupe même s'il est incomplet
            groups.append(group)
    
    group_assignments[assignment_id] = {
        'groups': groups,
        'type': 'auto'
    }
    
    # Mapper les étudiants à leurs groupes
    student_groups[assignment_id] = {}
    for group_id, group in enumerate(groups):
        for student in group:
            student_groups[assignment_id][student] = group_id

def get_course_students(course_id):
    """Récupérer les étudiants inscrits à un cours"""
    if not course_id:
        return []
    
    students_data = []
    for student_username in get_enrolled_students(course_id):
        if student_username in users and users[student_username]['role'] == 'student':
            students_data.append({
                'username': student_username,
                'name': users[student_username]['name'],
                'cip': users[student_username].get('cip', 'N/A')
            })
    return students_data











def is_results_published(assignment):
    """Vérifier si les résultats d'un devoir sont publiés"""
    from datetime import datetime
    
    # Si manuellement publié par le professeur
    if assignment.get('results_published', False):
        return True
    
    # Si date de publication automatique définie
    if assignment.get('results_release_date'):
        try:
            release_date = datetime.fromisoformat(assignment['results_release_date'])
            return datetime.now() >= release_date
        except (ValueError, TypeError) as e:
            print(f"Erreur de format de date: {e}")
            pass
    
    return False

# ===============================================================================
# Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 18:40
# Description: Routes pour fonctionnalités avancées
# Fonctionnalités: Compression ZIP, téléchargement lot, rapports PDF/CSV
# ===============================================================================













if relational_repository is not None:
    install_storage(app, relational_repository, globals(), collect_storage_snapshot)
else:
    install_json_storage(app, globals(), collect_storage_snapshot)

from academic_cache import cached_summary

@app.context_processor
def academic_dashboard_context():
    if request.endpoint == 'core.dashboard' and session.get('user'):
        return {'academic_overview': cached_summary(collect_storage_snapshot(), session['user'])}
    return {}

from academic_metrics import deadline_status
app.jinja_env.filters['deadline_status'] = deadline_status

from blueprint_compat import register_compat
from core_routes import create_blueprint as create_core_blueprint
register_compat(app, create_core_blueprint(globals()), globals())
from assignments_routes import create_blueprint as create_assignments_blueprint
register_compat(app, create_assignments_blueprint(globals()), globals())
from admin_routes import create_blueprint as create_admin_blueprint
register_compat(app, create_admin_blueprint(globals()), globals())
from courses_routes import create_blueprint as create_courses_blueprint
register_compat(app, create_courses_blueprint(globals()), globals())
from grading_routes import create_blueprint as create_grading_blueprint
register_compat(app, create_grading_blueprint(globals()), globals())
from groups_routes import create_blueprint as create_groups_blueprint
register_compat(app, create_groups_blueprint(globals()), globals())
from teachers_routes import create_blueprint as create_teachers_blueprint
register_compat(app, create_teachers_blueprint(globals()), globals())
from reports_routes import create_blueprint as create_reports_blueprint
register_compat(app, create_reports_blueprint(globals()), globals())

from auth_routes import register_auth
register_auth(app, globals())

from notification_routes import create_notification_blueprint
app.register_blueprint(create_notification_blueprint(lambda key: globals()[key], save_test_data))

from execution_routes import create_execution_blueprint
app.register_blueprint(create_execution_blueprint(lambda username: users.get(username)))

# Apply per-endpoint limits after route registration (all login variants included).
if LIMITER_AVAILABLE:
    for _endpoint in ('student_login', 'teacher_login', 'admin_login'):
        app.view_functions['auth.' + _endpoint] = app.view_functions[_endpoint] = limiter.limit('5 per minute; 30 per hour', methods=['POST'])(app.view_functions[_endpoint])
    app.view_functions['execution.test_submit'] = limiter.limit('10 per minute', methods=['POST'])(app.view_functions['execution.test_submit'])

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
