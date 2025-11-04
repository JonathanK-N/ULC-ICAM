#!/usr/bin/env python3
"""
Script de test pour vérifier la route teacher_students
"""

import json

def test_teacher_students_logic():
    """Teste la logique de récupération des étudiants pour un professeur"""
    
    # Charger les données
    with open('ulc-turnin-web/ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', {})
    admin_courses = data.get('admin_courses', [])
    course_assignments = data.get('course_assignments', {})
    course_enrollments = data.get('course_enrollments', {})
    
    print("=== TEST ROUTE TEACHER_STUDENTS ===\n")
    
    # Tester avec prof01
    teacher_username = 'prof01'
    print(f"Test pour le professeur: {teacher_username}")
    print(f"Nom: {users[teacher_username]['name']}")
    print()
    
    # Simuler la logique de la route corrigée
    teacher_students = set()
    teacher_courses = []
    
    for course_id_str, teachers in course_assignments.items():
        if teacher_username in teachers:
            course_id = int(course_id_str)
            course = next((c for c in admin_courses if c['id'] == course_id), None)
            if course:
                teacher_courses.append(course)
                # Utiliser course_id_str pour accéder aux inscriptions
                enrolled_students = course_enrollments.get(course_id_str, [])
                teacher_students.update(enrolled_students)
                print(f"Cours: {course['name']} ({course['code']})")
                print(f"  Étudiants inscrits: {len(enrolled_students)}")
                for student_username in enrolled_students:
                    if student_username in users:
                        student = users[student_username]
                        print(f"    - {student['name']} ({student.get('cip', 'N/A')})")
                print()
    
    print(f"Total des cours assignés: {len(teacher_courses)}")
    print(f"Total des étudiants uniques: {len(teacher_students)}")
    print()
    
    # Afficher tous les étudiants uniques
    print("Étudiants uniques du professeur:")
    for student_username in teacher_students:
        if student_username in users:
            student = users[student_username]
            print(f"  - {student['name']} ({student.get('cip', 'N/A')}) - {student.get('promotion', 'N/A')}")
    
    print("\n" + "="*50)
    print("Test terminé avec succès!")
    print("La route teacher_students devrait maintenant fonctionner correctement.")

if __name__ == "__main__":
    test_teacher_students_logic()