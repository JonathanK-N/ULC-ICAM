"""Admin controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('admin', __name__)

    @blueprint.route('/admin/users')
    def admin_users():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        return namespace['render_template']('admin_users.html', users=namespace['users'])

    @blueprint.route('/admin/add_student', methods=['GET', 'POST'])
    def add_student():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['request'].method == 'POST':
            temp_password = namespace['generate_temp_password']()
            username = namespace['request'].form['username'].strip()
            if username in namespace['users']:
                namespace['flash']("Nom d'utilisateur déjà existant")
            else:
                student_data = {'username': username, 'password': namespace['generate_password_hash'](temp_password), 'role': 'student', 'must_change_password': True, 'cip': namespace['request'].form['cip'].strip(), 'nom': namespace['request'].form['nom'].strip(), 'postnom': namespace['request'].form['postnom'].strip(), 'prenom': namespace['request'].form['prenom'].strip(), 'sexe': namespace['request'].form['sexe'], 'date_naissance': namespace['request'].form['date_naissance'], 'promotion': namespace['request'].form['promotion'], 'faculte': namespace['request'].form['faculte'], 'departement': namespace['request'].form['departement'], 'telephone': namespace['request'].form['telephone'].strip(), 'email': namespace['request'].form['email'].strip().lower(), 'adresse': namespace['request'].form['adresse'].strip()}
                student_data['name'] = f"{student_data['prenom']} {student_data['nom']}"
                namespace['users'][username] = student_data
                namespace['save_test_data']()
                namespace['logger'].info(f'Nouvel étudiant créé: {username}')
                return namespace['render_template']('account_credentials.html', credentials=[(username, temp_password)])
        return namespace['render_template']('add_student.html', system_config=namespace['system_config'])

    @blueprint.route('/admin/add_teacher', methods=['GET', 'POST'])
    def add_teacher():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['request'].method == 'POST':
            temp_password = namespace['generate_temp_password']()
            username = namespace['request'].form['username'].strip()
            if username in namespace['users']:
                namespace['flash']("Nom d'utilisateur déjà existant")
            else:
                teacher_data = {'username': username, 'password': namespace['generate_password_hash'](temp_password), 'role': 'teacher', 'must_change_password': True, 'cip': namespace['request'].form['cip'].strip(), 'nom': namespace['request'].form['nom'].strip(), 'postnom': namespace['request'].form['postnom'].strip(), 'prenom': namespace['request'].form['prenom'].strip(), 'sexe': namespace['request'].form['sexe'], 'date_naissance': namespace['request'].form['date_naissance'], 'cours_dispenses': namespace['request'].form['cours_dispenses'].strip(), 'departement': namespace['request'].form['departement'], 'grade': namespace['request'].form['grade'], 'telephone': namespace['request'].form['telephone'].strip(), 'email': namespace['request'].form['email'].strip().lower(), 'bureau': namespace['request'].form['bureau'].strip()}
                teacher_data['name'] = f"{teacher_data['grade']} {teacher_data['prenom']} {teacher_data['nom']}"
                namespace['users'][username] = teacher_data
                namespace['save_test_data']()
                namespace['logger'].info(f'Nouvel enseignant créé: {username}')
                return namespace['render_template']('account_credentials.html', credentials=[(username, temp_password)])
        return namespace['render_template']('add_teacher.html', system_config=namespace['system_config'])

    @blueprint.route('/admin/import_csv', methods=['GET', 'POST'])
    def import_csv():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['request'].method == 'POST':
            if 'file' not in namespace['request'].files:
                namespace['flash']('Aucun fichier sélectionné')
                return namespace['redirect'](namespace['request'].url)
            file = namespace['request'].files['file']
            if file.filename == '':
                namespace['flash']('Aucun fichier sélectionné')
                return namespace['redirect'](namespace['request'].url)
            if file and file.filename.endswith('.csv'):
                import csv
                import io
                stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
                csv_input = csv.reader(stream)
                header = next(csv_input)
                added_count = 0
                credentials = []
                errors = []
                for row_num, row in enumerate(csv_input, start=2):
                    if len(row) < 2:
                        continue
                    try:
                        username = row[0].strip()
                        role = row[1].strip()
                        if not username or role not in ['student', 'teacher']:
                            errors.append(f"Ligne {row_num}: Nom d'utilisateur ou rôle invalide")
                            continue
                        if username in namespace['users']:
                            errors.append(f'Ligne {row_num}: Utilisateur {username} existe déjà')
                            continue
                        temp_password = namespace['generate_temp_password']()
                        if role == 'student' and len(row) >= 13:
                            user_data = {'username': username, 'password': namespace['generate_password_hash'](temp_password), 'role': 'student', 'must_change_password': True, 'cip': row[2].strip(), 'nom': row[3].strip(), 'postnom': row[4].strip(), 'prenom': row[5].strip(), 'sexe': row[6].strip(), 'date_naissance': row[7].strip(), 'promotion': row[8].strip(), 'faculte': row[9].strip(), 'telephone': row[10].strip(), 'email': row[11].strip().lower(), 'adresse': row[12].strip()}
                            user_data['name'] = f"{user_data['prenom']} {user_data['nom']}"
                        elif role == 'teacher' and len(row) >= 14:
                            user_data = {'username': username, 'password': namespace['generate_password_hash'](temp_password), 'role': 'teacher', 'must_change_password': True, 'cip': row[2].strip(), 'nom': row[3].strip(), 'postnom': row[4].strip(), 'prenom': row[5].strip(), 'sexe': row[6].strip(), 'date_naissance': row[7].strip(), 'cours_dispenses': row[8].strip(), 'departement': row[9].strip(), 'grade': row[10].strip(), 'telephone': row[11].strip(), 'email': row[12].strip().lower(), 'bureau': row[13].strip()}
                            user_data['name'] = f"{user_data['grade']} {user_data['prenom']} {user_data['nom']}"
                        else:
                            errors.append(f'Ligne {row_num}: Nombre de colonnes insuffisant pour le rôle {role}')
                            continue
                        namespace['users'][username] = user_data
                        credentials.append((username, temp_password))
                        added_count += 1
                    except Exception as e:
                        errors.append(f'Ligne {row_num}: Erreur de traitement - {str(e)}')
                namespace['save_test_data']()
                if added_count > 0:
                    namespace['flash'](f'{added_count} utilisateurs importés avec succès')
                if errors:
                    namespace['flash'](f"Erreurs rencontrées: {'; '.join(errors[:5])}", 'warning')
                    if len(errors) > 5:
                        namespace['flash'](f'... et {len(errors) - 5} autres erreurs', 'warning')
                if credentials:
                    return namespace['render_template']('account_credentials.html', credentials=credentials)
                return namespace['redirect'](namespace['url_for']('admin_users'))
            else:
                namespace['flash']('Format de fichier non valide. Utilisez un fichier CSV.')
        return namespace['render_template']('import_csv.html')

    @blueprint.route('/admin/delete_user/<username>', methods=['POST'])
    def delete_user(username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if username in namespace['users']:
            if username == namespace['session']['user'] or namespace['users'][username]['role'] == 'admin':
                return (namespace['jsonify'](error='Compte administrateur protégé'), 409)
            referenced = any((a.get('teacher') == username for a in namespace['assignments'])) or any((s.get('student') == username for s in namespace['submissions'])) or any((username in names for names in list(namespace['course_assignments'].values()) + list(namespace['course_enrollments'].values())))
            if referenced:
                namespace['users'][username]['disabled'] = True
                namespace['flash'](f'Compte {username} désactivé ; historique académique conservé')
            else:
                del namespace['users'][username]
                namespace['flash'](f'Utilisateur {username} supprimé')
            namespace['push_subscriptions'][:] = [item for item in namespace['push_subscriptions'] if item['username'] != username]
            namespace['save_test_data']()
        return namespace['redirect'](namespace['url_for']('admin_users'))

    @blueprint.route('/admin/user_profile/<username>')
    def user_profile(username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if username not in namespace['users']:
            namespace['flash']('Utilisateur non trouvé')
            return namespace['redirect'](namespace['url_for']('admin_users'))
        user_data = namespace['users'][username]
        return namespace['render_template']('user_profile.html', username=username, user_data=user_data)

    @blueprint.route('/admin/upload_photo/<username>', methods=['POST'])
    def upload_photo(username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if 'photo' not in namespace['request'].files:
            namespace['flash']('Aucune photo sélectionnée')
            return namespace['redirect'](namespace['url_for']('user_profile', username=username))
        file = namespace['request'].files['photo']
        if file.filename == '':
            namespace['flash']('Aucune photo sélectionnée')
            return namespace['redirect'](namespace['url_for']('user_profile', username=username))
        if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            filename = namespace['secure_filename'](f"{username}_photo.{file.filename.split('.')[-1]}")
            photo_path = namespace['os'].path.join('app', 'static', 'photos')
            namespace['os'].makedirs(photo_path, exist_ok=True)
            file.save(namespace['os'].path.join(photo_path, filename))
            namespace['users'][username]['photo'] = filename
            namespace['flash']('Photo mise à jour avec succès')
        else:
            namespace['flash']('Format de fichier non valide. Utilisez PNG, JPG, JPEG ou GIF.')
        return namespace['redirect'](namespace['url_for']('user_profile', username=username))

    @blueprint.route('/admin/edit_user/<username>', methods=['GET', 'POST'])
    def edit_user(username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if username not in namespace['users']:
            namespace['flash']('Utilisateur non trouvé')
            return namespace['redirect'](namespace['url_for']('admin_users'))
        if namespace['request'].method == 'POST':
            user_data = namespace['users'][username]
            if user_data['role'] == 'student':
                user_data.update({'cip': namespace['request'].form.get('cip', user_data.get('cip', '')), 'nom': namespace['request'].form.get('nom', user_data.get('nom', '')), 'postnom': namespace['request'].form.get('postnom', user_data.get('postnom', '')), 'prenom': namespace['request'].form.get('prenom', user_data.get('prenom', '')), 'sexe': namespace['request'].form.get('sexe', user_data.get('sexe', '')), 'date_naissance': namespace['request'].form.get('date_naissance', user_data.get('date_naissance', '')), 'promotion': namespace['request'].form.get('promotion', user_data.get('promotion', '')), 'faculte': namespace['request'].form.get('faculte', user_data.get('faculte', '')), 'departement': namespace['request'].form.get('departement', user_data.get('departement', '')), 'telephone': namespace['request'].form.get('telephone', user_data.get('telephone', '')), 'email': namespace['request'].form.get('email', user_data.get('email', '')), 'adresse': namespace['request'].form.get('adresse', user_data.get('adresse', ''))})
            elif user_data['role'] == 'teacher':
                user_data.update({'cip': namespace['request'].form.get('cip', user_data.get('cip', '')), 'nom': namespace['request'].form.get('nom', user_data.get('nom', '')), 'postnom': namespace['request'].form.get('postnom', user_data.get('postnom', '')), 'prenom': namespace['request'].form.get('prenom', user_data.get('prenom', '')), 'sexe': namespace['request'].form.get('sexe', user_data.get('sexe', '')), 'date_naissance': namespace['request'].form.get('date_naissance', user_data.get('date_naissance', '')), 'cours_dispenses': namespace['request'].form.get('cours_dispenses', user_data.get('cours_dispenses', '')), 'departement': namespace['request'].form.get('departement', user_data.get('departement', '')), 'grade': namespace['request'].form.get('grade', user_data.get('grade', '')), 'telephone': namespace['request'].form.get('telephone', user_data.get('telephone', '')), 'email': namespace['request'].form.get('email', user_data.get('email', '')), 'bureau': namespace['request'].form.get('bureau', user_data.get('bureau', ''))})
            elif user_data['role'] == 'admin':
                user_data.update({'nom': namespace['request'].form.get('nom', user_data.get('nom', '')), 'postnom': namespace['request'].form.get('postnom', user_data.get('postnom', '')), 'prenom': namespace['request'].form.get('prenom', user_data.get('prenom', '')), 'sexe': namespace['request'].form.get('sexe', user_data.get('sexe', '')), 'date_naissance': namespace['request'].form.get('date_naissance', user_data.get('date_naissance', '')), 'telephone': namespace['request'].form.get('telephone', user_data.get('telephone', '')), 'email': namespace['request'].form.get('email', user_data.get('email', '')), 'adresse': namespace['request'].form.get('adresse', user_data.get('adresse', '')), 'fonction': namespace['request'].form.get('fonction', user_data.get('fonction', 'Administrateur Système'))})
            if user_data['role'] == 'admin':
                user_data['name'] = f"{user_data.get('prenom', '')} {user_data.get('nom', '')}" if user_data.get('prenom') and user_data.get('nom') else user_data.get('name', 'Administrateur ULC-ICAM')
            else:
                user_data['name'] = f"{user_data.get('prenom', '')} {user_data.get('nom', '')}"
            namespace['save_test_data']()
            namespace['flash']('Profil mis à jour avec succès')
            return namespace['redirect'](namespace['url_for']('user_profile', username=username))
        return namespace['render_template']('edit_user.html', username=username, user_data=namespace['users'][username], system_config=namespace['system_config'])

    @blueprint.route('/admin/system_config')
    def system_config_view():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        return namespace['render_template']('admin_config_management.html', config=namespace['system_config'])

    @blueprint.route('/admin/config/<config_type>', methods=['GET', 'POST'])
    def manage_config(config_type):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if config_type not in namespace['system_config']:
            namespace['flash']('Configuration non trouvée')
            return namespace['redirect'](namespace['url_for']('system_config_view'))
        if namespace['request'].method == 'POST':
            action = namespace['request'].form.get('action')
            if action == 'add':
                new_item = namespace['request'].form.get('new_item')
                if new_item and new_item not in namespace['system_config'][config_type]:
                    namespace['system_config'][config_type].append(new_item)
                    namespace['flash'](f'{new_item} ajouté avec succès')
            elif action == 'delete':
                item_to_delete = namespace['request'].form.get('item')
                protected_items = {'facultes': ['Faculté des Sciences et Technologies (ULC-ICAM)'], 'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'], 'departements': [], 'grades': []}
                if item_to_delete in protected_items.get(config_type, []):
                    namespace['flash'](f'{item_to_delete} ne peut pas être supprimé (élément protégé)', 'error')
                elif item_to_delete in namespace['system_config'][config_type]:
                    namespace['system_config'][config_type].remove(item_to_delete)
                    namespace['flash'](f'{item_to_delete} supprimé avec succès')
                else:
                    namespace['flash'](f'{item_to_delete} non trouvé', 'error')
            return namespace['redirect'](namespace['url_for']('manage_config', config_type=config_type))
        return namespace['render_template']('manage_config.html', config_type=config_type, items=namespace['system_config'][config_type])

    @blueprint.route('/admin/students')
    def admin_students():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        students = {k: v for k, v in namespace['users'].items() if v['role'] == 'student'}
        return namespace['render_template']('admin_students.html', students=students)

    @blueprint.route('/admin/teachers')
    def admin_teachers():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        teachers = {k: v for k, v in namespace['users'].items() if v['role'] == 'teacher'}
        return namespace['render_template']('admin_teachers.html', teachers=teachers, course_assignments=namespace['course_assignments'], admin_courses=namespace['admin_courses'])

    @blueprint.route('/admin/seed', methods=['GET', 'POST'])
    def admin_seed():
        """Injecte les données de démonstration (une seule fois, admin uniquement)."""
        if namespace['os'].environ.get('FLASK_ENV') == 'production' or namespace['relational_repository'] is not None:
            return (namespace['jsonify'](error='Données de démonstration interdites en production'), 403)
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        already_seeded = len(namespace['users']) > 1 or len(namespace['admin_courses']) > 0 or len(namespace['assignments']) > 0
        if namespace['request'].method == 'GET':
            return namespace['render_template_string']('\n<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">\n<title>Seed données démo</title>\n<style>\n  body { font-family: Arial, sans-serif; max-width: 600px; margin: 80px auto; padding: 20px; }\n  .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 6px; margin-bottom: 20px; }\n  .danger  { background: #f8d7da; border: 1px solid #dc3545; padding: 15px; border-radius: 6px; margin-bottom: 20px; }\n  .btn { padding: 10px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }\n  .btn-primary { background: #0d6efd; color: white; }\n  .btn-secondary { background: #6c757d; color: white; text-decoration: none; padding: 10px 24px; border-radius: 4px; }\n</style></head><body>\n<h2>Injection données de démonstration</h2>\n{% if already_seeded %}\n<div class="danger">\n  <strong>Attention :</strong> Des données existent déjà ({{ nb_users }} utilisateurs, {{ nb_courses }} cours).\n  Cliquer sur "Confirmer" va <strong>écraser toutes les données actuelles</strong>.\n</div>\n{% else %}\n<div class="warning">\n  Cela va créer : 1 admin, 5 professeurs, 20 étudiants, 8 cours, 10 devoirs, 29 soumissions.\n</div>\n{% endif %}\n<form method="POST">\n  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">\n  <button type="submit" class="btn btn-primary">Confirmer l\'injection</button>\n  <a href="{{ url_for(\'admin_users\') }}" class="btn-secondary" style="margin-left:10px;">Annuler</a>\n</form>\n</body></html>\n        ', already_seeded=already_seeded, nb_users=len(namespace['users']), nb_courses=len(namespace['admin_courses']))
        try:
            import importlib.util, sys as _sys
            seed_path = namespace['os'].path.join(namespace['os'].path.dirname(namespace['os'].path.abspath(__file__)), 'seed_data.py')
            if not namespace['os'].path.exists(seed_path):
                namespace['flash']('Fichier seed_data.py introuvable.', 'danger')
                return namespace['redirect'](namespace['url_for']('admin_users'))
            spec = importlib.util.spec_from_file_location('seed_data', seed_path)
            seed_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(seed_module)
            with namespace['_data_lock']:
                with open(namespace['DATA_FILE'], 'r', encoding='utf-8') as f:
                    fresh = namespace['json'].load(f)
                namespace['users'].clear()
                namespace['users'].update(fresh.get('users', {}))
                namespace['admin_courses'].clear()
                namespace['admin_courses'].extend(fresh.get('admin_courses', []))
                namespace['course_assignments'].clear()
                namespace['course_assignments'].update(fresh.get('course_assignments', {}))
                namespace['course_enrollments'].clear()
                namespace['course_enrollments'].update(fresh.get('course_enrollments', {}))
                namespace['assignments'].clear()
                namespace['assignments'].extend(fresh.get('assignments', []))
                namespace['submissions'].clear()
                namespace['submissions'].extend(fresh.get('submissions', []))
                namespace['next_course_admin_id'] = fresh.get('next_course_admin_id', len(namespace['admin_courses']) + 1)
                namespace['next_assignment_id'] = fresh.get('next_assignment_id', len(namespace['assignments']) + 1)
                namespace['course_content'].clear()
                namespace['course_content'].update({int(k): v for k, v in fresh.get('course_content', {}).items()})
                namespace['course_chapters'].clear()
                namespace['course_chapters'].update({int(k): v for k, v in fresh.get('course_chapters', {}).items()})
                namespace['next_chapter_id'] = fresh.get('next_chapter_id', 1)
            namespace['flash'](f"Données de démo injectées avec succès : {len(namespace['users'])} utilisateurs, {len(namespace['admin_courses'])} cours, {len(namespace['assignments'])} devoirs, {len(namespace['submissions'])} soumissions.", 'success')
            namespace['app'].logger.info('Seed exécuté par %s', namespace['session'].get('user'))
        except Exception as e:
            namespace['app'].logger.error('Erreur seed: %s', e, exc_info=True)
            namespace['flash'](f"Erreur lors de l'injection : {e}", 'danger')
        return namespace['redirect'](namespace['url_for']('admin_users'))
    return blueprint
