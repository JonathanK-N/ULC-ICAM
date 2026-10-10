#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de population de données de test pour ULC-ICAM
Crée 20 utilisateurs, des cours, et des devoirs avec logique de promotion
"""

from bootstrap_credentials import isolated_admin_hash
import sys
import os
sys.path.append('ulc-turnin-web')
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import json
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def populate_test_data():
    admin_hash = isolated_admin_hash()
    print("Debut de la population des donnees de test...")
    
    # Charger les données existantes
    try:
        with open('ulc-turnin-web/ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        data = {
            'users': {'admin': {'password': admin_hash, 'role': 'admin', 'name': 'Administrateur ULC-ICAM'}},
            'admin_courses': [],
            'course_assignments': {},
            'course_enrollments': {},
            'assignments': [],
            'submissions': [],
            'next_course_admin_id': 1,
            'next_assignment_id': 1
        }
        
    # Configuration système ULC-ICAM
    system_config = {
        'promotions': ['L1', 'L2', 'L3', 'M1', 'M2'],
        'facultes': ['Faculté des Sciences et Technologies (ULC-ICAM)'],
        'departements': [
            'Mathématiques & Informatique',
            'Génie Mécanique', 
            'Génie Électrique',
            'Physique & Chimie',
            'Génie Informatique',
            'Maintenance & Génie Industriels',
            'Énergie/Environnement/Matériaux',
            'Polytechnique Générale'
        ],
        'grades': ['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']
    }
    
    # Données des professeurs
    professors_data = [
            {"nom": "Dr. Ahmed Hassan", "email": "ahmed.hassan@ulc-icam.edu.km", "specialite": "Algorithmique", "dept": "Mathématiques & Informatique"},
            {"nom": "Prof. Fatima Said", "email": "fatima.said@ulc-icam.edu.km", "specialite": "Base de Données", "dept": "Mathématiques & Informatique"},
            {"nom": "Dr. Mohamed Ali", "email": "mohamed.ali@ulc-icam.edu.km", "specialite": "Mécanique des Fluides", "dept": "Génie Mécanique"},
            {"nom": "Prof. Amina Abdou", "email": "amina.abdou@ulc-icam.edu.km", "specialite": "Thermodynamique", "dept": "Génie Mécanique"},
            {"nom": "Dr. Ibrahim Soilihi", "email": "ibrahim.soilihi@ulc-icam.edu.km", "specialite": "Électronique", "dept": "Génie Électrique"},
            {"nom": "Prof. Zainab Omar", "email": "zainab.omar@ulc-icam.edu.km", "specialite": "Automatique", "dept": "Génie Électrique"},
            {"nom": "Dr. Saïd Bacar", "email": "said.bacar@ulc-icam.edu.km", "specialite": "Chimie Organique", "dept": "Physique & Chimie"},
            {"nom": "Prof. Mariama Combo", "email": "mariama.combo@ulc-icam.edu.km", "specialite": "Physique Quantique", "dept": "Physique & Chimie"},
            {"nom": "Dr. Abdallah Mmadi", "email": "abdallah.mmadi@ulc-icam.edu.km", "specialite": "Réseaux", "dept": "Génie Informatique"},
            {"nom": "Prof. Hadidja Attoumane", "email": "hadidja.attoumane@ulc-icam.edu.km", "specialite": "Intelligence Artificielle", "dept": "Génie Informatique"}
        ]
        
    # Créer les professeurs
    for i, prof_data in enumerate(professors_data):
        username = f"prof{i+1:02d}"
        if username not in data['users']:
            data['users'][username] = {
                'username': username,
                'password': 'prof123',
                'role': 'teacher',
                'name': prof_data["nom"],
                'cip': f"PROF{i+1:03d}",
                'nom': prof_data["nom"].split()[-1],
                'prenom': prof_data["nom"].split()[1] if len(prof_data["nom"].split()) > 2 else prof_data["nom"].split()[0],
                'email': prof_data["email"],
                'departement': prof_data["dept"],
                'specialite': prof_data["specialite"],
                'grade': random.choice(system_config['grades']),
                'faculte': 'Faculté des Sciences et Technologies (ULC-ICAM)',
                'telephone': f"+269 77 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                'bureau': f"Bureau {random.randint(100,299)}"
            }
    
    # Données des étudiants
    students_data = [
            {"nom": "Ali Mohamed Combo", "numero": "20240001", "promo": "L1", "dept": "Mathématiques & Informatique"},
            {"nom": "Fatima Ahmed Said", "numero": "20240002", "promo": "L1", "dept": "Génie Informatique"},
            {"nom": "Hassan Ibrahim Ali", "numero": "20240003", "promo": "L2", "dept": "Mathématiques & Informatique"},
            {"nom": "Amina Saïd Bacar", "numero": "20240004", "promo": "L2", "dept": "Génie Électrique"},
            {"nom": "Mohamed Abdou Hassan", "numero": "20240005", "promo": "L3", "dept": "Génie Mécanique"},
            {"nom": "Zainab Ali Omar", "numero": "20240006", "promo": "L3", "dept": "Physique & Chimie"},
            {"nom": "Ibrahim Mohamed Said", "numero": "20240007", "promo": "M1", "dept": "Génie Informatique"},
            {"nom": "Mariama Hassan Combo", "numero": "20240008", "promo": "M1", "dept": "Mathématiques & Informatique"},
            {"nom": "Abdallah Said Ali", "numero": "20240009", "promo": "M2", "dept": "Génie Électrique"},
            {"nom": "Hadidja Omar Bacar", "numero": "20240010", "promo": "M2", "dept": "Génie Mécanique"}
    ]
    
    # Créer les étudiants
    for i, student_data in enumerate(students_data):
        username = f"etud{i+1:02d}"
        if username not in data['users']:
            data['users'][username] = {
                'username': username,
                'password': 'student123',
                'role': 'student',
                'name': student_data["nom"],
                'cip': f"ETU{student_data['numero']}",
                'numero_etudiant': student_data["numero"],
                'nom': student_data["nom"].split()[-1],
                'prenom': student_data["nom"].split()[0],
                'email': f"{student_data['nom'].lower().replace(' ', '.')}@ulc-icam.edu.km",
                'departement': student_data["dept"],
                'promotion': student_data["promo"],
                'grade': 'Licence' if student_data["promo"].startswith('L') else 'Master',
                'faculte': 'Faculté des Sciences et Technologies (ULC-ICAM)',
                'telephone': f"+269 77 {random.randint(10,99)} {random.randint(10,99)} {random.randint(10,99)}",
                'adresse': f"Moroni, Comores",
                'sexe': random.choice(['M', 'F']),
                'date_naissance': f"199{random.randint(5,9)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
            }
    
    # Créer les cours par département et promotion
    courses_data = [
            # Mathématiques & Informatique
            {"nom": "Algorithmique et Structures de Données", "code": "INFO101", "dept": "Mathématiques & Informatique", "promo": "L1", "credits": 6},
            {"nom": "Programmation Python", "code": "INFO102", "dept": "Mathématiques & Informatique", "promo": "L1", "credits": 4},
            {"nom": "Base de Données", "code": "INFO201", "dept": "Mathématiques & Informatique", "promo": "L2", "credits": 5},
            {"nom": "Développement Web", "code": "INFO202", "dept": "Mathématiques & Informatique", "promo": "L2", "credits": 4},
            {"nom": "Intelligence Artificielle", "code": "INFO301", "dept": "Mathématiques & Informatique", "promo": "L3", "credits": 6},
            {"nom": "Machine Learning", "code": "INFO401", "dept": "Mathématiques & Informatique", "promo": "M1", "credits": 7},
            
            # Génie Informatique
            {"nom": "Programmation C++", "code": "GI101", "dept": "Génie Informatique", "promo": "L1", "credits": 5},
            {"nom": "Réseaux Informatiques", "code": "GI201", "dept": "Génie Informatique", "promo": "L2", "credits": 6},
            {"nom": "Sécurité Informatique", "code": "GI301", "dept": "Génie Informatique", "promo": "L3", "credits": 5},
            {"nom": "Systèmes Distribués", "code": "GI401", "dept": "Génie Informatique", "promo": "M1", "credits": 6},
            
            # Génie Électrique
            {"nom": "Circuits Électriques", "code": "GE101", "dept": "Génie Électrique", "promo": "L1", "credits": 5},
            {"nom": "Électronique Analogique", "code": "GE201", "dept": "Génie Électrique", "promo": "L2", "credits": 6},
            {"nom": "Automatique", "code": "GE301", "dept": "Génie Électrique", "promo": "L3", "credits": 5},
            {"nom": "Systèmes Embarqués", "code": "GE401", "dept": "Génie Électrique", "promo": "M1", "credits": 6},
            
            # Génie Mécanique
            {"nom": "Mécanique du Point", "code": "GM101", "dept": "Génie Mécanique", "promo": "L1", "credits": 5},
            {"nom": "Thermodynamique", "code": "GM201", "dept": "Génie Mécanique", "promo": "L2", "credits": 6},
            {"nom": "Mécanique des Fluides", "code": "GM301", "dept": "Génie Mécanique", "promo": "L3", "credits": 5},
            {"nom": "Conception Mécanique", "code": "GM401", "dept": "Génie Mécanique", "promo": "M1", "credits": 6},
            
            # Physique & Chimie
            {"nom": "Physique Générale", "code": "PC101", "dept": "Physique & Chimie", "promo": "L1", "credits": 5},
            {"nom": "Chimie Organique", "code": "PC201", "dept": "Physique & Chimie", "promo": "L2", "credits": 6}
    ]
    
    # Créer les cours
    next_course_id = data.get('next_course_admin_id', 1)
    for course_data in courses_data:
        # Trouver un professeur du même département
        prof_username = None
        for username, user in data['users'].items():
            if user.get('role') == 'teacher' and user.get('departement') == course_data['dept']:
                prof_username = username
                break
        
        if not prof_username:
            prof_username = 'prof01'  # Fallback
        
        course = {
            'id': next_course_id,
            'name': course_data['nom'],
            'code': course_data['code'],
            'credits': course_data['credits'],
            'faculte': 'Faculté des Sciences et Technologies (ULC-ICAM)',
            'departement': course_data['dept'],
            'promotions': [course_data['promo']],
            'description': f"Cours de {course_data['nom']} pour la promotion {course_data['promo']}"
        }
        
        data['admin_courses'].append(course)
        data['course_assignments'][str(next_course_id)] = [prof_username]
        next_course_id += 1
    
    # Inscrire les étudiants aux cours de leur promotion
    for username, user in data['users'].items():
        if user.get('role') == 'student':
            student_promo = user.get('promotion')
            for course in data['admin_courses']:
                if student_promo in course.get('promotions', []):
                    course_key = str(course['id'])
                    if course_key not in data['course_enrollments']:
                        data['course_enrollments'][course_key] = []
                    if username not in data['course_enrollments'][course_key]:
                        data['course_enrollments'][course_key].append(username)
    
    # Créer 3 devoirs pour chaque cours
    next_assignment_id = data.get('next_assignment_id', 1)
    programming_languages = ["python", "java", "cpp", "c", "javascript"]
    
    for course in data['admin_courses']:
        # Trouver le professeur assigné
        assigned_teachers = data['course_assignments'].get(str(course['id']), [])
        teacher_username = assigned_teachers[0] if assigned_teachers else 'prof01'
        teacher_name = data['users'][teacher_username]['name']
        
        for i in range(3):
            # Alterner entre devoirs traditionnels et de programmation
            is_programming = (i == 2) or (course['code'].startswith(("INFO", "GI")))
            
            due_date = (datetime.now() + timedelta(days=random.randint(7, 30))).strftime('%Y-%m-%d')
            
            if is_programming:
                # Devoir de programmation
                language = random.choice(programming_languages)
                assignment = {
                    'id': next_assignment_id,
                    'title': f"TP{i+1} - Programmation {language.upper()}",
                    'description': f"Développez un programme en {language} qui résout le problème suivant:\n\nÉcrivez une fonction qui prend deux nombres en entrée et retourne leur somme.\n\nExemple:\nEntrée: 5 3\nSortie: 8",
                    'due_date': due_date,
                    'course_id': course['id'],
                    'course': course['name'],
                    'teacher': teacher_username,
                    'teacher_name': teacher_name,
                    'max_score': 20,
                    'is_code_assignment': True,
                    'test_cases': [
                        {'input': '5 3', 'expected_output': '8'},
                        {'input': '10 -2', 'expected_output': '8'},
                        {'input': '0 0', 'expected_output': '0'}
                    ],
                    'auto_correct': True,
                    'plagiarism_check': True,
                    'results_published': False
                }
            else:
                # Devoir traditionnel
                assignment = {
                    'id': next_assignment_id,
                    'title': f"Devoir {i+1} - {course['name']}",
                    'description': f"Rédigez un rapport de 2-3 pages sur les concepts abordés dans le cours {course['name']}.\n\nLe rapport doit inclure:\n- Introduction au sujet\n- Développement des concepts clés\n- Exemples pratiques\n- Conclusion",
                    'due_date': due_date,
                    'course_id': course['id'],
                    'course': course['name'],
                    'teacher': teacher_username,
                    'teacher_name': teacher_name,
                    'max_score': 20,
                    'is_code_assignment': False,
                    'auto_correct': False,
                    'plagiarism_check': True,
                    'results_published': False
                }
            
            data['assignments'].append(assignment)
            next_assignment_id += 1
    
    # Mettre à jour les compteurs
    data['next_course_admin_id'] = next_course_id
    data['next_assignment_id'] = next_assignment_id
    
    # Sauvegarder les données
    with open('ulc-turnin-web/ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Statistiques finales
    total_users = len(data['users'])
    total_professors = sum(1 for u in data['users'].values() if u.get('role') == 'teacher')
    total_students = sum(1 for u in data['users'].values() if u.get('role') == 'student')
    total_courses = len(data['admin_courses'])
    total_assignments = len(data['assignments'])
    total_enrollments = sum(len(students) for students in data['course_enrollments'].values())
    
    print("Population des donnees terminee avec succes!")
    print(f"Statistiques:")
    print(f"   - Utilisateurs totaux: {total_users}")
    print(f"   - Professeurs: {total_professors}")
    print(f"   - Étudiants: {total_students}")
    print(f"   - Cours: {total_courses}")
    print(f"   - Devoirs: {total_assignments}")
    print(f"   - Inscriptions: {total_enrollments}")
    print(f"Donnees de test pretes pour ULC-ICAM!")

if __name__ == "__main__":
    populate_test_data()

