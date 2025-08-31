#!/usr/bin/env python3
"""
Script de test pour vérifier les inscriptions d'étudiants aux cours
"""

import json

def test_course_enrollments():
    """Teste les inscriptions d'étudiants aux cours"""
    
    # Charger les données
    with open('ulc-turnin-web/ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', {})
    admin_courses = data.get('admin_courses', [])
    course_enrollments = data.get('course_enrollments', {})
    
    print("=== TEST DES INSCRIPTIONS AUX COURS ===\n")
    
    # Afficher les statistiques générales
    total_students = sum(1 for u in users.values() if u.get('role') == 'student')
    total_courses = len(admin_courses)
    total_enrollments = sum(len(students) for students in course_enrollments.values())
    
    print(f"Statistiques générales:")
    print(f"   - Étudiants: {total_students}")
    print(f"   - Cours: {total_courses}")
    print(f"   - Inscriptions totales: {total_enrollments}")
    print()
    
    # Afficher les inscriptions par cours
    print("Inscriptions par cours:")
    for course in admin_courses:
        course_id = course['id']
        enrolled_students = course_enrollments.get(str(course_id), [])
        
        print(f"\n   {course['name']} ({course['code']})")
        print(f"      Promotion: {', '.join(course['promotions'])}")
        print(f"      Étudiants inscrits: {len(enrolled_students)}")
        
        if enrolled_students:
            for student_username in enrolled_students:
                if student_username in users:
                    student = users[student_username]
                    print(f"        - {student.get('name', student_username)} ({student.get('cip', 'N/A')})")
        else:
            print("        Aucun étudiant inscrit")
    
    print("\n" + "="*50)
    print("Test terminé avec succès!")
    print("Les données d'inscription sont correctement chargées.")

if __name__ == "__main__":
    test_course_enrollments()