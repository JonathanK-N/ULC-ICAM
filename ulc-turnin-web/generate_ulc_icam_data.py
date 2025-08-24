#!/usr/bin/env python3
"""
Generateur de donnees de test pour l'Universite Loyola du Congo - ICAM
"""

import json
import random
from datetime import datetime, timedelta

# Configuration de l'universite
FACULTES = {
    'Sciences': ['Mathematiques-Informatique', 'Physique', 'Chimie', 'Biologie'],
    'Medecine': ['Medecine Interne', 'Chirurgie', 'Pediatrie'],
    'Droit': ['Droit Prive', 'Droit Public', 'Droit International'],
    'Sciences Economiques': ['Economie', 'Gestion', 'Finance'],
    'Polytechnique': ['Genie Civil', 'Genie Electrique', 'Genie Mecanique'],
    'Lettres et Sciences Humaines': ['Philosophie', 'Histoire', 'Sociologie']
}

PROMOTIONS = ['L1', 'L2', 'L3', 'M1', 'M2']
GRADES = ['Prof. Ordinaire', 'Prof. Associe', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attache']

# Cours par faculte et promotion
COURS_PAR_FACULTE = {
    'Sciences': {
        'L1': ['Mathematiques I', 'Physique Generale', 'Chimie Generale', 'Biologie Cellulaire'],
        'L2': ['Mathematiques II', 'Physique Moderne', 'Chimie Organique', 'Genetique'],
        'L3': ['Analyse Numerique', 'Thermodynamique', 'Biochimie', 'Ecologie'],
        'M1': ['Recherche Operationnelle', 'Physique Quantique', 'Chimie Analytique'],
        'M2': ['Intelligence Artificielle', 'Physique des Particules', 'Biotechnologie']
    },
    'Medecine': {
        'L1': ['Anatomie I', 'Physiologie I', 'Histologie', 'Embryologie'],
        'L2': ['Anatomie II', 'Physiologie II', 'Pathologie Generale', 'Pharmacologie I'],
        'L3': ['Semiologie', 'Pathologie Speciale', 'Pharmacologie II', 'Microbiologie'],
        'M1': ['Medecine Interne', 'Chirurgie Generale', 'Pediatrie'],
        'M2': ['Specialites Medicales', 'Urgences', 'Ethique Medicale']
    },
    'Droit': {
        'L1': ['Introduction au Droit', 'Droit Civil I', 'Droit Constitutionnel', 'Histoire du Droit'],
        'L2': ['Droit Civil II', 'Droit Penal I', 'Droit Administratif', 'Droit Commercial'],
        'L3': ['Droit Penal II', 'Procedure Civile', 'Droit du Travail', 'Droit International'],
        'M1': ['Droit des Affaires', 'Droit Fiscal', 'Droit de la Famille'],
        'M2': ['Contentieux Administratif', 'Arbitrage', 'Droit Compare']
    },
    'Sciences Economiques': {
        'L1': ['Microeconomie I', 'Macroeconomie I', 'Mathematiques Economiques', 'Statistiques'],
        'L2': ['Microeconomie II', 'Macroeconomie II', 'Comptabilite Generale', 'Finance I'],
        'L3': ['Econometrie', 'Finance II', 'Marketing', 'Gestion des Ressources Humaines'],
        'M1': ['Economie Internationale', 'Finance d\'Entreprise', 'Audit'],
        'M2': ['Politique Economique', 'Finance de Marche', 'Strategie d\'Entreprise']
    },
    'Polytechnique': {
        'L1': ['Mathematiques pour Ingenieurs', 'Physique Appliquee', 'Dessin Technique', 'Informatique'],
        'L2': ['Resistance des Materiaux', 'Electrotechnique', 'Mecanique des Fluides', 'Programmation'],
        'L3': ['Beton Arme', 'Electronique', 'Thermique', 'Bases de Donnees'],
        'M1': ['Geotechnique', 'Automatique', 'Energetique', 'Reseaux'],
        'M2': ['Projet de Fin d\'Etudes', 'Management de Projet', 'Innovation Technologique']
    },
    'Lettres et Sciences Humaines': {
        'L1': ['Philosophie Generale', 'Histoire Contemporaine', 'Sociologie Generale', 'Methodologie'],
        'L2': ['Ethique', 'Histoire de l\'Afrique', 'Anthropologie', 'Psychologie'],
        'L3': ['Philosophie Politique', 'Histoire du Congo', 'Sociologie Urbaine', 'Linguistique'],
        'M1': ['Epistemologie', 'Recherche Historique', 'Sociologie du Developpement'],
        'M2': ['Philosophie Africaine', 'Patrimoine Culturel', 'Politiques Sociales']
    }
}

def generer_professeurs():
    """Genere des professeurs pour l'ULC-ICAM"""
    professeurs = []
    noms_congo = [
        ('Mukendi', 'Jean-Baptiste'), ('Tshisekedi', 'Marie-Claire'), ('Kabila', 'Joseph'),
        ('Mbuyi', 'Therese'), ('Kasongo', 'Pierre'), ('Ngoy', 'Francoise'),
        ('Ilunga', 'Emmanuel'), ('Mwamba', 'Sylvie'), ('Katanga', 'Andre'),
        ('Luboya', 'Bernadette'), ('Mulumba', 'Francois'), ('Kabongo', 'Jeanne'),
        ('Tshiaba', 'Michel'), ('Mujinga', 'Celestine'), ('Kalala', 'Robert')
    ]
    
    prof_id = 1
    for faculte, departements in FACULTES.items():
        for dept in departements:
            for i in range(2):  # 2 professeurs par departement
                nom, prenom = random.choice(noms_congo)
                grade = random.choice(GRADES)
                
                prof = {
                    'username': f'prof{prof_id:03d}',
                    'password': 'prof123',
                    'role': 'teacher',
                    'cip': f'PROF{prof_id:03d}',
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
                    'name': f'{grade} {prenom} {nom}'
                }
                professeurs.append(prof)
                prof_id += 1
    
    return professeurs

def generer_etudiants():
    """Genere des etudiants pour l'ULC-ICAM"""
    etudiants = []
    noms_congo = [
        ('Mukendi', 'Grace'), ('Tshisekedi', 'David'), ('Kabila', 'Sarah'),
        ('Mbuyi', 'Daniel'), ('Kasongo', 'Ruth'), ('Ngoy', 'Samuel'),
        ('Ilunga', 'Esther'), ('Mwamba', 'Jonathan'), ('Katanga', 'Rebecca'),
        ('Luboya', 'Matthieu'), ('Mulumba', 'Deborah'), ('Kabongo', 'Isaac'),
        ('Tshiaba', 'Naomi'), ('Mujinga', 'Caleb'), ('Kalala', 'Miriam'),
        ('Nkulu', 'Benjamin'), ('Mwenze', 'Rachel'), ('Kapend', 'Josue'),
        ('Lukusa', 'Hannah'), ('Mbayo', 'Elie'), ('Tshimanga', 'Lydia'),
        ('Kasanda', 'Moise'), ('Mwilambwe', 'Priscille'), ('Kabemba', 'Aaron')
    ]
    
    etud_id = 1
    for faculte in FACULTES.keys():
        for promotion in PROMOTIONS:
            nb_etudiants = random.randint(8, 12)
            for i in range(nb_etudiants):
                nom, prenom = random.choice(noms_congo)
                
                etudiant = {
                    'username': f'etud{etud_id:03d}',
                    'password': 'etud123',
                    'role': 'student',
                    'cip': f'ETUD{etud_id:03d}',
                    'nom': nom,
                    'prenom': prenom,
                    'sexe': random.choice(['M', 'F']),
                    'date_naissance': f'{random.randint(1995, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'promotion': promotion,
                    'faculte': faculte,
                    'telephone': f'+243{random.randint(800000000, 999999999)}',
                    'email': f'{prenom.lower()}.{nom.lower()}{etud_id}@student.ulc-icam.cd',
                    'adresse': f'Av. {random.choice(["Lumumba", "Mobutu", "Kabila", "Kasavubu"])}, Q. {random.choice(["Gombe", "Kinshasa", "Lemba", "Matete"])}, Kinshasa',
                    'name': f'{prenom} {nom}'
                }
                etudiants.append(etudiant)
                etud_id += 1
    
    return etudiants

def generer_cours():
    """Genere les cours de l'ULC-ICAM"""
    cours = []
    cours_id = 1
    
    for faculte, promotions_cours in COURS_PAR_FACULTE.items():
        dept = random.choice(FACULTES[faculte])
        for promotion, liste_cours in promotions_cours.items():
            for nom_cours in liste_cours:
                cours_obj = {
                    'id': cours_id,
                    'name': nom_cours,
                    'code': f'{faculte[:3].upper()}{promotion}{cours_id:03d}',
                    'credits': random.randint(3, 6),
                    'faculte': faculte,
                    'departement': dept,
                    'promotions': [promotion],
                    'description': f'Cours de {nom_cours} pour la promotion {promotion} en {faculte}'
                }
                cours.append(cours_obj)
                cours_id += 1
    
    return cours

def assigner_professeurs_cours(professeurs, cours):
    """Assigne les professeurs aux cours selon leur departement"""
    assignments = {}
    
    for cours_obj in cours:
        profs_eligibles = [
            p for p in professeurs 
            if p['faculte'] == cours_obj['faculte']
        ]
        
        if profs_eligibles:
            prof_assigne = random.choice(profs_eligibles)
            course_id = int(cours_obj['id'])
            if course_id not in assignments:
                assignments[course_id] = []
            assignments[course_id].append(prof_assigne['username'])
    
    return assignments

def inscrire_etudiants_cours(etudiants, cours):
    """Inscrit les etudiants aux cours de leur faculte et promotion"""
    enrollments = {}
    
    for cours_obj in cours:
        enrollments[int(cours_obj['id'])] = []
        
        etudiants_eligibles = [
            e for e in etudiants 
            if e['faculte'] == cours_obj['faculte'] and 
               e['promotion'] in cours_obj['promotions']
        ]
        
        for etudiant in etudiants_eligibles:
            enrollments[int(cours_obj['id'])].append(etudiant['username'])
    
    return enrollments

def generer_donnees_ulc_icam():
    """Genere toutes les donnees pour l'ULC-ICAM"""
    print("Generation des donnees pour l'Universite Loyola du Congo - ICAM")
    
    print("Generation des professeurs...")
    professeurs = generer_professeurs()
    
    print("Generation des etudiants...")
    etudiants = generer_etudiants()
    
    print("Generation des cours...")
    cours = generer_cours()
    
    print("Attribution des cours aux professeurs...")
    course_assignments = assigner_professeurs_cours(professeurs, cours)
    
    print("Inscription des etudiants aux cours...")
    course_enrollments = inscrire_etudiants_cours(etudiants, cours)
    
    users = {'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrateur ULC-ICAM'}}
    
    for prof in professeurs:
        users[prof['username']] = prof
    
    for etud in etudiants:
        users[etud['username']] = etud
    
    print(f"\nStatistiques generees:")
    print(f"   Professeurs: {len(professeurs)}")
    print(f"   Etudiants: {len(etudiants)}")
    print(f"   Cours: {len(cours)}")
    print(f"   Facultes: {len(FACULTES)}")
    
    return {
        'users': users,
        'admin_courses': cours,
        'course_assignments': course_assignments,
        'course_enrollments': course_enrollments,
        'next_course_admin_id': len(cours) + 1
    }

if __name__ == "__main__":
    data = generer_donnees_ulc_icam()
    
    with open('ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nDonnees sauvegardees dans 'ulc_icam_data.json'")
    print("\nPour integrer ces donnees dans l'application:")
    print("   1. Copiez le contenu du fichier JSON")
    print("   2. Remplacez les variables correspondantes dans app.py")
    print("   3. Redemarrez l'application")