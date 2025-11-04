"""
Modèles de base de données SQLAlchemy pour ULC-ICAM
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    cip = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(120), unique=True)
    
    # Champs étudiants
    nom = db.Column(db.String(100))
    postnom = db.Column(db.String(100))
    prenom = db.Column(db.String(100))
    sexe = db.Column(db.String(10))
    date_naissance = db.Column(db.Date)
    promotion = db.Column(db.String(20))
    faculte = db.Column(db.String(100))
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    
    # Champs professeurs
    cours_dispenses = db.Column(db.String(200))
    departement = db.Column(db.String(100))
    grade = db.Column(db.String(50))
    bureau = db.Column(db.String(50))
    
    # Métadonnées
    must_change_password = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    credits = db.Column(db.Integer, default=3)
    faculte = db.Column(db.String(100))
    departement = db.Column(db.String(100))
    promotions = db.Column(db.Text)  # JSON array
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CourseAssignment(db.Model):
    __tablename__ = 'course_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CourseEnrollment(db.Model):
    __tablename__ = 'course_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Options
    auto_correct = db.Column(db.Boolean, default=False)
    plagiarism_check = db.Column(db.Boolean, default=False)
    max_score = db.Column(db.Integer, default=100)
    is_group_work = db.Column(db.Boolean, default=False)
    group_formation = db.Column(db.String(20), default='manual')
    group_size = db.Column(db.Integer, default=2)
    
    # Publication
    results_published = db.Column(db.Boolean, default=False)
    results_release_date = db.Column(db.DateTime)
    
    # Fichiers
    files = db.Column(db.Text)  # JSON array
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    results_available = db.Column(db.Boolean, default=False)

class CorrectionResult(db.Model):
    __tablename__ = 'correction_results'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    score = db.Column(db.Float)
    max_score = db.Column(db.Float, default=100)
    feedback = db.Column(db.Text)  # JSON array
    feedback_file = db.Column(db.String(255))
    auto_generated = db.Column(db.Boolean, default=False)
    ai_model = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PlagiarismResult(db.Model):
    __tablename__ = 'plagiarism_results'
    
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    similarity = db.Column(db.Float, default=0)
    sources = db.Column(db.Text)  # JSON array
    status = db.Column(db.String(20), default='acceptable')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db(app):
    """Initialise la base de données"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Base de donnees initialisee")

def migrate_from_json():
    """Migre les données JSON vers SQLAlchemy"""
    import json
    import os
    
    if not os.path.exists('ulc_icam_data.json'):
        print("Aucun fichier JSON a migrer")
        return
    
    with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Migration des donnees JSON vers SQLAlchemy...")
    
    # Migrer les utilisateurs
    for username, user_data in data.get('users', {}).items():
        if not User.query.filter_by(username=username).first():
            user = User(
                username=username,
                password=user_data.get('password', ''),
                role=user_data.get('role', 'student'),
                name=user_data.get('name', ''),
                cip=user_data.get('cip'),
                email=user_data.get('email'),
                nom=user_data.get('nom'),
                postnom=user_data.get('postnom'),
                prenom=user_data.get('prenom'),
                sexe=user_data.get('sexe'),
                promotion=user_data.get('promotion'),
                faculte=user_data.get('faculte'),
                telephone=user_data.get('telephone'),
                adresse=user_data.get('adresse'),
                cours_dispenses=user_data.get('cours_dispenses'),
                departement=user_data.get('departement'),
                grade=user_data.get('grade'),
                bureau=user_data.get('bureau'),
                must_change_password=user_data.get('must_change_password', False),
                photo=user_data.get('photo')
            )
            db.session.add(user)
    
    # Migrer les cours
    for course_data in data.get('admin_courses', []):
        course_code = course_data.get('code', 'COURSE_' + str(course_data['id']))
        if not Course.query.filter_by(code=course_code).first():
            course = Course(
                name=course_data.get('name', ''),
                code=course_code,
                credits=course_data.get('credits', 3),
                faculte=course_data.get('faculte'),
                departement=course_data.get('departement'),
                promotions=json.dumps(course_data.get('promotions', [])),
                description=course_data.get('description', '')
            )
            db.session.add(course)
    
    db.session.commit()
    print("Migration terminee")