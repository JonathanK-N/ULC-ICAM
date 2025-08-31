import random
from datetime import datetime, timedelta

# Noms congolais réalistes
noms_congolais = [
    'MUKENDI', 'KABONGO', 'TSHILOBO', 'MBUYI', 'KASONGO', 'NGOY', 'KALALA', 'MWAMBA', 'KATANGA', 'LUBOYA',
    'ILUNGA', 'KAYEMBE', 'MULAMBA', 'TSHIMANGA', 'KAPEND', 'MUJINGA', 'KILOLO', 'MBAYO', 'NKASHAMA', 'TSHIBANGU',
    'MUTOMBO', 'KABILA', 'LUMUMBA', 'MOBUTU', 'TSHISEKEDI', 'BEMBA', 'KATUMBI', 'KAMERHE', 'MUZITO', 'RUBERWA'
]

prenoms_masculins = [
    'Jean', 'Pierre', 'Paul', 'André', 'Joseph', 'Michel', 'François', 'Antoine', 'Emmanuel', 'Daniel',
    'Patrick', 'Claude', 'Robert', 'Bernard', 'Alain', 'Philippe', 'Christian', 'Didier', 'Pascal', 'Olivier'
]

prenoms_feminins = [
    'Marie', 'Jeanne', 'Anne', 'Catherine', 'Françoise', 'Monique', 'Sylvie', 'Christine', 'Brigitte', 'Martine',
    'Nicole', 'Jacqueline', 'Nathalie', 'Isabelle', 'Véronique', 'Chantal', 'Dominique', 'Patricia', 'Sandrine', 'Valérie'
]

postnom_prefixes = ['wa', 'bin', 'binti', 'mwa', 'tshi', 'ka', 'mu', 'ki', 'lu', 'ma']

facultes_departements = {
    'Sciences': ['Mathématiques-Informatique', 'Physique', 'Chimie', 'Biologie', 'Géologie'],
    'Médecine': ['Médecine Interne', 'Chirurgie', 'Pédiatrie', 'Gynécologie', 'Anatomie'],
    'Droit': ['Droit Privé', 'Droit Public', 'Droit International', 'Droit Commercial'],
    'Sciences Économiques': ['Économie Politique', 'Gestion', 'Comptabilité', 'Finance'],
    'Polytechnique': ['Génie Civil', 'Génie Électrique', 'Génie Mécanique', 'Génie Informatique'],
    'Lettres et Sciences Humaines': ['Histoire', 'Géographie', 'Philosophie', 'Littérature', 'Linguistique']
}

cours_par_departement = {
    'Mathématiques-Informatique': [
        'Algorithmique et Programmation', 'Structures de Données', 'Base de Données', 'Réseaux Informatiques',
        'Génie Logiciel', 'Intelligence Artificielle', 'Analyse Numérique', 'Algèbre Linéaire', 'Calcul Différentiel'
    ],
    'Physique': [
        'Mécanique Classique', 'Électromagnétisme', 'Thermodynamique', 'Physique Quantique', 'Optique',
        'Physique Nucléaire', 'Mécanique des Fluides', 'Physique des Matériaux'
    ],
    'Chimie': [
        'Chimie Générale', 'Chimie Organique', 'Chimie Inorganique', 'Chimie Analytique', 'Biochimie',
        'Chimie Physique', 'Chimie Industrielle'
    ],
    'Biologie': [
        'Biologie Cellulaire', 'Génétique', 'Écologie', 'Microbiologie', 'Physiologie', 'Botanique', 'Zoologie'
    ],
    'Médecine Interne': [
        'Pathologie Générale', 'Cardiologie', 'Pneumologie', 'Gastroentérologie', 'Néphrologie', 'Endocrinologie'
    ],
    'Chirurgie': [
        'Chirurgie Générale', 'Orthopédie', 'Neurochirurgie', 'Chirurgie Cardiovasculaire', 'Urologie'
    ],
    'Droit Privé': [
        'Droit Civil', 'Droit Commercial', 'Droit du Travail', 'Droit de la Famille', 'Droit des Contrats'
    ],
    'Droit Public': [
        'Droit Constitutionnel', 'Droit Administratif', 'Droit Pénal', 'Droit International Public'
    ],
    'Économie Politique': [
        'Microéconomie', 'Macroéconomie', 'Économie du Développement', 'Économie Internationale', 'Économétrie'
    ],
    'Gestion': [
        'Management', 'Marketing', 'Gestion des Ressources Humaines', 'Gestion Financière', 'Stratégie d\'Entreprise'
    ],
    'Génie Civil': [
        'Résistance des Matériaux', 'Béton Armé', 'Construction Métallique', 'Hydraulique', 'Topographie'
    ],
    'Génie Électrique': [
        'Électrotechnique', 'Électronique', 'Automatique', 'Télécommunications', 'Énergie Électrique'
    ]
}

def generer_donnees_test():
    # Générer 50 professeurs
    professeurs = []
    for i in range(50):
        sexe = random.choice(['M', 'F'])
        prenom = random.choice(prenoms_masculins if sexe == 'M' else prenoms_feminins)
        nom = random.choice(noms_congolais)
        postnom = random.choice(postnom_prefixes) + nom[:3].lower()
        
        faculte = random.choice(list(facultes_departements.keys()))
        departement = random.choice(facultes_departements[faculte])
        
        prof = {
            'username': f'prof{i+1:03d}',
            'password': f'prof{i+1}pass',
            'role': 'teacher',
            'cip': f'P{2024000 + i}',
            'nom': nom,
            'postnom': postnom,
            'prenom': prenom,
            'sexe': sexe,
            'date_naissance': f'{random.randint(1960, 1980)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'grade': random.choice(['Prof. Ordinaire', 'Prof. Associé', 'Prof. Extraordinaire', 'CT', 'Ass.', 'Attaché']),
            'departement': departement,
            'faculte': faculte,
            'telephone': f'+243{random.randint(800000000, 999999999)}',
            'email': f'{prenom.lower()}.{nom.lower()}@unikin.ac.cd',
            'bureau': f'{random.choice(["A", "B", "C"])}-{random.randint(101, 350)}',
            'cours_dispenses': ', '.join(random.sample(cours_par_departement.get(departement, ['Cours Général']), min(3, len(cours_par_departement.get(departement, ['Cours Général']))))),
            'must_change_password': True,
            'name': f'{random.choice(["Prof.", "Dr.", "CT"])} {prenom} {nom}'
        }
        professeurs.append(prof)
    
    # Générer 100 étudiants
    etudiants = []
    for i in range(100):
        sexe = random.choice(['M', 'F'])
        prenom = random.choice(prenoms_masculins if sexe == 'M' else prenoms_feminins)
        nom = random.choice(noms_congolais)
        postnom = random.choice(postnom_prefixes) + nom[:3].lower()
        
        faculte = random.choice(list(facultes_departements.keys()))
        promotion = random.choice(['L1', 'L2', 'L3', 'M1', 'M2'])
        
        etudiant = {
            'username': f'etud{i+1:03d}',
            'password': f'etud{i+1}pass',
            'role': 'student',
            'cip': f'E{2024000 + i}',
            'nom': nom,
            'postnom': postnom,
            'prenom': prenom,
            'sexe': sexe,
            'date_naissance': f'{random.randint(1995, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
            'promotion': promotion,
            'faculte': faculte,
            'telephone': f'+243{random.randint(800000000, 999999999)}',
            'email': f'{prenom.lower()}.{nom.lower()}{i+1}@student.unikin.ac.cd',
            'adresse': f'Avenue {random.choice(["Kasavubu", "Lumumba", "Mobutu", "Kabila"])}, Commune de {random.choice(["Gombe", "Kinshasa", "Lemba", "Limete"])}',
            'must_change_password': True,
            'name': f'{prenom} {nom}'
        }
        etudiants.append(etudiant)
    
    # Générer 60 cours
    cours = []
    course_id = 1
    for faculte, departements in facultes_departements.items():
        for departement in departements:
            cours_dept = cours_par_departement.get(departement, ['Cours Général'])
            for cours_name in cours_dept:
                if course_id <= 60:
                    promotions = random.sample(['L1', 'L2', 'L3', 'M1', 'M2'], random.randint(1, 3))
                    cours_obj = {
                        'id': course_id,
                        'name': cours_name,
                        'code': f'{faculte[:3].upper()}{course_id:03d}',
                        'credits': random.randint(3, 8),
                        'faculte': faculte,
                        'departement': departement,
                        'promotions': promotions,
                        'description': f'Cours de {cours_name} pour les étudiants en {departement}'
                    }
                    cours.append(cours_obj)
                    course_id += 1
    
    # Assigner les cours aux professeurs
    course_assignments = {}
    for cours_obj in cours:
        # Trouver les professeurs du même département
        profs_dept = [p for p in professeurs if p['departement'] == cours_obj['departement']]
        if not profs_dept:
            # Si pas de prof dans le département, prendre de la même faculté
            profs_dept = [p for p in professeurs if p['faculte'] == cours_obj['faculte']]
        
        # Assigner 1-3 professeurs par cours
        nb_profs = min(random.randint(1, 3), len(profs_dept))
        profs_assignes = random.sample(profs_dept, nb_profs)
        course_assignments[int(cours_obj['id'])] = [p['username'] for p in profs_assignes]
    
    # Générer 95 devoirs
    devoirs = []
    titres_devoirs = [
        'TP Pratique', 'Projet de Fin de Module', 'Examen Blanc', 'Travail Dirigé', 'Étude de Cas',
        'Rapport de Recherche', 'Analyse Critique', 'Synthèse Documentaire', 'Exercices Pratiques',
        'Mémoire de Recherche', 'Présentation Orale', 'Travail de Groupe'
    ]
    
    for i in range(95):
        cours_obj = random.choice(cours)
        profs_assignes = course_assignments.get(int(cours_obj['id']), [])
        if profs_assignes:
            prof_username = random.choice(profs_assignes)
            prof = next(p for p in professeurs if p['username'] == prof_username)
            
            due_date = datetime.now() + timedelta(days=random.randint(7, 60))
            
            # Date de publication (1 jour après la date limite)
            release_date = due_date + timedelta(days=1)
            
            devoir = {
                'id': i + 1,
                'title': f"{random.choice(titres_devoirs)} - {cours_obj['name']}",
                'description': f"Travail à rendre pour le cours de {cours_obj['name']}. Veuillez respecter les consignes et la date limite.",
                'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
                'course_id': cours_obj['id'],
                'course': cours_obj['name'],
                'teacher': prof_username,
                'teacher_name': prof['name'],
                'files': [],
                'auto_correct': random.choice([True, False]),
                'plagiarism_check': random.choice([True, True, True, False]),  # 75% de chance
                'max_score': random.choice([20, 50, 100]),
                'results_release_date': release_date.strftime('%Y-%m-%dT%H:%M'),
                'results_published': random.choice([True, False])  # 50% publiés
            }
            devoirs.append(devoir)
    
    return professeurs, etudiants, cours, course_assignments, devoirs

if __name__ == '__main__':
    profs, etuds, cours, assignments, devoirs = generer_donnees_test()
    
    print("=== DONNÉES DE TEST GÉNÉRÉES ===")
    print(f"Professeurs: {len(profs)}")
    print(f"Étudiants: {len(etuds)}")
    print(f"Cours: {len(cours)}")
    print(f"Devoirs: {len(devoirs)}")
    
    # Afficher quelques exemples
    print("\n=== EXEMPLES ===")
    print("Premier professeur:", profs[0]['name'], "-", profs[0]['departement'])
    print("Premier étudiant:", etuds[0]['name'], "-", etuds[0]['faculte'], etuds[0]['promotion'])
    print("Premier cours:", cours[0]['name'], "-", cours[0]['code'])
    print("Premier devoir:", devoirs[0]['title'])