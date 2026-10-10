"""Teachers controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('teachers', __name__)

    @blueprint.route('/teacher/students')
    def teacher_students():
        if 'user' not in namespace['session'] or namespace['session']['role'] != 'teacher':
            return namespace['redirect'](namespace['url_for']('login'))
        teacher_students = set()
        teacher_courses = []
        for course_id_str, teachers in namespace['course_assignments'].items():
            if namespace['session']['user'] in teachers:
                course_id = int(course_id_str)
                course = next((c for c in namespace['admin_courses'] if c['id'] == course_id), None)
                if course:
                    teacher_courses.append(course)
                    teacher_students.update(namespace['get_enrolled_students'](course_id_str))
        students_data = []
        for student_username in teacher_students:
            if student_username in namespace['users']:
                students_data.append({'username': student_username, 'data': namespace['users'][student_username]})
        return namespace['render_template']('teacher_students.html', students=students_data, courses=teacher_courses)
    return blueprint
