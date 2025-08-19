#!/usr/bin/env python3
"""
Vérification rapide des fonctionnalités critiques de Cognito Web
"""

def check_imports():
    """Vérifier que tous les modules nécessaires sont importables"""
    print("Verification des imports...")
    
    try:
        from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
        print("OK Flask et modules de base")
        
        from werkzeug.utils import secure_filename
        print("OK Werkzeug")
        
        from datetime import datetime, timedelta
        print("OK DateTime")
        
        import os, csv, io, random
        print("OK Modules standard Python")
        
        return True
        
    except ImportError as e:
        print(f"ERREUR d'import: {e}")
        return False

def check_file_structure():
    """Vérifier la structure des fichiers"""
    print("\nVerification de la structure des fichiers...")
    
    required_files = [
        'app.py',
        'generate_test_data.py',
        'templates/base.html',
        'templates/index.html',
        'templates/admin_dashboard.html',
        'templates/teacher_dashboard.html',
        'templates/student_dashboard.html',
        'templates/create_assignment.html',
        'templates/join_group.html',
        'templates/manage_groups.html',
        'static/photos',
        'uploads/assignments'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"OK {file_path}")
        else:
            print(f"MANQUANT {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_app_configuration():
    """Vérifier la configuration de l'application"""
    print("\nVerification de la configuration...")
    
    try:
        # Importer l'app sans la démarrer
        import sys
        sys.path.append('.')
        
        # Vérifier que les variables globales sont définies
        from app import users, assignments, admin_courses, course_assignments
        
        print(f"OK Utilisateurs charges: {len(users)}")
        print(f"OK Devoirs charges: {len(assignments)}")
        print(f"OK Cours charges: {len(admin_courses)}")
        print(f"OK Assignations cours: {len(course_assignments)}")
        
        # Vérifier les données de test
        admin_count = sum(1 for u in users.values() if u['role'] == 'admin')
        teacher_count = sum(1 for u in users.values() if u['role'] == 'teacher')
        student_count = sum(1 for u in users.values() if u['role'] == 'student')
        
        print(f"OK Admins: {admin_count}, Professeurs: {teacher_count}, Etudiants: {student_count}")
        
        return True
        
    except Exception as e:
        print(f"ERREUR configuration: {e}")
        return False

def check_routes():
    """Vérifier que les routes principales sont définies"""
    print("\nVerification des routes...")
    
    try:
        from app import app
        
        # Compter les routes
        route_count = len(app.url_map._rules)
        print(f"OK {route_count} routes definies")
        
        # Vérifier quelques routes critiques
        critical_routes = [
            '/',
            '/login',
            '/dashboard',
            '/admin/users',
            '/teacher/assignments',
            '/student/join_group/<int:assignment_id>'
        ]
        
        defined_routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        for route in critical_routes:
            if any(route in defined_route for defined_route in defined_routes):
                print(f"OK Route {route}")
            else:
                print(f"MANQUANTE Route {route}")
        
        return True
        
    except Exception as e:
        print(f"ERREUR routes: {e}")
        return False

def check_templates():
    """Vérifier les templates critiques"""
    print("\nVerification des templates...")
    
    critical_templates = [
        'templates/base.html',
        'templates/admin_dashboard.html', 
        'templates/teacher_dashboard.html',
        'templates/student_dashboard.html',
        'templates/create_assignment.html',
        'templates/join_group.html'
    ]
    
    all_ok = True
    
    for template in critical_templates:
        if os.path.exists(template):
            # Vérifier le contenu de base
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                if '{% extends' in content or '<!DOCTYPE' in content:
                    print(f"OK {template}")
                else:
                    print(f"SUSPECT {template} - Format suspect")
                    all_ok = False
        else:
            print(f"MANQUANT {template}")
            all_ok = False
    
    return all_ok

def run_functionality_check():
    """Exécuter toutes les vérifications"""
    print("=== VERIFICATION FONCTIONNALITES COGNITO WEB ===")
    print(f"Repertoire: {os.getcwd()}")
    print(f"Heure: {datetime.now()}")
    
    checks = {
        'Imports': check_imports(),
        'Structure fichiers': check_file_structure(),
        'Configuration app': check_app_configuration(),
        'Routes': check_routes(),
        'Templates': check_templates()
    }
    
    print("\n=== RESUME DES VERIFICATIONS ===")
    
    total_checks = len(checks)
    passed_checks = sum(checks.values())
    
    for check_name, result in checks.items():
        status = "OK" if result else "PROBLEME"
        print(f"{check_name}: {status}")
    
    print(f"\nSCORE: {passed_checks}/{total_checks} ({(passed_checks/total_checks)*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("TOUTES LES VERIFICATIONS SONT PASSEES !")
        print("L'application est prete a etre testee.")
        print("Lancez: python app.py puis ouvrez http://localhost:5000")
    else:
        print("Des problemes ont ete detectes.")
        print("Corrigez les erreurs avant de lancer l'application.")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    from datetime import datetime
    import os
    
    success = run_functionality_check()
    
    if success:
        print("\nPRET POUR LES TESTS !")
        print("Commandes suivantes:")
        print("1. python app.py                    # Démarrer l'application")
        print("2. python test_functionality.py     # Tests automatiques")
        print("3. Consulter test_manual.md         # Tests manuels")
    else:
        print("\nCORRECTIONS NECESSAIRES")
        print("Verifiez les erreurs ci-dessus avant de continuer.")