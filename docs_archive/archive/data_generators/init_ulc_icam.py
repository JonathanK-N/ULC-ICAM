#!/usr/bin/env python3
"""
Initialisation des données ULC-ICAM directement dans app.py
"""

import random
from datetime import datetime, timedelta

# Configuration ULC-ICAM
FACULTES_ULC = {
    'Sciences': ['Mathématiques-Informatique', 'Physique', 'Chimie', 'Biologie'],
    'Médecine': ['Médecine Interne', 'Chirurgie', 'Pédiatrie'],
    'Droit': ['Droit Privé', 'Droit Public', 'Droit International'],
    'Sciences Économiques': ['Économie', 'Gestion', 'Finance'],
    'Polytechnique': ['Génie Civil', 'Génie Électrique', 'Génie Mécanique'],
    'Lettres et Sciences Humaines': ['Philosophie', 'Histoire', 'Sociologie']
}

PROMOTIONS = ['L1', 'L2', 'L3', 'M1', 'M2']
GRADES = ['Prof. Ordinaire', 'Prof. Associé', 'CT', 'Ass.', 'Attaché']

NOMS_CONGO = ['MUKENDI', 'KABONGO', 'MBUYI', 'KASONGO', 'NGOY', 'KALALA', 'MWAMBA', 'KATANGA', 'LUBOYA', 'ILUNGA']
PRENOMS = ['Jean', 'Marie', 'Pierre', 'Jeanne', 'Paul', 'Anne', 'André', 'Joseph', 'Michel', 'François']

def init_data():
    """Initialise toutes les données ULC-ICAM"""
    
    # Utilisateurs
    users_data = {'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrateur ULC-ICAM'}}
    
    # Générer 20 professeurs
    for i in range(1, 21):
        faculte = random.choice(list(FACULTES_ULC.keys()))
        dept = random.choice(FACULTES_ULC[faculte])
        nom = random.choice(NOMS_CONGO)
        prenom = random.choice(PRENOMS)
        grade = random.choice(GRADES)
        
        username = f'prof{i:03d}'
        users_data[username] = {
            'username': username,
            'password': 'prof123',
            'role': 'teacher',
            'cip': f'P{2024000 + i}',
            'nom': nom,
            'prenom': prenom,
            'sexe': random.choice(['M', 'F']),
            'date_naissance': f'{random.randint(1960, 1980)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'departement': dept,
            'faculte': faculte,
            'grade': grade,
            'telephone': f'+243{random.randint(800000000, 999999999)}',
            'email': f'{prenom.lower()}.{nom.lower()}@ulc-icam.cd',
            'bureau': f'{faculte[:3].upper()}-{random.randint(101, 350)}',
            'name': f'{grade} {prenom} {nom}',
            'must_change_password': True
        }
    
    # Générer 50 étudiants
    for i in range(1, 51):
        faculte = random.choice(list(FACULTES_ULC.keys()))
        promotion = random.choice(PROMOTIONS)
        nom = random.choice(NOMS_CONGO)
        prenom = random.choice(PRENOMS)
        
        username = f'etud{i:03d}'
        users_data[username] = {
            'username': username,
            'password': 'etud123',
            'role': 'student',
            'cip': f'E{2024000 + i}',
            'nom': nom,
            'prenom': prenom,
            'sexe': random.choice(['M', 'F']),
            'date_naissance': f'{random.randint(1995, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'promotion': promotion,
            'faculte': faculte,
            'telephone': f'+243{random.randint(800000000, 999999999)}',
            'email': f'{prenom.lower()}.{nom.lower()}{i}@student.ulc-icam.cd',
            'adresse': f'Av. Lumumba, Q. Gombe, Kinshasa',
            'name': f'{prenom} {nom}',
            'must_change_password': True
        }
    
    # Générer cours
    cours_data = []
    cours_id = 1
    
    cours_par_dept = {
        'Mathématiques-Informatique': ['Algorithmique', 'Base de Données', 'Programmation'],
        'Physique': ['Mécanique', 'Électromagnétisme', 'Thermodynamique'],
        'Chimie': ['Chimie Générale', 'Chimie Organique'],
        'Biologie': ['Biologie Cellulaire', 'Génétique'],
        'Médecine Interne': ['Pathologie', 'Cardiologie'],
        'Chirurgie': ['Chirurgie Générale', 'Orthopédie'],
        'Pédiatrie': ['Pédiatrie Générale'],
        'Droit Privé': ['Droit Civil', 'Droit Commercial'],
        'Droit Public': ['Droit Constitutionnel'],
        'Droit International': ['Droit International Public'],
        'Économie': ['Microéconomie', 'Macroéconomie'],
        'Gestion': ['Management', 'Marketing'],
        'Finance': ['Finance d\'Entreprise'],
        'Génie Civil': ['Résistance des Matériaux'],
        'Génie Électrique': ['Électrotechnique'],
        'Génie Mécanique': ['Mécanique des Fluides'],
        'Philosophie': ['Philosophie Générale'],
        'Histoire': ['Histoire du Congo'],
        'Sociologie': ['Sociologie Générale']
    }
    
    for faculte, departements in FACULTES_ULC.items():
        for dept in departements:
            cours_dept = cours_par_dept.get(dept, ['Cours Général'])
            for nom_cours in cours_dept:
                promotions = random.sample(PROMOTIONS, random.randint(2, 3))
                
                cours_data.append({
                    'id': cours_id,
                    'name': nom_cours,
                    'code': f'{faculte[:3].upper()}{cours_id:03d}',
                    'credits': random.randint(3, 6),
                    'faculte': faculte,
                    'departement': dept,
                    'promotions': promotions,
                    'description': f'Cours de {nom_cours} - {dept}'
                })
                cours_id += 1
    
    # Assignations cours-professeurs
    course_assignments_data = {}
    for cours in cours_data:
        profs_dept = [u for u in users_data.values() 
                     if u['role'] == 'teacher' and u.get('departement') == cours['departement']]
        if profs_dept:
            prof_assigne = random.choice(profs_dept)
            course_assignments_data[cours['id']] = [prof_assigne['username']]
    
    # Inscriptions étudiants
    course_enrollments_data = {}
    for cours in cours_data:
        etudiants_eligibles = [u for u in users_data.values() 
                              if u['role'] == 'student' and 
                                 u.get('faculte') == cours['faculte'] and 
                                 u.get('promotion') in cours['promotions']]
        
        nb_inscrits = min(random.randint(3, 8), len(etudiants_eligibles))
        inscrits = random.sample(etudiants_eligibles, nb_inscrits)
        course_enrollments_data[cours['id']] = [e['username'] for e in inscrits]
    
    # Devoirs
    assignments_data = []
    assignment_id = 1
    
    titres = ['TP Pratique', 'Projet', 'Examen Blanc', 'Travail Dirigé', 'Étude de Cas']
    
    for cours in cours_data:
        if cours['id'] in course_assignments_data:
            prof_username = course_assignments_data[cours['id']][0]
            prof = users_data[prof_username]
            
            due_date = datetime.now() + timedelta(days=random.randint(7, 30))
            
            assignments_data.append({
                'id': assignment_id,
                'title': f"{random.choice(titres)} - {cours['name']}",
                'description': f"Travail pour le cours de {cours['name']}",
                'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
                'course_id': cours['id'],
                'course': cours['name'],
                'teacher': prof_username,
                'teacher_name': prof['name'],
                'files': [],
                'auto_correct': random.choice([True, False]),
                'plagiarism_check': True,
                'max_score': 100,
                'is_group_work': False,
                'results_published': False
            })
            assignment_id += 1
    
    # Soumissions
    submissions_data = []
    submission_id = 1
    
    for assignment in assignments_data:
        etudiants_inscrits = course_enrollments_data.get(assignment['course_id'], [])
        nb_soumissions = int(len(etudiants_inscrits) * 0.7)  # 70% soumettent
        
        for i in range(nb_soumissions):
            if i < len(etudiants_inscrits):
                etudiant = etudiants_inscrits[i]
                submit_date = datetime.now() - timedelta(days=random.randint(1, 10))
                
                submissions_data.append({
                    'id': submission_id,
                    'student': etudiant,
                    'assignment_id': assignment['id'],
                    'filename': f"{etudiant}_{assignment['id']}_travail.pdf",
                    'submitted_at': submit_date.strftime('%Y-%m-%d %H:%M:%S')
                })
                submission_id += 1
    
    return {
        'users': users_data,
        'admin_courses': cours_data,
        'course_assignments': course_assignments_data,
        'course_enrollments': course_enrollments_data,
        'assignments': assignments_data,
        'submissions': submissions_data,
        'next_course_admin_id': cours_id,
        'next_assignment_id': assignment_id
    }

if __name__ == "__main__":
    data = init_data()
    print(f"Données générées:")
    print(f"- Utilisateurs: {len(data['users'])}")
    print(f"- Cours: {len(data['admin_courses'])}")
    print(f"- Devoirs: {len(data['assignments'])}")
    print(f"- Soumissions: {len(data['submissions'])}")