"""Assignments controllers using the shared transition state."""
from flask import Blueprint
from ai_service import rubric_from_form

def create_blueprint(namespace):
    blueprint = Blueprint('assignments', __name__)

    @blueprint.route('/submit/<int:assignment_id>', methods=['GET', 'POST'])
    def submit_assignment(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        course_id = assignment.get('course_id')
        if course_id and namespace['session']['user'] not in namespace['get_enrolled_students'](course_id):
            namespace['flash']("Vous n'êtes pas inscrit au cours de ce devoir")
            return namespace['redirect'](namespace['url_for']('dashboard'))
        if namespace['request'].method == 'POST':
            if 'code_content' in namespace['request'].form:
                try:
                    code = namespace['request'].form['code_content']
                    language = namespace['request'].form.get('language', 'python')
                    if not code.strip():
                        return namespace['jsonify']({'success': False, 'error': 'Le code ne peut pas être vide'})
                    executor = namespace['CodeExecutor']()
                    test_cases = assignment.get('test_cases', [])
                    execution_result = executor.execute_code(code, language, test_cases=test_cases)
                    if execution_result.get('error_code'):
                        return (namespace['jsonify'](success=False, error=execution_result['error'], execution_result=execution_result), 503 if execution_result.get('retryable') else 400)
                    max_score = assignment.get('max_score', 100)
                    if assignment.get('is_mixed_assignment'):
                        code_max_score = max_score // 2
                        remaining_score = max_score - code_max_score
                    else:
                        code_max_score = max_score
                        remaining_score = 0
                    has_compilation_error = bool(execution_result.get('compile_output', '').strip())
                    has_runtime_error = bool(execution_result.get('stderr', '').strip())
                    execution_success = execution_result.get('success', False)
                    status = execution_result.get('status', '')
                    is_system_error = 'non installé' in status or 'non trouvé' in status or 'non supporté' in status
                    if execution_success and (not has_compilation_error) and (not has_runtime_error):
                        code_score = code_max_score
                        if assignment.get('is_mixed_assignment'):
                            feedback = ['✅ Code compilé et exécuté avec succès', f'📝 Note code: {code_score}/{code_max_score}', f"⏳ En attente des fichiers d'analyse ({remaining_score} points)"]
                        else:
                            feedback = ['✅ Code compilé et exécuté avec succès', f'🎉 Note maximale obtenue: {code_score}/{code_max_score}']
                    elif is_system_error:
                        code_score = 0
                        feedback = [f'⚠️ {status}', "🔧 Contactez l'administrateur pour installer les outils nécessaires"]
                    else:
                        code_score = 0
                        feedback = []
                        if has_compilation_error:
                            feedback.append('❌ Erreurs de compilation')
                        if has_runtime_error:
                            feedback.append("❌ Erreurs d'exécution")
                        if not execution_success:
                            feedback.append("❌ Échec de l'exécution")
                        feedback.append('🔧 Corrigez les erreurs pour obtenir des points')
                    score = code_score
                    execution_result['score'] = score
                    execution_result['max_score'] = max_score
                    execution_result['feedback'] = feedback
                    file_info = namespace['save_code_submission'](namespace['session']['user'], assignment_id, code, language, execution_result)
                    correction = {'score': score, 'max_score': max_score, 'feedback': feedback, 'auto_generated': True}
                    plagiarism = {'similarity': 0, 'status': 'non_verifie', 'sources': []}
                    if assignment.get('plagiarism_check'):
                        plagiarism = namespace['check_plagiarism_local'](code, len(namespace['submissions']) + 1)
                    submission = {'id': max((item['id'] for item in namespace['submissions']), default=0) + 1, 'student': namespace['session']['user'], 'assignment_id': assignment_id, 'filename': file_info['code_file'], 'submitted_at': namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S'), 'results_available': True, 'code_submission': True, 'language': language, 'execution_result': execution_result, 'correction': correction, 'plagiarism': plagiarism}
                    namespace['correction_results'][submission['id']] = correction
                    namespace['submissions'].append(submission)
                    namespace['save_test_data']()
                    return namespace['jsonify']({'success': True, 'execution_result': execution_result, 'submission_id': submission['id'], 'score': score, 'max_score': max_score})
                except Exception as e:
                    return namespace['jsonify']({'success': False, 'error': f"Erreur lors de l'exécution: {str(e)}"})
            elif 'file' in namespace['request'].files:
                file = namespace['request'].files['file']
                if file.filename == '':
                    namespace['flash']('Aucun fichier sélectionné')
                    return namespace['redirect'](namespace['request'].url)
                if file:
                    filename = namespace['secure_filename'](file.filename)
                    timestamp = namespace['datetime'].now().strftime('%Y%m%d_%H%M%S')
                    filename = namespace['secure_filename'](f"{namespace['session']['user']}_{assignment_id}_{namespace['secrets'].token_hex(8)}_{filename}")
                    file.save(namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], filename))
                    submission = {'id': max((item['id'] for item in namespace['submissions']), default=0) + 1, 'student': namespace['session']['user'], 'assignment_id': assignment_id, 'filename': filename, 'submitted_at': namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S'), 'results_available': False}
                    namespace['submissions'].append(submission)
                    file_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], filename)
                    if assignment.get('plagiarism_check') or assignment.get('auto_correct'):
                        namespace['process_submission_async'](file_path, assignment, submission['id'])
                    namespace['save_test_data']()
                    namespace['flash']('Fichier soumis avec succès!')
                    return namespace['redirect'](namespace['url_for']('dashboard'))
        return namespace['render_template']('submit_code.html', assignment=assignment)

    @blueprint.route('/admin/assignments')
    def admin_assignments():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        return namespace['render_template']('admin_assignments.html', assignments=namespace['assignments'], users=namespace['users'])

    @blueprint.route('/admin/submissions')
    def admin_submissions():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        if 'correction_results' not in namespace:
            namespace['correction_results'] = {}
        return namespace['render_template']('admin_submissions.html', submissions=namespace['submissions'], assignments=namespace['assignments'], users=namespace['users'], correction_results=namespace['correction_results'], plagiarism_results=namespace['plagiarism_results'])

    @blueprint.route('/teacher/assignments')
    def teacher_assignments():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        teacher_assignments = [a for a in namespace['assignments'] if a.get('teacher') == namespace['session']['user']]
        return namespace['render_template']('teacher_assignments.html', assignments=teacher_assignments)

    @blueprint.route('/teacher/create_assignment', methods=['GET', 'POST'])
    def create_assignment():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['request'].method == 'POST':
            selected_course = namespace['request'].form.get('course_id', type=int)
            if selected_course is not None and namespace['session']['user'] not in namespace['get_assigned_teachers'](selected_course):
                return (namespace['jsonify'](error='Accès interdit au cours'), 403)
            requested_group_size = namespace['request'].form.get('group_size', '2') or '2'
            if not requested_group_size.isdigit() or not 1 <= int(requested_group_size) <= 100:
                return (namespace['jsonify'](error='Taille de groupe invalide'), 400)
            try:
                maximum = int(namespace['request'].form.get('max_score', 100))
                rubric = rubric_from_form(namespace['request'].form.get('rubric', ''), maximum)
            except (ValueError, TypeError, KeyError):
                return namespace['jsonify'](error='Grille invalide : les points doivent totaliser la note maximale.'), 400
            current_id = namespace['next_assignment_id']
            namespace['next_assignment_id'] += 1
            uploaded_files = []
            if 'files' in namespace['request'].files:
                files = namespace['request'].files.getlist('files')
                for file in files:
                    if file and file.filename != '':
                        filename = namespace['secure_filename'](f"assignment_{current_id}_{namespace['secrets'].token_hex(8)}_{file.filename}")
                        file_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'assignments')
                        namespace['os'].makedirs(file_path, exist_ok=True)
                        file.save(namespace['os'].path.join(file_path, filename))
                        uploaded_files.append(filename)
            test_cases = []
            if 'is_code_assignment' in namespace['request'].form:
                test_inputs = namespace['request'].form.getlist('test_input')
                test_outputs = namespace['request'].form.getlist('test_output')
                for i, (input_val, output_val) in enumerate(zip(test_inputs, test_outputs)):
                    if input_val.strip() or output_val.strip():
                        test_cases.append({'input': input_val, 'expected_output': output_val})
            course_id_raw = namespace['request'].form.get('course_id')
            course_id_value = None
            if course_id_raw:
                try:
                    course_id_value = int(course_id_raw)
                except ValueError:
                    course_id_value = None
            course_name = namespace['request'].form.get('course', '').strip()
            if course_id_value is not None and (not course_name):
                matched_course = next((c for c in namespace['admin_courses'] if c['id'] == course_id_value), None)
                if matched_course:
                    course_name = matched_course.get('name', '')
            assignment = {'id': current_id, 'title': namespace['request'].form.get('title', '').strip(), 'description': namespace['request'].form['description'], 'due_date': namespace['request'].form['due_date'], 'course_id': course_id_value, 'course': course_name, 'teacher': namespace['session']['user'], 'teacher_name': namespace['session']['name'], 'files': uploaded_files, 'auto_correct': 'auto_correct' in namespace['request'].form, 'plagiarism_check': 'plagiarism_check' in namespace['request'].form, 'max_score': int(namespace['request'].form.get('max_score', 100)), 'is_group_work': 'is_group_work' in namespace['request'].form, 'group_formation': namespace['request'].form.get('group_formation', 'manual'), 'group_size': int(namespace['request'].form.get('group_size', 2)) if namespace['request'].form.get('group_size') else 2, 'results_release_date': namespace['request'].form.get('results_release_date', ''), 'results_published': False, 'is_code_assignment': 'is_code_assignment' in namespace['request'].form, 'is_mixed_assignment': 'is_mixed_assignment' in namespace['request'].form, 'test_cases': test_cases}
            if assignment.get('is_group_work') and assignment.get('group_formation') == 'auto' and (assignment.get('course_id') is not None):
                namespace['generate_automatic_groups'](current_id, assignment.get('course_id'), assignment.get('group_size', 2))
            assignment['rubric'] = rubric
            namespace['assignments'].append(assignment)
            namespace['save_test_data']()
            namespace['flash']('Devoir créé avec succès')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        teacher_courses = []
        for course in namespace['admin_courses']:
            if namespace['session']['user'] in namespace['get_assigned_teachers'](course['id']):
                teacher_courses.append(course)
        preselected_course_id = namespace['request'].args.get('course_id', type=int)
        return namespace['render_template']('create_assignment.html', admin_courses=namespace['admin_courses'], course_assignments=namespace['course_assignments'], system_config=namespace['system_config'], teacher_courses=teacher_courses, preselected_course_id=preselected_course_id)

    @blueprint.route('/download_assignment_file/<filename>')
    def download_assignment_file(filename):
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        user = namespace['users'].get(namespace['session']['user'])
        allowed = any((filename in assignment.get('files', []) and (user and (user.get('role') == 'admin' or (user.get('role') == 'teacher' and assignment.get('teacher') == namespace['session']['user']) or (user.get('role') == 'student' and namespace['session']['user'] in namespace['get_enrolled_students'](assignment.get('course_id'))))) for assignment in namespace['assignments']))
        if not allowed:
            return (namespace['jsonify'](error='Accès interdit'), 403)
        filename = namespace['secure_filename'](filename)
        if not filename:
            namespace['flash']('Nom de fichier invalide')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        return namespace['send_from_directory'](namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'assignments'), filename, as_attachment=True)

    @blueprint.route('/download_file/<filename>')
    def download_file(filename):
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        filename = namespace['secure_filename'](filename)
        if not filename:
            namespace['flash']('Nom de fichier invalide')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        possible_paths = [namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], filename), namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'code_submissions', filename), namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'submissions', filename)]
        file_path = None
        for path in possible_paths:
            if namespace['os'].path.exists(path):
                file_path = path
                break
        if not file_path:
            namespace['flash']('Fichier introuvable')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        if namespace['session']['role'] == 'admin':
            return namespace['send_from_directory'](namespace['os'].path.dirname(file_path), namespace['os'].path.basename(file_path), as_attachment=True)
        if namespace['session']['role'] == 'teacher':
            submission = next((s for s in namespace['submissions'] if s['filename'] == filename), None)
            if submission:
                assignment = next((a for a in namespace['assignments'] if a['id'] == submission['assignment_id']), None)
                if assignment and assignment.get('teacher') == namespace['session']['user']:
                    return namespace['send_from_directory'](namespace['os'].path.dirname(file_path), namespace['os'].path.basename(file_path), as_attachment=True)
        if namespace['session']['role'] == 'student':
            submission = next((s for s in namespace['submissions'] if s['filename'] == filename and s['student'] == namespace['session']['user']), None)
            if submission:
                return namespace['send_from_directory'](namespace['os'].path.dirname(file_path), namespace['os'].path.basename(file_path), as_attachment=True)
        namespace['flash']('Accès non autorisé à ce fichier')
        return namespace['redirect'](namespace['url_for']('dashboard'))

    @blueprint.route('/teacher/submissions')
    def teacher_submissions():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        teacher_submissions = [s for s in namespace['submissions'] if any((a['id'] == s['assignment_id'] and a.get('teacher') == namespace['session']['user'] for a in namespace['assignments']))]
        return namespace['render_template']('teacher_submissions.html', submissions=teacher_submissions, assignments=namespace['assignments'], users=namespace['users'], correction_results=namespace['correction_results'], plagiarism_results=namespace['plagiarism_results'])

    @blueprint.route('/teacher/assignment_submissions/<int:assignment_id>')
    def assignment_submissions(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        assignment_submissions = [s for s in namespace['submissions'] if s['assignment_id'] == assignment_id]
        enrolled_students = namespace['get_enrolled_students'](assignment.get('course_id'))
        return namespace['render_template']('assignment_submissions.html', assignment=assignment, submissions=assignment_submissions, enrolled_students=enrolled_students, users=namespace['users'])

    @blueprint.route('/teacher/download_all_submissions/<int:assignment_id>')
    def download_all_submissions(assignment_id):
        """Télécharge toutes les soumissions d'un devoir en ZIP"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        assignment_submissions = [s for s in namespace['submissions'] if s['assignment_id'] == assignment_id]
        files_data = []
        for sub in assignment_submissions:
            sub_filename = sub.get('filename', '')
            if not sub_filename:
                continue
            file_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], sub_filename)
            if not namespace['os'].path.exists(file_path):
                for sub_dir in ('submissions', 'code_submissions'):
                    alt = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], sub_dir, sub_filename)
                    if namespace['os'].path.exists(alt):
                        file_path = alt
                        break
            if namespace['os'].path.exists(file_path):
                student_key = sub.get('student', 'unknown')
                student_name = namespace['users'].get(student_key, {}).get('name', student_key)
                archive_name = f'{student_name}_{sub_filename}'
                files_data.append((file_path, archive_name))
        if not files_data:
            namespace['flash']('Aucune soumission à télécharger')
            return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))
        assignment_title = assignment.get('title', f'devoir_{assignment_id}')
        zip_buffer = namespace['create_zip_archive'](files_data, f'soumissions_{assignment_title}')
        response = namespace['make_response'](zip_buffer.getvalue())
        response.headers['Content-Type'] = 'application/zip'
        response.headers['Content-Disposition'] = f'attachment; filename="soumissions_{assignment_title}.zip"'
        return response

    @blueprint.route('/upload_analysis_files/<int:assignment_id>', methods=['POST'])
    def upload_analysis_files(assignment_id):
        """Upload des fichiers d'analyse pour devoirs mixtes"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['jsonify']({'success': False, 'error': 'Non autorisé'})
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id), None)
        if not assignment or not assignment.get('is_mixed_assignment'):
            return namespace['jsonify']({'success': False, 'error': 'Devoir non trouvé ou pas un devoir mixte'})
        if namespace['session']['user'] not in namespace['get_enrolled_students'](assignment.get('course_id')):
            return (namespace['jsonify'](success=False, error='Accès interdit'), 403)
        if 'analysis_files' not in namespace['request'].files:
            return namespace['jsonify']({'success': False, 'error': 'Aucun fichier fourni'})
        files = namespace['request'].files.getlist('analysis_files')
        uploaded_files = []
        for file in files:
            if file and file.filename != '':
                filename = namespace['secure_filename'](file.filename)
                timestamp = namespace['datetime'].now().strftime('%Y%m%d_%H%M%S')
                filename = namespace['secure_filename'](f"analysis_{namespace['session']['user']}_{assignment_id}_{namespace['secrets'].token_hex(8)}_{filename}")
                analysis_folder = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'analysis')
                namespace['os'].makedirs(analysis_folder, exist_ok=True)
                file.save(namespace['os'].path.join(analysis_folder, filename))
                uploaded_files.append(filename)
        submission = next((s for s in namespace['submissions'] if s['student'] == namespace['session']['user'] and s['assignment_id'] == assignment_id), None)
        if submission:
            submission['analysis_files'] = uploaded_files
            submission['analysis_submitted_at'] = namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            submission = {'id': max((item['id'] for item in namespace['submissions']), default=0) + 1, 'student': namespace['session']['user'], 'assignment_id': assignment_id, 'analysis_files': uploaded_files, 'analysis_submitted_at': namespace['datetime'].now().strftime('%Y-%m-%d %H:%M:%S'), 'results_available': False, 'analysis_only': True}
            namespace['submissions'].append(submission)
        namespace['save_test_data']()
        return namespace['jsonify']({'success': True, 'message': f"{len(uploaded_files)} fichier(s) d'analyse téléversé(s) avec succès", 'files': uploaded_files})
    return blueprint
