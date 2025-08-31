#!/usr/bin/env python3
"""
Version debug simplifiée pour tester la soumission
"""

from flask import Flask, request, jsonify, session
import sys
import os

# Ajouter le chemin pour importer code_execution
sys.path.append('ulc-turnin-web')

app = Flask(__name__)
app.secret_key = 'debug_key'

@app.route('/test_submit', methods=['POST'])
def test_submit():
    """Route de test simplifiée"""
    try:
        print("=== DEBUG ROUTE ===")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Form data: {dict(request.form)}")
        
        code = request.form.get('code_content', '')
        language = request.form.get('language', 'python')
        
        print(f"Code: {code[:50]}...")
        print(f"Language: {language}")
        
        if not code.strip():
            return jsonify({
                'success': False,
                'error': 'Code vide'
            })
        
        # Test d'exécution simple
        try:
            from code_execution import CodeExecutor
            executor = CodeExecutor()
            result = executor.execute_code(code, language)
            
            print(f"Execution result: {result}")
            
            return jsonify({
                'success': True,
                'execution_result': result
            })
            
        except Exception as exec_error:
            print(f"Execution error: {exec_error}")
            return jsonify({
                'success': False,
                'error': f'Erreur exécution: {str(exec_error)}'
            })
            
    except Exception as e:
        print(f"Route error: {e}")
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        })

@app.route('/test')
def test_page():
    """Page de test simple"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Debug</title>
    </head>
    <body>
        <h1>Test de Soumission</h1>
        <form id="testForm">
            <textarea id="code" rows="5" cols="50">print("Hello, World!")</textarea><br>
            <button type="button" onclick="submitCode()">Tester</button>
        </form>
        <div id="result"></div>
        
        <script>
        function submitCode() {
            const code = document.getElementById('code').value;
            
            fetch('/test_submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'code_content': code,
                    'language': 'python'
                })
            })
            .then(response => {
                console.log('Status:', response.status);
                return response.text();
            })
            .then(text => {
                console.log('Response:', text);
                document.getElementById('result').innerHTML = '<pre>' + text + '</pre>';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('result').innerHTML = 'Erreur: ' + error.message;
            });
        }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Serveur debug démarré sur http://localhost:5001/test")
    app.run(host='0.0.0.0', port=5001, debug=True)