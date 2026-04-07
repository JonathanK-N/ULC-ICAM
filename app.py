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

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI non installé - correction IA désactivée")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
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
        if 'text/html' in response.content_type:
            token = generate_csrf()
            html = response.get_data(as_text=True)
            # Injecter dans chaque <form>
            hidden = f'<input type="hidden" name="csrf_token" value="{token}">'
            html = re.sub(
                r'(<form\b[^>]*>)',
                r'\1' + hidden,
                html,
                flags=re.IGNORECASE
            )
            # Injecter une meta pour les requêtes AJAX
            meta = f'<meta name="csrf-token" content="{token}">'
            html = html.replace('</head>', meta + '\n</head>', 1)
            response.set_data(html)
        return response

    # Exempter les endpoints JSON (ils utilisent le header X-CSRFToken)
    @csrf.exempt
    def csrf_exempt_json():
        pass

except ImportError:
    CSRF_AVAILABLE = False
    logging.warning("Flask-WTF non installé — protection CSRF désactivée. "
                    "Installez flask-wtf pour activer la protection.")

# -----------------------------------------------------------------------
# Rate Limiting (Flask-Limiter)
# -----------------------------------------------------------------------
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=os.environ.get('REDIS_URL', 'memory://'),
    )
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    logging.warning("Flask-Limiter non installé — rate limiting désactivé.")

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
_data_lock = threading.Lock()

# -----------------------------------------------------------------------
# Chemin du fichier de données (configurable via DATA_FILE env var)
# -----------------------------------------------------------------------
DATA_FILE = os.environ.get('DATA_FILE', 'ulc_icam_data.json')
DATA_FILE_TMP = DATA_FILE + '.tmp'

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
        last_active = session.get('last_active')
        if last_active:
            elapsed = (datetime.now() - datetime.fromisoformat(last_active)).total_seconds()
            if elapsed > 3600:  # 1 heure
                session.clear()
                flash('Votre session a expiré. Veuillez vous reconnecter.')
                return redirect(url_for('login'))
        session['last_active'] = datetime.now().isoformat()


@app.route('/manifest.json')
def web_manifest():
    """Serve the PWA manifest with the expected MIME type."""
    manifest_path = Path(app.static_folder) / 'manifest.json'

    if manifest_path.exists():
        return send_from_directory(
            app.static_folder,
            'manifest.json',
            mimetype='application/manifest+json',
            max_age=0
        )

    response = make_response(json.dumps(PWA_MANIFEST, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/manifest+json'
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/sw.js')
def service_worker():
    """Expose the service worker at the application root for full scope coverage."""
    sw_path = Path(app.static_folder) / 'sw.js'
    if not sw_path.exists():
        # Retourner un service worker vide si le fichier n'existe pas encore
        response = make_response("// Service Worker ULC-ICAM\nself.addEventListener('fetch', function(){});")
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Cache-Control'] = 'no-store'
        return response
    return send_from_directory(
        app.static_folder,
        'sw.js',
        mimetype='application/javascript',
        max_age=0
    )

def load_test_data():
    """Charge les données depuis le fichier JSON"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Erreur chargement: {e}")
        return None

def save_test_data():
    """Sauvegarde les données actuelles dans le fichier JSON (thread-safe)."""
    with _data_lock:
        try:
            data = {
                'users': globals().get('users', {}),
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
            }
            # Écriture atomique via fichier temporaire
            tmp_path = DATA_FILE_TMP
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, DATA_FILE)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des données: {e}")

# -----------------------------------------------------------------------
# Chargement des données depuis le fichier JSON
# -----------------------------------------------------------------------
_DEFAULT_ADMIN_PASSWORD = 'Admin@ULC2024'   # mot de passe initial (hashé)

def _build_default_data():
    """Crée le jeu de données initial avec un admin dont le mot de passe est hashé."""
    return {
        'users': {
            'admin': {
                'password': generate_password_hash(_DEFAULT_ADMIN_PASSWORD),
                'role': 'admin',
                'name': 'Administrateur ULC-ICAM',
                'email': ''
            }
        },
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
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
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
        logger.info(f"Migration mots de passe : {_migrated} compte(s) migré(s) vers hash sécurisé")
        # Sauvegarder immédiatement la migration
        with open(DATA_FILE_TMP, 'w', encoding='utf-8') as _f:
            json.dump(data, _f, ensure_ascii=False, indent=2)
        os.replace(DATA_FILE_TMP, DATA_FILE)

    if not users:
        _default = _build_default_data()
        users = _default['users']
        logger.warning(f"Aucun utilisateur trouvé — compte admin créé. "
                       f"Mot de passe initial : {_DEFAULT_ADMIN_PASSWORD}")

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
                    f"identifiant: admin / mot de passe: {_DEFAULT_ADMIN_PASSWORD}")
    except Exception as _e:
        logger.error(f"Impossible de créer ulc_icam_data.json : {_e}")

except Exception as e:
    logger.error(f"Erreur chargement données : {e}")
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
group_assignments = {}  # {assignment_id: {'groups': [[student1, student2], [student3, student4]], 'type': 'manual/auto'}}
student_groups = {}     # {assignment_id: {student_username: group_id}}
next_group_id = 1

# Gestion des cours
courses = []
next_course_id = 1

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

# Contenu des cours par professeur
course_content = {}  # {course_id: {'description': '', 'documents': [], 'chapters': []}}
course_chapters = {}  # {course_id: [{id, title, description, content, exercises, documents}]}
next_chapter_id = 1

# Fonctions de notification email
def send_email_notification(subject, recipients, html_body):
    """Envoie une notification email"""
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
    length = 8
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
                avg_score = sum(scores) / len(scores) if scores else 0
            
            writer.writerow([
                student.get('name', student_username),
                student.get('email', ''),
                len(student_submissions),
                f"{avg_score:.1f}"
            ])
    
    output.seek(0)
    return output.getvalue()

@app.route('/health')
def health_check():
    """Endpoint de santé pour Railway healthcheck."""
    return jsonify({'status': 'ok'}), 200


@app.route('/')
def index():
    teachers = sum(1 for u in users.values() if u.get('role') == 'teacher')
    students = sum(1 for u in users.values() if u.get('role') == 'student')
    courses_count = len(admin_courses)
    assignments_count = len(assignments)
    return render_template(
        'index.html',
        teachers=teachers,
        students=students,
        courses=courses_count,
        assignments=assignments_count,
    )

@app.route('/login')
def login():
    return render_template('login_select.html')

@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # CIP ou email
        password = request.form['password']
        
        # Chercher l'utilisateur par CIP ou email
        user_found = None
        username_found = None
        
        for username, user_data in users.items():
            if (user_data['role'] == 'student' and
                    (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                if _verify_password(password, user_data['password']):
                    user_found = user_data
                    username_found = username
                    break

        if user_found:
            session.permanent = True
            session['user'] = username_found
            session['role'] = user_found['role']
            session['name'] = user_found['name']
            session['last_active'] = datetime.now().isoformat()
            logger.info(f"Connexion étudiant: {username_found}")
            if user_found.get('must_change_password', False):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            flash('CIP/Email incorrect ou utilisateur non trouvé')
    
    return render_template('student_login.html')

@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # CIP ou email
        password = request.form['password']
        
        # Chercher l'utilisateur par CIP ou email
        user_found = None
        username_found = None
        
        for username, user_data in users.items():
            if (user_data['role'] == 'teacher' and
                    (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                if _verify_password(password, user_data['password']):
                    user_found = user_data
                    username_found = username
                    break

        if user_found:
            session.permanent = True
            session['user'] = username_found
            session['role'] = user_found['role']
            session['name'] = user_found['name']
            session['last_active'] = datetime.now().isoformat()
            logger.info(f"Connexion professeur: {username_found}")
            if user_found.get('must_change_password', False):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            flash('CIP/Email incorrect ou utilisateur non trouvé')
    
    return render_template('teacher_login.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if (username in users and
                _verify_password(password, users[username]['password']) and
                users[username]['role'] == 'admin'):
            session.permanent = True
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            session['last_active'] = datetime.now().isoformat()
            logger.info(f"Connexion admin: {username}")
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'student':
        # Filtrer les devoirs selon les cours auxquels l'étudiant est inscrit
        student_assignments = []
        for assignment in assignments:
            course_id = assignment.get('course_id')
            if course_id and session['user'] in get_enrolled_students(course_id):
                student_assignments.append(assignment)
        
        return render_template('student_dashboard.html', assignments=student_assignments, student_groups=student_groups)
    elif session['role'] == 'teacher':
        # Calculer les statistiques pour le professeur
        teacher_assignments = [a for a in assignments if a.get('teacher') == session['user']]
        teacher_submissions = [s for s in submissions if any(a['id'] == s['assignment_id'] and a.get('teacher') == session['user'] for a in assignments)]
        
        # Calculer les statistiques par devoir
        assignment_stats = {}
        for assignment in teacher_assignments:
            enrolled_count = len(get_enrolled_students(assignment.get('course_id')))
            submitted_count = len([s for s in submissions if s['assignment_id'] == assignment['id']])
            assignment_stats[assignment['id']] = {
                'enrolled': enrolled_count,
                'submitted': submitted_count
            }
        
        # Compter les étudiants uniques dans tous les cours du professeur
        all_students = set()
        for course_id, teachers in course_assignments.items():
            if session['user'] in teachers:
                all_students.update(get_enrolled_students(course_id))
        
        # Récupérer les cours assignés au professeur
        teacher_courses = []
        for course in admin_courses:
            if session['user'] in get_assigned_teachers(course['id']):
                teacher_courses.append(course)
        
        return render_template('teacher_dashboard.html', 
                             teacher_assignments=teacher_assignments,
                             teacher_assignments_count=len(teacher_assignments),
                             total_submissions=len(teacher_submissions),
                             total_students=len(all_students),
                             teacher_courses_count=len(teacher_courses),
                             teacher_courses=teacher_courses,
                             course_enrollments=course_enrollments,
                             assignment_stats=assignment_stats)
    else:
        # Calculer les statistiques pour l'admin
        users_count = len(users)
        students_count = sum(1 for u in users.values() if u.get('role') == 'student')
        teachers_count = sum(1 for u in users.values() if u.get('role') == 'teacher')
        courses_count = len(admin_courses)
        assignments_count = len(assignments)
        submissions_count = len(submissions)
        
        return render_template('admin_dashboard.html', 
                             users=users, 
                             assignments=assignments, 
                             submissions=submissions, 
                             admin_courses=admin_courses,
                             course_assignments=course_assignments,
                             users_count=users_count,
                             students_count=students_count,
                             teachers_count=teachers_count,
                             courses_count=courses_count,
                             assignments_count=assignments_count,
                             submissions_count=submissions_count)

@app.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
def submit_assignment(assignment_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('dashboard'))
    
    # Vérifier que l'étudiant est inscrit au cours du devoir
    course_id = assignment.get('course_id')
    if course_id and session['user'] not in get_enrolled_students(course_id):
        flash('Vous n\'êtes pas inscrit au cours de ce devoir')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Soumission de code via éditeur
        if 'code_content' in request.form:
            try:
                code = request.form['code_content']
                language = request.form.get('language', 'python')
                
                if not code.strip():
                    return jsonify({
                        'success': False,
                        'error': 'Le code ne peut pas être vide'
                    })
                
                # Exécution automatique du code
                executor = CodeExecutor()
                test_cases = assignment.get('test_cases', [])
                execution_result = executor.execute_code(code, language, test_cases=test_cases)
                
                # Calculer la note basée sur les résultats réels d'exécution
                max_score = assignment.get('max_score', 100)
                
                # Pour les devoirs mixtes, le code ne vaut que 50% de la note
                if assignment.get('is_mixed_assignment'):
                    code_max_score = max_score // 2
                    remaining_score = max_score - code_max_score
                else:
                    code_max_score = max_score
                    remaining_score = 0
                
                has_compilation_error = bool(execution_result.get('compile_output', '').strip())
                has_runtime_error = bool(execution_result.get('stderr', '').strip())
                execution_success = execution_result.get('success', False)
                
                status = execution_result.get('status', '')
                is_system_error = 'non installé' in status or 'non trouvé' in status or 'non supporté' in status
                
                if execution_success and not has_compilation_error and not has_runtime_error:
                    code_score = code_max_score
                    if assignment.get('is_mixed_assignment'):
                        feedback = ["✅ Code compilé et exécuté avec succès", f"📝 Note code: {code_score}/{code_max_score}", f"⏳ En attente des fichiers d'analyse ({remaining_score} points)"]
                    else:
                        feedback = ["✅ Code compilé et exécuté avec succès", f"🎉 Note maximale obtenue: {code_score}/{code_max_score}"]
                elif is_system_error:
                    code_score = 0
                    feedback = [f"⚠️ {status}", "🔧 Contactez l'administrateur pour installer les outils nécessaires"]
                else:
                    code_score = 0
                    feedback = []
                    if has_compilation_error:
                        feedback.append("❌ Erreurs de compilation")
                    if has_runtime_error:
                        feedback.append("❌ Erreurs d'exécution")
                    if not execution_success:
                        feedback.append("❌ Échec de l'exécution")
                    feedback.append("🔧 Corrigez les erreurs pour obtenir des points")
                
                score = code_score
                
                execution_result['score'] = score
                execution_result['max_score'] = max_score
                execution_result['feedback'] = feedback
                
                # Sauvegarde de la soumission
                file_info = save_code_submission(session['user'], assignment_id, code, language, execution_result)
                
                # Créer la correction automatique basée sur l'exécution
                correction = {
                    'score': score,
                    'max_score': max_score,
                    'feedback': feedback,
                    'auto_generated': True
                }
                
                # Détection de plagiat pour le code si activée
                plagiarism = {'similarity': 0, 'status': 'non_verifie', 'sources': []}
                if assignment.get('plagiarism_check'):
                    plagiarism = check_plagiarism_local(code, len(submissions) + 1)
                
                submission = {
                    'id': len(submissions) + 1,
                    'student': session['user'],
                    'assignment_id': assignment_id,
                    'filename': file_info['code_file'],
                    'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results_available': True,
                    'code_submission': True,
                    'language': language,
                    'execution_result': execution_result,
                    'correction': correction,
                    'plagiarism': plagiarism
                }
                
                # Sauvegarder aussi dans correction_results
                correction_results[submission['id']] = correction
                submissions.append(submission)
                save_test_data()
                
                return jsonify({
                    'success': True,
                    'execution_result': execution_result,
                    'submission_id': submission['id'],
                    'score': score,
                    'max_score': max_score
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erreur lors de l\'exécution: {str(e)}'
                })
        
        # Soumission de fichier classique
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('Aucun fichier sélectionné')
                return redirect(request.url)
            
            if file:
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{session['user']}_{assignment_id}_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                submission = {
                    'id': len(submissions) + 1,
                    'student': session['user'],
                    'assignment_id': assignment_id,
                    'filename': filename,
                    'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'results_available': False
                }
                submissions.append(submission)

                # Traitement automatique si activé (asynchrone)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if assignment.get('plagiarism_check') or assignment.get('auto_correct'):
                    process_submission_async(file_path, assignment, submission['id'])
                    
                if assignment.get('auto_correct'):
                    assignment['results_published'] = True

                save_test_data()

                flash('Fichier soumis avec succès!')
                return redirect(url_for('dashboard'))
    
    return render_template('submit_code.html', assignment=assignment)

@app.route('/admin/users')
def admin_users():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_users.html', users=users)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        temp_password = generate_temp_password()
        username = request.form['username'].strip()

        if username in users:
            flash('Nom d\'utilisateur déjà existant')
        else:
            student_data = {
                'username': username,
                'password': generate_password_hash(temp_password),  # Hashé
                'temp_password': temp_password,  # Affiché une seule fois à l'admin
                'role': 'student',
                'must_change_password': True,
                'cip': request.form['cip'].strip(),
                'nom': request.form['nom'].strip(),
                'postnom': request.form['postnom'].strip(),
                'prenom': request.form['prenom'].strip(),
                'sexe': request.form['sexe'],
                'date_naissance': request.form['date_naissance'],
                'promotion': request.form['promotion'],
                'faculte': request.form['faculte'],
                'departement': request.form['departement'],
                'telephone': request.form['telephone'].strip(),
                'email': request.form['email'].strip().lower(),
                'adresse': request.form['adresse'].strip()
            }
            student_data['name'] = f"{student_data['prenom']} {student_data['nom']}"
            users[username] = student_data
            save_test_data()
            logger.info(f"Nouvel étudiant créé: {username}")
            flash(f'Étudiant {username} ajouté avec mot de passe temporaire: {temp_password}')
            return redirect(url_for('admin_users'))
    
    return render_template('add_student.html', system_config=system_config)

@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        temp_password = generate_temp_password()
        username = request.form['username'].strip()

        if username in users:
            flash('Nom d\'utilisateur déjà existant')
        else:
            teacher_data = {
                'username': username,
                'password': generate_password_hash(temp_password),  # Hashé
                'temp_password': temp_password,  # Affiché une seule fois à l'admin
                'role': 'teacher',
                'must_change_password': True,
                'cip': request.form['cip'].strip(),
                'nom': request.form['nom'].strip(),
                'postnom': request.form['postnom'].strip(),
                'prenom': request.form['prenom'].strip(),
                'sexe': request.form['sexe'],
                'date_naissance': request.form['date_naissance'],
                'cours_dispenses': request.form['cours_dispenses'].strip(),
                'departement': request.form['departement'],
                'grade': request.form['grade'],
                'telephone': request.form['telephone'].strip(),
                'email': request.form['email'].strip().lower(),
                'bureau': request.form['bureau'].strip()
            }
            teacher_data['name'] = f"{teacher_data['grade']} {teacher_data['prenom']} {teacher_data['nom']}"
            users[username] = teacher_data
            save_test_data()
            logger.info(f"Nouvel enseignant créé: {username}")
            flash(f'Enseignant {username} ajouté avec mot de passe temporaire: {temp_password}')
            return redirect(url_for('admin_users'))
    
    return render_template('add_teacher.html', system_config=system_config)

@app.route('/admin/import_csv', methods=['GET', 'POST'])
def import_csv():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            import csv
            import io
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            header = next(csv_input)  # Lire l'en-tête
            
            added_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_input, start=2):
                if len(row) < 2:
                    continue
                    
                try:
                    username = row[0].strip()
                    role = row[1].strip()
                    
                    if not username or role not in ['student', 'teacher']:
                        errors.append(f'Ligne {row_num}: Nom d\'utilisateur ou rôle invalide')
                        continue
                        
                    if username in users:
                        errors.append(f'Ligne {row_num}: Utilisateur {username} existe déjà')
                        continue
                    
                    temp_password = generate_temp_password()
                    
                    if role == 'student' and len(row) >= 13:
                        user_data = {
                            'username': username,
                            'password': generate_password_hash(temp_password),  # Hashé
                            'temp_password': temp_password,
                            'role': 'student',
                            'must_change_password': True,
                            'cip': row[2].strip(),
                            'nom': row[3].strip(),
                            'postnom': row[4].strip(),
                            'prenom': row[5].strip(),
                            'sexe': row[6].strip(),
                            'date_naissance': row[7].strip(),
                            'promotion': row[8].strip(),
                            'faculte': row[9].strip(),
                            'telephone': row[10].strip(),
                            'email': row[11].strip().lower(),
                            'adresse': row[12].strip()
                        }
                        user_data['name'] = f"{user_data['prenom']} {user_data['nom']}"

                    elif role == 'teacher' and len(row) >= 14:
                        user_data = {
                            'username': username,
                            'password': generate_password_hash(temp_password),  # Hashé
                            'temp_password': temp_password,
                            'role': 'teacher',
                            'must_change_password': True,
                            'cip': row[2].strip(),
                            'nom': row[3].strip(),
                            'postnom': row[4].strip(),
                            'prenom': row[5].strip(),
                            'sexe': row[6].strip(),
                            'date_naissance': row[7].strip(),
                            'cours_dispenses': row[8].strip(),
                            'departement': row[9].strip(),
                            'grade': row[10].strip(),
                            'telephone': row[11].strip(),
                            'email': row[12].strip().lower(),
                            'bureau': row[13].strip()
                        }
                        user_data['name'] = f"{user_data['grade']} {user_data['prenom']} {user_data['nom']}"
                        
                    else:
                        errors.append(f'Ligne {row_num}: Nombre de colonnes insuffisant pour le rôle {role}')
                        continue
                    
                    users[username] = user_data
                    added_count += 1
                    
                except Exception as e:
                    errors.append(f'Ligne {row_num}: Erreur de traitement - {str(e)}')
            
            save_test_data()
            
            if added_count > 0:
                flash(f'{added_count} utilisateurs importés avec succès')
            
            if errors:
                flash(f'Erreurs rencontrées: {"; ".join(errors[:5])}', 'warning')
                if len(errors) > 5:
                    flash(f'... et {len(errors) - 5} autres erreurs', 'warning')
            
            return redirect(url_for('admin_users'))
        else:
            flash('Format de fichier non valide. Utilisez un fichier CSV.')
    
    return render_template('import_csv.html')

@app.route('/admin/delete_user/<username>')
def delete_user(username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if username != 'admin' and username in users:
        del users[username]
        flash(f'Utilisateur {username} supprimé')
    
    return redirect(url_for('admin_users'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        current_hash = users[session['user']]['password']
        if not _verify_password(current_password, current_hash):
            flash('Mot de passe actuel incorrect')
        elif new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas')
        elif len(new_password) < 8:
            flash('Le nouveau mot de passe doit contenir au moins 8 caractères')
        else:
            users[session['user']]['password'] = generate_password_hash(new_password)
            users[session['user']]['must_change_password'] = False
            if 'temp_password' in users[session['user']]:
                del users[session['user']]['temp_password']
            save_test_data()
            logger.info(f"Mot de passe changé pour: {session['user']}")
            flash('Mot de passe changé avec succès')
            return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')



@app.route('/teacher/course/<int:course_id>')
def course_detail(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Vérifier que le professeur est assigné à ce cours
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé à ce cours')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('teacher_assigned_courses'))
    
    # Étudiants éligibles selon les critères du cours
    eligible_students = []
    for username, user in users.items():
        if user['role'] == 'student':
            # Vérifier si l'étudiant correspond aux critères du cours
            promotion_match = not course.get('promotions') or user.get('promotion') in course.get('promotions', [])
            faculte_match = not course.get('faculte') or user.get('faculte') == course.get('faculte')
            
            if promotion_match and faculte_match:
                eligible_students.append({'username': username, 'data': user})
    
    # Étudiants inscrits
    enrolled_students = get_enrolled_students(course_id)
    enrolled_data = [{'username': u, 'data': users[u]} for u in enrolled_students if u in users]
    
    return render_template('course_detail.html', course=course, 
                         eligible_students=eligible_students, enrolled_students=enrolled_data)

@app.route('/teacher/enroll_student/<int:course_id>/<username>')
def enroll_student(course_id, username):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Vérifier que le professeur est assigné à ce cours
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé à ce cours')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if course and username in users and users[username]['role'] == 'student':
        enrolled_list = ensure_course_enrollments(course_id)
        if username not in enrolled_list:
            enrolled_list.append(username)
            save_test_data()  # Sauvegarder les changements
            flash(f'Étudiant {users[username].get("name", username)} inscrit au cours')
        else:
            flash('Étudiant déjà inscrit à ce cours')
    else:
        flash('Erreur lors de l\'inscription')
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/teacher/unenroll_student/<int:course_id>/<username>')
def unenroll_student(course_id, username):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Vérifier que le professeur est assigné à ce cours
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé à ce cours')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    enrolled_list = get_enrolled_students(course_id) if course else []
    if course and username in enrolled_list:
        enrolled_list.remove(username)
        save_test_data()  # Sauvegarder les changements
        flash(f'Étudiant {users[username].get("name", username)} désinscrit du cours')
    else:
        flash('Erreur lors de la désinscription')
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/admin/user_profile/<username>')
def user_profile(username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if username not in users:
        flash('Utilisateur non trouvé')
        return redirect(url_for('admin_users'))
    
    user_data = users[username]
    return render_template('user_profile.html', username=username, user_data=user_data)

@app.route('/admin/upload_photo/<username>', methods=['POST'])
def upload_photo(username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if 'photo' not in request.files:
        flash('Aucune photo sélectionnée')
        return redirect(url_for('user_profile', username=username))
    
    file = request.files['photo']
    if file.filename == '':
        flash('Aucune photo sélectionnée')
        return redirect(url_for('user_profile', username=username))
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        filename = secure_filename(f"{username}_photo.{file.filename.split('.')[-1]}")
        photo_path = os.path.join('app', 'static', 'photos')
        os.makedirs(photo_path, exist_ok=True)
        file.save(os.path.join(photo_path, filename))
        
        users[username]['photo'] = filename
        flash('Photo mise à jour avec succès')
    else:
        flash('Format de fichier non valide. Utilisez PNG, JPG, JPEG ou GIF.')
    
    return redirect(url_for('user_profile', username=username))

@app.route('/admin/edit_user/<username>', methods=['GET', 'POST'])
def edit_user(username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if username not in users:
        flash('Utilisateur non trouvé')
        return redirect(url_for('admin_users'))
    
    if request.method == 'POST':
        user_data = users[username]
        # Mise à jour des champs selon le rôle
        if user_data['role'] == 'student':
            user_data.update({
                'cip': request.form.get('cip', user_data.get('cip', '')),
                'nom': request.form.get('nom', user_data.get('nom', '')),
                'postnom': request.form.get('postnom', user_data.get('postnom', '')),
                'prenom': request.form.get('prenom', user_data.get('prenom', '')),
                'sexe': request.form.get('sexe', user_data.get('sexe', '')),
                'date_naissance': request.form.get('date_naissance', user_data.get('date_naissance', '')),
                'promotion': request.form.get('promotion', user_data.get('promotion', '')),
                'faculte': request.form.get('faculte', user_data.get('faculte', '')),
                'departement': request.form.get('departement', user_data.get('departement', '')),
                'telephone': request.form.get('telephone', user_data.get('telephone', '')),
                'email': request.form.get('email', user_data.get('email', '')),
                'adresse': request.form.get('adresse', user_data.get('adresse', ''))
            })
        elif user_data['role'] == 'teacher':
            user_data.update({
                'cip': request.form.get('cip', user_data.get('cip', '')),
                'nom': request.form.get('nom', user_data.get('nom', '')),
                'postnom': request.form.get('postnom', user_data.get('postnom', '')),
                'prenom': request.form.get('prenom', user_data.get('prenom', '')),
                'sexe': request.form.get('sexe', user_data.get('sexe', '')),
                'date_naissance': request.form.get('date_naissance', user_data.get('date_naissance', '')),
                'cours_dispenses': request.form.get('cours_dispenses', user_data.get('cours_dispenses', '')),
                'departement': request.form.get('departement', user_data.get('departement', '')),
                'grade': request.form.get('grade', user_data.get('grade', '')),
                'telephone': request.form.get('telephone', user_data.get('telephone', '')),
                'email': request.form.get('email', user_data.get('email', '')),
                'bureau': request.form.get('bureau', user_data.get('bureau', ''))
            })
        elif user_data['role'] == 'admin':
            user_data.update({
                'nom': request.form.get('nom', user_data.get('nom', '')),
                'postnom': request.form.get('postnom', user_data.get('postnom', '')),
                'prenom': request.form.get('prenom', user_data.get('prenom', '')),
                'sexe': request.form.get('sexe', user_data.get('sexe', '')),
                'date_naissance': request.form.get('date_naissance', user_data.get('date_naissance', '')),
                'telephone': request.form.get('telephone', user_data.get('telephone', '')),
                'email': request.form.get('email', user_data.get('email', '')),
                'adresse': request.form.get('adresse', user_data.get('adresse', '')),
                'fonction': request.form.get('fonction', user_data.get('fonction', 'Administrateur Système'))
            })
        
        # Mise à jour du nom d'affichage
        if user_data['role'] == 'admin':
            user_data['name'] = f"{user_data.get('prenom', '')} {user_data.get('nom', '')}" if user_data.get('prenom') and user_data.get('nom') else user_data.get('name', 'Administrateur ULC-ICAM')
        else:
            user_data['name'] = f"{user_data.get('prenom', '')} {user_data.get('nom', '')}"
        
        save_test_data()
        flash('Profil mis à jour avec succès')
        return redirect(url_for('user_profile', username=username))
    
    return render_template('edit_user.html', username=username, user_data=users[username], system_config=system_config)

@app.route('/admin/system_config')
def system_config_view():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_config_management.html', config=system_config)

@app.route('/admin/config/<config_type>', methods=['GET', 'POST'])
def manage_config(config_type):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if config_type not in system_config:
        flash('Configuration non trouvée')
        return redirect(url_for('system_config_view'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            new_item = request.form.get('new_item')
            if new_item and new_item not in system_config[config_type]:
                system_config[config_type].append(new_item)
                flash(f'{new_item} ajouté avec succès')
        elif action == 'delete':
            item_to_delete = request.form.get('item')
            
            # Protection pour les éléments critiques
            protected_items = {
                'facultes': ['Faculté des Sciences et Technologies (ULC-ICAM)'],
                'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'],
                'departements': [],
                'grades': []
            }
            
            if item_to_delete in protected_items.get(config_type, []):
                flash(f'{item_to_delete} ne peut pas être supprimé (élément protégé)', 'error')
            elif item_to_delete in system_config[config_type]:
                system_config[config_type].remove(item_to_delete)
                flash(f'{item_to_delete} supprimé avec succès')
            else:
                flash(f'{item_to_delete} non trouvé', 'error')
        return redirect(url_for('manage_config', config_type=config_type))
    
    return render_template('manage_config.html', config_type=config_type, items=system_config[config_type])

@app.route('/admin/courses')
def admin_courses_view():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_courses.html', courses=admin_courses, course_assignments=course_assignments, users=users)

@app.route('/admin/add_course', methods=['GET', 'POST'])
def admin_add_course():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        global next_course_admin_id
        course = {
            'id': next_course_admin_id,
            'name': request.form['name'],
            'code': request.form['code'],
            'credits': int(request.form['credits']),
            'faculte': request.form['faculte'],
            'departement': request.form['departement'],
            'promotions': request.form.getlist('promotions'),
            'description': request.form.get('description', '')
        }
        admin_courses.append(course)
        ensure_course_assignment(next_course_admin_id)
        next_course_admin_id += 1
        save_test_data()
        flash('Cours ajouté avec succès')
        return redirect(url_for('admin_courses_view'))
    
    return render_template('admin_add_course.html', config=system_config)

@app.route('/admin/assign_teacher/<int:course_id>', methods=['GET', 'POST'])
def assign_teacher_to_course(course_id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('admin_courses_view'))
    
    if request.method == 'POST':
        teacher_username = request.form['teacher']
        if teacher_username in users and users[teacher_username]['role'] == 'teacher':
            assigned_list = ensure_course_assignment(course_id)
            if teacher_username not in assigned_list:
                assigned_list.append(teacher_username)
                save_test_data()
                flash(f'Professeur {teacher_username} assigné au cours')
            else:
                flash('Professeur déjà assigné à ce cours')
        return redirect(url_for('admin_courses_view'))

    teachers = {k: v for k, v in users.items() if v['role'] == 'teacher'}

    # Récupérer la liste d'enseignants assignés en tenant compte du format des clés
    key_used = _course_key(course_id)
    assigned_teachers_raw = course_assignments.get(key_used, [])

    # Nettoyer les références obsolètes (comptes supprimés ou non-professeurs)
    valid_assigned_teachers = []
    removed_usernames = []
    for teacher_username in assigned_teachers_raw:
        teacher = users.get(teacher_username)
        if teacher and teacher.get('role') == 'teacher':
            valid_assigned_teachers.append(teacher_username)
        else:
            removed_usernames.append(teacher_username)

    if removed_usernames:
        course_assignments[key_used] = valid_assigned_teachers
        save_test_data()
        flash("Certaines assignations faisaient référence à des comptes supprimés et ont été nettoyées.", "warning")

    assigned_teachers = course_assignments.get(key_used, valid_assigned_teachers)

    return render_template(
        'assign_teacher.html',
        course=course,
        teachers=teachers,
        assigned_teachers=assigned_teachers
    )

@app.route('/admin/unassign_teacher/<int:course_id>/<teacher_username>')
def unassign_teacher_from_course(course_id, teacher_username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    assigned_list = get_assigned_teachers(course_id)
    if teacher_username in assigned_list:
        assigned_list.remove(teacher_username)
        save_test_data()
        flash(f'Professeur {teacher_username} désassigné du cours')
    
    return redirect(url_for('admin_courses_view'))

@app.route('/teacher/my_assigned_courses')
def teacher_assigned_courses():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Trouver les cours assignés à ce professeur
    teacher_courses = []
    for course in admin_courses:
        if session['user'] in get_assigned_teachers(course['id']):
            teacher_courses.append(course)
    
    return render_template('teacher_assigned_courses.html', courses=teacher_courses)


@app.route('/teacher/courses')
def teacher_courses():
    return redirect(url_for('teacher_assigned_courses'))

@app.route('/teacher/course_content/<int:course_id>')
def course_content_view(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé à ce cours')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if course_id not in course_content:
        course_content[course_id] = {'description': '', 'documents': []}
    if course_id not in course_chapters:
        course_chapters[course_id] = []
    
    return render_template('course_content.html', course=course, content=course_content[course_id], chapters=course_chapters[course_id])

@app.route('/teacher/upload_syllabus/<int:course_id>', methods=['POST'])
def upload_syllabus(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if 'syllabus' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(url_for('course_content_view', course_id=course_id))
    
    file = request.files['syllabus']
    allowed_extensions = ['.pdf', '.ppt', '.pptx']
    if file.filename == '' or not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        flash('Veuillez sélectionner un fichier PDF, PPT ou PPTX')
        return redirect(url_for('course_content_view', course_id=course_id))
    
    filename = secure_filename(f"syllabus_{course_id}_{file.filename}")
    syllabus_path = os.path.join(app.config['UPLOAD_FOLDER'], 'syllabus')
    os.makedirs(syllabus_path, exist_ok=True)
    file.save(os.path.join(syllabus_path, filename))
    
    if course_id not in course_content:
        course_content[course_id] = {'description': '', 'documents': []}
    
    course_content[course_id]['syllabus_file'] = filename
    flash('Plan de cours téléversé avec succès')
    return redirect(url_for('course_content_view', course_id=course_id))

@app.route('/download_syllabus/<int:course_id>/<filename>')
def download_syllabus(course_id, filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    filename = secure_filename(filename)
    if not filename:
        flash('Nom de fichier invalide')
        return redirect(url_for('dashboard'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'syllabus'), filename)

@app.route('/teacher/update_course_description/<int:course_id>', methods=['POST'])
def update_course_description(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if course_id not in course_content:
        course_content[course_id] = {'description': '', 'documents': []}
    
    course_content[course_id]['description'] = request.form.get('description', '')
    flash('Description mise à jour')
    return redirect(url_for('course_content_view', course_id=course_id))

@app.route('/teacher/add_chapter/<int:course_id>', methods=['POST'])
def add_chapter(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    global next_chapter_id
    
    # Traiter les fichiers uploadés
    uploaded_documents = []
    if 'chapter_files' in request.files:
        files = request.files.getlist('chapter_files')
        for file in files:
            allowed_extensions = ['.pdf', '.ppt', '.pptx']
            if file and file.filename != '' and any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                filename = secure_filename(f"chapter_{next_chapter_id}_{file.filename}")
                doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chapters')
                os.makedirs(doc_path, exist_ok=True)
                file.save(os.path.join(doc_path, filename))
                
                uploaded_documents.append({
                    'filename': filename,
                    'original_name': file.filename,
                    'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
    
    chapter = {
        'id': next_chapter_id,
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'content': '',
        'exercises': [],
        'documents': uploaded_documents
    }
    
    if course_id not in course_chapters:
        course_chapters[course_id] = []
    
    course_chapters[course_id].append(chapter)
    next_chapter_id += 1
    
    if uploaded_documents:
        flash(f'Chapitre ajouté avec {len(uploaded_documents)} fichier(s) PDF')
    else:
        flash('Chapitre ajouté avec succès')
    return redirect(url_for('course_content_view', course_id=course_id))

@app.route('/teacher/chapter/<int:course_id>/<int:chapter_id>')
def chapter_detail(course_id, chapter_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    chapter = None
    
    if course_id in course_chapters:
        chapter = next((ch for ch in course_chapters[course_id] if ch['id'] == chapter_id), None)
    
    if not chapter:
        flash('Chapitre non trouvé')
        return redirect(url_for('course_content_view', course_id=course_id))
    
    return render_template('chapter_detail.html', course=course, chapter=chapter)

@app.route('/teacher/update_chapter/<int:course_id>/<int:chapter_id>', methods=['POST'])
def update_chapter(course_id, chapter_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if course_id in course_chapters:
        chapter = next((ch for ch in course_chapters[course_id] if ch['id'] == chapter_id), None)
        if chapter:
            chapter['title'] = request.form.get('title', chapter['title'])
            chapter['description'] = request.form.get('description', chapter['description'])
            chapter['content'] = request.form.get('content', chapter['content'])
            flash('Chapitre mis à jour')
    
    return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))

@app.route('/teacher/add_exercise/<int:course_id>/<int:chapter_id>', methods=['POST'])
def add_exercise(course_id, chapter_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if course_id in course_chapters:
        chapter = next((ch for ch in course_chapters[course_id] if ch['id'] == chapter_id), None)
        if chapter:
            exercise = {
                'title': request.form.get('exercise_title', ''),
                'description': request.form.get('exercise_description', ''),
                'solution': request.form.get('exercise_solution', '')
            }
            chapter['exercises'].append(exercise)
            flash('Exercice ajouté')
    
    return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))

@app.route('/teacher/upload_chapter_document/<int:course_id>/<int:chapter_id>', methods=['POST'])
def upload_chapter_document(course_id, chapter_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if 'document' not in request.files:
        flash('Aucun document sélectionné')
        return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))
    
    file = request.files['document']
    allowed_extensions = ['.pdf', '.ppt', '.pptx']
    if file.filename == '' or not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        flash('Veuillez sélectionner un fichier PDF, PPT ou PPTX')
        return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))
    
    filename = secure_filename(f"chapter_{chapter_id}_{file.filename}")
    doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chapters')
    os.makedirs(doc_path, exist_ok=True)
    file.save(os.path.join(doc_path, filename))
    
    if course_id in course_chapters:
        chapter = next((ch for ch in course_chapters[course_id] if ch['id'] == chapter_id), None)
        if chapter:
            chapter['documents'].append({
                'filename': filename,
                'original_name': file.filename,
                'uploaded_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            flash('Document PDF ajouté au chapitre')
    
    return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))

@app.route('/download_chapter_document/<filename>')
def download_chapter_document(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    filename = secure_filename(filename)
    if not filename:
        flash('Nom de fichier invalide')
        return redirect(url_for('dashboard'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'chapters'), filename)

@app.route('/admin/assignments')
def admin_assignments():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_assignments.html', assignments=assignments, users=users)

@app.route('/admin/submissions')
def admin_submissions():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # S'assurer que correction_results est défini
    global correction_results
    if 'correction_results' not in globals():
        correction_results = {}
    
    return render_template('admin_submissions.html', 
                         submissions=submissions, 
                         assignments=assignments, 
                         users=users, 
                         correction_results=correction_results, 
                         plagiarism_results=plagiarism_results)

@app.route('/admin/students')
def admin_students():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    students = {k: v for k, v in users.items() if v['role'] == 'student'}
    return render_template('admin_students.html', students=students)

@app.route('/admin/teachers')
def admin_teachers():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    teachers = {k: v for k, v in users.items() if v['role'] == 'teacher'}
    return render_template('admin_teachers.html', teachers=teachers, course_assignments=course_assignments, admin_courses=admin_courses)

@app.route('/teacher/assignments')
def teacher_assignments():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_assignments = [a for a in assignments if a.get('teacher') == session['user']]
    return render_template('teacher_assignments.html', assignments=teacher_assignments)

@app.route('/teacher/create_assignment', methods=['GET', 'POST'])
def create_assignment():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        global next_assignment_id
        current_id = next_assignment_id
        next_assignment_id += 1

        # Gestion des fichiers téléversés
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(f"assignment_{current_id}_{file.filename}")
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments')
                    os.makedirs(file_path, exist_ok=True)
                    file.save(os.path.join(file_path, filename))
                    uploaded_files.append(filename)
        
        # Gestion des cas de test pour les devoirs de code
        test_cases = []
        if 'is_code_assignment' in request.form:
            test_inputs = request.form.getlist('test_input')
            test_outputs = request.form.getlist('test_output')
            for i, (input_val, output_val) in enumerate(zip(test_inputs, test_outputs)):
                if input_val.strip() or output_val.strip():
                    test_cases.append({
                        'input': input_val,
                        'expected_output': output_val
                    })
        
        course_id_raw = request.form.get('course_id')
        course_id_value = None
        if course_id_raw:
            try:
                course_id_value = int(course_id_raw)
            except ValueError:
                course_id_value = None

        course_name = request.form.get('course', '').strip()
        if course_id_value is not None and not course_name:
            matched_course = next((c for c in admin_courses if c['id'] == course_id_value), None)
            if matched_course:
                course_name = matched_course.get('name', '')

        assignment = {
            'id': current_id,
            'title': request.form.get('title', '').strip(),
            'description': request.form['description'],
            'due_date': request.form['due_date'],
            'course_id': course_id_value,
            'course': course_name,
            'teacher': session['user'],
            'teacher_name': session['name'],
            'files': uploaded_files,
            'auto_correct': 'auto_correct' in request.form,
            'plagiarism_check': 'plagiarism_check' in request.form,
            'max_score': int(request.form.get('max_score', 100)),
            'is_group_work': 'is_group_work' in request.form,
            'group_formation': request.form.get('group_formation', 'manual'),
            'group_size': int(request.form.get('group_size', 2)) if request.form.get('group_size') else 2,
            'results_release_date': request.form.get('results_release_date', ''),
            'results_published': False,
            'is_code_assignment': 'is_code_assignment' in request.form,
            'is_mixed_assignment': 'is_mixed_assignment' in request.form,
            'test_cases': test_cases
        }
        
        # Générer les groupes automatiquement si nécessaire
        if assignment.get('is_group_work') and assignment.get('group_formation') == 'auto' and assignment.get('course_id') is not None:
            generate_automatic_groups(current_id, assignment.get('course_id'), assignment.get('group_size', 2))

        assignments.append(assignment)
        save_test_data()
        flash('Devoir créé avec succès')
        return redirect(url_for('teacher_assignments'))
    
    # Récupérer les cours assignés au professeur
    teacher_courses = []
    for course in admin_courses:
        if session['user'] in get_assigned_teachers(course['id']):
            teacher_courses.append(course)
    
    # Cours pré-sélectionné depuis l'URL
    preselected_course_id = request.args.get('course_id', type=int)
    
    return render_template('create_assignment.html', 
                         admin_courses=admin_courses, 
                         course_assignments=course_assignments, 
                         system_config=system_config,
                         teacher_courses=teacher_courses,
                         preselected_course_id=preselected_course_id)

@app.route('/download_assignment_file/<filename>')
def download_assignment_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    filename = secure_filename(filename)
    if not filename:
        flash('Nom de fichier invalide')
        return redirect(url_for('dashboard'))
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'assignments'), filename)

@app.route('/offline.html')
def offline():
    return render_template('offline.html')

@app.route('/download_file/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))

    # Sécurité : empêcher le path traversal
    filename = secure_filename(filename)
    if not filename:
        flash('Nom de fichier invalide')
        return redirect(url_for('dashboard'))

    # Chercher le fichier dans différents dossiers
    possible_paths = [
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        os.path.join(app.config['UPLOAD_FOLDER'], 'code_submissions', filename),
        os.path.join(app.config['UPLOAD_FOLDER'], 'submissions', filename)
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        flash('Fichier introuvable')
        return redirect(url_for('dashboard'))

    # Admin peut tout télécharger
    if session['role'] == 'admin':
        return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)
    
    # Vérifier que le professeur a le droit de télécharger ce fichier
    if session['role'] == 'teacher':
        submission = next((s for s in submissions if s['filename'] == filename), None)
        if submission:
            assignment = next((a for a in assignments if a['id'] == submission['assignment_id']), None)
            if assignment and assignment.get('teacher') == session['user']:
                return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)
    
    # Étudiant peut télécharger ses propres fichiers
    if session['role'] == 'student':
        submission = next((s for s in submissions if s['filename'] == filename and s['student'] == session['user']), None)
        if submission:
            return send_from_directory(os.path.dirname(file_path), os.path.basename(file_path), as_attachment=True)

    flash('Accès non autorisé à ce fichier')
    return redirect(url_for('dashboard'))


@app.route('/download_correction/<filename>')
def download_correction_file(filename):
    """Permet de télécharger un fichier de correction"""
    if 'user' not in session:
        return redirect(url_for('login'))

    # Trouver la soumission associée au fichier de correction
    submission = next((s for s in submissions
                       if s.get('correction', {}).get('feedback_file') == filename), None)
    if not submission:
        flash('Fichier introuvable')
        return redirect(url_for('dashboard'))

    user_role = session.get('role')
    # Vérification des droits d'accès
    if user_role == 'student' and submission.get('student') != session.get('user'):
        flash('Accès non autorisé à ce fichier')
        return redirect(url_for('dashboard'))
    if user_role == 'teacher':
        assignment = next((a for a in assignments if a['id'] == submission['assignment_id']), None)
        if not assignment or assignment.get('teacher') != session.get('user'):
            flash('Accès non autorisé à ce fichier')
            return redirect(url_for('dashboard'))

    filename = secure_filename(filename)
    if not filename:
        flash('Nom de fichier invalide')
        return redirect(url_for('dashboard'))
    corrections_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'corrections')
    return send_from_directory(corrections_folder, filename)


@app.route('/teacher/assignment_results/<int:assignment_id>')
def assignment_results(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('teacher_assignments'))
    
    # Récupérer les soumissions pour ce devoir
    assignment_submissions = [s for s in submissions if s.get('assignment_id') == assignment_id]
    
    # Ajouter les résultats de correction et plagiat
    for sub in assignment_submissions:
        if not sub.get('correction') and sub['id'] in correction_results:
            sub['correction'] = correction_results[sub['id']]
        if not sub.get('plagiarism') and sub['id'] in plagiarism_results:
            sub['plagiarism'] = plagiarism_results[sub['id']]
        # Assurer que correction existe même si vide
        if not sub.get('correction'):
            sub['correction'] = {'score': 0, 'max_score': assignment.get('max_score', 100), 'feedback': [], 'auto_generated': False}
        # Assurer que plagiarism existe même si vide
        if not sub.get('plagiarism'):
            sub['plagiarism'] = {'similarity': 0, 'status': 'non_verifie', 'sources': []}
    

    return render_template('assignment_results.html', assignment=assignment, submissions=assignment_submissions)


@app.route('/teacher/grade_submission/<int:submission_id>', methods=['GET', 'POST'])
def grade_submission(submission_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    submission = next((s for s in submissions if s['id'] == submission_id), None)
    if not submission:
        flash('Soumission non trouvée')
        return redirect(url_for('teacher_submissions'))

    assignment = next((a for a in assignments if a['id'] == submission['assignment_id']), None)
    if not assignment or assignment.get('teacher') != session['user']:
        flash('Accès non autorisé')
        return redirect(url_for('teacher_submissions'))

    if request.method == 'POST':
        score = request.form.get('score', type=float)
        max_score = request.form.get('max_score', type=float) or assignment.get('max_score', 100)
        feedback_text = request.form.get('feedback', '')
        feedback_list = [line.strip() for line in feedback_text.splitlines() if line.strip()]

        feedback_file = request.files.get('feedback_file')
        filename = correction_results.get(submission_id, {}).get('feedback_file')
        if feedback_file and feedback_file.filename:
            corrections_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'corrections')
            os.makedirs(corrections_folder, exist_ok=True)
            filename = secure_filename(feedback_file.filename)
            feedback_file.save(os.path.join(corrections_folder, filename))

        correction = {
            'score': score,
            'max_score': max_score,
            'feedback': feedback_list,
            'feedback_file': filename,
            'auto_generated': False
        }

        correction_results[submission_id] = correction
        submission['correction'] = correction

        if 'publish_now' in request.form:
            submission['results_available'] = True

        flash('Soumission corrigée')
        return redirect(url_for('assignment_results', assignment_id=submission['assignment_id']))

    correction = correction_results.get(submission_id)
    return render_template('grade_submission.html', submission=submission, assignment=assignment, correction=correction)


@app.route('/teacher/publish_submissions/<int:assignment_id>')
def publish_submissions(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    for sub in submissions:
        if sub.get('assignment_id') == assignment_id:
            sub['results_available'] = True

    flash('Notes publiées pour toutes les soumissions')
    return redirect(url_for('assignment_results', assignment_id=assignment_id))


@app.route('/teacher/unpublish_submissions/<int:assignment_id>')
def unpublish_submissions(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))

    for sub in submissions:
        if sub.get('assignment_id') == assignment_id:
            sub['results_available'] = False

    flash('Notes masquées pour toutes les soumissions')
    return redirect(url_for('assignment_results', assignment_id=assignment_id))

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
_KEYWORDS = frozenset({
    # Python
    'def','class','return','if','else','elif','for','while','in','not','and',
    'or','import','from','as','with','try','except','finally','raise','pass',
    'break','continue','lambda','yield','None','True','False','self','print',
    # C / C++ / Java
    'int','float','double','char','void','bool','long','short','unsigned',
    'signed','const','static','public','private','protected','new','delete',
    'this','super','extends','implements','interface','class','struct','enum',
    'switch','case','default','do','while','goto','sizeof','typedef','return',
    'include','define','ifdef','endif','printf','scanf','cout','cin','endl',
    'string','vector','map','set','list','array','null','true','false',
    # JavaScript
    'var','let','const','function','arrow','console','log','document',
    'window','event','async','await','promise','then','catch',
})

# Regex : identifiants (noms de variables, fonctions, classes)
_IDENT_RE = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]{2,})\b')

# Regex pour supprimer les commentaires multi-lignes /* ... */
_BLOCK_COMMENT_RE = re.compile(r'/\*.*?\*/', re.DOTALL)
# Regex pour supprimer les docstrings Python """ ... """ ou ''' ... '''
_DOCSTRING_RE = re.compile(r'(""".*?"""|\'\'\'.*?\'\'\')', re.DOTALL)
# Regex pour supprimer les littéraux de chaînes (après suppression des commentaires)
_STRING_LITERAL_RE = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'')
# Regex pour remplacer les nombres par un token générique
_NUMBER_RE = re.compile(r'\b\d+(\.\d+)?\b')


def _strip_comments(source: str) -> str:
    """Supprime tous les styles de commentaires d'un code source."""
    # Commentaires bloc /* ... */
    source = _BLOCK_COMMENT_RE.sub(' ', source)
    # Docstrings Python
    source = _DOCSTRING_RE.sub(' ', source)
    # Commentaires ligne // ...
    lines = []
    for line in source.split('\n'):
        if '//' in line:
            line = line[:line.index('//')].rstrip()
        lines.append(line)
    source = '\n'.join(lines)
    # Commentaires Python # ... (pas les directives #include / #define)
    lines = []
    for line in source.split('\n'):
        stripped = line.lstrip()
        if '#' in line and not stripped.startswith('#include') and not stripped.startswith('#define'):
            line = line[:line.index('#')].rstrip()
        lines.append(line)
    return '\n'.join(lines)


def normalize_code_line(line: str) -> str:
    """
    Normalise une ligne de code pour la comparaison de base.
    Supprime les commentaires inline, la casse et les espaces multiples.
    """
    line = line.strip()
    # Commentaire inline //
    if '//' in line:
        line = line[:line.index('//')].strip()
    # Commentaire Python # (sauf #include / #define)
    if '#' in line and not line.lstrip().startswith(('#include', '#define')):
        line = line[:line.index('#')].strip()
    # Espaces multiples
    line = ' '.join(line.split())
    return line.lower()


def _normalize_lines(text: str) -> list:
    """
    Retourne la liste des lignes normalisées non-vides d'un texte.
    Supprime d'abord tous les commentaires bloc.
    """
    clean = _strip_comments(text)
    result = []
    for line in clean.split('\n'):
        norm = normalize_code_line(line)
        if norm:
            result.append(norm)
    return result


def _tokenize_variables(text: str) -> str:
    """
    Remplace les noms de variables / fonctions par des tokens génériques.
    Exemple : 'int compteur = 0;' → 'int VAR_1 = NUM;'

    Résiste aux attaques de renommage de variables.
    """
    clean = _strip_comments(text)
    # Remplacer les chaînes de caractères par STRING
    clean = _STRING_LITERAL_RE.sub('STRING', clean)
    # Remplacer les nombres par NUM
    clean = _NUMBER_RE.sub('NUM', clean)

    # Construire le mapping identifiant → token
    mapping = {}
    counter = [1]  # liste pour mutation dans la closure

    def replace_ident(match):
        name = match.group(1)
        if name in _KEYWORDS or name.isupper():
            return name  # garder les mots-clés et constantes ALL_CAPS
        if name not in mapping:
            mapping[name] = f'VAR_{counter[0]}'
            counter[0] += 1
        return mapping[name]

    tokenized = _IDENT_RE.sub(replace_ident, clean)
    return tokenized


def _sequence_similarity(seq_a: list, seq_b: list) -> float:
    """
    Calcule la similarité entre deux séquences de chaînes via SequenceMatcher.
    Retourne un float entre 0 et 100.
    """
    if not seq_a or not seq_b:
        return 0.0
    matcher = SequenceMatcher(None, seq_a, seq_b, autojunk=False)
    return matcher.ratio() * 100


def _text_to_token_lines(text: str) -> list:
    """Tokenise les variables puis découpe en lignes normalisées."""
    tokenized = _tokenize_variables(text)
    return _normalize_lines(tokenized)


def check_plagiarism_local(text: str, submission_id: int) -> dict:
    """
    Détection de plagiat améliorée — 3 niveaux :
      1. Similarité exacte   (SequenceMatcher sur lignes normalisées)
      2. Similarité structurelle (SequenceMatcher après tokenisation variables)
      3. Plagiat web         (Google Custom Search, si clé configurée)

    Retourne un dict :
      { similarity, sources, status, details }
    """
    if not text or not text.strip():
        return {'similarity': 0, 'sources': [], 'status': 'acceptable', 'details': {}}

    # Préparer les représentations du texte à vérifier
    lines_exact = _normalize_lines(text)
    lines_token = _text_to_token_lines(text)

    max_similarity = 0.0
    sources = []  # liste de dict détaillés

    # -------------------------------------------------------
    # Niveau 1 & 2 : comparaison contre toutes les soumissions
    # -------------------------------------------------------
    for sub in submissions:
        if sub['id'] == submission_id:
            continue
        if not sub.get('filename'):
            continue

        try:
            other_text = ''
            if sub.get('code_submission'):
                path = os.path.join(
                    app.config['UPLOAD_FOLDER'], 'code_submissions', sub['filename']
                )
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        other_text = f.read()
            else:
                path = os.path.join(app.config['UPLOAD_FOLDER'], sub['filename'])
                if os.path.exists(path):
                    other_text = extract_text_from_file(path)

            if not other_text.strip():
                continue

            other_lines_exact = _normalize_lines(other_text)
            other_lines_token = _text_to_token_lines(other_text)

            # Score 1 : comparaison exacte
            sim_exact = _sequence_similarity(lines_exact, other_lines_exact)
            # Score 2 : comparaison structurelle (résiste au renommage)
            sim_struct = _sequence_similarity(lines_token, other_lines_token)

            # On prend le maximum des deux scores pour chaque paire
            sim_pair = max(sim_exact, sim_struct)

            if sim_pair >= 20:
                student_name = users.get(sub.get('student', ''), {}).get('name', sub.get('student', '?'))
                method = 'structurelle' if sim_struct > sim_exact else 'exacte'
                sources.append({
                    'label': (
                        f"Soumission de {student_name} — "
                        f"{sim_pair:.1f}% (similarité {method})"
                    ),
                    'student': sub.get('student', ''),
                    'submission_id': sub['id'],
                    'similarity_exact': round(sim_exact, 1),
                    'similarity_structural': round(sim_struct, 1),
                    'similarity': round(sim_pair, 1),
                })
                max_similarity = max(max_similarity, sim_pair)
                logger.info(
                    f"Plagiat local — sub {submission_id} vs sub {sub['id']}: "
                    f"exact={sim_exact:.1f}% struct={sim_struct:.1f}%"
                )

        except Exception as e:
            logger.warning(f"Erreur comparaison plagiat (sub {sub['id']}): {e}")

    # -------------------------------------------------------
    # Niveau 3 : plagiat web (Google Custom Search)
    # -------------------------------------------------------
    web_score, web_source = check_web_plagiarism(text)
    if web_score > 0:
        max_similarity = max(max_similarity, web_score)
        sources.append({
            'label': f"Source web détectée — {web_score:.0f}% de similarité ({web_source})",
            'student': None,
            'submission_id': None,
            'similarity': web_score,
            'similarity_exact': web_score,
            'similarity_structural': web_score,
        })
        logger.info(f"Plagiat web — sub {submission_id}: {web_score}% ({web_source})")

    # Trier les sources par similarité décroissante, garder les 5 premières
    sources.sort(key=lambda s: s['similarity'], reverse=True)

    # Déterminer le statut
    sim = round(max_similarity, 1)
    if sim >= 70:
        status = 'suspect'
    elif sim >= 40:
        status = 'attention'
    else:
        status = 'acceptable'

    result = {
        'similarity': sim,
        'sources': [s['label'] for s in sources[:5]],   # labels texte pour l'affichage
        'sources_detail': sources[:5],                   # données complètes pour les APIs
        'status': status,
        'details': {
            'checked_submissions': len([s for s in sources if s['student']]),
            'web_checked': web_score > 0 or bool(os.environ.get('GOOGLE_API_KEY')),
        }
    }

    plagiarism_results[submission_id] = result
    return result


def check_web_plagiarism(text_sample: str) -> tuple:
    """
    Vérifie le plagiat web via Google Custom Search API.

    Retourne un tuple (score: float, source_label: str) :
      - score = 0    → rien trouvé ou API non configurée
      - score = 60   → 1-2 résultats trouvés
      - score = 80   → 3-4 résultats trouvés
      - score = 95   → 5+ résultats trouvés (copie quasi-certaine)
    """
    api_key = os.environ.get('GOOGLE_API_KEY', '').strip()
    search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', '').strip()

    if not api_key or not search_engine_id:
        return 0, ''

    try:
        # Choisir la phrase la plus significative (>50 chars, sans mots triviaux)
        candidates = re.split(r'[.!?\n]+', text_sample)
        query = ''
        for candidate in candidates:
            candidate = candidate.strip()
            if 60 <= len(candidate) <= 200 and not candidate.startswith(('import ', '#include', '//')):
                query = candidate
                break

        if not query:
            # Fallback : premiers 100 caractères significatifs
            clean = re.sub(r'\s+', ' ', text_sample.strip())
            query = clean[:120]

        if not query:
            return 0, ''

        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': f'"{query}"',
            'num': 10,
        }
        response = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            logger.warning(f"Google Search API erreur: {response.status_code}")
            return 0, ''

        data = response.json()
        items = data.get('items', [])
        total = data.get('searchInformation', {}).get('totalResults', '0')
        nb_results = len(items)

        if nb_results == 0:
            return 0, ''

        # Premier résultat le plus pertinent
        first_url = items[0].get('link', '') if items else ''
        first_title = items[0].get('title', '') if items else ''

        if nb_results >= 5:
            score = 95
        elif nb_results >= 3:
            score = 80
        else:
            score = 60

        label = f"{first_title} ({first_url})" if first_url else f"{nb_results} résultat(s) trouvé(s)"
        return score, label

    except requests.Timeout:
        logger.warning("Google Search API: timeout")
        return 0, ''
    except Exception as e:
        logger.warning(f"Erreur vérification web: {e}")
        return 0, ''

def ai_auto_correction(text, assignment, submission_id):
    """Correction automatique avec IA"""
    try:
        # Utiliser OpenAI GPT pour la correction
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key and OPENAI_AVAILABLE:
            return openai_correction(text, assignment, submission_id)
        elif TRANSFORMERS_AVAILABLE:
            # Fallback avec Hugging Face Transformers
            return huggingface_correction(text, assignment, submission_id)
        else:
            return fallback_correction(assignment, submission_id)
    except Exception as e:
        print(f"Erreur correction IA: {e}")
        return fallback_correction(assignment, submission_id)

def openai_correction(text, assignment, submission_id):
    """Correction avec OpenAI GPT (SDK v1.x)"""
    if not OPENAI_AVAILABLE:
        return huggingface_correction(text, assignment, submission_id)

    try:
        # SDK v1.x : instancier le client (breaking change depuis openai 0.x)
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        prompt = (
            f"Évaluez ce devoir académique selon les critères suivants:\n"
            f"- Titre: {assignment.get('title', 'Non spécifié')}\n"
            f"- Description: {assignment.get('description', 'Non spécifiée')}\n"
            f"- Note maximale: {assignment.get('max_score', 100)}\n\n"
            f"Contenu à évaluer:\n{text[:2000]}\n\n"
            f"Donnez une note sur {assignment.get('max_score', 100)} et 3-5 commentaires "
            f"constructifs en français.\n"
            f"Format: NOTE: X/Y\nCOMMENTAIRES:\n- Point 1\n- Point 2\n..."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )

        result_text = response.choices[0].message.content
        score, feedback = parse_ai_response(result_text, assignment.get('max_score', 100))

        correction = {
            'score': score,
            'max_score': assignment.get('max_score', 100),
            'feedback': feedback,
            'auto_generated': True,
            'ai_model': 'OpenAI GPT-3.5'
        }

        correction_results[submission_id] = correction
        return correction

    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        return huggingface_correction(text, assignment, submission_id)

def huggingface_correction(text, assignment, submission_id):
    """Correction avec Hugging Face (modèle local)"""
    if not TRANSFORMERS_AVAILABLE:
        return fallback_correction(assignment, submission_id)
        
    try:
        # Utiliser un modèle de sentiment/qualité pour évaluation basique
        classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        
        # Analyser le sentiment/qualité du texte
        chunks = [text[i:i+500] for i in range(0, len(text), 500)][:3]  # Premiers 1500 chars
        scores = []
        
        for chunk in chunks:
            if chunk.strip():
                result = classifier(chunk)
                # Convertir le score de sentiment en note
                confidence = result[0]['score']
                if result[0]['label'] in ['POSITIVE', '4 stars', '5 stars']:
                    scores.append(confidence * 0.9)  # 90% max pour positif
                else:
                    scores.append(confidence * 0.6)  # 60% max pour négatif
        
        avg_score = sum(scores) / len(scores) if scores else 0.7
        final_score = int(avg_score * assignment.get('max_score', 100))
        
        # Générer feedback basique
        feedback = generate_basic_feedback(text, final_score, assignment.get('max_score', 100))
        
        correction = {
            'score': final_score,
            'max_score': assignment.get('max_score', 100),
            'feedback': feedback,
            'auto_generated': True,
            'ai_model': 'Hugging Face BERT'
        }
        
        correction_results[submission_id] = correction
        return correction
        
    except Exception as e:
        print(f"Erreur Hugging Face: {e}")
        return fallback_correction(assignment, submission_id)

def generate_basic_feedback(text, score, max_score):
    """Génère un feedback basique basé sur l'analyse du texte"""
    feedback = []
    
    # Analyse de longueur
    word_count = len(text.split())
    if word_count < 100:
        feedback.append("Le travail semble trop court, développez davantage vos idées")
    elif word_count > 1000:
        feedback.append("Travail bien développé avec un contenu substantiel")
    
    # Analyse de structure
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    if paragraphs > 3:
        feedback.append("Bonne structuration en paragraphes")
    
    # Feedback basé sur la note
    percentage = (score / max_score) * 100
    if percentage >= 80:
        feedback.append("Excellent travail, continuez ainsi")
    elif percentage >= 60:
        feedback.append("Bon travail avec quelques améliorations possibles")
    else:
        feedback.append("Travail à améliorer, revoyez les concepts de base")
    
    return feedback[:5]  # Limiter à 5 commentaires

def parse_ai_response(response_text, max_score):
    """Parse la réponse de l'IA pour extraire note et commentaires"""
    try:
        lines = response_text.split('\n')
        score = max_score * 0.75  # Score par défaut
        feedback = []
        
        for line in lines:
            if 'NOTE:' in line.upper():
                # Extraire la note
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = min(int(numbers[0]), max_score)
            elif line.strip().startswith('-'):
                # Extraire les commentaires
                feedback.append(line.strip()[1:].strip())
        
        if not feedback:
            feedback = ["Travail évalué automatiquement", "Consultez votre professeur pour plus de détails"]
        
        return score, feedback[:5]
    except:
        return max_score * 0.75, ["Évaluation automatique effectuée"]

def fallback_correction(assignment, submission_id):
    """Correction de secours si les IA ne fonctionnent pas"""
    import random
    score = random.randint(int(assignment.get('max_score', 100) * 0.6), int(assignment.get('max_score', 100) * 0.9))
    feedback = [
        "Travail évalué automatiquement",
        "Structure générale acceptable",
        "Consultez votre professeur pour un feedback détaillé"
    ]
    
    correction = {
        'score': score,
        'max_score': assignment.get('max_score', 100),
        'feedback': feedback,
        'auto_generated': True,
        'ai_model': 'Fallback'
    }
    
    correction_results[submission_id] = correction
    return correction

def process_submission_async(file_path, assignment, submission_id):
    """Traite la soumission de manière asynchrone"""
    def process():
        try:
            text = extract_text_from_file(file_path)
            
            # Détection de plagiat
            if assignment.get('plagiarism_check'):
                check_plagiarism_local(text, submission_id)
            
            # Correction automatique
            if assignment.get('auto_correct'):
                ai_auto_correction(text, assignment, submission_id)
                
        except Exception as e:
            print(f"Erreur traitement asynchrone: {e}")
    
    thread = threading.Thread(target=process)
    thread.daemon = True
    thread.start()

def generate_automatic_groups(assignment_id, course_id, group_size):
    """Générer automatiquement des groupes pour un devoir"""
    global group_assignments, student_groups
    if not course_id:
        return
    
    enrolled_students = ensure_course_enrollments(course_id)
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

@app.route('/student/join_group/<int:assignment_id>', methods=['GET', 'POST'])
def join_group(assignment_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    if not assignment or not assignment.get('is_group_work'):
        flash('Devoir non trouvé ou pas un travail de groupe')
        return redirect(url_for('dashboard'))
    
    # Vérifier que l'étudiant est inscrit au cours du devoir
    course_id = assignment.get('course_id')
    if course_id and session['user'] not in get_enrolled_students(course_id):
        flash('Vous n\'êtes pas inscrit au cours de ce devoir')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        global group_assignments, student_groups
        selected_students = request.form.getlist('group_members')
        selected_students.append(session['user'])  # Ajouter l'étudiant actuel

        # Créer le groupe
        if assignment_id not in group_assignments:
            group_assignments[assignment_id] = {'groups': [], 'type': 'manual'}
        if assignment_id not in student_groups:
            student_groups[assignment_id] = {}
        
        group_id = len(group_assignments[assignment_id]['groups'])
        group_assignments[assignment_id]['groups'].append(selected_students)
        
        for student in selected_students:
            student_groups[assignment_id][student] = group_id
        
        flash('Groupe formé avec succès')
        return redirect(url_for('dashboard'))
    
    # Récupérer les étudiants du cours
    course_students = get_course_students(assignment.get('course_id')) if assignment.get('course_id') else []
    
    # Exclure les étudiants déjà dans un groupe
    available_students = []
    for student in course_students:
        if assignment_id not in student_groups or student['username'] not in student_groups[assignment_id]:
            if student['username'] != session['user']:  # Exclure l'étudiant actuel
                available_students.append(student)
    
    return render_template('join_group.html', assignment=assignment, available_students=available_students)

@app.route('/teacher/manage_groups/<int:assignment_id>')
def manage_groups(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a['teacher'] == session['user']), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('teacher_assignments'))
    
    groups_info = group_assignments.get(assignment_id, {'groups': [], 'type': 'manual'})
    course_students = get_course_students(assignment.get('course_id')) if assignment.get('course_id') else []
    
    return render_template('manage_groups.html', assignment=assignment, groups_info=groups_info, course_students=course_students, student_groups=student_groups, users=users)

@app.route('/teacher/submissions')
def teacher_submissions():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_submissions = [s for s in submissions if any(a['id'] == s['assignment_id'] and a.get('teacher') == session['user'] for a in assignments)]
    return render_template('teacher_submissions.html', submissions=teacher_submissions, assignments=assignments, users=users, correction_results=correction_results, plagiarism_results=plagiarism_results)

@app.route('/teacher/students')
def teacher_students():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Récupérer tous les étudiants des cours du professeur
    teacher_students = set()
    teacher_courses = []
    for course_id_str, teachers in course_assignments.items():
        if session['user'] in teachers:
            course_id = int(course_id_str)
            course = next((c for c in admin_courses if c['id'] == course_id), None)
            if course:
                teacher_courses.append(course)
                # Utiliser course_id_str (chaîne) pour accéder aux inscriptions
                teacher_students.update(get_enrolled_students(course_id_str))
    
    students_data = []
    for student_username in teacher_students:
        if student_username in users:
            students_data.append({
                'username': student_username,
                'data': users[student_username]
            })
    
    return render_template('teacher_students.html', students=students_data, courses=teacher_courses)

@app.route('/teacher/assignment_submissions/<int:assignment_id>')
def assignment_submissions(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('teacher_assignments'))
    
    assignment_submissions = [s for s in submissions if s['assignment_id'] == assignment_id]
    enrolled_students = get_enrolled_students(assignment.get('course_id'))
    
    return render_template('assignment_submissions.html', 
                         assignment=assignment, 
                         submissions=assignment_submissions, 
                         enrolled_students=enrolled_students,
                         users=users)

@app.route('/student/my_grades')
def student_grades():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    # Récupérer les soumissions de l'étudiant avec notes
    student_submissions = [s for s in submissions if s['student'] == session['user']]
    
    grades_data = []
    for submission in student_submissions:
        assignment = next((a for a in assignments if a['id'] == submission['assignment_id']), None)
        if assignment:
            # Vérifier que l'étudiant est inscrit au cours du devoir
            course_id = assignment.get('course_id')
            if course_id and session['user'] not in get_enrolled_students(course_id):
                continue  # Ignorer ce devoir si l'étudiant n'est pas inscrit
            
            # Vérifier si les résultats sont publiés globalement ou individuellement
            results_available = submission.get('results_available') or is_results_published(assignment)
            
            correction = submission.get('correction', {})
            plagiarism = submission.get('plagiarism', {})
            if results_available:
                if not correction and submission['id'] in correction_results:
                    correction = correction_results[submission['id']]
                    submission['correction'] = correction
                if not plagiarism and submission['id'] in plagiarism_results:
                    plagiarism = plagiarism_results[submission['id']]
                    submission['plagiarism'] = plagiarism
            else:
                correction = {}
                plagiarism = {}

            grade_info = {
                'assignment': assignment,
                'submission': submission,
                'correction': correction,
                'plagiarism': plagiarism,
                'results_available': results_available
            }
            grades_data.append(grade_info)
    
    return render_template('student_grades.html', grades=grades_data)

@app.route('/student/courses')
def student_courses():
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    enrolled_ids = {cid for cid, students in course_enrollments.items() if session['user'] in students}
    enrolled_courses = [c for c in admin_courses if _course_key(c['id']) in enrolled_ids]

    return render_template('student_courses.html', courses=enrolled_courses)

@app.route('/student/course/<int:course_id>')
def student_course_detail(course_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    if session['user'] not in get_enrolled_students(course_id):
        flash("Accès non autorisé à ce cours")
        return redirect(url_for('student_courses'))

    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('student_courses'))

    content = course_content.get(course_id, {'description': '', 'documents': []})
    chapters = course_chapters.get(course_id, [])

    return render_template('student_course_detail.html', course=course, content=content, chapters=chapters)

@app.route('/teacher/publish_results/<int:assignment_id>')
def publish_results(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if assignment:
        assignment['results_published'] = True
        flash('Résultats publiés avec succès')
    else:
        flash('Devoir non trouvé')
    
    return redirect(url_for('assignment_results', assignment_id=assignment_id))

@app.route('/teacher/unpublish_results/<int:assignment_id>')
def unpublish_results(assignment_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if assignment:
        assignment['results_published'] = False
        flash('Résultats masqués aux étudiants')
    else:
        flash('Devoir non trouvé')
    
    return redirect(url_for('assignment_results', assignment_id=assignment_id))

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

@app.route('/teacher/download_all_submissions/<int:assignment_id>')
def download_all_submissions(assignment_id):
    """Télécharge toutes les soumissions d'un devoir en ZIP"""
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('teacher_assignments'))
    
    # Collecter les fichiers de soumission
    assignment_submissions = [s for s in submissions if s['assignment_id'] == assignment_id]
    files_data = []
    
    for sub in assignment_submissions:
        sub_filename = sub.get('filename', '')
        if not sub_filename:
            continue
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], sub_filename)
        if not os.path.exists(file_path):
            # Chercher aussi dans les sous-dossiers
            for sub_dir in ('submissions', 'code_submissions'):
                alt = os.path.join(app.config['UPLOAD_FOLDER'], sub_dir, sub_filename)
                if os.path.exists(alt):
                    file_path = alt
                    break
        if os.path.exists(file_path):
            student_key = sub.get('student', 'unknown')
            student_name = users.get(student_key, {}).get('name', student_key)
            archive_name = f"{student_name}_{sub_filename}"
            files_data.append((file_path, archive_name))

    if not files_data:
        flash('Aucune soumission à télécharger')
        return redirect(url_for('assignment_results', assignment_id=assignment_id))

    # Créer l'archive ZIP
    assignment_title = assignment.get('title', f'devoir_{assignment_id}')
    zip_buffer = create_zip_archive(files_data, f"soumissions_{assignment_title}")

    response = make_response(zip_buffer.getvalue())
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f'attachment; filename="soumissions_{assignment_title}.zip"'
    
    return response

@app.route('/teacher/generate_report/<int:assignment_id>')
def generate_assignment_report(assignment_id):
    """Génère un rapport PDF pour un devoir"""
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id and a.get('teacher') == session['user']), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('teacher_assignments'))
    
    # Générer le rapport PDF
    pdf_buffer = generate_assignment_report_pdf(assignment_id)
    if not pdf_buffer:
        flash('Erreur lors de la génération du rapport')
        return redirect(url_for('assignment_results', assignment_id=assignment_id))
    
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="rapport_{assignment["title"]}.pdf"'
    
    return response

@app.route('/teacher/export_course_data/<int:course_id>')
def export_course_data(course_id):
    """Exporte les données d'un cours en CSV"""
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Vérifier l'accès au cours
    if session['user'] not in get_assigned_teachers(course_id):
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    course = next((c for c in admin_courses if c['id'] == course_id), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('teacher_assigned_courses'))
    
    # Générer le CSV
    csv_data = generate_course_report_csv(course_id)
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="donnees_{course["name"]}.csv"'
    
    return response

@app.route('/admin/system_report')
def system_report():
    """Génère un rapport système complet"""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Statistiques générales
    stats = {
        'total_users': len(users),
        'students': sum(1 for u in users.values() if u.get('role') == 'student'),
        'teachers': sum(1 for u in users.values() if u.get('role') == 'teacher'),
        'courses': len(admin_courses),
        'assignments': len(assignments),
        'submissions': len(submissions),
        'corrected': len(correction_results)
    }
    
    return render_template('system_report.html', stats=stats)

@app.route('/admin/export_all_data')
def export_all_data():
    """Exporte toutes les données système"""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    data = {
        'users': users,
        'admin_courses': admin_courses,
        'course_assignments': course_assignments,
        'course_enrollments': course_enrollments,
        'assignments': assignments,
        'submissions': submissions,
        'correction_results': correction_results,
        'plagiarism_results': plagiarism_results
    }
    
    response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename="ulc_export_complet.json"'
    return response

@app.route('/admin/generate_full_report')
def generate_full_report():
    """Génère un rapport PDF complet"""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if not REPORTLAB_AVAILABLE:
        flash('ReportLab non disponible - génération PDF impossible')
        return redirect(url_for('system_report'))
    
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Titre
        title = Paragraph("Rapport Système - Université Loyola du Congo", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Statistiques
        stats_data = [
            ['Utilisateurs totaux:', str(len(users))],
            ['Étudiants:', str(sum(1 for u in users.values() if u.get('role') == 'student'))],
            ['Professeurs:', str(sum(1 for u in users.values() if u.get('role') == 'teacher'))],
            ['Cours:', str(len(admin_courses))],
            ['Devoirs:', str(len(assignments))],
            ['Soumissions:', str(len(submissions))]
        ]
        stats_table = Table(stats_data)
        story.append(stats_table)
        
        doc.build(story)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename="rapport_systeme_ulc.pdf"'
        return response
    except Exception as e:
        flash(f'Erreur génération PDF: {e}')
        return redirect(url_for('system_report'))

@app.route('/admin/download_backup')
def download_backup():
    """Télécharge une sauvegarde complète"""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Créer une sauvegarde avec timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Sécurité : ne jamais exporter les mots de passe en clair
    safe_users = {}
    for uname, udata in users.items():
        safe_user = {k: v for k, v in udata.items()
                     if k not in ('password', 'temp_password')}
        safe_users[uname] = safe_user

    backup_data = {
        'timestamp': timestamp,
        'version': '1.0',
        'university': 'Université Loyola du Congo',
        'note': 'Les mots de passe sont exclus de la sauvegarde pour des raisons de sécurité.',
        'data': {
            'users': safe_users,
            'admin_courses': admin_courses,
            'course_assignments': course_assignments,
            'course_enrollments': course_enrollments,
            'assignments': assignments,
            'submissions': submissions
        }
    }

    response = make_response(json.dumps(backup_data, ensure_ascii=False, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename="sauvegarde_ulc_{timestamp}.json"'
    return response

@app.route('/admin/check_all_plagiarism')
def check_all_plagiarism():
    """Vérifie le plagiat pour toutes les soumissions de code"""
    if 'user' not in session or session['role'] not in ['admin', 'teacher']:
        return redirect(url_for('login'))
    
    checked_count = 0
    for submission in submissions:
        if submission.get('code_submission'):
            try:
                code_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'code_submissions', submission['filename'])
                if os.path.exists(code_file_path):
                    with open(code_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code_content = f.read()
                    
                    plagiarism_result = check_plagiarism_local(code_content, submission['id'])
                    submission['plagiarism'] = plagiarism_result
                    checked_count += 1
            except Exception as e:
                print(f"Erreur vérification plagiat pour {submission['id']}: {e}")
    
    save_test_data()
    flash(f'Plagiat vérifié pour {checked_count} soumissions de code')
    if session['role'] == 'admin':
        return redirect(url_for('admin_submissions'))
    else:
        return redirect(url_for('teacher_submissions'))

@app.route('/admin/recheck_plagiarism/<int:submission_id>')
def recheck_plagiarism(submission_id):
    """Force la revérification du plagiat pour une soumission"""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    submission = next((s for s in submissions if s['id'] == submission_id), None)
    if not submission:
        flash('Soumission non trouvée')
        return redirect(url_for('admin_submissions'))
    
    try:
        # Récupérer le contenu du code
        if submission.get('code_submission'):
            code_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'code_submissions', submission['filename'])
            if os.path.exists(code_file_path):
                with open(code_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    code_content = f.read()
                
                # Relancer la détection de plagiat
                plagiarism_result = check_plagiarism_local(code_content, submission_id)
                submission['plagiarism'] = plagiarism_result
                save_test_data()
                
                flash(f'Plagiat revérifié: {plagiarism_result["similarity"]}% de similarité')
            else:
                flash('Fichier de code non trouvé')
        else:
            flash('Cette soumission n\'est pas une soumission de code')
    except Exception as e:
        flash(f'Erreur lors de la revérification: {str(e)}')
    
    return redirect(url_for('admin_submissions'))

@app.route('/upload_analysis_files/<int:assignment_id>', methods=['POST'])
def upload_analysis_files(assignment_id):
    """Upload des fichiers d'analyse pour devoirs mixtes"""
    if 'user' not in session or session['role'] != 'student':
        return jsonify({'success': False, 'error': 'Non autorisé'})
    
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    if not assignment or not assignment.get('is_mixed_assignment'):
        return jsonify({'success': False, 'error': 'Devoir non trouvé ou pas un devoir mixte'})
    
    if 'analysis_files' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier fourni'})
    
    files = request.files.getlist('analysis_files')
    uploaded_files = []
    
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"analysis_{session['user']}_{assignment_id}_{timestamp}_{filename}"
            
            analysis_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'analysis')
            os.makedirs(analysis_folder, exist_ok=True)
            file.save(os.path.join(analysis_folder, filename))
            uploaded_files.append(filename)
    
    # Mettre à jour la soumission existante ou créer une nouvelle
    submission = next((s for s in submissions if s['student'] == session['user'] and s['assignment_id'] == assignment_id), None)
    
    if submission:
        submission['analysis_files'] = uploaded_files
        submission['analysis_submitted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        # Créer une nouvelle soumission pour les fichiers d'analyse uniquement
        submission = {
            'id': len(submissions) + 1,
            'student': session['user'],
            'assignment_id': assignment_id,
            'analysis_files': uploaded_files,
            'analysis_submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results_available': False,
            'analysis_only': True
        }
        submissions.append(submission)
    
    save_test_data()
    
    return jsonify({
        'success': True,
        'message': f'{len(uploaded_files)} fichier(s) d\'analyse téléversé(s) avec succès',
        'files': uploaded_files
    })

@app.route('/test_submit', methods=['POST'])
def test_submit():
    """Route de test pour la soumission"""
    try:
        code = request.form.get('code_content', '')
        language = request.form.get('language', 'python')
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': 'Code vide'
            })
        
        # Test d'exécution simple
        executor = CodeExecutor()
        result = executor.execute_code(code, language)
        
        # Note basée sur le résultat réel de compilation/exécution
        max_score = 100
        
        # Vérifier si le code s'est exécuté sans erreur
        has_compilation_error = bool(result.get('compile_output', '').strip())
        has_runtime_error = bool(result.get('stderr', '').strip())
        execution_success = result.get('success', False)
        
        # Déterminer la note selon les résultats réels
        status = result.get('status', '')
        is_system_error = 'non installé' in status or 'non trouvé' in status or 'non supporté' in status
        
        if execution_success and not has_compilation_error and not has_runtime_error:
            score = max_score
            feedback = [
                "✅ Compilation réussie",
                "✅ Exécution sans erreur", 
                f"🎉 Félicitations ! Note maximale obtenue: {max_score}/{max_score}"
            ]
        elif is_system_error:
            score = 0
            feedback = [
                f"⚠️ {status}",
                "🔧 Contactez l'administrateur pour installer les outils nécessaires"
            ]
        else:
            score = 0
            feedback = []
            if has_compilation_error:
                feedback.append("❌ Erreurs de compilation détectées")
            if has_runtime_error:
                feedback.append("❌ Erreurs d'exécution détectées")
            if not execution_success:
                feedback.append("❌ Le programme ne s'exécute pas correctement")
            feedback.append("🔧 Corrigez les erreurs pour obtenir des points")
        
        result['score'] = score
        result['max_score'] = max_score
        result['feedback'] = feedback
        
        return jsonify({
            'success': True,
            'execution_result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/admin/seed', methods=['GET', 'POST'])
def admin_seed():
    """Injecte les données de démonstration (une seule fois, admin uniquement)."""
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    global users, admin_courses, course_assignments, course_enrollments, assignments, submissions, course_content, course_chapters, next_chapter_id

    # Vérifier si les données existent déjà
    already_seeded = (
        len(users) > 1 or
        len(admin_courses) > 0 or
        len(assignments) > 0
    )

    if request.method == 'GET':
        return render_template_string('''
<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
<title>Seed données démo</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 600px; margin: 80px auto; padding: 20px; }
  .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
  .danger  { background: #f8d7da; border: 1px solid #dc3545; padding: 15px; border-radius: 6px; margin-bottom: 20px; }
  .btn { padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }
  .btn-primary { background: #0d6efd; color: white; }
  .btn-secondary { background: #6c757d; color: white; text-decoration: none; padding: 10px 24px; border-radius: 4px; }
</style></head><body>
<h2>Injection données de démonstration</h2>
{% if already_seeded %}
<div class="danger">
  <strong>Attention :</strong> Des données existent déjà ({{ nb_users }} utilisateurs, {{ nb_courses }} cours).
  Cliquer sur "Confirmer" va <strong>écraser toutes les données actuelles</strong>.
</div>
{% else %}
<div class="warning">
  Cela va créer : 1 admin, 5 professeurs, 20 étudiants, 8 cours, 10 devoirs, 29 soumissions.
</div>
{% endif %}
<form method="POST">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <button type="submit" class="btn btn-primary">Confirmer l\'injection</button>
  <a href="{{ url_for(\'admin_users\') }}" class="btn-secondary" style="margin-left:10px;">Annuler</a>
</form>
</body></html>
        ''', already_seeded=already_seeded, nb_users=len(users), nb_courses=len(admin_courses))

    # POST — exécuter le seed
    try:
        import importlib.util, sys as _sys
        seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_data.py')

        if not os.path.exists(seed_path):
            flash('Fichier seed_data.py introuvable.', 'danger')
            return redirect(url_for('admin_users'))

        spec = importlib.util.spec_from_file_location('seed_data', seed_path)
        seed_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seed_module)

        # Recharger les données en mémoire depuis le fichier JSON mis à jour
        with _data_lock:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                fresh = json.load(f)
            users.clear();               users.update(fresh.get('users', {}))
            admin_courses.clear();       admin_courses.extend(fresh.get('admin_courses', []))
            course_assignments.clear();  course_assignments.update(fresh.get('course_assignments', {}))
            course_enrollments.clear();  course_enrollments.update(fresh.get('course_enrollments', {}))
            assignments.clear();         assignments.extend(fresh.get('assignments', []))
            submissions.clear();         submissions.extend(fresh.get('submissions', []))
            global next_course_admin_id, next_assignment_id
            next_course_admin_id = fresh.get('next_course_admin_id', len(admin_courses) + 1)
            next_assignment_id   = fresh.get('next_assignment_id', len(assignments) + 1)
            course_content.clear();  course_content.update({int(k): v for k, v in fresh.get('course_content', {}).items()})
            course_chapters.clear(); course_chapters.update({int(k): v for k, v in fresh.get('course_chapters', {}).items()})
            next_chapter_id = fresh.get('next_chapter_id', 1)

        flash(
            f'Données de démo injectées avec succès : {len(users)} utilisateurs, '
            f'{len(admin_courses)} cours, {len(assignments)} devoirs, {len(submissions)} soumissions.',
            'success'
        )
        app.logger.info('Seed exécuté par %s', session.get('user'))

    except Exception as e:
        app.logger.error('Erreur seed: %s', e, exc_info=True)
        flash(f'Erreur lors de l\'injection : {e}', 'danger')

    return redirect(url_for('admin_users'))


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
