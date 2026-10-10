"""Authorization policies shared by academic routes."""


def can_access_course(username, user, course_id, teachers, enrollments):
    if not user:
        return False
    role = user.get('role')
    key = str(course_id)
    return (role == 'admin'
            or (role == 'teacher' and username in teachers.get(key, []))
            or (role == 'student' and username in enrollments.get(key, [])))


def owns_assignment(username, assignments, assignment_id):
    return any(a.get('id') == assignment_id and a.get('teacher') == username
               for a in assignments)
