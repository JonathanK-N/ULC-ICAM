#!/usr/bin/env python3
"""
ULC-ICAM TURNIN SYSTEM - MOTEUR D'EXÉCUTION DE CODE
Copyright (c) 2024 Université Loyola du Congo - ULC-ICAM
Tous droits réservés - Logiciel Propriétaire

Moteur d'exécution de code pour ULC-ICAM
Utilise Judge0 API pour l'exécution sécurisée

UTILISATION RESTREINTE - Voir LICENSE pour les conditions
"""
import requests
import time
import json
import os
from datetime import datetime

# Configuration Judge0
JUDGE0_URL = os.environ.get('JUDGE0_URL', 'https://judge0-ce.p.rapidapi.com')
JUDGE0_API_KEY = os.environ.get('JUDGE0_API_KEY', '')

# Mapping des langages
LANGUAGE_MAP = {
    'python': 71,    # Python 3.8.1
    'java': 62,      # Java OpenJDK 13.0.1
    'cpp': 54,       # C++ GCC 9.2.0
    'c': 50,         # C GCC 9.2.0
    'javascript': 63 # Node.js 12.14.0
}

class CodeExecutor:
    def __init__(self):
        self.headers = {
            'X-RapidAPI-Key': JUDGE0_API_KEY,
            'X-RapidAPI-Host': 'judge0-ce.p.rapidapi.com',
            'Content-Type': 'application/json'
        }
    
    def execute_code(self, code, language, stdin='', test_cases=None):
        """Exécute le code et retourne les résultats"""
        try:
            language_id = LANGUAGE_MAP.get(language.lower())
            if not language_id:
                return {'error': f'Langage {language} non supporté'}
            
            # Soumission du code
            submission_data = {
                'source_code': code,
                'language_id': language_id,
                'stdin': stdin,
                'cpu_time_limit': 2,
                'memory_limit': 128000,
                'wall_time_limit': 5
            }
            
            response = requests.post(
                f'{JUDGE0_URL}/submissions',
                headers=self.headers,
                json=submission_data
            )
            
            if response.status_code != 201:
                return {'error': 'Erreur lors de la soumission'}
            
            token = response.json()['token']
            
            # Attendre les résultats
            result = self._wait_for_result(token)
            
            # Exécuter les cas de test si fournis
            if test_cases and result.get('status_id') == 3:  # Accepted
                test_results = self._run_test_cases(code, language_id, test_cases)
                result['test_results'] = test_results
            
            return result
            
        except Exception as e:
            return {'error': f'Erreur d\'exécution: {str(e)}'}
    
    def _wait_for_result(self, token, max_wait=10):
        """Attend le résultat de l'exécution"""
        for _ in range(max_wait):
            response = requests.get(
                f'{JUDGE0_URL}/submissions/{token}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if result['status']['id'] > 2:  # Terminé
                    return self._format_result(result)
            
            time.sleep(1)
        
        return {'error': 'Timeout lors de l\'exécution'}
    
    def _format_result(self, raw_result):
        """Formate le résultat pour l'interface"""
        status = raw_result['status']
        
        result = {
            'status_id': status['id'],
            'status': status['description'],
            'stdout': raw_result.get('stdout', ''),
            'stderr': raw_result.get('stderr', ''),
            'compile_output': raw_result.get('compile_output', ''),
            'time': raw_result.get('time', '0'),
            'memory': raw_result.get('memory', '0'),
            'success': status['id'] == 3  # Accepted
        }
        
        return result
    
    def _run_test_cases(self, code, language_id, test_cases):
        """Exécute les cas de test"""
        results = []
        
        for i, test_case in enumerate(test_cases):
            submission_data = {
                'source_code': code,
                'language_id': language_id,
                'stdin': test_case['input'],
                'expected_output': test_case['expected_output'],
                'cpu_time_limit': 2,
                'memory_limit': 128000
            }
            
            response = requests.post(
                f'{JUDGE0_URL}/submissions',
                headers=self.headers,
                json=submission_data
            )
            
            if response.status_code == 201:
                token = response.json()['token']
                result = self._wait_for_result(token)
                
                # Comparer la sortie
                actual_output = result.get('stdout', '').strip()
                expected_output = test_case['expected_output'].strip()
                
                test_result = {
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected_output': expected_output,
                    'actual_output': actual_output,
                    'passed': actual_output == expected_output,
                    'time': result.get('time', '0'),
                    'memory': result.get('memory', '0')
                }
                
                results.append(test_result)
        
        return results

def save_code_submission(student, assignment_id, code, language, execution_result):
    """Sauvegarde la soumission de code"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"code_{student}_{assignment_id}_{timestamp}.{language}"
    
    # Créer le répertoire s'il n'existe pas
    code_dir = os.path.join('uploads', 'code_submissions')
    os.makedirs(code_dir, exist_ok=True)
    
    # Sauvegarder le code
    code_path = os.path.join(code_dir, filename)
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    # Sauvegarder les résultats
    result_path = os.path.join(code_dir, f"result_{student}_{assignment_id}_{timestamp}.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(execution_result, f, indent=2, ensure_ascii=False)
    
    return {
        'code_file': filename,
        'result_file': f"result_{student}_{assignment_id}_{timestamp}.json",
        'timestamp': timestamp
    }