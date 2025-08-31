#!/usr/bin/env python3
"""
Test de la route submit_assignment
"""

import requests
import json

def test_submit_route():
    """Test de la route de soumission"""
    
    print("=== TEST DE LA ROUTE SUBMIT ===\n")
    
    # URL de test
    url = "http://localhost:5000/submit/1"
    
    # Données de test
    data = {
        'code_content': 'print("Hello, World!")',
        'language': 'python'
    }
    
    try:
        # Test de la route
        response = requests.post(url, data=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"Response Text: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"JSON Response: {json.dumps(json_data, indent=2)}")
            except:
                print("Response is not JSON")
        
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Flask non démarré!")
        print("Démarrez le serveur avec: python app.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_submit_route()