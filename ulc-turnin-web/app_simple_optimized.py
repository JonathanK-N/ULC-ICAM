"""
Application Flask optimisée ULC-ICAM Turnin (Version Simplifiée)
Avec SQLAlchemy, Cache et JWT (sans Celery pour éviter les erreurs)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_compress import Compress
from flask_caching import Cache
from flask_jwt_extended import JWTManager, create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta
import logging

# Imports des modules d'optimisation
from models import db, init_db, migrate_from_json, User, Course, Assignment, Submission
from performance_monitor import init_monitoring
from config import get_config

def create_app():
    """Factory pour créer l'application Flask optimisée"""
    
    app = Flask(__name__)
    
    # Configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configuration base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ulc_icam.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration JWT
    app.config['JWT_SECRET_KEY'] = app.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    # Configuration Cache
    if os.environ.get('REDIS_URL'):
        cache_config = {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
            'CACHE_DEFAULT_TIMEOUT': 300
        }
    else:
        cache_config = {
            'CACHE_TYPE': 'FileSystemCache',
            'CACHE_DIR': 'cache',
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_THRESHOLD': 1000
        }
    
    app.config.update(cache_config)
    
    # Initialisation des extensions
    Compress(app)
    cache = Cache(app)
    jwt = JWTManager(app)
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    # Créer dossier cache si nécessaire
    if cache_config['CACHE_TYPE'] == 'FileSystemCache':
        os.makedirs('cache', exist_ok=True)
    
    # Base de données
    init_db(app)
    
    # Monitoring
    init_monitoring(app)
    
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('ulc_icam.log'), logging.StreamHandler()]
    )
    
    # Migration des données JSON si nécessaire
    with app.app_context():
        migrate_from_json()
    
    # Routes optimisées avec cache
    @app.route('/')
    @cache.cached(timeout=300)
    def index():
        """Page d'accueil avec cache"""
        stats = {
            'teachers': User.query.filter_by(role='teacher').count(),
            'students': User.query.filter_by(role='student').count(),
            'courses': Course.query.count(),
            'assignments': Assignment.query.count()
        }
        return render_template('index.html', **stats)
    
    @app.route('/login/student', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def student_login():
        """Connexion étudiant avec rate limiting"""
        if request.method == 'POST':
            identifier = request.form['identifier']
            password = request.form.get('password', '')
            
            # Recherche optimisée avec SQLAlchemy
            user = User.query.filter(
                (User.cip == identifier) | (User.email == identifier),
                User.role == 'student'
            ).first()
            
            if user and (not password or user.password == password):
                # Créer token JWT
                token = create_access_token(
                    identity=user.username,
                    additional_claims={'role': user.role, 'name': user.name}
                )
                
                # Session traditionnelle pour compatibilité
                session['user'] = user.username
                session['role'] = user.role
                session['name'] = user.name
                session['token'] = token
                
                return redirect(url_for('dashboard'))
            else:
                flash('Identifiants incorrects')
        
        return render_template('student_login.html')
    
    @app.route('/login/teacher', methods=['GET', 'POST'])
    @limiter.limit("5 per minute")
    def teacher_login():
        """Connexion professeur avec rate limiting"""
        if request.method == 'POST':
            identifier = request.form['identifier']
            password = request.form.get('password', '')
            
            user = User.query.filter(
                (User.cip == identifier) | (User.email == identifier),
                User.role == 'teacher'
            ).first()
            
            if user and (not password or user.password == password):
                token = create_access_token(
                    identity=user.username,
                    additional_claims={'role': user.role, 'name': user.name}
                )
                
                session['user'] = user.username
                session['role'] = user.role
                session['name'] = user.name
                session['token'] = token
                
                return redirect(url_for('dashboard'))
            else:
                flash('Identifiants incorrects')
        
        return render_template('teacher_login.html')
    
    @app.route('/login/admin', methods=['GET', 'POST'])
    @limiter.limit("3 per minute")
    def admin_login():
        """Connexion admin avec rate limiting strict"""
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username, role='admin').first()
            
            if user and user.password == password:
                token = create_access_token(
                    identity=user.username,
                    additional_claims={'role': user.role, 'name': user.name}
                )
                
                session['user'] = user.username
                session['role'] = user.role
                session['name'] = user.name
                session['token'] = token
                
                return redirect(url_for('dashboard'))
            else:
                flash('Identifiants incorrects')
        
        return render_template('admin_login.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard optimisé"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=session['user']).first()
        
        if user.role == 'student':
            # Requête optimisée pour les devoirs de l'étudiant
            assignments = Assignment.query.join(Course).join(
                'course_enrollments'
            ).filter_by(student_id=user.id).all()
            
            return render_template('student_dashboard.html', assignments=assignments)
        
        elif user.role == 'teacher':
            # Statistiques professeur optimisées
            teacher_assignments = Assignment.query.filter_by(teacher_id=user.id).all()
            total_submissions = Submission.query.join(Assignment).filter(
                Assignment.teacher_id == user.id
            ).count()
            
            return render_template('teacher_dashboard.html', 
                                 teacher_assignments=teacher_assignments,
                                 total_submissions=total_submissions)
        
        else:  # admin
            return render_template('admin_dashboard.html')
    
    @app.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")
    def submit_assignment(assignment_id):
        """Soumission avec traitement synchrone optimisé"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        assignment = Assignment.query.get_or_404(assignment_id)
        
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('Aucun fichier sélectionné')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('Aucun fichier sélectionné')
                return redirect(request.url)
            
            if file:
                from werkzeug.utils import secure_filename
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{session['user']}_{assignment_id}_{timestamp}_{filename}"
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Créer la soumission en base
                user = User.query.filter_by(username=session['user']).first()
                submission = Submission(
                    assignment_id=assignment_id,
                    student_id=user.id,
                    filename=filename
                )
                db.session.add(submission)
                db.session.commit()
                
                # Traitement synchrone rapide (sans Celery)
                if assignment.plagiarism_check or assignment.auto_correct:
                    flash('Fichier soumis avec succès! Traitement en cours...')
                    # Le traitement IA se fera en arrière-plan via threading
                    import threading
                    thread = threading.Thread(
                        target=process_submission_sync,
                        args=(file_path, assignment, submission.id)
                    )
                    thread.daemon = True
                    thread.start()
                else:
                    flash('Fichier soumis avec succès!')
                
                return redirect(url_for('dashboard'))
        
        return render_template('submit.html', assignment=assignment)
    
    @app.route('/admin/system_stats')
    def system_stats():
        """Statistiques système pour admin"""
        if session.get('role') != 'admin':
            return "Accès non autorisé", 403
        
        stats = {
            'database': {
                'users': User.query.count(),
                'courses': Course.query.count(),
                'assignments': Assignment.query.count(),
                'submissions': Submission.query.count()
            },
            'cache': {
                'type': app.config.get('CACHE_TYPE', 'Unknown'),
                'timeout': app.config.get('CACHE_DEFAULT_TIMEOUT', 0)
            }
        }
        
        return jsonify(stats)
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
    
    # Gestion d'erreurs optimisée
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erreur serveur: {error}')
        return render_template('500.html'), 500
    
    return app

def process_submission_sync(file_path, assignment, submission_id):
    """Traitement synchrone des soumissions (sans Celery)"""
    try:
        # Import des fonctions IA depuis l'app originale
        from app import extract_text_from_file, check_plagiarism_local, ai_auto_correction
        
        text = extract_text_from_file(file_path)
        
        if assignment.plagiarism_check:
            check_plagiarism_local(text, submission_id)
        
        if assignment.auto_correct:
            assignment_data = {
                'title': assignment.title,
                'description': assignment.description,
                'max_score': assignment.max_score
            }
            ai_auto_correction(text, assignment_data, submission_id)
            
    except Exception as e:
        print(f"Erreur traitement soumission: {e}")

# Point d'entrée
if __name__ == '__main__':
    app = create_app()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("Application ULC-ICAM optimisee demarree")
    print(f"Base de donnees: SQLite")
    print(f"Cache: {app.config.get('CACHE_TYPE', 'FileSystem')}")
    print(f"JWT: Active")
    print(f"Rate Limiting: Active")
    print(f"Monitoring: Active")
    
    app.run(host='0.0.0.0', port=port, debug=debug)