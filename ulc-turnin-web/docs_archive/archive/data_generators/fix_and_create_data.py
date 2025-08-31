#!/usr/bin/env python3
"""
Script pour corriger les assignations et créer des devoirs/soumissions
"""

import json
import random
from datetime import datetime, timedelta

def fix_and_create_data():
    """Corrige les assignations et crée des devoirs/soumissions"""
    
    # Charger les données
    with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data['users']
    courses = data['admin_courses']
    
    # 1. Créer les assignations cours-professeurs
    course_assignments = {}
    course_enrollments = {}
    
    print("Creation des assignations cours-professeurs...")
    
    for course in courses:
        # Trouver un professeur de la même faculté
        profs_faculte = [u for u in users.values() 
                        if u.get('role') == 'teacher' and u.get('faculte') == course['faculte']]
        
        if profs_faculte:
            prof = random.choice(profs_faculte)
            course_assignments[int(course['id'])] = [prof['username']]
            
            # Inscrire des étudiants
            etudiants_eligibles = [u for u in users.values() 
                                  if u.get('role') == 'student' and 
                                     u.get('faculte') == course['faculte'] and 
                                     u.get('promotion') in course['promotions']]
            
            # Inscrire 3-8 étudiants par cours
            nb_inscrits = min(random.randint(3, 8), len(etudiants_eligibles))
            if etudiants_eligibles:
                inscrits = random.sample(etudiants_eligibles, nb_inscrits)
                course_enrollments[int(course['id'])] = [e['username'] for e in inscrits]
    
    print(f"Assignations creees: {len(course_assignments)} cours")
    
    # 2. Créer des devoirs
    titres = [
        "TP Pratique", "Projet de Module", "Examen Blanc", 
        "Travail Dirige", "Etude de Cas", "Rapport",
        "Analyse", "Presentation", "Memoire", "Exercices"
    ]
    
    assignments = []
    submissions = []
    assignment_id = 1
    submission_id = 1
    
    print("Creation des devoirs...")
    
    for course in courses[:30]:  # Limiter à 30 cours pour commencer
        if int(course['id']) in course_assignments:
            prof_username = course_assignments[int(course['id'])][0]
            prof = users[prof_username]
            
            # 1-2 devoirs par cours
            nb_devoirs = random.randint(1, 2)
            
            for i in range(nb_devoirs):
                due_date = datetime.now() + timedelta(days=random.randint(7, 30))
                
                assignment = {
                    'id': assignment_id,
                    'title': f"{random.choice(titres)} - {course['name']}",
                    'description': f"Travail pour le cours de {course['name']}",
                    'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
                    'course_id': course['id'],
                    'course': course['name'],
                    'teacher': prof_username,
                    'teacher_name': prof['name'],
                    'files': [],
                    'auto_correct': random.choice([True, False]),
                    'plagiarism_check': True,
                    'max_score': random.choice([20, 50, 100]),
                    'is_group_work': False,
                    'results_published': random.choice([True, False])
                }
                
                assignments.append(assignment)
                
                # Créer des soumissions
                etudiants_inscrits = course_enrollments.get(int(course['id']), [])
                nb_soumissions = int(len(etudiants_inscrits) * random.uniform(0.6, 0.9))
                
                etudiants_soumettent = random.sample(etudiants_inscrits, 
                                                   min(nb_soumissions, len(etudiants_inscrits)))
                
                for etudiant in etudiants_soumettent:
                    submit_date = datetime.now() - timedelta(days=random.randint(1, 5))
                    
                    submission = {
                        'id': submission_id,
                        'student': etudiant,
                        'assignment_id': assignment_id,
                        'filename': f"{etudiant}_{assignment_id}_travail.pdf",
                        'submitted_at': submit_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    submissions.append(submission)
                    submission_id += 1
                
                assignment_id += 1
    
    # 3. Mettre à jour les données
    data['course_assignments'] = course_assignments
    data['course_enrollments'] = course_enrollments
    data['assignments'] = assignments
    data['submissions'] = submissions
    data['next_assignment_id'] = assignment_id
    
    # Sauvegarder
    with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultats:")
    print(f"- Cours avec professeurs: {len(course_assignments)}")
    print(f"- Cours avec etudiants: {len(course_enrollments)}")
    print(f"- Devoirs crees: {len(assignments)}")
    print(f"- Soumissions creees: {len(submissions)}")
    
    # Exemples
    print(f"\nExemples de devoirs:")
    for i, assignment in enumerate(assignments[:5], 1):
        nb_soumissions = len([s for s in submissions if s['assignment_id'] == assignment['id']])
        print(f"  {i}. {assignment['title']}")
        print(f"     Prof: {assignment['teacher_name']} | {nb_soumissions} soumissions")

if __name__ == "__main__":
    fix_and_create_data()