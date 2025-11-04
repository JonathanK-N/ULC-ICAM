#!/usr/bin/env python3
"""
Test du système d'exécution de code
"""

import sys
import os
sys.path.append('ulc-turnin-web')

from code_execution import CodeExecutor

def test_code_execution():
    """Teste l'exécution de code Python"""
    
    print("=== TEST D'EXÉCUTION DE CODE ===\n")
    
    executor = CodeExecutor()
    
    # Test 1: Code Python simple
    print("Test 1: Code Python simple")
    code = 'print("Hello, World!")'
    result = executor.execute_code(code, 'python')
    
    print(f"Statut: {result.get('status', 'N/A')}")
    print(f"Sortie: {result.get('stdout', 'N/A')}")
    print(f"Erreurs: {result.get('stderr', 'N/A')}")
    print(f"Temps: {result.get('time', 'N/A')}s")
    print(f"Mémoire: {result.get('memory', 'N/A')} KB")
    print(f"Succès: {result.get('success', False)}")
    print()
    
    # Test 2: Code avec entrée
    print("Test 2: Code avec entrée")
    code = '''
name = input("Nom: ")
print(f"Bonjour {name}!")
'''
    result = executor.execute_code(code, 'python', stdin='Alice')
    
    print(f"Statut: {result.get('status', 'N/A')}")
    print(f"Sortie: {result.get('stdout', 'N/A')}")
    print(f"Succès: {result.get('success', False)}")
    print()
    
    # Test 3: Code avec cas de test
    print("Test 3: Code avec cas de test")
    code = '''
a, b = map(int, input().split())
print(a + b)
'''
    test_cases = [
        {'input': '5 3', 'expected_output': '8'},
        {'input': '10 -2', 'expected_output': '8'},
        {'input': '0 0', 'expected_output': '0'}
    ]
    
    result = executor.execute_code(code, 'python', test_cases=test_cases)
    
    print(f"Statut: {result.get('status', 'N/A')}")
    print(f"Succès: {result.get('success', False)}")
    
    if 'test_results' in result:
        print("Résultats des tests:")
        for test in result['test_results']:
            status = "✓" if test['passed'] else "✗"
            print(f"  {status} Test {test['test_case']}: {test['input']} -> {test['actual_output']} (attendu: {test['expected_output']})")
    
    print("\n" + "="*50)
    print("Test terminé!")

if __name__ == "__main__":
    test_code_execution()