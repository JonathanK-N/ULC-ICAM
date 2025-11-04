#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger l'assignation des cours aux professeurs selon leurs spécialités
"""

import json

def fix_course_assignments():
    print("Correction de l'assignation des cours aux professeurs...")
    
    # Charger les données
    with open('ulc-turnin-web/ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Mapping des cours aux professeurs selon leurs spécialités
    course_professor_mapping = {
        # Mathématiques & Informatique - Prof01 (Algorithmique) et Prof02 (Base de Données)
        1: "prof01",  # Algorithmique et Structures de Données
        2: "prof01",  # Programmation Python
        3: "prof02",  # Base de Données
        4: "prof01",  # Développement Web
        5: "prof10",  # Intelligence Artificielle (Prof. Hadidja - IA)
        6: "prof10",  # Machine Learning
        
        # Génie Informatique - Prof09 (Réseaux) et Prof10 (IA)
        7: "prof09",  # Programmation C++
        8: "prof09",  # Réseaux Informatiques
        9: "prof09",  # Sécurité Informatique
        10: "prof10", # Systèmes Distribués
        
        # Génie Électrique - Prof05 (Électronique) et Prof06 (Automatique)
        11: "prof05", # Circuits Électriques
        12: "prof05", # Électronique Analogique
        13: "prof06", # Automatique
        14: "prof05", # Systèmes Embarqués
        
        # Génie Mécanique - Prof03 (Mécanique des Fluides) et Prof04 (Thermodynamique)
        15: "prof03", # Mécanique du Point
        16: "prof04", # Thermodynamique
        17: "prof03", # Mécanique des Fluides
        18: "prof03", # Conception Mécanique
        
        # Physique & Chimie - Prof07 (Chimie Organique) et Prof08 (Physique Quantique)
        19: "prof08", # Physique Générale
        20: "prof07"  # Chimie Organique
    }
    
    # Mettre à jour les assignations de cours
    for course_id, prof_username in course_professor_mapping.items():
        data['course_assignments'][str(course_id)] = [prof_username]
    
    # Mettre à jour les devoirs avec les bons professeurs
    for assignment in data['assignments']:
        course_id = assignment['course_id']
        if course_id in course_professor_mapping:
            prof_username = course_professor_mapping[course_id]
            assignment['teacher'] = prof_username
            assignment['teacher_name'] = data['users'][prof_username]['name']
    
    # Sauvegarder les données corrigées
    with open('ulc-turnin-web/ulc_icam_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Afficher le résumé des assignations
    print("Assignations corrigées:")
    prof_course_count = {}
    for course_id, prof_list in data['course_assignments'].items():
        prof = prof_list[0]
        if prof not in prof_course_count:
            prof_course_count[prof] = 0
        prof_course_count[prof] += 1
    
    for prof, count in prof_course_count.items():
        prof_name = data['users'][prof]['name']
        specialite = data['users'][prof]['specialite']
        print(f"  - {prof_name} ({specialite}): {count} cours")
    
    print("Correction terminée avec succès!")

if __name__ == "__main__":
    fix_course_assignments()