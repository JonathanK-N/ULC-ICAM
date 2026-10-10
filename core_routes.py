"""Core controllers using the shared transition state."""
from flask import Blueprint

def create_blueprint(namespace):
    blueprint = Blueprint('core', __name__)

    @blueprint.route('/manifest.json')
    def web_manifest():
        """Serve the PWA manifest with the expected MIME type."""
        manifest_path = namespace['Path'](namespace['app'].static_folder) / 'manifest.json'
        if manifest_path.exists():
            return namespace['send_from_directory'](namespace['app'].static_folder, 'manifest.json', mimetype='application/manifest+json', max_age=0)
        response = namespace['make_response'](namespace['json'].dumps(namespace['PWA_MANIFEST'], ensure_ascii=False))
        response.headers['Content-Type'] = 'application/manifest+json'
        response.headers['Cache-Control'] = 'no-store'
        return response

    @blueprint.route('/sw.js')
    def service_worker():
        """Expose the service worker at the application root for full scope coverage."""
        sw_path = namespace['Path'](namespace['app'].static_folder) / 'sw.js'
        if not sw_path.exists():
            response = namespace['make_response']("// Service Worker ULC-ICAM\nself.addEventListener('fetch', function(){});")
            response.headers['Content-Type'] = 'application/javascript'
            response.headers['Cache-Control'] = 'no-store'
            return response
        return namespace['send_from_directory'](namespace['app'].static_folder, 'sw.js', mimetype='application/javascript', max_age=0)

    @blueprint.route('/health')
    def health_check():
        """Endpoint de santé pour Railway healthcheck."""
        return (namespace['jsonify']({'status': 'ok'}), 200)

    @blueprint.route('/')
    def index():
        teachers = sum((1 for u in namespace['users'].values() if u.get('role') == 'teacher'))
        students = sum((1 for u in namespace['users'].values() if u.get('role') == 'student'))
        courses_count = len(namespace['admin_courses'])
        assignments_count = len(namespace['assignments'])
        return namespace['render_template']('index.html', teachers=teachers, students=students, courses=courses_count, assignments=assignments_count)

    @blueprint.route('/dashboard')
    def dashboard():
        if 'user' not in namespace['session']:
            return namespace['redirect'](namespace['url_for']('login'))
        if namespace['session']['role'] == 'student':
            student_assignments = []
            for assignment in namespace['assignments']:
                course_id = assignment.get('course_id')
                if course_id and namespace['session']['user'] in namespace['get_enrolled_students'](course_id):
                    student_assignments.append(assignment)
            return namespace['render_template']('student_dashboard.html', assignments=student_assignments, student_groups=namespace['student_groups'])
        elif namespace['session']['role'] == 'teacher':
            teacher_assignments = [a for a in namespace['assignments'] if a.get('teacher') == namespace['session']['user']]
            teacher_submissions = [s for s in namespace['submissions'] if any((a['id'] == s['assignment_id'] and a.get('teacher') == namespace['session']['user'] for a in namespace['assignments']))]
            assignment_stats = {}
            for assignment in teacher_assignments:
                enrolled_count = len(namespace['get_enrolled_students'](assignment.get('course_id')))
                submitted_count = len([s for s in namespace['submissions'] if s['assignment_id'] == assignment['id']])
                assignment_stats[assignment['id']] = {'enrolled': enrolled_count, 'submitted': submitted_count}
            all_students = set()
            for course_id, teachers in namespace['course_assignments'].items():
                if namespace['session']['user'] in teachers:
                    all_students.update(namespace['get_enrolled_students'](course_id))
            teacher_courses = []
            for course in namespace['admin_courses']:
                if namespace['session']['user'] in namespace['get_assigned_teachers'](course['id']):
                    teacher_courses.append(course)
            return namespace['render_template']('teacher_dashboard.html', teacher_assignments=teacher_assignments, teacher_assignments_count=len(teacher_assignments), total_submissions=len(teacher_submissions), total_students=len(all_students), teacher_courses_count=len(teacher_courses), teacher_courses=teacher_courses, course_enrollments=namespace['course_enrollments'], assignment_stats=assignment_stats)
        else:
            users_count = len(namespace['users'])
            students_count = sum((1 for u in namespace['users'].values() if u.get('role') == 'student'))
            teachers_count = sum((1 for u in namespace['users'].values() if u.get('role') == 'teacher'))
            courses_count = len(namespace['admin_courses'])
            assignments_count = len(namespace['assignments'])
            submissions_count = len(namespace['submissions'])
            return namespace['render_template']('admin_dashboard.html', users=namespace['users'], assignments=namespace['assignments'], submissions=namespace['submissions'], admin_courses=namespace['admin_courses'], course_assignments=namespace['course_assignments'], users_count=users_count, students_count=students_count, teachers_count=teachers_count, courses_count=courses_count, assignments_count=assignments_count, submissions_count=submissions_count)

    @blueprint.route('/offline.html')
    def offline():
        return namespace['render_template']('offline.html')
    return blueprint
