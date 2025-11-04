#!/usr/bin/env python3
"""
Création de données d'exemple pour ULC-ICAM Turnin
Génère des utilisateurs, cours et devoirs réalistes
"""

import json
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Crée des données d'exemple complètes"""
    
    # Données de base
    data = {
        'users': {},
        'courses': {},
        'assignments': {},
        'submissions': {},
        'enrollments': {},
        'course_teachers': {},
        'grades': {},
        'notifications': {},
        'counters': {
            'next_user_id': 1,
            'next_course_id': 1,
            'next_assignment_id': 1,
            'next_submission_id': 1
        }
    }
    
    user_id = 1
    course_id = 1
    assignment_id = 1
    
    # === UTILISATEURS ===
    
    # Admin
    data['users']['admin'] = {
        'id': user_id,
        'username': 'admin',
        'password': 'admin123',
        'role': 'admin',
        'name': 'Administrateur ULC-ICAM',
        'email': 'admin@ulc-icam.cd',
        'created_at': datetime.now().isoformat(),
        'active': True
    }
    user_id += 1
    
    # Professeurs
    professors = [
        {
            'username': 'prof001',
            'name': 'Prof. Jean Mukendi',
            'email': 'j.mukendi@ulc-icam.cd',
            'cip': 'PROF001',
            'grade': 'Prof. Ordinaire',
            'departement': 'Mathématiques-Informatique',
            'faculte': 'Sciences'
        },
        {
            'username': 'prof002',
            'name': 'Prof. Marie Kabongo',
            'email': 'm.kabongo@ulc-icam.cd',
            'cip': 'PROF002',
            'grade': 'Prof. Associé',
            'departement': 'Physique',
            'faculte': 'Sciences'
        },
        {
            'username': 'prof003',
            'name': 'Dr. Paul Tshisekedi',
            'email': 'p.tshisekedi@ulc-icam.cd',
            'cip': 'PROF003',
            'grade': 'CT',
            'departement': 'Médecine Interne',
            'faculte': 'Médecine'
        },
        {
            'username': 'prof004',
            'name': 'Ass. Thérèse Mbuyi',
            'email': 'therese.mbuyi@ulc-icam.cd',
            'cip': 'PROF004',
            'grade': 'Ass.',
            'departement': 'Chimie',
            'faculte': 'Sciences'
        }
    ]
    
    for prof in professors:
        data['users'][prof['username']] = {
            'id': user_id,
            'password': 'prof123',
            'role': 'teacher',
            'created_at': datetime.now().isoformat(),
            'active': True,
            **prof
        }
        user_id += 1
    
    # Étudiants
    students = [
        {
            'username': 'etu001',
            'name': 'Marie Kabila',
            'email': 'm.kabila@ulc-icam.cd',
            'cip': 'ETU001',
            'matricule': '2024001',
            'promotion': 'L3',
            'faculte': 'Sciences'
        },
        {
            'username': 'etu002',
            'name': 'Joseph Kasongo',
            'email': 'j.kasongo@ulc-icam.cd',
            'cip': 'ETU002',
            'matricule': '2024002',
            'promotion': 'L3',
            'faculte': 'Sciences'
        },
        {
            'username': 'etu003',
            'name': 'Grace Mwamba',
            'email': 'g.mwamba@ulc-icam.cd',
            'cip': 'ETU003',
            'matricule': '2024003',
            'promotion': 'L2',
            'faculte': 'Sciences'
        },
        {
            'username': 'etu004',
            'name': 'David Mulamba',
            'email': 'd.mulamba@ulc-icam.cd',
            'cip': 'ETU004',
            'matricule': '2024004',
            'promotion': 'L3',
            'faculte': 'Sciences'
        },
        {
            'username': 'etu005',
            'name': 'Sarah Ngoy',
            'email': 's.ngoy@ulc-icam.cd',
            'cip': 'ETU005',
            'matricule': '2024005',
            'promotion': 'M1',
            'faculte': 'Médecine'
        }
    ]
    
    for student in students:
        data['users'][student['username']] = {
            'id': user_id,
            'password': 'etu123',
            'role': 'student',
            'created_at': datetime.now().isoformat(),
            'active': True,
            **student
        }
        user_id += 1
    
    # === COURS ===
    
    courses = [
        {
            'code': 'INF301',
            'title': 'Programmation Orientée Objet',
            'description': 'Introduction aux concepts de la programmation orientée objet avec Java',
            'credits': 4,
            'faculte': 'Sciences',
            'departement': 'Mathématiques-Informatique',
            'session': 'Automne',
            'year': '2024',
            'teacher': 'prof001'
        },
        {
            'code': 'PHY201',
            'title': 'Mécanique Classique',
            'description': 'Étude des lois de Newton et applications',
            'credits': 3,
            'faculte': 'Sciences',
            'departement': 'Physique',
            'session': 'Automne',
            'year': '2024',
            'teacher': 'prof002'
        },
        {
            'code': 'CHI101',
            'title': 'Chimie Générale',
            'description': 'Principes fondamentaux de la chimie',
            'credits': 3,
            'faculte': 'Sciences',
            'departement': 'Chimie',
            'session': 'Automne',
            'year': '2024',
            'teacher': 'prof004'
        },
        {
            'code': 'MED401',
            'title': 'Pathologie Générale',
            'description': 'Étude des mécanismes pathologiques',
            'credits': 5,
            'faculte': 'Médecine',
            'departement': 'Médecine Interne',
            'session': 'Automne',
            'year': '2024',
            'teacher': 'prof003'
        }
    ]
    
    for course in courses:
        teacher = course.pop('teacher')
        data['courses'][str(course_id)] = {
            'id': course_id,
            'created_at': datetime.now().isoformat(),
            'active': True,
            **course
        }
        
        # Assigner le professeur
        data['course_teachers'][str(course_id)] = [teacher]
        
        # Inscrire des étudiants
        if course['code'] in ['INF301', 'PHY201', 'CHI101']:
            # Cours de sciences pour L2/L3
            data['enrollments'][str(course_id)] = ['etu001', 'etu002', 'etu003', 'etu004']
        elif course['code'] == 'MED401':
            # Cours de médecine pour M1
            data['enrollments'][str(course_id)] = ['etu005']
        
        course_id += 1
    
    # === DEVOIRS ===
    
    assignments = [
        {
            'title': 'Projet Java - Système de Gestion',
            'description': 'Développer une application Java avec interface graphique pour gérer une bibliothèque',
            'course_id': '1',  # INF301
            'teacher': 'prof001',
            'due_date': (datetime.now() + timedelta(days=14)).isoformat(),
            'max_score': 100,
            'allow_late': True,
            'allow_resubmission': True,
            'group_assignment': True,
            'max_group_size': 3,
            'published': True,
            'ai_grading': True,
            'plagiarism_check': True,
            'ai_feedback': True
        },
        {
            'title': 'Exercices de Mécanique',
            'description': 'Résoudre les problèmes du chapitre 3 sur les forces et le mouvement',
            'course_id': '2',  # PHY201
            'teacher': 'prof002',
            'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
            'max_score': 50,
            'allow_late': False,
            'allow_resubmission': False,
            'group_assignment': False,
            'max_group_size': 1,
            'published': True,
            'ai_grading': True,
            'plagiarism_check': False,
            'ai_feedback': True
        },
        {
            'title': 'Rapport de Laboratoire - Synthèse',
            'description': 'Rédiger un rapport complet sur l\'expérience de synthèse organique',
            'course_id': '3',  # CHI101
            'teacher': 'prof004',
            'due_date': (datetime.now() + timedelta(days=10)).isoformat(),
            'max_score': 75,
            'allow_late': True,
            'allow_resubmission': True,
            'group_assignment': False,
            'max_group_size': 1,
            'published': True,
            'ai_grading': False,
            'plagiarism_check': True,
            'ai_feedback': False
        }
    ]
    
    for assignment in assignments:
        data['assignments'][str(assignment_id)] = {
            'id': assignment_id,
            'created_at': datetime.now().isoformat(),
            'files': [],
            **assignment
        }
        assignment_id += 1
    
    # Mettre à jour les compteurs
    data['counters']['next_user_id'] = user_id
    data['counters']['next_course_id'] = course_id
    data['counters']['next_assignment_id'] = assignment_id
    data['counters']['next_submission_id'] = 1
    
    return data

def save_sample_data():
    """Sauvegarde les données d'exemple"""
    data = create_sample_data()
    
    with open('ulc_turnin_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Donnees d'exemple creees avec succes!")
    print(f"Utilisateurs: {len(data['users'])}")
    print(f"Cours: {len(data['courses'])}")
    print(f"Devoirs: {len(data['assignments'])}")
    print("")
    print("Comptes de test:")
    print("   Admin: admin / admin123")
    print("   Prof: prof001 / prof123")
    print("   Étudiant: etu001 / etu123")

if __name__ == "__main__":
    save_sample_data()