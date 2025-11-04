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
            # Si Judge0 API est configuré, l'utiliser
            if JUDGE0_API_KEY:
                return self._execute_with_judge0(code, language, stdin, test_cases)
            else:
                # Sinon, utiliser l'exécution locale
                return self._execute_locally(code, language, stdin, test_cases)
            
        except Exception as e:
            return {
                'status': 'Erreur',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False,
                'error': f'Erreur d\'exécution: {str(e)}'
            }
    
    def _execute_locally(self, code, language, stdin='', test_cases=None):
        """Exécution locale du code"""
        try:
            if language.lower() == 'python':
                return self._execute_python(code, stdin, test_cases)
            elif language.lower() == 'java':
                return self._execute_java(code, stdin, test_cases)
            elif language.lower() in ['c', 'cpp']:
                return self._execute_c_cpp(code, language, stdin, test_cases)
            elif language.lower() == 'javascript':
                return self._execute_javascript(code, stdin, test_cases)
            else:
                return {
                    'status': 'Langage non supporté',
                    'stdout': '',
                    'stderr': f'Langage {language} non supporté pour l\'exécution locale',
                    'compile_output': '',
                    'time': '0.0',
                    'memory': '0',
                    'success': False
                }
        except FileNotFoundError as e:
            return {
                'status': 'Compilateur non trouvé',
                'stdout': '',
                'stderr': f'Compilateur/Interpréteur pour {language} non installé sur le système',
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'Erreur locale',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
    
    def _execute_python(self, code, stdin='', test_cases=None):
        """Exécute du code Python localement avec vérification de syntaxe"""
        import subprocess
        import tempfile
        import time
        import os
        
        try:
            # Vérifier d'abord la syntaxe Python
            try:
                compile(code, '<string>', 'exec')
                compile_output = ''
            except SyntaxError as e:
                return {
                    'status': 'Erreur de syntaxe',
                    'stdout': '',
                    'stderr': '',
                    'compile_output': f'SyntaxError: {e.msg} (ligne {e.lineno})',
                    'time': '0.0',
                    'memory': '0',
                    'success': False
                }
            except Exception as e:
                return {
                    'status': 'Erreur de compilation',
                    'stdout': '',
                    'stderr': '',
                    'compile_output': f'Erreur: {str(e)}',
                    'time': '0.0',
                    'memory': '0',
                    'success': False
                }
            
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Exécuter le code
            process = subprocess.run(
                ['python', temp_file],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            execution_time = time.time() - start_time
            
            # Nettoyer
            os.unlink(temp_file)
            
            # Déterminer le succès : code de retour 0 ET pas d'erreurs stderr
            success = process.returncode == 0 and not process.stderr.strip()
            
            result = {
                'status': 'Exécuté' if success else 'Erreur d\'exécution',
                'stdout': process.stdout,
                'stderr': process.stderr,
                'compile_output': '',
                'time': f'{execution_time:.2f}',
                'memory': '1024',
                'success': success
            }
            
            return result
            
        except subprocess.TimeoutExpired:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Timeout',
                'stdout': '',
                'stderr': 'Temps d\'exécution dépassé (5s)',
                'compile_output': '',
                'time': '5.0',
                'memory': '0',
                'success': False
            }
        except Exception as e:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Erreur système',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
    
    def _execute_java(self, code, stdin='', test_cases=None):
        """Exécute du code Java localement"""
        import subprocess
        import tempfile
        import time
        import os
        
        try:
            # Créer un fichier temporaire Java
            with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Compilation
            compile_process = subprocess.run(
                ['javac', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_process.returncode != 0:
                os.unlink(temp_file)
                return {
                    'status': 'Erreur de compilation',
                    'stdout': '',
                    'stderr': '',
                    'compile_output': compile_process.stderr,
                    'time': '0.0',
                    'memory': '0',
                    'success': False
                }
            
            # Exécution
            class_name = os.path.splitext(os.path.basename(temp_file))[0]
            class_file = temp_file.replace('.java', '.class')
            
            process = subprocess.run(
                ['java', '-cp', os.path.dirname(temp_file), class_name],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            execution_time = time.time() - start_time
            
            # Nettoyer
            os.unlink(temp_file)
            if os.path.exists(class_file):
                os.unlink(class_file)
            
            success = process.returncode == 0 and not process.stderr.strip()
            
            return {
                'status': 'Exécuté' if success else 'Erreur d\'exécution',
                'stdout': process.stdout,
                'stderr': process.stderr,
                'compile_output': '',
                'time': f'{execution_time:.2f}',
                'memory': '1024',
                'success': success
            }
            
        except subprocess.TimeoutExpired:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            if 'class_file' in locals() and os.path.exists(class_file):
                os.unlink(class_file)
            return {
                'status': 'Timeout',
                'stdout': '',
                'stderr': 'Temps d\'exécution dépassé',
                'compile_output': '',
                'time': '5.0',
                'memory': '0',
                'success': False
            }
        except FileNotFoundError:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Java non installé',
                'stdout': '',
                'stderr': 'Java JDK non installé sur le système',
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'Erreur système',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
    
    def _execute_c_cpp(self, code, language, stdin='', test_cases=None):
        """Exécute du code C/C++ localement"""
        import subprocess
        import tempfile
        import time
        import os
        
        try:
            # Créer un fichier temporaire
            ext = '.c' if language.lower() == 'c' else '.cpp'
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Compilation avec chemin complet MSYS2
            if language.lower() == 'c':
                compiler = r'C:\msys64\mingw64\bin\gcc.exe'
            else:
                compiler = r'C:\msys64\mingw64\bin\g++.exe'
            
            exe_file = temp_file.replace(ext, '.exe')
            
            try:
                # Ajouter MSYS2 au PATH pour les DLL
                env = os.environ.copy()
                env['PATH'] = r'C:\msys64\mingw64\bin;' + env.get('PATH', '')
                
                compile_process = subprocess.run(
                    [compiler, temp_file, '-o', exe_file],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=env
                )
                
                if compile_process.returncode != 0:
                    os.unlink(temp_file)
                    compile_error = compile_process.stderr or compile_process.stdout or 'Erreur de compilation'
                    return {
                        'status': 'Erreur de compilation',
                        'stdout': '',
                        'stderr': '',
                        'compile_output': compile_error,
                        'time': '0.0',
                        'memory': '0',
                        'success': False
                    }
            except Exception as compile_err:
                os.unlink(temp_file)
                return {
                    'status': 'Erreur compilation',
                    'stdout': '',
                    'stderr': str(compile_err),
                    'compile_output': '',
                    'time': '0.0',
                    'memory': '0',
                    'success': False
                }
            
            # Exécution avec PATH modifié
            env = os.environ.copy()
            env['PATH'] = r'C:\msys64\mingw64\bin;' + env.get('PATH', '')
            
            process = subprocess.run(
                [exe_file],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=5,
                env=env
            )
            
            execution_time = time.time() - start_time
            
            # Nettoyer
            os.unlink(temp_file)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
            
            success = process.returncode == 0 and not process.stderr.strip()
            
            return {
                'status': 'Exécuté' if success else 'Erreur d\'exécution',
                'stdout': process.stdout,
                'stderr': process.stderr,
                'compile_output': '',
                'time': f'{execution_time:.2f}',
                'memory': '1024',
                'success': success
            }
            
        except subprocess.TimeoutExpired:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            if 'exe_file' in locals() and os.path.exists(exe_file):
                os.unlink(exe_file)
            return {
                'status': 'Timeout',
                'stdout': '',
                'stderr': 'Temps d\'exécution dépassé',
                'compile_output': '',
                'time': '5.0',
                'memory': '0',
                'success': False
            }
        except FileNotFoundError:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Compilateur trouvé',
                'stdout': '',
                'stderr': 'Test avec chemin complet MSYS2',
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'Erreur système',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
    
    def _execute_javascript(self, code, stdin='', test_cases=None):
        """Exécute du code JavaScript localement avec Node.js"""
        import subprocess
        import tempfile
        import time
        import os
        
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            start_time = time.time()
            
            # Exécution avec Node.js
            process = subprocess.run(
                ['node', temp_file],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            execution_time = time.time() - start_time
            
            # Nettoyer
            os.unlink(temp_file)
            
            success = process.returncode == 0 and not process.stderr.strip()
            
            return {
                'status': 'Exécuté' if success else 'Erreur d\'exécution',
                'stdout': process.stdout,
                'stderr': process.stderr,
                'compile_output': '',
                'time': f'{execution_time:.2f}',
                'memory': '1024',
                'success': success
            }
            
        except subprocess.TimeoutExpired:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Timeout',
                'stdout': '',
                'stderr': 'Temps d\'exécution dépassé',
                'compile_output': '',
                'time': '5.0',
                'memory': '0',
                'success': False
            }
        except FileNotFoundError:
            if 'temp_file' in locals():
                os.unlink(temp_file)
            return {
                'status': 'Node.js non installé',
                'stdout': '',
                'stderr': 'Node.js non installé sur le système',
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
        except Exception as e:
            return {
                'status': 'Erreur système',
                'stdout': '',
                'stderr': str(e),
                'compile_output': '',
                'time': '0.0',
                'memory': '0',
                'success': False
            }
    
    def _run_local_test_cases(self, code, language, test_cases):
        """Exécute les cas de test localement"""
        results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                result = self._execute_locally(code, language, test_case['input'])
                
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
            except Exception as e:
                results.append({
                    'test_case': i + 1,
                    'input': test_case['input'],
                    'expected_output': test_case['expected_output'],
                    'actual_output': f'Erreur: {str(e)}',
                    'passed': False,
                    'time': '0',
                    'memory': '0'
                })
        
        return results
    
    def _execute_with_judge0(self, code, language, stdin='', test_cases=None):
        """Exécute avec Judge0 API"""
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