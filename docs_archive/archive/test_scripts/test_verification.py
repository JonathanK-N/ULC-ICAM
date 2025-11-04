#!/usr/bin/env python3
"""
Script de vérification des fonctionnalités après génération des données ULC-ICAM
"""

import sys
import os
sys.path.append('.')

from app import users, admin_courses, course_assignments, course_enrollments, assignments, submissions

def verifier_donnees():
    """Vérifie que les données ont été correctement générées"""
    print("VERIFICATION DES DONNEES GENEREES")
    print("=" * 50)
    
    # Vérification des utilisateurs
    admins = [u for u in users.values() if u['role'] == 'admin']
    profs = [u for u in users.values() if u['role'] == 'teacher']
    etuds = [u for u in users.values() if u['role'] == 'student']
    
    print(f"Utilisateurs: {len(users)} total")
    print(f"  - Admins: {len(admins)}")
    print(f"  - Professeurs: {len(profs)}")
    print(f"  - Etudiants: {len(etuds)}")
    
    # Vérification des cours
    print(f"\nCours: {len(admin_courses)} total")
    
    # Vérification des assignations
    cours_avec_profs = sum(1 for c_id in course_assignments if course_assignments[c_id])
    print(f"Cours avec professeurs: {cours_avec_profs}")
    
    # Vérification que chaque prof a au moins 2 cours
    profs_sans_cours = []
    for username, user in users.items():
        if user['role'] == 'teacher':
            nb_cours = sum(1 for assignes in course_assignments.values() if username in assignes)
            if nb_cours < 2:
                profs_sans_cours.append(f"{username} ({nb_cours} cours)")
    
    if profs_sans_cours:
        print(f"ATTENTION: Professeurs avec moins de 2 cours: {profs_sans_cours}")
    else:
        print("OK - Tous les professeurs ont au moins 2 cours")
    
    # Vérification des inscriptions étudiants
    etuds_sans_cours = []
    for username, user in users.items():
        if user['role'] == 'student':
            nb_cours = sum(1 for inscrits in course_enrollments.values() if username in inscrits)
            if nb_cours < 3:
                etuds_sans_cours.append(f"{username} ({nb_cours} cours)")
    
    if etuds_sans_cours:
        print(f"ATTENTION: Etudiants avec moins de 3 cours: {len(etuds_sans_cours)}")
    else:
        print("OK - Tous les etudiants ont au moins 3 cours")
    
    print(f"\nDevoirs: {len(assignments)} total")
    print(f"Soumissions: {len(submissions)} total")
    
    return len(profs_sans_cours) == 0 and len(etuds_sans_cours) == 0

def tester_comptes_connexion():
    """Teste quelques comptes de connexion"""
    print("\nTEST DES COMPTES DE CONNEXION")
    print("=" * 40)
    
    # Test admin
    if 'admin' in users and users['admin']['password'] == 'admin123':
        print("OK - Compte admin fonctionnel")
    else:
        print("ERREUR - Compte admin non fonctionnel")
    
    # Test quelques professeurs
    profs_test = ['prof001', 'prof015', 'prof030']
    for prof in profs_test:
        if prof in users and users[prof]['password'] == 'prof123':
            print(f"OK - Compte {prof} fonctionnel")
        else:
            print(f"ERREUR - Compte {prof} non fonctionnel")
    
    # Test quelques étudiants
    etuds_test = ['etud001', 'etud040', 'etud080']
    for etud in etuds_test:
        if etud in users and users[etud]['password'] == 'etud123':
            print(f"OK - Compte {etud} fonctionnel")
        else:
            print(f"ERREUR - Compte {etud} non fonctionnel")

def afficher_exemples():
    """Affiche des exemples de données générées"""
    print("\nEXEMPLES DE DONNEES GENEREES")
    print("=" * 40)
    
    # Exemple professeur
    prof_exemple = next((u for u in users.values() if u['role'] == 'teacher'), None)
    if prof_exemple:
        print(f"Professeur exemple: {prof_exemple['name']}")
        print(f"  - Faculte: {prof_exemple['faculte']}")
        print(f"  - Departement: {prof_exemple['departement']}")
        print(f"  - Email: {prof_exemple['email']}")
    
    # Exemple étudiant
    etud_exemple = next((u for u in users.values() if u['role'] == 'student'), None)
    if etud_exemple:
        print(f"\nEtudiant exemple: {etud_exemple['name']}")
        print(f"  - Faculte: {etud_exemple['faculte']}")
        print(f"  - Promotion: {etud_exemple['promotion']}")
        print(f"  - Email: {etud_exemple['email']}")
    
    # Exemple cours
    if admin_courses:
        cours_exemple = admin_courses[0]
        print(f"\nCours exemple: {cours_exemple['name']}")
        print(f"  - Code: {cours_exemple['code']}")
        print(f"  - Faculte: {cours_exemple['faculte']}")
        print(f"  - Credits: {cours_exemple['credits']}")
    
    # Exemple devoir
    if assignments:
        devoir_exemple = assignments[0]
        print(f"\nDevoir exemple: {devoir_exemple['title']}")
        print(f"  - Cours: {devoir_exemple['course']}")
        print(f"  - Professeur: {devoir_exemple['teacher_name']}")
        print(f"  - Date limite: {devoir_exemple['due_date']}")

def main():
    """Fonction principale de vérification"""
    print("VERIFICATION COMPLETE - ULC-ICAM")
    print("=" * 50)
    
    # Vérifications
    donnees_ok = verifier_donnees()
    tester_comptes_connexion()
    afficher_exemples()
    
    print("\n" + "=" * 50)
    if donnees_ok:
        print("VERIFICATION REUSSIE - Toutes les donnees sont correctes")
    else:
        print("VERIFICATION PARTIELLE - Quelques problemes detectes")
    
    print("\nPour tester l'application:")
    print("1. Lancez: python app.py")
    print("2. Ouvrez: http://localhost:5000")
    print("3. Connectez-vous avec les comptes de test")

if __name__ == "__main__":
    main()