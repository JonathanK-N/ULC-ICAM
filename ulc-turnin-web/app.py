from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-change-this")
# Configuration pour différents environnements
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Créer le dossier uploads s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Charger les données de test ULC-ICAM
def load_test_data():
    """Charge les données de test depuis le fichier JSON"""
    try:
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print("Fichier de données non trouvé, utilisation des données par défaut")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return None

# Charger les données de test
test_data = load_test_data()

if test_data:
    # Utiliser les données de test
    users = test_data.get('users', {})
    admin_courses = test_data.get('admin_courses', [])
    course_assignments = {int(k): v for k, v in test_data.get('course_assignments', {}).items()}
    course_enrollments = {int(k): v for k, v in test_data.get('course_enrollments', {}).items()}
    assignments = test_data.get('assignments', [])
    submissions = test_data.get('submissions', [])
    next_course_admin_id = test_data.get('next_course_admin_id', 1)
    next_assignment_id = test_data.get('next_assignment_id', 1)
    print(f"✅ Données de test chargées: {len(users)} utilisateurs, {len(admin_courses)} cours")
else:
    # Données par défaut
    users = {
        'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrateur Cognito Web'}
    }
    admin_courses = []
    course_assignments = {}
    course_enrollments = {}
    assignments = []
    submissions = []
    next_course_admin_id = 1
    next_assignment_id = 1

# Les données sont maintenant chargées depuis le fichier JSON ci-dessus

# Résultats de correction et plagiat
correction_results = {}  # {submission_id: {'score': 85, 'feedback': 'Bon travail'}}
plagiarism_results = {}  # {submission_id: {'similarity': 15, 'sources': []}}

# Gestion des groupes pour les devoirs
group_assignments = {}  # {assignment_id: {'groups': [[student1, student2], [student3, student4]], 'type': 'manual/auto'}}
student_groups = {}     # {assignment_id: {student_username: group_id}}
next_group_id = 1

# Gestion des cours
courses = []
next_course_id = 1

# Inscriptions des étudiants aux cours chargées depuis le fichier JSON ci-dessus

# Configuration système (modifiable par l'admin)
system_config = {
    'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'],
    'facultes': ['Sciences', 'Médecine', 'Droit', 'Sciences Économiques', 'Polytechnique', 'Lettres et Sciences Humaines'],
    'departements': ['Mathématiques-Informatique', 'Physique', 'Chimie', 'Biologie', 'Médecine Interne', 'Chirurgie', 'Droit Privé', 'Droit Public'],
    'grades': ['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']
}

# Les cours sont maintenant chargés depuis le fichier JSON ci-dessus

# Contenu des cours par professeur
course_content = {}  # {course_id: {'description': '', 'documents': [], 'chapters': []}}
course_chapters = {}  # {course_id: [{id, title, description, content, exercises, documents}]}
next_chapter_id = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login_select.html')

@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # CIP ou email
        password = request.form.get('password', '')  # Mot de passe optionnel pour les tests
        
        # Chercher l'utilisateur par CIP ou email
        user_found = None
        username_found = None
        
        for username, user_data in users.items():
            if (user_data['role'] == 'student' and 
                (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                # Mode test : connexion avec CIP seulement (sans mot de passe)
                if not password or user_data['password'] == password:
                    user_found = user_data
                    username_found = username
                    break
        
        if user_found:
            session['user'] = username_found
            session['role'] = user_found['role']
            session['name'] = user_found['name']
            # Ignorer le changement de mot de passe obligatoire en mode test
            if password and user_found.get('must_change_password', False):
                return redirect(url_for('change_password'))
            return redirect(url_for('dashboard'))
        else:
            flash('CIP/Email incorrect ou utilisateur non trouvé')
    
    return render_template('student_login.html')

@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # CIP ou email
        password = request.form.get('password', '')  # Mot de passe optionnel pour les tests
        
        # Chercher l'utilisateur par CIP ou email
        user_found = None
        username_found = None
        
        for username, user_data in users.items():
            if (user_data['role'] == 'teacher' and 
                (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                # Mode test : connexion avec CIP seulement (sans mot de passe)
                if not password or user_data['password'] == password:
                    user_found = user_data
                    username_found = username
                    break
        
        if user_found:
            session['user'] = username_found
            session['role'] = user_found['role']
            session['name'] = user_found['name']
            # Ignorer le changement de mot de passe obligatoire en mode test
            if password and user_found.get('must_change_password', False):
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
        # Filtrer les devoirs selon les cours auxquels l'étudiant est inscrit
        student_assignments = []
        for assignment in assignments:
            course_id = assignment.get('course_id')
            if course_id and course_id in course_enrollments:
                if session['user'] in course_enrollments[course_id]:
                    student_assignments.append(assignment)
        
        return render_template('student_dashboard.html', assignments=student_assignments, student_groups=student_groups)
    elif session['role'] == 'teacher':
        # Calculer les statistiques pour le professeur
        teacher_assignments = [a for a in assignments if a.get('teacher') == session['user']]
        teacher_submissions = [s for s in submissions if any(a['id'] == s['assignment_id'] and a.get('teacher') == session['user'] for a in assignments)]
        
        # Calculer les statistiques par devoir
        assignment_stats = {}
        for assignment in teacher_assignments:
            enrolled_count = len(course_enrollments.get(assignment.get('course_id', 0), []))
            submitted_count = len([s for s in submissions if s['assignment_id'] == assignment['id']])
            assignment_stats[assignment['id']] = {
                'enrolled': enrolled_count,
                'submitted': submitted_count
            }
        
        # Compter les étudiants uniques dans tous les cours du professeur
        all_students = set()
        for course_id, teachers in course_assignments.items():
            if session['user'] in teachers:
                all_students.update(course_enrollments.get(course_id, []))
        
        return render_template('teacher_dashboard.html', 
                             teacher_assignments=teacher_assignments,
                             teacher_assignments_count=len(teacher_assignments),
                             total_submissions=len(teacher_submissions),
                             total_students=len(all_students),
                             teacher_courses_count=sum(1 for teachers in course_assignments.values() if session['user'] in teachers),
                             assignment_stats=assignment_stats)
    else:
        return render_template('admin_dashboard.html', users=users, assignments=assignments, submissions=submissions, admin_courses=admin_courses)

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
    if course_id:
        if course_id not in course_enrollments or session['user'] not in course_enrollments[course_id]:
            flash('Vous n\'êtes pas inscrit au cours de ce devoir')
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
            
            # Traitement automatique si activé
            if assignment.get('plagiarism_check'):
                simulate_plagiarism_check('contenu du fichier', submission['id'])
            
            if assignment.get('auto_correct'):
                simulate_auto_correction('contenu du fichier', assignment, submission['id'])
            
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
    
    return render_template('import_csv_congo.html')

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

@app.route('/admin/system_config')
def system_config_view():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('system_config.html', config=system_config)

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
            if item_to_delete in system_config[config_type]:
                system_config[config_type].remove(item_to_delete)
                flash(f'{item_to_delete} supprimé avec succès')
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
        course_assignments[next_course_admin_id] = []
        next_course_admin_id += 1
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
            if course_id not in course_assignments:
                course_assignments[course_id] = []
            if teacher_username not in course_assignments[course_id]:
                course_assignments[course_id].append(teacher_username)
                flash(f'Professeur {teacher_username} assigné au cours')
            else:
                flash('Professeur déjà assigné à ce cours')
        return redirect(url_for('admin_courses_view'))
    
    teachers = {k: v for k, v in users.items() if v['role'] == 'teacher'}
    assigned_teachers = course_assignments.get(course_id, [])
    return render_template('assign_teacher.html', course=course, teachers=teachers, assigned_teachers=assigned_teachers)

@app.route('/admin/unassign_teacher/<int:course_id>/<teacher_username>')
def unassign_teacher_from_course(course_id, teacher_username):
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    if course_id in course_assignments and teacher_username in course_assignments[course_id]:
        course_assignments[course_id].remove(teacher_username)
        flash(f'Professeur {teacher_username} désassigné du cours')
    
    return redirect(url_for('admin_courses_view'))

@app.route('/teacher/my_assigned_courses')
def teacher_assigned_courses():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Trouver les cours assignés à ce professeur
    teacher_courses = []
    for course in admin_courses:
        if course['id'] in course_assignments and session['user'] in course_assignments[course['id']]:
            teacher_courses.append(course)
    
    return render_template('teacher_assigned_courses.html', courses=teacher_courses)

@app.route('/teacher/course_content/<int:course_id>')
def course_content_view(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
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

@app.route('/teacher/update_course_description/<int:course_id>', methods=['POST'])
def update_course_description(course_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
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
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    global next_chapter_id
    
    chapter = {
        'id': next_chapter_id,
        'title': request.form.get('title', ''),
        'description': request.form.get('description', ''),
        'content': '',
        'exercises': [],
        'documents': []
    }
    
    if course_id not in course_chapters:
        course_chapters[course_id] = []
    
    course_chapters[course_id].append(chapter)
    next_chapter_id += 1
    
    flash('Chapitre ajouté avec succès')
    return redirect(url_for('course_content_view', course_id=course_id))

@app.route('/teacher/chapter/<int:course_id>/<int:chapter_id>')
def chapter_detail(course_id, chapter_id):
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
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
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
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
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
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
    
    if course_id not in course_assignments or session['user'] not in course_assignments[course_id]:
        flash('Accès non autorisé')
        return redirect(url_for('teacher_assigned_courses'))
    
    if 'document' not in request.files:
        flash('Aucun document sélectionné')
        return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))
    
    file = request.files['document']
    if file.filename == '':
        flash('Aucun document sélectionné')
        return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))
    
    if file:
        filename = secure_filename(f"chapter_{chapter_id}_{file.filename}")
        doc_path = os.path.join('uploads', 'chapters')
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
                flash('Document ajouté au chapitre')
    
    return redirect(url_for('chapter_detail', course_id=course_id, chapter_id=chapter_id))

@app.route('/download_chapter_document/<filename>')
def download_chapter_document(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return send_from_directory(os.path.join('uploads', 'chapters'), filename)

@app.route('/admin/assignments')
def admin_assignments():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_assignments.html', assignments=assignments, users=users)

@app.route('/admin/submissions')
def admin_submissions():
    if 'user' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_submissions.html', submissions=submissions, assignments=assignments, users=users, correction_results=correction_results, plagiarism_results=plagiarism_results)

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
        
        # Gestion des fichiers téléversés
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(f"assignment_{next_assignment_id}_{file.filename}")
                    file_path = os.path.join('uploads', 'assignments')
                    os.makedirs(file_path, exist_ok=True)
                    file.save(os.path.join(file_path, filename))
                    uploaded_files.append(filename)
        
        assignment = {
            'id': next_assignment_id,
            'title': request.form['title'],
            'description': request.form['description'],
            'due_date': request.form['due_date'],
            'course_id': int(request.form['course_id']) if request.form.get('course_id') else None,
            'course': request.form['course'],
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
            'results_published': False
        }
        
        # Générer les groupes automatiquement si nécessaire
        if assignment['is_group_work'] and assignment['group_formation'] == 'auto':
            generate_automatic_groups(next_assignment_id, assignment['course_id'], assignment['group_size'])
        
        assignments.append(assignment)
        next_assignment_id += 1
        flash('Devoir créé avec succès')
        return redirect(url_for('teacher_assignments'))
    
    # Récupérer les cours assignés au professeur
    teacher_courses = []
    for course in admin_courses:
        if course['id'] in course_assignments and session['user'] in course_assignments[course['id']]:
            teacher_courses.append(course)
    
    return render_template('create_assignment.html', admin_courses=admin_courses, course_assignments=course_assignments)

@app.route('/download_assignment_file/<filename>')
def download_assignment_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return send_from_directory(os.path.join('uploads', 'assignments'), filename)

@app.route('/download_file/<filename>')
def download_file(filename):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Vérifier que le professeur a le droit de télécharger ce fichier
    if session['role'] == 'teacher':
        # Trouver la soumission correspondante
        submission = next((s for s in submissions if s['filename'] == filename), None)
        if submission:
            # Vérifier que le devoir appartient au professeur
            assignment = next((a for a in assignments if a['id'] == submission['assignment_id']), None)
            if assignment and assignment.get('teacher') == session['user']:
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Admin peut tout télécharger
    elif session['role'] == 'admin':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    flash('Accès non autorisé à ce fichier')
    return redirect(url_for('dashboard'))

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
        sub['correction'] = correction_results.get(sub['id'], {})
        sub['plagiarism'] = plagiarism_results.get(sub['id'], {})
    
    return render_template('assignment_results.html', assignment=assignment, submissions=assignment_submissions)

def simulate_plagiarism_check(content, submission_id):
    """Simulation de détection de plagiat"""
    import random
    similarity = random.randint(0, 30)  # Simulation
    sources = []
    if similarity > 20:
        sources = ['Document similaire 1', 'Source web détectée']
    
    plagiarism_results[submission_id] = {
        'similarity': similarity,
        'sources': sources,
        'status': 'suspect' if similarity > 25 else 'acceptable'
    }
    return plagiarism_results[submission_id]

def simulate_auto_correction(content, assignment, submission_id):
    """Simulation de correction automatique"""
    import random
    score = random.randint(60, 95)  # Simulation
    feedback = [
        'Bonne structure du code',
        'Logique correcte',
        'Quelques améliorations possibles'
    ]
    
    correction_results[submission_id] = {
        'score': score,
        'max_score': assignment.get('max_score', 100),
        'feedback': feedback,
        'auto_generated': True
    }
    return correction_results[submission_id]

def generate_automatic_groups(assignment_id, course_id, group_size):
    """Générer automatiquement des groupes pour un devoir"""
    if not course_id or course_id not in course_enrollments:
        return
    
    enrolled_students = course_enrollments[course_id]
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
    if course_id not in course_enrollments:
        return []
    
    students_data = []
    for student_username in course_enrollments[course_id]:
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
    if course_id:
        if course_id not in course_enrollments or session['user'] not in course_enrollments[course_id]:
            flash('Vous n\'êtes pas inscrit au cours de ce devoir')
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
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
    course_students = get_course_students(assignment['course_id']) if assignment.get('course_id') else []
    
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
    course_students = get_course_students(assignment['course_id']) if assignment.get('course_id') else []
    
    return render_template('manage_groups.html', assignment=assignment, groups_info=groups_info, course_students=course_students, student_groups=student_groups, users=users)

@app.route('/teacher/submissions')
def teacher_submissions():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_submissions = [s for s in submissions if any(a['id'] == s['assignment_id'] and a.get('teacher') == session['user'] for a in assignments)]
    return render_template('teacher_submissions.html', submissions=teacher_submissions, assignments=assignments, users=users)

@app.route('/teacher/students')
def teacher_students():
    if 'user' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    # Récupérer tous les étudiants des cours du professeur
    teacher_students = set()
    teacher_courses = []
    for course_id, teachers in course_assignments.items():
        if session['user'] in teachers:
            course = next((c for c in admin_courses if c['id'] == course_id), None)
            if course:
                teacher_courses.append(course)
                teacher_students.update(course_enrollments.get(course_id, []))
    
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
    enrolled_students = course_enrollments.get(assignment.get('course_id', 0), [])
    
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
            if course_id and (course_id not in course_enrollments or session['user'] not in course_enrollments[course_id]):
                continue  # Ignorer ce devoir si l'étudiant n'est pas inscrit
            
            # Vérifier si les résultats sont publiés
            results_available = is_results_published(assignment)
            
            grade_info = {
                'assignment': assignment,
                'submission': submission,
                'correction': correction_results.get(submission['id'], {}) if results_available else {},
                'plagiarism': plagiarism_results.get(submission['id'], {}) if results_available else {},
                'results_available': results_available
            }
            grades_data.append(grade_info)
    
    return render_template('student_grades.html', grades=grades_data)

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
        except:
            pass
    
    return False

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)