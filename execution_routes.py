"""Code sandbox HTTP endpoints; storage and account lookup are injected."""
from flask import Blueprint, request, session, jsonify
from code_execution import CodeExecutor


def create_execution_blueprint(lookup_user):
    blueprint = Blueprint('execution', __name__)
    @blueprint.route('/test_submit', methods=['POST'])
    def test_submit():
        user = lookup_user(session.get('user'))
        if not user:
            return jsonify(success=False, error='Authentification requise'), 401
        if user.get('role') not in ('student', 'teacher', 'admin'):
            return jsonify(success=False, error='Accès interdit'), 403
        """Route de test pour la soumission"""
        try:
            code = request.form.get('code_content', '')
            language = request.form.get('language', 'python')
            
            if not code.strip():
                return jsonify({
                    'success': False,
                    'error': 'Code vide'
                })
            
            # Test d'exécution simple
            executor = CodeExecutor()
            result = executor.execute_code(code, language)
            if result.get('error_code'):
                return jsonify(success=False, error=result['error'], execution_result=result), (503 if result.get('retryable') else 400)
            
            # Note basée sur le résultat réel de compilation/exécution
            max_score = 100
            
            # Vérifier si le code s'est exécuté sans erreur
            has_compilation_error = bool(result.get('compile_output', '').strip())
            has_runtime_error = bool(result.get('stderr', '').strip())
            execution_success = result.get('success', False)
            
            # Déterminer la note selon les résultats réels
            status = result.get('status', '')
            is_system_error = 'non installé' in status or 'non trouvé' in status or 'non supporté' in status
            
            if execution_success and not has_compilation_error and not has_runtime_error:
                score = max_score
                feedback = [
                    "✅ Compilation réussie",
                    "✅ Exécution sans erreur", 
                    f"🎉 Félicitations ! Note maximale obtenue: {max_score}/{max_score}"
                ]
            elif is_system_error:
                score = 0
                feedback = [
                    f"⚠️ {status}",
                    "🔧 Contactez l'administrateur pour installer les outils nécessaires"
                ]
            else:
                score = 0
                feedback = []
                if has_compilation_error:
                    feedback.append("❌ Erreurs de compilation détectées")
                if has_runtime_error:
                    feedback.append("❌ Erreurs d'exécution détectées")
                if not execution_success:
                    feedback.append("❌ Le programme ne s'exécute pas correctement")
                feedback.append("🔧 Corrigez les erreurs pour obtenir des points")
            
            result['score'] = score
            result['max_score'] = max_score
            result['feedback'] = feedback
            
            return jsonify({
                'success': True,
                'execution_result': result
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Erreur interne du service d’exécution'
            })

    return blueprint
