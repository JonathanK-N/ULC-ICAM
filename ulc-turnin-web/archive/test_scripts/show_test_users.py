#!/usr/bin/env python3
"""
Script pour afficher les utilisateurs de test avec leurs CIP
"""

import json

def show_test_users():
    """Affiche les utilisateurs de test avec leurs CIP"""
    try:
        with open('ulc_icam_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        users = data.get('users', {})
        
        print("=" * 80)
        print("UTILISATEURS DE TEST ULC-ICAM - MODE CONNEXION SIMPLIFIEE")
        print("=" * 80)
        
        # Administrateur
        print("\nADMINISTRATEUR:")
        print("   Username: admin")
        print("   Mot de passe: admin123")
        print("   (L'admin garde son authentification normale)")
        
        # Professeurs
        print("\nPROFESSEURS (connexion avec CIP seulement):")
        teachers = [(k, v) for k, v in users.items() if v.get('role') == 'teacher']
        teachers.sort(key=lambda x: x[0])  # Trier par username
        
        for i, (username, user_data) in enumerate(teachers[:10], 1):  # Afficher les 10 premiers
            cip = user_data.get('cip', 'N/A')
            name = user_data.get('name', 'N/A')
            faculte = user_data.get('faculte', 'N/A')
            print(f"   {i:2d}. CIP: {cip:<8} | {name:<35} | {faculte}")
        
        if len(teachers) > 10:
            print(f"   ... et {len(teachers) - 10} autres professeurs")
        
        # Etudiants
        print(f"\nETUDIANTS (connexion avec CIP seulement):")
        students = [(k, v) for k, v in users.items() if v.get('role') == 'student']
        students.sort(key=lambda x: x[0])  # Trier par username
        
        for i, (username, user_data) in enumerate(students[:15], 1):  # Afficher les 15 premiers
            cip = user_data.get('cip', 'N/A')
            name = user_data.get('name', 'N/A')
            promotion = user_data.get('promotion', 'N/A')
            faculte = user_data.get('faculte', 'N/A')
            print(f"   {i:2d}. CIP: {cip:<8} | {name:<25} | {promotion} {faculte}")
        
        if len(students) > 15:
            print(f"   ... et {len(students) - 15} autres etudiants")
        
        print("\n" + "=" * 80)
        print("INSTRUCTIONS DE CONNEXION:")
        print("   1. Allez sur /login/student ou /login/teacher")
        print("   2. Entrez seulement le CIP (ex: PROF001 ou ETUD001)")
        print("   3. Laissez le champ mot de passe VIDE")
        print("   4. Cliquez sur 'Se connecter'")
        print("=" * 80)
        
        print(f"\nSTATISTIQUES:")
        print(f"   - Total utilisateurs: {len(users)}")
        print(f"   - Professeurs: {len(teachers)}")
        print(f"   - Etudiants: {len(students)}")
        print(f"   - Cours disponibles: {len(data.get('admin_courses', []))}")
        print(f"   - Devoirs crees: {len(data.get('assignments', []))}")
        
    except FileNotFoundError:
        print("Fichier ulc_icam_data.json non trouve!")
        print("Assurez-vous que le fichier existe dans le repertoire courant.")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    show_test_users()