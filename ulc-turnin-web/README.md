# 🎓 ULC-ICAM Turnin System

**Système de gestion de devoirs et soumissions de code pour l'Université Loyola du Congo - Institut Catholique d'Arts et Métiers**

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- pip (gestionnaire de paquets Python)

### Installation
```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Créer les dossiers nécessaires
mkdir uploads\code_submissions uploads\submissions uploads\corrections uploads\assignments uploads\chapters uploads\syllabus uploads\analysis

# 3. Lancer l'application
python app.py
```

### Accès
- **URL**: http://localhost:5000
- **Admin**: admin / admin123
- **Port**: 5000 (configurable)

## 📁 Structure du Projet

```
ulc-turnin-web/
├── app.py                 # Application Flask principale
├── code_execution.py      # Moteur d'exécution de code
├── requirements.txt       # Dépendances Python
├── ulc_icam_data.json    # Base de données JSON
├── templates/            # Templates HTML
├── static/              # Fichiers statiques (CSS, JS, images)
├── uploads/             # Fichiers téléversés
└── docs_archive/        # Documentation et tests (non essentiel)
```

## ✨ Fonctionnalités Principales

### 👨‍💼 Administration
- Gestion des utilisateurs (étudiants, professeurs)
- Configuration système (facultés, départements, promotions)
- Import CSV en masse
- Rapports et statistiques

### 👨‍🏫 Professeurs
- Création de devoirs (code, mixtes, fichiers)
- Gestion du contenu de cours (chapitres, documents PDF/PPT)
- Correction automatique et manuelle
- Détection de plagiat locale
- Publication des résultats

### 👨‍🎓 Étudiants
- Soumission de code avec éditeur Monaco
- Support multi-langages (Python, Java, C++, C, JavaScript)
- Soumission de fichiers d'analyse
- Consultation des notes et feedback
- Accès au contenu des cours

## 🔧 Configuration

### Variables d'Environnement
```bash
FLASK_ENV=production          # Mode production
FLASK_SECRET_KEY=your_key     # Clé de sécurité
UPLOAD_FOLDER=uploads         # Dossier uploads
MAX_CONTENT_LENGTH=16777216   # Taille max fichiers (16MB)
```

### Formats Supportés
- **Code**: .py, .java, .cpp, .c, .js
- **Documents**: .pdf, .ppt, .pptx
- **Analyse**: .pdf, .doc, .docx, .txt

## 🛡️ Sécurité

- Authentification par rôles (admin/professeur/étudiant)
- Validation stricte des fichiers
- Isolation des soumissions par utilisateur
- Protection contre l'injection de code
- Sessions chiffrées

## 📊 Fonctionnalités Avancées

### Détection de Plagiat
- Comparaison ligne par ligne du code
- Normalisation automatique
- Seuils configurables (suspect >60%, attention >30%)
- **100% locale** - aucune API externe requise

### Exécution de Code
- Support multi-langages
- Compilation et exécution automatiques
- Tests unitaires intégrés
- Feedback détaillé avec erreurs

### Devoirs Mixtes
- Code (50% de la note)
- Fichiers d'analyse (50% de la note)
- Correction séparée des deux parties

## 🚀 Déploiement Production

### Avec Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Avec Docker
```bash
# Construire l'image
docker build -t ulc-turnin .

# Lancer le conteneur
docker run -p 5000:5000 -v ./uploads:/app/uploads ulc-turnin
```

## 📞 Support

**Développeur**: Jonathan Kakesa  
**Institution**: Université Loyola du Congo - ULC-ICAM  
**Version**: 1.0 Production Ready  
**Date**: Décembre 2024  

## 📄 Licence

Propriété intellectuelle de l'Université Loyola du Congo.  
Tous droits réservés - Logiciel Propriétaire.

---

## 📚 Documentation Complète

La documentation détaillée, les guides d'installation avancés, et les fichiers de test se trouvent dans le dossier `docs_archive/`.

**🎉 Système prêt pour la production !**