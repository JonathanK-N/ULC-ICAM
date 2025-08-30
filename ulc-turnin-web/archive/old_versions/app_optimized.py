"""
Application Flask optimisée ULC-ICAM Turnin
Avec SQLAlchemy, Cache, JWT, Celery et monitoring
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_compress import Compress
import os
from datetime import datetime
import logging

# Imports des modules d'optimisation
from models import db, init_db, migrate_from_json, User, Course, Assignment, Submission
from cache_config import init_cache
from auth_jwt import init_jwt, init_limiter, hash_password, verify_password, create_user_token
from celery_tasks import make_celery, process_plagiarism_async, process_correction_async
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
    
    # Compression des réponses
    Compress(app)
    
    # Initialisation des extensions
    init_db(app)
    cache = init_cache(app)
    jwt = init_jwt(app)
    limiter = init_limiter(app)
    celery = make_celery(app)
    init_monitoring(app)
    
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ulc_icam.log'),
            logging.StreamHandler()
        ]
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
            
            if user and verify_password(password, user.password):
                # Créer token JWT
                token = create_user_token({
                    'username': user.username,
                    'role': user.role,
                    'name': user.name
                })
                
                # Session traditionnelle pour compatibilité
                session['user'] = user.username
                session['role'] = user.role
                session['name'] = user.name
                session['token'] = token
                
                return redirect(url_for('dashboard'))
            else:
                flash('Identifiants incorrects')
        
        return render_template('student_login.html')
    
    @app.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
    @limiter.limit("10 per minute")
    def submit_assignment(assignment_id):
        """Soumission avec traitement asynchrone"""
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
                
                # Traitement asynchrone avec Celery
                if assignment.plagiarism_check:
                    process_plagiarism_async.delay(submission.id, file_path)
                
                if assignment.auto_correct:
                    assignment_data = {
                        'title': assignment.title,
                        'description': assignment.description,
                        'max_score': assignment.max_score
                    }
                    process_correction_async.delay(submission.id, file_path, assignment_data)
                
                flash('Fichier soumis avec succès! Traitement en cours...')
                return redirect(url_for('dashboard'))
        
        return render_template('submit.html', assignment=assignment)
    
    @app.route('/dashboard')
    @cache.cached(timeout=60, key_prefix='dashboard')
    def dashboard():
        """Dashboard avec cache par utilisateur"""
        if 'user' not in session:
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=session['user']).first()
        
        if user.role == 'student':
            # Requête optimisée pour les devoirs de l'étudiant
            assignments = db.session.query(Assignment).join(Course).join(
                CourseEnrollment, Course.id == CourseEnrollment.course_id
            ).filter(CourseEnrollment.student_id == user.id).all()
            
            return render_template('student_dashboard.html', assignments=assignments)
        
        elif user.role == 'teacher':
            # Statistiques professeur optimisées
            teacher_assignments = Assignment.query.filter_by(teacher_id=user.id).all()
            total_submissions = db.session.query(Submission).join(Assignment).filter(
                Assignment.teacher_id == user.id
            ).count()
            
            return render_template('teacher_dashboard.html', 
                                 teacher_assignments=teacher_assignments,
                                 total_submissions=total_submissions)
        
        else:  # admin
            return render_template('admin_dashboard.html')
    
    @app.route('/api/task_status/<task_id>')
    def task_status(task_id):
        """API pour suivre le statut des tâches asynchrones"""
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {'state': task.state, 'status': 'En attente...'}
        elif task.state == 'PROGRESS':
            response = {'state': task.state, 'status': task.info.get('status', '')}
        elif task.state == 'SUCCESS':
            response = {'state': task.state, 'result': task.info}
        else:  # FAILURE
            response = {'state': task.state, 'error': str(task.info)}
        
        return jsonify(response)
    
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
            },
            'celery': {
                'active_tasks': len(celery.control.active()),
                'scheduled_tasks': len(celery.control.scheduled())
            }
        }
        
        return jsonify(stats)
    
    # Gestion d'erreurs optimisée
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erreur serveur: {error}')
        return render_template('500.html'), 500
    
    return app, celery

# Point d'entrée
if __name__ == '__main__':
    app, celery_app = create_app()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Application ULC-ICAM optimisée démarrée")
    print(f"📊 Base de données: SQLite")
    print(f"⚡ Cache: {app.config.get('CACHE_TYPE', 'FileSystem')}")
    print(f"🔐 JWT: Activé")
    print(f"🚦 Rate Limiting: Activé")
    print(f"📈 Monitoring: Activé")
    
    app.run(host='0.0.0.0', port=port, debug=debug)