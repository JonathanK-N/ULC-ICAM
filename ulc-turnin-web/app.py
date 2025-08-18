from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Données simulées (remplacer par une base de données)
users = {
    'student': {'password': 'password', 'role': 'student', 'name': 'Étudiant Test'},
    'teacher': {'password': 'password', 'role': 'teacher', 'name': 'Professeur Test'}
}

assignments = [
    {'id': 1, 'title': 'TP Python', 'course': 'Programmation', 'due_date': '2024-02-15', 'description': 'Exercices Python'},
    {'id': 2, 'title': 'Projet Web', 'course': 'Développement Web', 'due_date': '2024-02-20', 'description': 'Application Flask'}
]

submissions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if session['role'] == 'student':
        return render_template('student_dashboard.html', assignments=assignments)
    else:
        return render_template('teacher_dashboard.html', assignments=assignments, submissions=submissions)

@app.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
def submit_assignment(assignment_id):
    if 'user' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    assignment = next((a for a in assignments if a['id'] == assignment_id), None)
    if not assignment:
        flash('Devoir non trouvé')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné')
            return redirect(request.url)
        
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
                'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            submissions.append(submission)
            
            flash('Fichier soumis avec succès!')
            return redirect(url_for('dashboard'))
    
    return render_template('submit.html', assignment=assignment)

if __name__ == '__main__':
    app.run(debug=True)