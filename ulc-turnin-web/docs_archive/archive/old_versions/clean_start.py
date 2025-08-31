#!/usr/bin/env python3
"""
Application ULC-ICAM Turnin - Démarrage propre
Version 100% conforme à Turnin Web UdeS avec fonctionnalités IA en plus
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Créer dossiers nécessaires
os.makedirs('uploads', exist_ok=True)

# Données initiales propres (comme UdeS Turnin)
users = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'Administrateur ULC-ICAM',
        'email': 'admin@ulc-icam.cd'
    }
}

courses = []
assignments = []
submissions = []
next_course_id = 1
next_assignment_id = 1

# Configuration système ULC-ICAM
system_config = {
    'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'],
    'facultes': ['Sciences', 'Médecine', 'Droit', 'Sciences Économiques', 'Polytechnique', 'Lettres et Sciences Humaines'],
    'departements': ['Mathématiques-Informatique', 'Physique', 'Chimie', 'Biologie', 'Médecine Interne', 'Chirurgie', 'Droit Privé', 'Droit Public'],
    'grades': ['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']
}

def save_data():
    """Sauvegarde les données"""
    data = {
        'users': users,
        'courses': courses,
        'assignments': assignments,
        'submissions': submissions,
        'next_course_id': next_course_id,
        'next_assignment_id': next_assignment_id,
        'system_config': system_config
    }
    with open('ulc_icam_clean.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Page d'accueil - Style UdeS Turnin"""
    stats = {
        'total_users': len(users),
        'total_courses': len(courses),
        'total_assignments': len(assignments),
        'total_submissions': len(submissions)
    }
    return render_template('index.html', **stats)

@app.route('/login')
def login():
    """Page de sélection de connexion"""
    return render_template('login_select.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    """Connexion administrateur"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password and users[username]['role'] == 'admin':
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants incorrects')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Dashboard administrateur"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    stats = {
        'users_count': len(users),
        'courses_count': len(courses),
        'assignments_count': len(assignments),
        'submissions_count': len(submissions)
    }
    
    return render_template('admin_dashboard.html', **stats)

@app.route('/admin/users')
def admin_users():
    """Gestion des utilisateurs"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/add_student', methods=['GET', 'POST'])
def add_student():
    """Ajouter un étudiant"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        
        if username not in users:
            users[username] = {
                'username': username,
                'password': request.form['password'],
                'role': 'student',
                'name': f"{request.form['prenom']} {request.form['nom']}",
                'cip': request.form['cip'],
                'email': request.form['email'],
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'promotion': request.form['promotion'],
                'faculte': request.form['faculte'],
                'must_change_password': True
            }
            save_data()
            flash(f'Étudiant {username} ajouté avec succès')
            return redirect(url_for('admin_users'))
        else:
            flash('Nom d\'utilisateur déjà existant')
    
    return render_template('add_student.html', config=system_config)

@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    """Ajouter un professeur"""
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        
        if username not in users:
            users[username] = {
                'username': username,
                'password': request.form['password'],
                'role': 'teacher',
                'name': f"{request.form['grade']} {request.form['prenom']} {request.form['nom']}",
                'cip': request.form['cip'],
                'email': request.form['email'],
                'nom': request.form['nom'],
                'prenom': request.form['prenom'],
                'grade': request.form['grade'],
                'departement': request.form['departement'],
                'must_change_password': True
            }
            save_data()
            flash(f'Professeur {username} ajouté avec succès')
            return redirect(url_for('admin_users'))
        else:
            flash('Nom d\'utilisateur déjà existant')
    
    return render_template('add_teacher.html', config=system_config)

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    print("ULC-ICAM Turnin - Démarrage propre")
    print("Application conforme à Turnin Web UdeS")
    print("URL: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)