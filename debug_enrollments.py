#!/usr/bin/env python3
"""
Script de debug pour vérifier les types de clés dans course_enrollments
"""

import json

def debug_enrollments():
    """Debug les types de clés dans course_enrollments"""
    
    # Charger les données
    with open('ulc-turnin-web/ulc_icam_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    course_assignments = data.get('course_assignments', {})
    course_enrollments = data.get('course_enrollments', {})
    
    print("=== DEBUG COURSE_ENROLLMENTS ===\n")
    
    print("Types de clés dans course_assignments:")
    for key in list(course_assignments.keys())[:5]:
        print(f"  {key} (type: {type(key)})")
    
    print("\nTypes de clés dans course_enrollments:")
    for key in list(course_enrollments.keys())[:5]:
        print(f"  {key} (type: {type(key)})")
    
    print("\nComparaison des clés:")
    print("course_assignments keys:", list(course_assignments.keys())[:10])
    print("course_enrollments keys:", list(course_enrollments.keys())[:10])
    
    print("\nTest de correspondance:")
    for course_id_str in list(course_assignments.keys())[:5]:
        course_id_int = int(course_id_str)
        print(f"  {course_id_str} -> {course_id_int}")
        print(f"    Dans course_enrollments avec str: {course_id_str in course_enrollments}")
        print(f"    Dans course_enrollments avec int: {course_id_int in course_enrollments}")

if __name__ == "__main__":
    debug_enrollments()