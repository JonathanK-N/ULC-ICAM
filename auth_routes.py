"""Authentication routes with compatibility endpoint names."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from werkzeug.routing import Rule
from datetime import datetime


def create_auth_blueprint(namespace):
    blueprint = Blueprint('auth', __name__)

    @blueprint.route('/login')
    def login():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
        return render_template('login_select.html')


    @blueprint.route('/login/student', methods=['GET', 'POST'])
    def student_login():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
        if request.method == 'POST':
            identifier = request.form['identifier']  # CIP ou email
            password = request.form['password']
        
            # Chercher l'utilisateur par CIP ou email
            user_found = None
            username_found = None
        
            for username, user_data in users.items():
                if (user_data['role'] == 'student' and
                        (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                    if not user_data.get('disabled') and _verify_password(password, user_data['password']):
                        user_found = user_data
                        username_found = username
                        break

            if user_found:
                session.clear()
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


    @blueprint.route('/login/teacher', methods=['GET', 'POST'])
    def teacher_login():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
        if request.method == 'POST':
            identifier = request.form['identifier']  # CIP ou email
            password = request.form['password']
        
            # Chercher l'utilisateur par CIP ou email
            user_found = None
            username_found = None
        
            for username, user_data in users.items():
                if (user_data['role'] == 'teacher' and
                        (user_data.get('cip') == identifier or user_data.get('email') == identifier)):
                    if not user_data.get('disabled') and _verify_password(password, user_data['password']):
                        user_found = user_data
                        username_found = username
                        break

            if user_found:
                session.clear()
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


    @blueprint.route('/login/admin', methods=['GET', 'POST'])
    def admin_login():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
        
            if (username in users and not users[username].get('disabled') and
                    _verify_password(password, users[username]['password']) and
                    users[username]['role'] == 'admin'):
                session.clear()
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


    @blueprint.route('/logout')
    def logout():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
        session.clear()
        return redirect(url_for('index'))


    @blueprint.route('/change_password', methods=['GET', 'POST'])
    def change_password():
        users = namespace['users']
        logger = namespace['logger']
        _verify_password = namespace['_verify_password']
        save_test_data = namespace['save_test_data']
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

    return blueprint


def register_auth(app, namespace):
    blueprint = create_auth_blueprint(namespace)
    app.register_blueprint(blueprint)
    for rule in list(app.url_map.iter_rules()):
        if rule.endpoint.startswith('auth.'):
            legacy = rule.endpoint.split('.', 1)[1]
            app.url_map.add(Rule(rule.rule, endpoint=legacy, methods=rule.methods, build_only=True))
            app.view_functions[legacy] = app.view_functions[rule.endpoint]
