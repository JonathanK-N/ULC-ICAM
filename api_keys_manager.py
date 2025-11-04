#!/usr/bin/env python3
"""
Gestionnaire de clés API pour ULC-ICAM Turnin
Permet de configurer, tester et gérer toutes les clés API
"""

import os
import sys
from config import Config
import requests
import openai
from datetime import datetime

class APIKeysManager:
    """Gestionnaire centralisé des clés API"""
    
    def __init__(self):
        self.config = Config()
        self.status = {}
    
    def check_openai_key(self):
        """Teste la clé OpenAI"""
        if not self.config.OPENAI_API_KEY or self.config.OPENAI_API_KEY == 'your_openai_api_key_here':
            return {'status': 'missing', 'message': 'Clé OpenAI non configurée'}
        
        try:
            openai.api_key = self.config.OPENAI_API_KEY
            # Test simple avec un prompt minimal
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return {'status': 'valid', 'message': 'Clé OpenAI valide', 'model': 'gpt-3.5-turbo'}
        except openai.error.AuthenticationError:
            return {'status': 'invalid', 'message': 'Clé OpenAI invalide'}
        except openai.error.RateLimitError:
            return {'status': 'limited', 'message': 'Quota OpenAI dépassé'}
        except Exception as e:
            return {'status': 'error', 'message': f'Erreur OpenAI: {str(e)}'}
    
    def check_google_key(self):
        """Teste la clé Google Custom Search"""
        if not self.config.GOOGLE_API_KEY or self.config.GOOGLE_API_KEY == 'your_google_api_key_here':
            return {'status': 'missing', 'message': 'Clé Google non configurée'}
        
        if not self.config.GOOGLE_SEARCH_ENGINE_ID or self.config.GOOGLE_SEARCH_ENGINE_ID == 'your_search_engine_id_here':
            return {'status': 'missing', 'message': 'ID moteur de recherche Google manquant'}
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.GOOGLE_API_KEY,
                'cx': self.config.GOOGLE_SEARCH_ENGINE_ID,
                'q': 'test',
                'num': 1
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                queries_today = data.get('queries', {}).get('request', [{}])[0].get('totalResults', 'N/A')
                return {'status': 'valid', 'message': 'Clé Google valide', 'queries_today': queries_today}
            elif response.status_code == 403:
                return {'status': 'limited', 'message': 'Quota Google dépassé ou API désactivée'}
            else:
                return {'status': 'invalid', 'message': f'Erreur Google API: {response.status_code}'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Erreur Google: {str(e)}'}
    
    def check_huggingface_key(self):
        """Teste la clé Hugging Face (optionnelle)"""
        if not self.config.HUGGINGFACE_API_KEY or self.config.HUGGINGFACE_API_KEY == 'your_huggingface_token_here':
            return {'status': 'missing', 'message': 'Token Hugging Face non configuré (optionnel)'}
        
        try:
            headers = {'Authorization': f'Bearer {self.config.HUGGINGFACE_API_KEY}'}
            response = requests.get('https://huggingface.co/api/whoami', headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_info = response.json()
                return {'status': 'valid', 'message': f'Token HF valide - Utilisateur: {user_info.get("name", "N/A")}'}
            else:
                return {'status': 'invalid', 'message': 'Token Hugging Face invalide'}
                
        except Exception as e:
            return {'status': 'error', 'message': f'Erreur HF: {str(e)}'}
    
    def test_all_keys(self):
        """Teste toutes les clés API"""
        print("Test des cles API ULC-ICAM")
        print("=" * 50)
        
        # Test OpenAI
        print("\nOpenAI API:")
        openai_status = self.check_openai_key()
        self.status['openai'] = openai_status
        self._print_status(openai_status)
        
        # Test Google
        print("\nGoogle Custom Search API:")
        google_status = self.check_google_key()
        self.status['google'] = google_status
        self._print_status(google_status)
        
        # Test Hugging Face
        print("\nHugging Face API:")
        hf_status = self.check_huggingface_key()
        self.status['huggingface'] = hf_status
        self._print_status(hf_status)
        
        # Résumé
        self._print_summary()
        
        return self.status
    
    def _print_status(self, status_info):
        """Affiche le statut d'une API"""
        status = status_info['status']
        message = status_info['message']
        
        if status == 'valid':
            print(f"  [OK] {message}")
        elif status == 'missing':
            print(f"  [WARN] {message}")
        elif status == 'invalid':
            print(f"  [ERROR] {message}")
        elif status == 'limited':
            print(f"  [LIMITED] {message}")
        else:
            print(f"  [INFO] {message}")
    
    def _print_summary(self):
        """Affiche un résumé des tests"""
        print("\n" + "=" * 50)
        print("RESUME")
        
        valid_keys = sum(1 for s in self.status.values() if s['status'] == 'valid')
        total_keys = len([k for k in self.status.keys() if k != 'huggingface'])  # HF optionnel
        
        print(f"Clés valides: {valid_keys}/{total_keys}")
        
        if valid_keys == total_keys:
            print("[SUCCESS] Toutes les cles sont configurees et valides!")
        elif valid_keys > 0:
            print("[OK] L'application fonctionnera avec les alternatives locales")
        else:
            print("[WARN] Aucune cle configuree - mode local uniquement")
        
        print("\nRECOMMANDATIONS:")
        if self.status['openai']['status'] != 'valid':
            print("- Configurez OpenAI pour une correction automatique avancée")
        if self.status['google']['status'] != 'valid':
            print("- Configurez Google pour la détection de plagiat web")
        
        print(f"\nTest effectue le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def generate_config_template(self):
        """Génère un template de configuration"""
        template = """
# === GUIDE DE CONFIGURATION DES CLÉS API ===

# 1. OPENAI API KEY
# - Allez sur: https://platform.openai.com/api-keys
# - Créez un compte et ajoutez une méthode de paiement
# - Générez une nouvelle clé API
# - Coût approximatif: $0.002 par correction
OPENAI_API_KEY=sk-...

# 2. GOOGLE CUSTOM SEARCH API
# - Allez sur: https://console.developers.google.com/
# - Créez un nouveau projet
# - Activez "Custom Search API"
# - Créez des identifiants (clé API)
# - Allez sur: https://cse.google.com/
# - Créez un moteur de recherche personnalisé
# - Notez l'ID du moteur de recherche
GOOGLE_API_KEY=AIza...
GOOGLE_SEARCH_ENGINE_ID=...

# 3. HUGGING FACE TOKEN (Optionnel)
# - Allez sur: https://huggingface.co/settings/tokens
# - Créez un nouveau token
HUGGINGFACE_API_KEY=hf_...
"""
        return template

def main():
    """Fonction principale"""
    import sys
    import os
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    manager = APIKeysManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            manager.test_all_keys()
        elif command == 'template':
            print(manager.generate_config_template())
        elif command == 'openai':
            status = manager.check_openai_key()
            manager._print_status(status)
        elif command == 'google':
            status = manager.check_google_key()
            manager._print_status(status)
        else:
            print("Usage: python api_keys_manager.py [test|template|openai|google]")
    else:
        manager.test_all_keys()

if __name__ == "__main__":
    main()