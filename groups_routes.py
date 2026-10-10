"""Groups controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('groups', __name__)

    @blueprint.route('/student/join_group/<int:assignment_id>', methods=['GET', 'POST'])
    def join_group(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'student':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id), None)
        if not assignment or not assignment.get('is_group_work'):
            namespace['flash']('Devoir non trouvé ou pas un travail de groupe')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        course_id = assignment.get('course_id')
        if course_id and namespace['session']['user'] not in namespace['get_enrolled_students'](course_id):
            namespace['flash']("Vous n'êtes pas inscrit au cours de ce devoir")
            return namespace['redirect'](namespace['url_for']('dashboard'))
        if namespace['request'].method == 'POST':
            selected_students = namespace['request'].form.getlist('group_members')
            selected_students.append(namespace['session']['user'])
            if len(set(selected_students)) != len(selected_students):
                return (namespace['jsonify'](error='Membres dupliqués'), 400)
            if not 1 <= len(selected_students) <= assignment.get('group_size', 2):
                return (namespace['jsonify'](error='Taille de groupe invalide'), 400)
            enrolled = namespace['get_enrolled_students'](course_id)
            existing_members = namespace['student_groups'].get(assignment_id, {})
            if any((name not in enrolled or namespace['users'].get(name, {}).get('role') != 'student' for name in selected_students)):
                return (namespace['jsonify'](error='Membres non autorisés'), 403)
            if any((name in existing_members for name in selected_students)):
                return (namespace['jsonify'](error='Un membre appartient déjà à un groupe'), 409)
            if assignment_id not in namespace['group_assignments']:
                namespace['group_assignments'][assignment_id] = {'groups': [], 'type': 'manual'}
            if assignment_id not in namespace['student_groups']:
                namespace['student_groups'][assignment_id] = {}
            group_id = len(namespace['group_assignments'][assignment_id]['groups'])
            namespace['group_assignments'][assignment_id]['groups'].append(selected_students)
            for student in selected_students:
                namespace['student_groups'][assignment_id][student] = group_id
            namespace['save_test_data']()
            namespace['flash']('Groupe formé avec succès')
            return namespace['redirect'](namespace['url_for']('dashboard'))
        course_students = namespace['get_course_students'](assignment.get('course_id')) if assignment.get('course_id') else []
        available_students = []
        for student in course_students:
            if assignment_id not in namespace['student_groups'] or student['username'] not in namespace['student_groups'][assignment_id]:
                if student['username'] != namespace['session']['user']:
                    available_students.append(student)
        return namespace['render_template']('join_group.html', assignment=assignment, available_students=available_students)

    @blueprint.route('/teacher/manage_groups/<int:assignment_id>')
    def manage_groups(assignment_id):
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        assignment = next((a for a in namespace['assignments'] if a['id'] == assignment_id and a['teacher'] == namespace['session']['user']), None)
        if not assignment:
            namespace['flash']('Devoir non trouvé')
            return namespace['redirect'](namespace['url_for']('teacher_assignments'))
        groups_info = namespace['group_assignments'].get(assignment_id, {'groups': [], 'type': 'manual'})
        course_students = namespace['get_course_students'](assignment.get('course_id')) if assignment.get('course_id') else []
        return namespace['render_template']('manage_groups.html', assignment=assignment, groups_info=groups_info, course_students=course_students, student_groups=namespace['student_groups'], users=namespace['users'])
    return blueprint
