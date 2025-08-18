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
    'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrateur'},
    'student': {'password': 'password', 'role': 'student', 'name': 'Étudiant Test'},
    'teacher': {'password': 'password', 'role': 'teacher', 'name': 'Professeur Test'}
}

assignments = [
    {'id': 1, 'title': 'TP Python', 'course': 'Programmation', 'due_date': '2024-02-15', 'description': 'Exercices Python'},
    {'id': 2, 'title': 'Projet Web', 'course': 'Développement Web', 'due_date': '2024-02-20', 'description': 'Application Flask'}
]

submissions = []

# Gestion des cours
courses = []
next_course_id = 1

# Inscriptions des étudiants aux cours
course_enrollments = {}  # {course_id: [student_usernames]}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login_select.html')

@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password and users[username]['role'] == 'student':
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            if users[username].get('must_change_password', False):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects ou accès non autorisé')
    
    return render_template('student_login.html')

@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password and users[username]['role'] == 'teacher':
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            if users[username].get('must_change_password', False):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects ou accès non autorisé')
    
    return render_template('teacher_login.html')

@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password and users[username]['role'] == 'admin':
            session['user'] = username
            session['role'] = users[username]['role']
            session['name'] = users[username]['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants incorrects ou accès non autorisé')
    
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
        return render_template('student_dashboard.html', assignments=assignments)
    elif session['role'] == 'teacher':
        return render_template('teacher_dashboard.html', assignments=assignments, submissions=submissions)
    else:
        return render_template('admin_dashboard.html', users=users, assignments=assignments, submissions=submissions)

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
        student_data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'role': 'student',
            'must_change_password': True,
            'cip': request.form['cip'],
            'nom': request.form['nom'],
            'postnom': request.form['postnom'],
            'prenom': request.form['prenom'],
            'sexe': request.form['sexe'],
            'date_naissance': request.form['date_naissance'],
            'promotion': request.form['promotion'],
            'faculte': request.form['faculte'],
            'telephone': request.form['telephone'],
            'email': request.form['email'],
            'adresse': request.form['adresse']
        }
        
        if student_data['username'] in users:
            flash('Nom d\'utilisateur déjà existant')
        else:
            student_data['name'] = f"{student_data['prenom']} {student_data['nom']}"
            users[student_data['username']] = student_data
            flash(f'Étudiant {student_data["username"]} ajouté avec succès')
            return redirect(url_for('admin_users'))
    
    return render_template('add_student.html')

@app.route('/admin/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        teacher_data = {
            'username': request.form['username'],
            'password': request.form['password'],
            'role': 'teacher',
            'must_change_password': True,
            'cip': request.form['cip'],
            'nom': request.form['nom'],
            'postnom': request.form['postnom'],
            'prenom': request.form['prenom'],
            'sexe': request.form['sexe'],
            'date_naissance': request.form['date_naissance'],
            'cours_dispenses': request.form['cours_dispenses'],
            'departement': request.form['departement'],
            'grade': request.form['grade'],
            'telephone': request.form['telephone'],
            'email': request.form['email'],
            'bureau': request.form['bureau']
        }
        
        if teacher_data['username'] in users:
            flash('Nom d\'utilisateur déjà existant')
        else:
            teacher_data['name'] = f"{teacher_data['grade']} {teacher_data['prenom']} {teacher_data['nom']}"
            users[teacher_data['username']] = teacher_data
            flash(f'Enseignant {teacher_data["username"]} ajouté avec succès')
            return redirect(url_for('admin_users'))
    
    return render_template('add_teacher.html')

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
            next(csv_input)  # Skip header
            
            added_count = 0
            for row in csv_input:
                if len(row) >= 4:
                    username, name, role, password = row[0], row[1], row[2], row[3]
                    if username not in users and role in ['student', 'teacher']:
                        users[username] = {'password': password, 'role': role, 'name': name, 'must_change_password': True}
                        added_count += 1
            
            flash(f'{added_count} utilisateurs importés avec succès')
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
        
        if users[session['user']]['password'] != current_password:
            flash('Mot de passe actuel incorrect')
        elif new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas')
        else:
            users[session['user']]['password'] = new_password
            users[session['user']]['must_change_password'] = False
            flash('Mot de passe changé avec succès')
            return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

@app.route('/teacher/courses')
def teacher_courses():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_courses = [c for c in courses if c['teacher'] == session['user']]
    return render_template('teacher_courses.html', courses=teacher_courses)

@app.route('/teacher/add_course', methods=['GET', 'POST'])
def add_course():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        global next_course_id
        course = {
            'id': next_course_id,
            'title': request.form['title'],
            'description': request.form['description'],
            'teacher': session['user'],
            'teacher_name': session['name'],
            'target_promotions': request.form.getlist('promotions'),
            'target_facultes': request.form.getlist('facultes'),
            'credits': request.form['credits']
        }
        courses.append(course)
        course_enrollments[next_course_id] = []
        next_course_id += 1
        flash('Cours ajouté avec succès')
        return redirect(url_for('teacher_courses'))
    
    return render_template('add_course.html')

@app.route('/teacher/course/<int:course_id>')
def course_detail(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    course = next((c for c in courses if c['id'] == course_id and c['teacher'] == session['user']), None)
    if not course:
        flash('Cours non trouvé')
        return redirect(url_for('teacher_courses'))
    
    # Étudiants éligibles selon les critères du cours
    eligible_students = []
    for username, user in users.items():
        if user['role'] == 'student':
            if (not course['target_promotions'] or user.get('promotion') in course['target_promotions']) and \
               (not course['target_facultes'] or user.get('faculte') in course['target_facultes']):
                eligible_students.append({'username': username, 'data': user})
    
    # Étudiants inscrits
    enrolled_students = course_enrollments.get(course_id, [])
    enrolled_data = [{'username': u, 'data': users[u]} for u in enrolled_students if u in users]
    
    return render_template('course_detail.html', course=course, 
                         eligible_students=eligible_students, enrolled_students=enrolled_data)

@app.route('/teacher/enroll_student/<int:course_id>/<username>')
def enroll_student(course_id, username):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    course = next((c for c in courses if c['id'] == course_id and c['teacher'] == session['user']), None)
    if course and username in users and users[username]['role'] == 'student':
        if course_id not in course_enrollments:
            course_enrollments[course_id] = []
        if username not in course_enrollments[course_id]:
            course_enrollments[course_id].append(username)
            flash(f'Étudiant {username} inscrit au cours')
    
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/teacher/unenroll_student/<int:course_id>/<username>')
def unenroll_student(course_id, username):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    course = next((c for c in courses if c['id'] == course_id and c['teacher'] == session['user']), None)
    if course and course_id in course_enrollments and username in course_enrollments[course_id]:
        course_enrollments[course_id].remove(username)
        flash(f'Étudiant {username} désinscrit du cours')
    
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
        
        user_data['name'] = f"{user_data.get('prenom', '')} {user_data.get('nom', '')}"
        flash('Profil mis à jour avec succès')
        return redirect(url_for('user_profile', username=username))
    
    return render_template('edit_user.html', username=username, user_data=users[username])

if __name__ == '__main__':
    app.run(debug=True)