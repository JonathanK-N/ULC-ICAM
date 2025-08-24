import io
import app as flask_app


def test_full_workflow():
    app = flask_app.app

    # Reset in-memory data
    flask_app.users = {
        'admin': {
            'password': 'admin123',
            'role': 'admin',
            'name': 'Administrateur Test'
        }
    }
    flask_app.admin_courses = []
    flask_app.course_assignments = {}
    flask_app.courses = []
    flask_app.course_enrollments = {}
    flask_app.assignments = []
    flask_app.submissions = []
    flask_app.next_course_admin_id = 1
    flask_app.next_assignment_id = 1

    teacher = {
        'username': 'prof_test',
        'password': 'profpass',
        'cip': 'cip_prof',
        'nom': 'Prof',
        'postnom': 'Test',
        'prenom': 'John',
        'sexe': 'M',
        'date_naissance': '1980-01-01',
        'cours_dispenses': 'Algo',
        'departement': 'Mathématiques-Informatique',
        'grade': 'Prof. Ordinaire',
        'telephone': '123',
        'email': 'prof@example.com',
        'bureau': 'B1'
    }

    student1 = {
        'username': 'stud_sci',
        'password': 'studpass',
        'cip': 'cip_sci',
        'nom': 'Sci',
        'postnom': 'One',
        'prenom': 'Alice',
        'sexe': 'F',
        'date_naissance': '2001-01-01',
        'promotion': 'L1',
        'faculte': 'Sciences',
        'telephone': '111',
        'email': 'sci@example.com',
        'adresse': 'Addr1'
    }

    student2 = {
        'username': 'stud_dro',
        'password': 'studpass',
        'cip': 'cip_dro',
        'nom': 'Dro',
        'postnom': 'Two',
        'prenom': 'Bob',
        'sexe': 'M',
        'date_naissance': '2001-02-02',
        'promotion': 'L1',
        'faculte': 'Droit',
        'telephone': '222',
        'email': 'dro@example.com',
        'adresse': 'Addr2'
    }

    course = {
        'name': 'Algorithmique',
        'code': 'ALG101',
        'credits': '3',
        'faculte': 'Sciences',
        'departement': 'Mathématiques-Informatique',
        'promotions': ['L1'],
        'description': 'Intro'
    }

    assignment_data = {
        'title': 'TP1',
        'description': 'Premier devoir',
        'due_date': '2030-01-01',
        'course': 'Algorithmique',
        'max_score': '100'
    }

    with app.test_client() as client:
        # Admin login
        resp = client.post('/login/admin', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        assert resp.status_code == 200

        # Add teacher
        resp = client.post('/admin/add_teacher', data=teacher, follow_redirects=True)
        assert resp.status_code == 200
        assert teacher['username'] in flask_app.users

        # Add course
        resp = client.post('/admin/add_course', data=course, follow_redirects=True)
        assert resp.status_code == 200
        course_id = flask_app.admin_courses[-1]['id']
        assert any(c['id'] == course_id for c in flask_app.admin_courses)

        # Assign teacher to course
        resp = client.post(f'/admin/assign_teacher/{course_id}', data={'teacher': teacher['username']}, follow_redirects=True)
        assert resp.status_code == 200
        assert teacher['username'] in flask_app.course_assignments[course_id]

        # Add students
        for stu in (student1, student2):
            resp = client.post('/admin/add_student', data=stu, follow_redirects=True)
            assert resp.status_code == 200
            assert stu['username'] in flask_app.users
            assert flask_app.users[stu['username']]['faculte'] == stu['faculte']

        # Prepare course list for enrollment route
        flask_app.courses.append({'id': course_id, 'teacher': teacher['username'],
                                  'target_promotions': [], 'target_facultes': []})

        # Logout admin
        client.get('/logout')

        # Teacher login
        resp = client.post('/login/teacher', data={'identifier': teacher['cip'], 'password': teacher['password']}, follow_redirects=True)
        assert resp.status_code == 200

        # Enroll students
        for stu in (student1, student2):
            resp = client.get(f'/teacher/enroll_student/{course_id}/{stu["username"]}')
            assert resp.status_code == 302
            assert stu['username'] in flask_app.course_enrollments[course_id]

        # Create assignment
        assign_form = assignment_data.copy()
        assign_form['course_id'] = str(course_id)
        resp = client.post('/teacher/create_assignment', data=assign_form, follow_redirects=True)
        assert resp.status_code == 200
        assignment_id = flask_app.assignments[-1]['id']

        # Logout teacher
        client.get('/logout')

        # Students submit
        for stu in (student1, student2):
            resp = client.post('/login/student', data={'identifier': stu['cip'], 'password': stu['password']}, follow_redirects=True)
            assert resp.status_code == 200
            data = {'file': (io.BytesIO(b'submission content'), 'work.txt')}
            resp = client.post(f'/submit/{assignment_id}', data=data,
                               content_type='multipart/form-data', follow_redirects=True)
            assert resp.status_code == 200
            assert any(s['student'] == stu['username'] and s['assignment_id'] == assignment_id
                       for s in flask_app.submissions)
            client.get('/logout')

        assert len(flask_app.submissions) == 2
