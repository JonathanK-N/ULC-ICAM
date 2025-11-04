#!/usr/bin/env python3
"""
Test complet pour l'Université Loyola du Congo - ICAM
Génère des données réalistes : professeurs, étudiants, cours, devoirs et soumissions
"""

import sys
import os
sys.path.append('.')

from app import app, users, admin_courses, course_assignments, course_enrollments, assignments, submissions
from app import next_course_admin_id, next_assignment_id
import random
from datetime import datetime, timedelta

# Configuration ULC-ICAM
FACULTES_ULC = {
    'Sciences': ['Mathématiques-Informatique', 'Physique', 'Chimie', 'Biologie'],
    'Médecine': ['Médecine Interne', 'Chirurgie', 'Pédiatrie', 'Gynécologie'],
    'Droit': ['Droit Privé', 'Droit Public', 'Droit International'],
    'Sciences Économiques': ['Économie', 'Gestion', 'Finance', 'Comptabilité'],
    'Polytechnique': ['Génie Civil', 'Génie Électrique', 'Génie Mécanique'],
    'Lettres et Sciences Humaines': ['Philosophie', 'Histoire', 'Sociologie', 'Linguistique']
}

PROMOTIONS = ['L1', 'L2', 'L3', 'M1', 'M2']
GRADES = ['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']

# Noms congolais réalistes
NOMS_CONGO = [
    'MUKENDI', 'KABONGO', 'TSHILOBO', 'MBUYI', 'KASONGO', 'NGOY', 'KALALA', 
    'MWAMBA', 'KATANGA', 'LUBOYA', 'ILUNGA', 'KAYEMBE', 'MULAMBA', 'TSHIMANGA',
    'KAPEND', 'MUJINGA', 'KILOLO', 'MBAYO', 'NKASHAMA', 'TSHIBANGU'
]

PRENOMS = [
    'Jean', 'Marie', 'Pierre', 'Jeanne', 'Paul', 'Anne', 'André', 'Catherine',
    'Joseph', 'Françoise', 'Michel', 'Monique', 'François', 'Sylvie', 'Antoine',
    'Christine', 'Emmanuel', 'Brigitte', 'Daniel', 'Martine'
]

def generer_professeurs():
    """Génère 30 professeurs répartis dans toutes les facultés"""
    print("Génération des professeurs...")
    
    prof_id = 1
    for faculte, departements in FACULTES_ULC.items():
        for dept in departements:
            # 2-3 professeurs par département
            nb_profs = random.randint(2, 3)
            for i in range(nb_profs):
                if prof_id > 30:
                    break
                    
                nom = random.choice(NOMS_CONGO)
                prenom = random.choice(PRENOMS)
                grade = random.choice(GRADES)
                
                username = f'prof{prof_id:03d}'
                prof = {
                    'username': username,
                    'password': 'prof123',
                    'role': 'teacher',
                    'cip': f'P{2024000 + prof_id}',
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
                
                users[username] = prof
                prof_id += 1
    
    print(f"OK - {prof_id-1} professeurs generes")

def generer_etudiants():
    """Génère 80 étudiants répartis dans toutes les facultés et promotions"""
    print("Génération des étudiants...")
    
    etud_id = 1
    for faculte in FACULTES_ULC.keys():
        for promotion in PROMOTIONS:
            # 2-4 étudiants par faculté/promotion
            nb_etuds = random.randint(2, 4)
            for i in range(nb_etuds):
                if etud_id > 80:
                    break
                    
                nom = random.choice(NOMS_CONGO)
                prenom = random.choice(PRENOMS)
                
                username = f'etud{etud_id:03d}'
                etudiant = {
                    'username': username,
                    'password': 'etud123',
                    'role': 'student',
                    'cip': f'E{2024000 + etud_id}',
                    'nom': nom,
                    'prenom': prenom,
                    'sexe': random.choice(['M', 'F']),
                    'date_naissance': f'{random.randint(1995, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'promotion': promotion,
                    'faculte': faculte,
                    'telephone': f'+243{random.randint(800000000, 999999999)}',
                    'email': f'{prenom.lower()}.{nom.lower()}{etud_id}@student.ulc-icam.cd',
                    'adresse': f'Av. {random.choice(["Lumumba", "Mobutu", "Kabila", "Kasavubu"])}, Q. {random.choice(["Gombe", "Kinshasa", "Lemba", "Matete"])}, Kinshasa',
                    'name': f'{prenom} {nom}',
                    'must_change_password': True
                }
                
                users[username] = etudiant
                etud_id += 1
    
    print(f"OK - {etud_id-1} etudiants generes")

def generer_cours():
    """Génère des cours pour chaque faculté et département"""
    print("Génération des cours...")
    
    cours_par_dept = {
        'Mathématiques-Informatique': ['Algorithmique', 'Base de Données', 'Programmation Python', 'Analyse Numérique'],
        'Physique': ['Mécanique', 'Électromagnétisme', 'Thermodynamique', 'Optique'],
        'Chimie': ['Chimie Générale', 'Chimie Organique', 'Chimie Analytique'],
        'Biologie': ['Biologie Cellulaire', 'Génétique', 'Écologie'],
        'Médecine Interne': ['Pathologie', 'Cardiologie', 'Pneumologie'],
        'Chirurgie': ['Chirurgie Générale', 'Orthopédie', 'Neurochirurgie'],
        'Pédiatrie': ['Pédiatrie Générale', 'Néonatologie'],
        'Gynécologie': ['Obstétrique', 'Gynécologie Médicale'],
        'Droit Privé': ['Droit Civil', 'Droit Commercial', 'Droit du Travail'],
        'Droit Public': ['Droit Constitutionnel', 'Droit Administratif'],
        'Droit International': ['Droit International Public', 'Droit International Privé'],
        'Économie': ['Microéconomie', 'Macroéconomie', 'Économétrie'],
        'Gestion': ['Management', 'Marketing', 'GRH'],
        'Finance': ['Finance d\'Entreprise', 'Marchés Financiers'],
        'Comptabilité': ['Comptabilité Générale', 'Audit'],
        'Génie Civil': ['Résistance des Matériaux', 'Béton Armé', 'Hydraulique'],
        'Génie Électrique': ['Électrotechnique', 'Électronique', 'Automatique'],
        'Génie Mécanique': ['Mécanique des Fluides', 'Thermique'],
        'Philosophie': ['Philosophie Générale', 'Éthique', 'Logique'],
        'Histoire': ['Histoire du Congo', 'Histoire Contemporaine'],
        'Sociologie': ['Sociologie Générale', 'Sociologie Urbaine'],
        'Linguistique': ['Linguistique Générale', 'Phonétique']
    }
    
    global next_course_admin_id
    cours_id = next_course_admin_id
    
    for faculte, departements in FACULTES_ULC.items():
        for dept in departements:
            cours_dept = cours_par_dept.get(dept, ['Cours Général'])
            for nom_cours in cours_dept:
                promotions = random.sample(PROMOTIONS, random.randint(2, 4))
                
                cours = {
                    'id': cours_id,
                    'name': nom_cours,
                    'code': f'{faculte[:3].upper()}{cours_id:03d}',
                    'credits': random.randint(3, 6),
                    'faculte': faculte,
                    'departement': dept,
                    'promotions': promotions,
                    'description': f'Cours de {nom_cours} - Département {dept}'
                }
                
                admin_courses.append(cours)
                cours_id += 1
    
    next_course_admin_id = cours_id
    print(f"OK - {len(admin_courses)} cours generes")

def assigner_professeurs_cours():
    """Assigne chaque professeur à au moins 2 cours de son département"""
    print("Attribution des cours aux professeurs...")
    
    for cours in admin_courses:
        # Trouver les professeurs du même département
        profs_dept = [
            username for username, user in users.items()
            if user['role'] == 'teacher' and user.get('departement') == cours['departement']
        ]
        
        if profs_dept:
            # Assigner 1-2 professeurs par cours
            nb_profs = min(random.randint(1, 2), len(profs_dept))
            profs_assignes = random.sample(profs_dept, nb_profs)
            course_assignments[cours['id']] = profs_assignes
    
    # Vérifier que chaque prof a au moins 2 cours
    for username, user in users.items():
        if user['role'] == 'teacher':
            cours_prof = sum(1 for assignes in course_assignments.values() if username in assignes)
            if cours_prof < 2:
                # Assigner des cours supplémentaires de sa faculté
                cours_faculte = [c for c in admin_courses if c['faculte'] == user['faculte']]
                for cours in random.sample(cours_faculte, min(2, len(cours_faculte))):
                    if cours['id'] not in course_assignments:
                        course_assignments[cours['id']] = []
                    if username not in course_assignments[cours['id']]:
                        course_assignments[cours['id']].append(username)
    
    print(f"OK - Cours assignes aux professeurs")

def inscrire_etudiants_cours():
    """Inscrit chaque étudiant à au moins 3 cours de sa faculté"""
    print("Inscription des étudiants aux cours...")
    
    for username, user in users.items():
        if user['role'] == 'student':
            # Trouver les cours de sa faculté et promotion
            cours_eligibles = [
                c for c in admin_courses
                if c['faculte'] == user['faculte'] and user['promotion'] in c['promotions']
            ]
            
            # Inscrire à 3-5 cours
            nb_cours = min(random.randint(3, 5), len(cours_eligibles))
            cours_choisis = random.sample(cours_eligibles, nb_cours)
            
            for cours in cours_choisis:
                if cours['id'] not in course_enrollments:
                    course_enrollments[cours['id']] = []
                if username not in course_enrollments[cours['id']]:
                    course_enrollments[cours['id']].append(username)
    
    print(f"OK - Etudiants inscrits aux cours")

def generer_devoirs():
    """Génère des devoirs pour les cours avec professeurs assignés"""
    print("Génération des devoirs...")
    
    global next_assignment_id
    
    titres_devoirs = [
        'TP Pratique', 'Projet de Fin de Module', 'Examen Blanc', 'Travail Dirigé',
        'Étude de Cas', 'Rapport de Recherche', 'Analyse Critique', 'Synthèse',
        'Exercices Pratiques', 'Mémoire', 'Présentation', 'Travail de Groupe'
    ]
    
    for cours in admin_courses:
        if cours['id'] in course_assignments and course_assignments[cours['id']]:
            # 1-3 devoirs par cours
            nb_devoirs = random.randint(1, 3)
            
            for i in range(nb_devoirs):
                prof_username = random.choice(course_assignments[cours['id']])
                prof = users[prof_username]
                
                due_date = datetime.now() + timedelta(days=random.randint(7, 60))
                
                devoir = {
                    'id': next_assignment_id,
                    'title': f"{random.choice(titres_devoirs)} - {cours['name']}",
                    'description': f"Travail à rendre pour le cours de {cours['name']}. Respectez les consignes et la date limite.",
                    'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
                    'course_id': cours['id'],
                    'course': cours['name'],
                    'teacher': prof_username,
                    'teacher_name': prof['name'],
                    'files': [],
                    'auto_correct': random.choice([True, False]),
                    'plagiarism_check': random.choice([True, True, False]),  # 66% de chance
                    'max_score': random.choice([20, 50, 100]),
                    'is_group_work': random.choice([True, False]),
                    'group_formation': random.choice(['manual', 'auto']),
                    'group_size': random.randint(2, 4),
                    'results_release_date': (due_date + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
                    'results_published': random.choice([True, False])
                }
                
                assignments.append(devoir)
                next_assignment_id += 1
    
    print(f"OK - {len(assignments)} devoirs generes")

def generer_soumissions():
    """Génère des soumissions d'étudiants pour les devoirs"""
    print("Génération des soumissions...")
    
    submission_id = 1
    
    for assignment in assignments:
        # Étudiants inscrits au cours du devoir
        etudiants_inscrits = course_enrollments.get(assignment['course_id'], [])
        
        # 50-80% des étudiants soumettent
        nb_soumissions = int(len(etudiants_inscrits) * random.uniform(0.5, 0.8))
        etudiants_soumettent = random.sample(etudiants_inscrits, min(nb_soumissions, len(etudiants_inscrits)))
        
        for etudiant in etudiants_soumettent:
            # Date de soumission aléatoire avant la date limite
            due_date = datetime.strptime(assignment['due_date'], '%Y-%m-%dT%H:%M')
            submit_date = due_date - timedelta(days=random.randint(1, 14))
            
            filename = f"{etudiant}_{assignment['id']}_{submit_date.strftime('%Y%m%d_%H%M%S')}_travail.pdf"
            
            soumission = {
                'id': submission_id,
                'student': etudiant,
                'assignment_id': assignment['id'],
                'filename': filename,
                'submitted_at': submit_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            submissions.append(soumission)
            submission_id += 1
    
    print(f"OK - {len(submissions)} soumissions generees")

def afficher_statistiques():
    """Affiche les statistiques finales"""
    print("\n" + "="*50)
    print("STATISTIQUES ULC-ICAM")
    print("="*50)
    
    # Compter par role
    admins = sum(1 for u in users.values() if u['role'] == 'admin')
    profs = sum(1 for u in users.values() if u['role'] == 'teacher')
    etuds = sum(1 for u in users.values() if u['role'] == 'student')
    
    print(f"Utilisateurs:")
    print(f"   - Administrateurs: {admins}")
    print(f"   - Professeurs: {profs}")
    print(f"   - Etudiants: {etuds}")
    print(f"   - Total: {len(users)}")
    
    print(f"\nAcademique:")
    print(f"   - Facultes: {len(FACULTES_ULC)}")
    print(f"   - Cours: {len(admin_courses)}")
    print(f"   - Devoirs: {len(assignments)}")
    print(f"   - Soumissions: {len(submissions)}")
    
    # Statistiques par faculte
    print(f"\nRepartition par faculte:")
    for faculte in FACULTES_ULC.keys():
        etuds_fac = sum(1 for u in users.values() if u['role'] == 'student' and u.get('faculte') == faculte)
        profs_fac = sum(1 for u in users.values() if u['role'] == 'teacher' and u.get('faculte') == faculte)
        cours_fac = sum(1 for c in admin_courses if c['faculte'] == faculte)
        print(f"   - {faculte}: {etuds_fac} étudiants, {profs_fac} profs, {cours_fac} cours")
    
    # Taux de soumission
    if assignments:
        total_possible = sum(len(course_enrollments.get(a['course_id'], [])) for a in assignments)
        taux_soumission = (len(submissions) / total_possible * 100) if total_possible > 0 else 0
        print(f"\nTaux de soumission global: {taux_soumission:.1f}%")

def main():
    """Fonction principale de génération des données de test"""
    print("GENERATION DES DONNEES DE TEST - ULC-ICAM")
    print("=" * 60)
    
    # Vider les données existantes (sauf admin)
    admin_user = users.get('admin')
    users.clear()
    if admin_user:
        users['admin'] = admin_user
    
    admin_courses.clear()
    course_assignments.clear()
    course_enrollments.clear()
    assignments.clear()
    submissions.clear()
    
    # Génération des données
    generer_professeurs()
    generer_etudiants()
    generer_cours()
    assigner_professeurs_cours()
    inscrire_etudiants_cours()
    generer_devoirs()
    generer_soumissions()
    
    # Affichage des statistiques
    afficher_statistiques()
    
    print("\nGENERATION TERMINEE AVEC SUCCES!")
    print("\nComptes de test:")
    print("   - Admin: admin / admin123")
    print("   - Professeurs: prof001-prof030 / prof123")
    print("   - Etudiants: etud001-etud080 / etud123")
    print("\nLancez l'application: python app.py")

if __name__ == "__main__":
    main()