"""Courses controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('courses', __name__)

    @blueprint.route('/teacher/course/<int:course_id>')
    def course_detail(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé à ce cours')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if not course:
            namespace['flash']('Cours non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        eligible_students = []
        for username, user in namespace['users'].items():
            if user['role'] == 'student':
                promotion_match = not course.get('promotions') or user.get('promotion') in course.get('promotions', [])
                faculte_match = not course.get('faculte') or user.get('faculte') == course.get('faculte')
                if promotion_match and faculte_match:
                    eligible_students.append({'username': username, 'data': user})
        enrolled_students = namespace['get_enrolled_students'](course_id)
        enrolled_data = [{'username': u, 'data': namespace['users'][u]} for u in enrolled_students if u in namespace['users']]
        return namespace['render_template']('course_detail.html', course=course, eligible_students=eligible_students, enrolled_students=enrolled_data)

    @blueprint.route('/teacher/enroll_student/<int:course_id>/<username>', methods=['POST'])
    def enroll_student(course_id, username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé à ce cours')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if course and username in namespace['users'] and (namespace['users'][username]['role'] == 'student'):
            enrolled_list = namespace['ensure_course_enrollments'](course_id)
            if username not in enrolled_list:
                enrolled_list.append(username)
                namespace['save_test_data']()
                namespace['flash'](f"Étudiant {namespace['users'][username].get('name', username)} inscrit au cours")
            else:
                namespace['flash']('Étudiant déjà inscrit à ce cours')
        else:
            namespace['flash']("Erreur lors de l'inscription")
        return namespace['redirect'](namespace['url_for']('course_detail', course_id=course_id))

    @blueprint.route('/teacher/unenroll_student/<int:course_id>/<username>', methods=['POST'])
    def unenroll_student(course_id, username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé à ce cours')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        enrolled_list = namespace['get_enrolled_students'](course_id) if course else []
        if course and username in enrolled_list:
            enrolled_list.remove(username)
            namespace['save_test_data']()
            namespace['flash'](f"Étudiant {namespace['users'][username].get('name', username)} désinscrit du cours")
        else:
            namespace['flash']('Erreur lors de la désinscription')
        return namespace['redirect'](namespace['url_for']('course_detail', course_id=course_id))

    @blueprint.route('/admin/courses')
    def admin_courses_view():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        return namespace['render_template']('admin_courses.html', courses=namespace['admin_courses'], course_assignments=namespace['course_assignments'], users=namespace['users'])

    @blueprint.route('/admin/add_course', methods=['GET', 'POST'])
    def admin_add_course():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['request'].method == 'POST':
            course = {'id': namespace['next_course_admin_id'], 'name': namespace['request'].form['name'], 'code': namespace['request'].form['code'], 'credits': int(namespace['request'].form['credits']), 'faculte': namespace['request'].form['faculte'], 'departement': namespace['request'].form['departement'], 'promotions': namespace['request'].form.getlist('promotions'), 'description': namespace['request'].form.get('description', '')}
            namespace['admin_courses'].append(course)
            namespace['ensure_course_assignment'](namespace['next_course_admin_id'])
            namespace['next_course_admin_id'] += 1
            namespace['save_test_data']()
            namespace['flash']('Cours ajouté avec succès')
            return namespace['redirect'](namespace['url_for']('admin_courses_view'))
        return namespace['render_template']('admin_add_course.html', config=namespace['system_config'])

    @blueprint.route('/admin/assign_teacher/<int:course_id>', methods=['GET', 'POST'])
    def assign_teacher_to_course(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if not course:
            namespace['flash']('Cours non trouvé')
            return namespace['redirect'](namespace['url_for']('admin_courses_view'))
        if namespace['request'].method == 'POST':
            teacher_username = namespace['request'].form['teacher']
            if teacher_username in namespace['users'] and namespace['users'][teacher_username]['role'] == 'teacher':
                assigned_list = namespace['ensure_course_assignment'](course_id)
                if teacher_username not in assigned_list:
                    assigned_list.append(teacher_username)
                    namespace['save_test_data']()
                    namespace['flash'](f'Professeur {teacher_username} assigné au cours')
                else:
                    namespace['flash']('Professeur déjà assigné à ce cours')
            return namespace['redirect'](namespace['url_for']('admin_courses_view'))
        teachers = {k: v for k, v in namespace['users'].items() if v['role'] == 'teacher'}
        key_used = namespace['_course_key'](course_id)
        assigned_teachers_raw = namespace['course_assignments'].get(key_used, [])
        valid_assigned_teachers = []
        removed_usernames = []
        for teacher_username in assigned_teachers_raw:
            teacher = namespace['users'].get(teacher_username)
            if teacher and teacher.get('role') == 'teacher':
                valid_assigned_teachers.append(teacher_username)
            else:
                removed_usernames.append(teacher_username)
        if removed_usernames:
            namespace['course_assignments'][key_used] = valid_assigned_teachers
            namespace['save_test_data']()
            namespace['flash']('Certaines assignations faisaient référence à des comptes supprimés et ont été nettoyées.', 'warning')
        assigned_teachers = namespace['course_assignments'].get(key_used, valid_assigned_teachers)
        return namespace['render_template']('assign_teacher.html', course=course, teachers=teachers, assigned_teachers=assigned_teachers)

    @blueprint.route('/admin/unassign_teacher/<int:course_id>/<teacher_username>', methods=['POST'])
    def unassign_teacher_from_course(course_id, teacher_username):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        assigned_list = namespace['get_assigned_teachers'](course_id)
        if teacher_username in assigned_list:
            assigned_list.remove(teacher_username)
            namespace['save_test_data']()
            namespace['flash'](f'Professeur {teacher_username} désassigné du cours')
        return namespace['redirect'](namespace['url_for']('admin_courses_view'))

    @blueprint.route('/teacher/my_assigned_courses')
    def teacher_assigned_courses():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        teacher_courses = []
        for course in namespace['admin_courses']:
            if namespace['session']['user'] in namespace['get_assigned_teachers'](course['id']):
                teacher_courses.append(course)
        return namespace['render_template']('teacher_assigned_courses.html', courses=teacher_courses)

    @blueprint.route('/teacher/courses')
    def teacher_courses():
        return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))

    @blueprint.route('/teacher/course_content/<int:course_id>')
    def course_content_view(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé à ce cours')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if not course:
            namespace['flash']('Cours non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if course_id not in namespace['course_content']:
            namespace['course_content'][course_id] = {'description': '', 'documents': []}
        if course_id not in namespace['course_chapters']:
            namespace['course_chapters'][course_id] = []
        return namespace['render_template']('course_content.html', course=course, content=namespace['course_content'][course_id], chapters=namespace['course_chapters'][course_id])

    @blueprint.route('/teacher/upload_syllabus/<int:course_id>', methods=['POST'])
    def upload_syllabus(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if 'syllabus' not in namespace['request'].files:
            namespace['flash']('Aucun fichier sélectionné')
            return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))
        file = namespace['request'].files['syllabus']
        allowed_extensions = ['.pdf', '.ppt', '.pptx']
        if file.filename == '' or not any((file.filename.lower().endswith(ext) for ext in allowed_extensions)):
            namespace['flash']('Veuillez sélectionner un fichier PDF, PPT ou PPTX')
            return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))
        filename = namespace['secure_filename'](f"syllabus_{course_id}_{namespace['secrets'].token_hex(8)}_{file.filename}")
        syllabus_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'syllabus')
        namespace['os'].makedirs(syllabus_path, exist_ok=True)
        file.save(namespace['os'].path.join(syllabus_path, filename))
        if course_id not in namespace['course_content']:
            namespace['course_content'][course_id] = {'description': '', 'documents': []}
        namespace['course_content'][course_id]['syllabus_file'] = filename
        namespace['flash']('Plan de cours téléversé avec succès')
        return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))

    @blueprint.route('/download_syllabus/<int:course_id>/<filename>')
    def download_syllabus(course_id, filename):
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['can_access_course'](namespace['session']['user'], namespace['users'].get(namespace['session']['user']), course_id, namespace['course_assignments'], namespace['course_enrollments']):
            return (namespace['jsonify'](error='Accès interdit'), 403)
        if namespace['course_content'].get(course_id, {}).get('syllabus_file') != filename:
            return (namespace['jsonify'](error='Fichier introuvable'), 404)
        filename = namespace['secure_filename'](filename)
        if not filename:
            namespace['flash']('Nom de fichier invalide')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        return namespace['send_from_directory'](namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'syllabus'), filename, as_attachment=True)

    @blueprint.route('/teacher/update_course_description/<int:course_id>', methods=['POST'])
    def update_course_description(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if course_id not in namespace['course_content']:
            namespace['course_content'][course_id] = {'description': '', 'documents': []}
        namespace['course_content'][course_id]['description'] = namespace['request'].form.get('description', '')
        namespace['flash']('Description mise à jour')
        return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))

    @blueprint.route('/teacher/add_chapter/<int:course_id>', methods=['POST'])
    def add_chapter(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        uploaded_documents = []
        if 'chapter_files' in namespace['request'].files:
            files = namespace['request'].files.getlist('chapter_files')
            for file in files:
                allowed_extensions = ['.pdf', '.ppt', '.pptx']
                if file and file.filename != '' and any((file.filename.lower().endswith(ext) for ext in allowed_extensions)):
                    filename = namespace['secure_filename'](f"chapter_{namespace['next_chapter_id']}_{namespace['secrets'].token_hex(8)}_{file.filename}")
                    doc_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'chapters')
                    namespace['os'].makedirs(doc_path, exist_ok=True)
                    file.save(namespace['os'].path.join(doc_path, filename))
                    uploaded_documents.append({'filename': filename, 'original_name': file.filename, 'uploaded_at': namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S')})
        chapter = {'id': namespace['next_chapter_id'], 'title': namespace['request'].form.get('title', ''), 'description': namespace['request'].form.get('description', ''), 'content': '', 'exercises': [], 'documents': uploaded_documents}
        if course_id not in namespace['course_chapters']:
            namespace['course_chapters'][course_id] = []
        namespace['course_chapters'][course_id].append(chapter)
        namespace['next_chapter_id'] += 1
        if uploaded_documents:
            namespace['flash'](f'Chapitre ajouté avec {len(uploaded_documents)} fichier(s) PDF')
        else:
            namespace['flash']('Chapitre ajouté avec succès')
        return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))

    @blueprint.route('/teacher/chapter/<int:course_id>/<int:chapter_id>')
    def chapter_detail(course_id, chapter_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        chapter = None
        if course_id in namespace['course_chapters']:
            chapter = next((ch for ch in namespace['course_chapters'][course_id] if ch['id'] == chapter_id), None)
        if not chapter:
            namespace['flash']('Chapitre non trouvé')
            return namespace['redirect'](namespace['url_for']('course_content_view', course_id=course_id))
        return namespace['render_template']('chapter_detail.html', course=course, chapter=chapter)

    @blueprint.route('/teacher/update_chapter/<int:course_id>/<int:chapter_id>', methods=['POST'])
    def update_chapter(course_id, chapter_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if course_id in namespace['course_chapters']:
            chapter = next((ch for ch in namespace['course_chapters'][course_id] if ch['id'] == chapter_id), None)
            if chapter:
                chapter['title'] = namespace['request'].form.get('title', chapter['title'])
                chapter['description'] = namespace['request'].form.get('description', chapter['description'])
                chapter['content'] = namespace['request'].form.get('content', chapter['content'])
                namespace['flash']('Chapitre mis à jour')
        return namespace['redirect'](namespace['url_for']('chapter_detail', course_id=course_id, chapter_id=chapter_id))

    @blueprint.route('/teacher/add_exercise/<int:course_id>/<int:chapter_id>', methods=['POST'])
    def add_exercise(course_id, chapter_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if course_id in namespace['course_chapters']:
            chapter = next((ch for ch in namespace['course_chapters'][course_id] if ch['id'] == chapter_id), None)
            if chapter:
                exercise = {'title': namespace['request'].form.get('exercise_title', ''), 'description': namespace['request'].form.get('exercise_description', ''), 'solution': namespace['request'].form.get('exercise_solution', '')}
                chapter['exercises'].append(exercise)
                namespace['flash']('Exercice ajouté')
        return namespace['redirect'](namespace['url_for']('chapter_detail', course_id=course_id, chapter_id=chapter_id))

    @blueprint.route('/teacher/upload_chapter_document/<int:course_id>/<int:chapter_id>', methods=['POST'])
    def upload_chapter_document(course_id, chapter_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_assigned_teachers'](course_id):
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_assigned_courses'))
        if 'document' not in namespace['request'].files:
            namespace['flash']('Aucun document sélectionné')
            return namespace['redirect'](namespace['url_for']('chapter_detail', course_id=course_id, chapter_id=chapter_id))
        file = namespace['request'].files['document']
        allowed_extensions = ['.pdf', '.ppt', '.pptx']
        if file.filename == '' or not any((file.filename.lower().endswith(ext) for ext in allowed_extensions)):
            namespace['flash']('Veuillez sélectionner un fichier PDF, PPT ou PPTX')
            return namespace['redirect'](namespace['url_for']('chapter_detail', course_id=course_id, chapter_id=chapter_id))
        filename = namespace['secure_filename'](f"chapter_{chapter_id}_{namespace['secrets'].token_hex(8)}_{file.filename}")
        doc_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'chapters')
        namespace['os'].makedirs(doc_path, exist_ok=True)
        file.save(namespace['os'].path.join(doc_path, filename))
        if course_id in namespace['course_chapters']:
            chapter = next((ch for ch in namespace['course_chapters'][course_id] if ch['id'] == chapter_id), None)
            if chapter:
                chapter['documents'].append({'filename': filename, 'original_name': file.filename, 'uploaded_at': namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S')})
                namespace['flash']('Document PDF ajouté au chapitre')
        return namespace['redirect'](namespace['url_for']('chapter_detail', course_id=course_id, chapter_id=chapter_id))

    @blueprint.route('/download_chapter_document/<filename>')
    def download_chapter_document(filename):
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        authorized = any((namespace['can_access_course'](namespace['session']['user'], namespace['users'].get(namespace['session']['user']), cid, namespace['course_assignments'], namespace['course_enrollments']) and any((doc.get('filename') == filename for chapter in chapters for doc in chapter.get('documents', []))) for cid, chapters in namespace['course_chapters'].items()))
        if not authorized:
            return (namespace['jsonify'](error='Accès interdit'), 403)
        filename = namespace['secure_filename'](filename)
        if not filename:
            namespace['flash']('Nom de fichier invalide')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        return namespace['send_from_directory'](namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'chapters'), filename, as_attachment=True)

    @blueprint.route('/student/courses')
    def student_courses():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['redirect'](namespace['url_for']('login'))
        enrolled_ids = {cid for cid, students in namespace['course_enrollments'].items() if namespace['session']['user'] in students}
        enrolled_courses = [c for c in namespace['admin_courses'] if namespace['_course_key'](c['id']) in enrolled_ids]
        return namespace['render_template']('student_courses.html', courses=enrolled_courses)

    @blueprint.route('/student/course/<int:course_id>')
    def student_course_detail(course_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['user'] not in namespace['get_enrolled_students'](course_id):
            namespace['flash']('Accès non autorisé à ce cours')
            return namespace['redirect'](namespace['url_for']('student_courses'))
        course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
        if not course:
            namespace['flash']('Cours non trouvé')
            return namespace['redirect'](namespace['url_for']('student_courses'))
        content = namespace['course_content'].get(course_id, {'description': '', 'documents': []})
        chapters = namespace['course_chapters'].get(course_id, [])
        return namespace['render_template']('student_course_detail.html', course=course, content=content, chapters=chapters)
    return blueprint
