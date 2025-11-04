#!/usr/bin/env python3
"""
Script de configuration pour les outils d'IA et de détection de plagiat
"""

import os
import sys
import subprocess

def install_requirements():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dépendances installées avec succès")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False
    return True

def setup_environment():
    """Configure les variables d'environnement"""
    print("\n🔧 Configuration des variables d'environnement...")
    
    if not os.path.exists('.env'):
        print("Création du fichier .env...")
        with open('.env', 'w') as f:
            f.write("# Configuration ULC-ICAM\n")
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_SECRET_KEY=dev-secret-key-change-in-production\n")
            f.write("\n# API Keys (optionnelles)\n")
            f.write("# OPENAI_API_KEY=your_key_here\n")
            f.write("# GOOGLE_API_KEY=your_key_here\n")
            f.write("# GOOGLE_SEARCH_ENGINE_ID=your_id_here\n")
        print("✅ Fichier .env créé")
    else:
        print("ℹ️  Fichier .env existe déjà")

def test_ai_services():
    """Teste les services d'IA disponibles"""
    print("\n🧪 Test des services d'IA...")
    
    # Test Hugging Face Transformers
    try:
        from transformers import pipeline
        print("✅ Hugging Face Transformers disponible")
    except ImportError:
        print("❌ Hugging Face Transformers non disponible")
    
    # Test OpenAI
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        try:
            import openai
            openai.api_key = openai_key
            print("✅ OpenAI API configurée")
        except ImportError:
            print("❌ OpenAI non disponible")
    else:
        print("ℹ️  OpenAI API key non configurée (optionnel)")
    
    # Test Google API
    google_key = os.environ.get('GOOGLE_API_KEY')
    if google_key:
        print("✅ Google API configurée")
    else:
        print("ℹ️  Google API key non configurée (optionnel)")

def create_directories():
    """Crée les dossiers nécessaires"""
    print("\n📁 Création des dossiers...")
    
    directories = [
        'uploads',
        'uploads/assignments',
        'uploads/corrections',
        'uploads/chapters'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Dossier {directory} créé")

def main():
    """Fonction principale"""
    print("🚀 Configuration ULC-ICAM avec IA et détection de plagiat")
    print("=" * 60)
    
    # Installation des dépendances
    if not install_requirements():
        print("❌ Échec de l'installation")
        return
    
    # Configuration de l'environnement
    setup_environment()
    
    # Création des dossiers
    create_directories()
    
    # Test des services
    test_ai_services()
    
    print("\n" + "=" * 60)
    print("✅ Configuration terminée!")
    print("\n📋 Prochaines étapes:")
    print("1. Configurez vos clés API dans le fichier .env (optionnel)")
    print("2. Lancez l'application: python app.py")
    print("\n🔑 Clés API optionnelles:")
    print("- OpenAI: Pour une correction automatique avancée")
    print("- Google Custom Search: Pour la détection de plagiat web")
    print("\n💡 L'application fonctionne sans ces clés avec des alternatives locales")

if __name__ == "__main__":
    main()