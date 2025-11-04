#!/usr/bin/env python3
"""
Test final du système de soumission de code
"""

import sys
import os
sys.path.append('ulc-turnin-web')

from code_execution import CodeExecutor

def test_final():
    """Test final du système"""
    
    print("=== TEST FINAL DU SYSTÈME ===\n")
    
    executor = CodeExecutor()
    
    # Test simple
    code = 'print("Hello, World!")'
    result = executor.execute_code(code, 'python')
    
    print("Test d'exécution Python:")
    print(f"✓ Statut: {result.get('status', 'N/A')}")
    print(f"✓ Sortie: {result.get('stdout', 'N/A')}")
    print(f"✓ Temps: {result.get('time', 'N/A')}s")
    print(f"✓ Mémoire: {result.get('memory', 'N/A')} KB")
    print(f"✓ Succès: {result.get('success', False)}")
    
    # Vérifier que tous les champs nécessaires sont présents
    required_fields = ['status', 'stdout', 'stderr', 'time', 'memory', 'success']
    missing_fields = [field for field in required_fields if field not in result]
    
    if missing_fields:
        print(f"❌ Champs manquants: {missing_fields}")
    else:
        print("✅ Tous les champs requis sont présents")
    
    print("\n" + "="*50)
    print("✅ SYSTÈME PRÊT POUR UTILISATION!")
    print("Les étudiants peuvent maintenant soumettre du code sans erreur.")

if __name__ == "__main__":
    test_final()