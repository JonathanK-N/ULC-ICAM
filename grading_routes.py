"""Grading controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('grading', __name__)

    @blueprint.route('/download_correction/<filename>')
    def download_correction_file(filename):
        """Permet de télécharger un fichier de correction"""
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        submission = next((s for s in namespace['submissions'] if s.get('correction', {}).get('feedback_file') == filename), None)
        if not submission:
            namespace['flash']('Fichier introuvable')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        user_role = namespace['session'].get('role')
        if user_role == 'student' and submission.get('student') != namespace['session'].get('user'):
            namespace['flash']('Accès non autorisé à ce fichier')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        if user_role == 'teacher':
            assignment = next((a for a in namespace['assignments'] if a['id'] == submission['assignment_id']), None)
            if not assignment or assignment.get('teacher') != namespace['session'].get('user'):
                namespace['flash']('Accès non autorisé à ce fichier')
                return namespace['redirect'](namespace['url_for']('dashboard'))
        filename = namespace['secure_filename'](filename)
        if not filename:
            namespace['flash']('Nom de fichier invalide')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        corrections_folder = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'corrections')
        return namespace['send_from_directory'](corrections_folder, filename, as_attachment=True)

    @blueprint.route('/teacher/assignment_results/<int:assignment_id>')
    def assignment_results(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        assignment_submissions = [s for s in namespace['submissions'] if s.get('assignment_id') == assignment_id]
        for sub in assignment_submissions:
            if not sub.get('correction') and sub['id'] in namespace['correction_results']:
                sub['correction'] = namespace['correction_results'][sub['id']]
            if not sub.get('plagiarism') and sub['id'] in namespace['plagiarism_results']:
                sub['plagiarism'] = namespace['plagiarism_results'][sub['id']]
            if not sub.get('correction'):
                sub['correction'] = {'score': 0, 'max_score': assignment.get('max_score', 100), 'feedback': [], 'auto_generated': False}
            if not sub.get('plagiarism'):
                sub['plagiarism'] = {'similarity': 0, 'status': 'non_verifie', 'sources': []}
        return namespace['render_template']('assignment_results.html', assignment=assignment, submissions=assignment_submissions)

    @blueprint.route('/teacher/grade_submission/<int:submission_id>', methods=['GET', 'POST'])
    def grade_submission(submission_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        submission = next((s for s in namespace['submissions'] if s['id'] == submission_id), None)
        if not submission:
            namespace['flash']('Soumission non trouvée')
            return namespace['redirect'](namespace['url_for']('teacher_submissions'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == submission['assignment_id']), None)
        if not assignment or assignment.get('teacher') != namespace['session']['user']:
            namespace['flash']('Accès non autorisé')
            return namespace['redirect'](namespace['url_for']('teacher_submissions'))
        if namespace['request'].method == 'POST':
            score = namespace['request'].form.get('score', type=float)
            max_score = namespace['request'].form.get('max_score', type=float) or assignment.get('max_score', 100)
            import math
            if score is None or not math.isfinite(score) or (not math.isfinite(max_score)) or (max_score <= 0) or (not 0 <= score <= max_score):
                return (namespace['jsonify'](error='Note invalide'), 400)
            feedback_text = namespace['request'].form.get('feedback', '')
            feedback_list = [line.strip() for line in feedback_text.splitlines() if line.strip()]
            feedback_file = namespace['request'].files.get('feedback_file')
            filename = namespace['correction_results'].get(submission_id, {}).get('feedback_file')
            if feedback_file and feedback_file.filename:
                corrections_folder = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'corrections')
                namespace['os'].makedirs(corrections_folder, exist_ok=True)
                filename = namespace['secure_filename'](f"correction_{submission_id}_{namespace['secrets'].token_hex(8)}_{feedback_file.filename}")
                feedback_file.save(namespace['os'].path.join(corrections_folder, filename))
            correction = {'score': score, 'max_score': max_score, 'feedback': feedback_list, 'feedback_file': filename, 'auto_generated': False, 'review_status': 'approved'}
            namespace['correction_results'][submission_id] = correction
            submission['correction'] = correction
            if 'publish_now' in namespace['request'].form:
                submission['results_available'] = True
            namespace['save_test_data']()
            namespace['flash']('Soumission corrigée')
            return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=submission['assignment_id']))
        correction = namespace['correction_results'].get(submission_id)
        return namespace['render_template']('grade_submission.html', submission=submission, assignment=assignment, correction=correction)

    @blueprint.route('/teacher/publish_submissions/<int:assignment_id>', methods=['POST'])
    def publish_submissions(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['owns_assignment'](namespace['session']['user'], namespace['assignments'], assignment_id):
            return (namespace['jsonify'](error='Accès interdit'), 403)
        if any((namespace['requires_review'](sub.get('correction', namespace['correction_results'].get(sub['id'], {}))) for sub in namespace['submissions'] if sub.get('assignment_id') == assignment_id)):
            return (namespace['jsonify'](error='Validez les corrections proposées avant publication'), 409)
        for sub in namespace['submissions']:
            if sub.get('assignment_id') == assignment_id:
                sub['results_available'] = True
        namespace['save_test_data']()
        namespace['flash']('Notes publiées pour toutes les soumissions')
        return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))

    @blueprint.route('/teacher/unpublish_submissions/<int:assignment_id>', methods=['POST'])
    def unpublish_submissions(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['owns_assignment'](namespace['session']['user'], namespace['assignments'], assignment_id):
            return (namespace['jsonify'](error='Accès interdit'), 403)
        for sub in namespace['submissions']:
            if sub.get('assignment_id') == assignment_id:
                sub['results_available'] = False
        namespace['save_test_data']()
        namespace['flash']('Notes masquées pour toutes les soumissions')
        return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))

    @blueprint.route('/student/my_grades')
    def student_grades():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['redirect'](namespace['url_for']('login'))
        student_submissions = [s for s in namespace['submissions'] if s['student'] == namespace['session']['user']]
        grades_data = []
        for submission in student_submissions:
            assignment = next((a for a in namespace['assignments'] if a['id'] == submission['assignment_id']), None)
            if assignment:
                course_id = assignment.get('course_id')
                if course_id and namespace['session']['user'] not in namespace['get_enrolled_students'](course_id):
                    continue
                results_available = submission.get('results_available') or namespace['is_results_published'](assignment)
                correction = submission.get('correction', {})
                if namespace['requires_review'](correction or namespace['correction_results'].get(submission['id'], {})):
                    results_available = False
                plagiarism = submission.get('plagiarism', {})
                if results_available:
                    if not correction and submission['id'] in namespace['correction_results']:
                        correction = namespace['correction_results'][submission['id']]
                        submission['correction'] = correction
                    if not plagiarism and submission['id'] in namespace['plagiarism_results']:
                        plagiarism = namespace['plagiarism_results'][submission['id']]
                        submission['plagiarism'] = plagiarism
                else:
                    correction = {}
                    plagiarism = {}
                grade_info = {'assignment': assignment, 'submission': submission, 'correction': correction, 'plagiarism': plagiarism, 'results_available': results_available}
                grades_data.append(grade_info)
        return namespace['render_template']('student_grades.html', grades=grades_data)

    @blueprint.route('/teacher/publish_results/<int:assignment_id>', methods=['POST'])
    def publish_results(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['owns_assignment'](namespace['session']['user'], namespace['assignments'], assignment_id):
            return (namespace['jsonify'](error='Accès interdit'), 403)
        if any((namespace['requires_review'](sub.get('correction', namespace['correction_results'].get(sub['id'], {}))) for sub in namespace['submissions'] if sub.get('assignment_id') == assignment_id)):
            return (namespace['jsonify'](error='Validez les corrections proposées avant publication'), 409)
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if assignment:
            assignment['results_published'] = True
            namespace['flash']('Résultats publiés avec succès')
        else:
            namespace['flash']('Devoir non trouvé')
        namespace['save_test_data']()
        return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))

    @blueprint.route('/teacher/unpublish_results/<int:assignment_id>', methods=['POST'])
    def unpublish_results(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        if not namespace['owns_assignment'](namespace['session']['user'], namespace['assignments'], assignment_id):
            return (namespace['jsonify'](error='Accès interdit'), 403)
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a.get('teacher') == namespace['session']['user']), None)
        if assignment:
            assignment['results_published'] = False
            namespace['flash']('Résultats masqués aux étudiants')
        else:
            namespace['flash']('Devoir non trouvé')
        namespace['save_test_data']()
        return namespace['redirect'](namespace['url_for']('assignment_results', assignment_id=assignment_id))

    @blueprint.route('/admin/check_all_plagiarism', methods=['POST'])
    def check_all_plagiarism():
        """Vérifie le plagiat pour toutes les soumissions de code"""
        if 'user' not in namespace['session'] or namespace['session']['role'] not in ['admin', 'teacher']:
            return namespace['redirect'](namespace['url_for']('login'))
        checked_count = 0
        for submission in namespace['submissions']:
            if namespace['session']['role'] == 'teacher' and (not namespace['owns_assignment'](namespace['session']['user'], namespace['assignments'], submission.get('assignment_id'))):
                continue
            if submission.get('code_submission'):
                try:
                    code_file_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'code_submissions', submission['filename'])
                    if namespace['os'].path.exists(code_file_path):
                        with open(code_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            code_content = f.read()
                        plagiarism_result = namespace['check_plagiarism_local'](code_content, submission['id'])
                        submission['plagiarism'] = plagiarism_result
                        checked_count += 1
                except Exception as e:
                    print(f"Erreur vérification plagiat pour {submission['id']}: {e}")
        namespace['save_test_data']()
        namespace['flash'](f'Plagiat vérifié pour {checked_count} soumissions de code')
        if namespace['session']['role'] == 'admin':
            return namespace['redirect'](namespace['url_for']('admin_submissions'))
        else:
            return namespace['redirect'](namespace['url_for']('teacher_submissions'))

    @blueprint.route('/admin/recheck_plagiarism/<int:submission_id>', methods=['POST'])
    def recheck_plagiarism(submission_id):
        """Force la revérification du plagiat pour une soumission"""
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'admin':
            return namespace['redirect'](namespace['url_for']('login'))
        submission = next((s for s in namespace['submissions'] if s['id'] == submission_id), None)
        if not submission:
            namespace['flash']('Soumission non trouvée')
            return namespace['redirect'](namespace['url_for']('admin_submissions'))
        try:
            if submission.get('code_submission'):
                code_file_path = namespace['os'].path.join(namespace['app'].config['UPLOAD_FOLDER'], 'code_submissions', submission['filename'])
                if namespace['os'].path.exists(code_file_path):
                    with open(code_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        code_content = f.read()
                    plagiarism_result = namespace['check_plagiarism_local'](code_content, submission_id)
                    submission['plagiarism'] = plagiarism_result
                    namespace['save_test_data']()
                    namespace['flash'](f"Plagiat revérifié: {plagiarism_result['similarity']}% de similarité")
                else:
                    namespace['flash']('Fichier de code non trouvé')
            else:
                namespace['flash']("Cette soumission n'est pas une soumission de code")
        except Exception as e:
            namespace['flash'](f'Erreur lors de la revérification: {str(e)}')
        return namespace['redirect'](namespace['url_for']('admin_submissions'))
    return blueprint
