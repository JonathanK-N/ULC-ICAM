#!/usr/bin/env python3
"""
Script pour créer des devoirs et soumissions de test
"""

import json
import random
from datetime import datetime, timedelta

def create_assignments_and_submissions():
    """Crée des devoirs et soumissions de test"""
    
    # Charger les données existantes
    with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data['users']
    courses = data['admin_courses']
    course_assignments = data['course_assignments']
    course_enrollments = data['course_enrollments']
    
    # Titres de devoirs
    titres = [
        "TP Pratique", "Projet de Fin de Module", "Examen Blanc", 
        "Travail Dirigé", "Étude de Cas", "Rapport de Stage",
        "Analyse Critique", "Présentation Orale", "Mémoire",
        "Exercices Pratiques"
    ]
    
    assignments = []
    submissions = []
    assignment_id = 1
    submission_id = 1
    
    # Créer des devoirs pour chaque cours qui a un professeur assigné
    for course in courses:
        if course['id'] in course_assignments:
            prof_username = course_assignments[course['id']][0]
            prof = users[prof_username]
            
            # Créer 1-3 devoirs par cours
            nb_devoirs = random.randint(1, 3)
            
            for i in range(nb_devoirs):
                # Date d'échéance dans 7-30 jours
                due_date = datetime.now() + timedelta(days=random.randint(7, 30))
                
                assignment = {
                    'id': assignment_id,
                    'title': f"{random.choice(titres)} - {course['name']}",
                    'description': f"Travail à rendre pour le cours de {course['name']}. Veuillez suivre les consignes données en cours.",
                    'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
                    'course_id': course['id'],
                    'course': course['name'],
                    'teacher': prof_username,
                    'teacher_name': prof['name'],
                    'files': [],
                    'auto_correct': random.choice([True, False]),
                    'plagiarism_check': True,
                    'max_score': random.choice([20, 50, 100]),
                    'is_group_work': random.choice([True, False]) if random.random() < 0.3 else False,
                    'results_published': random.choice([True, False]),
                    'group_formation': 'manual',
                    'group_size': random.randint(2, 4),
                    'results_release_date': ''
                }
                
                assignments.append(assignment)
                
                # Créer des soumissions pour ce devoir
                etudiants_inscrits = course_enrollments.get(course['id'], [])
                
                # 60-90% des étudiants soumettent
                taux_soumission = random.uniform(0.6, 0.9)
                nb_soumissions = int(len(etudiants_inscrits) * taux_soumission)
                
                # Sélectionner aléatoirement les étudiants qui soumettent
                etudiants_soumettent = random.sample(etudiants_inscrits, min(nb_soumissions, len(etudiants_inscrits)))
                
                for etudiant in etudiants_soumettent:
                    # Date de soumission entre 1-10 jours avant l'échéance
                    jours_avant = random.randint(1, 10)
                    submit_date = due_date - timedelta(days=jours_avant)
                    
                    # Si la date est dans le futur, la mettre dans le passé
                    if submit_date > datetime.now():
                        submit_date = datetime.now() - timedelta(days=random.randint(1, 5))
                    
                    submission = {
                        'id': submission_id,
                        'student': etudiant,
                        'assignment_id': assignment_id,
                        'filename': f"{etudiant}_{assignment_id}_{random.randint(1000,9999)}_travail.pdf",
                        'submitted_at': submit_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    submissions.append(submission)
                    submission_id += 1
                
                assignment_id += 1
    
    # Mettre à jour les données
    data['assignments'] = assignments
    data['submissions'] = submissions
    data['next_assignment_id'] = assignment_id
    
    # Sauvegarder
    with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Cree {len(assignments)} devoirs et {len(submissions)} soumissions")
    print(f"Statistiques:")
    print(f"   - Devoirs crees: {len(assignments)}")
    print(f"   - Soumissions creees: {len(submissions)}")
    print(f"   - Cours avec devoirs: {len(set(a['course_id'] for a in assignments))}")
    
    # Afficher quelques exemples
    print(f"\nExemples de devoirs crees:")
    for i, assignment in enumerate(assignments[:5], 1):
        prof_name = assignment['teacher_name']
        course_name = assignment['course']
        nb_soumissions = len([s for s in submissions if s['assignment_id'] == assignment['id']])
        print(f"   {i}. {assignment['title']}")
        print(f"      Prof: {prof_name} | Cours: {course_name} | {nb_soumissions} soumissions")

if __name__ == "__main__":
    create_assignments_and_submissions()