# Documentation Système de Gestion Académique ULC-ICAM

## Vue d'ensemble

Le Système de Gestion Académique ULC-ICAM est une plateforme web complète développée spécifiquement pour l'Université Libre des Comores - Institut Catholique d'Arts et Métiers. Cette application permet la gestion intégrée des cours, devoirs, soumissions et évaluations avec exécution automatique de code.

## Structure de la Documentation

- **[Guide Administrateur](ADMIN_GUIDE.md)** - Documentation complète pour les administrateurs système
- **[Guide Professeur](TEACHER_GUIDE.md)** - Manuel d'utilisation pour les enseignants
- **[Guide Étudiant](STUDENT_GUIDE.md)** - Guide d'utilisation pour les étudiants
- **[Installation et Configuration](INSTALLATION.md)** - Instructions d'installation et de configuration
- **[Guide de Sauvegarde](BACKUP_GUIDE.md)** - Procédures de sauvegarde et restauration

## Fonctionnalités Principales

### 🎓 Gestion Académique
- Gestion des facultés, départements et promotions
- Création et assignation de cours
- Gestion des utilisateurs (étudiants, professeurs, administrateurs)

### 📝 Système de Devoirs
- Création de devoirs traditionnels et de programmation
- Soumission de fichiers et de code
- Correction automatique et manuelle
- Détection de plagiat intégrée

### 💻 Exécution de Code
- Support multi-langages (Python, Java, C++, C, JavaScript)
- Exécution sécurisée via Judge0 API
- Tests automatiques avec cas de test
- Éditeur de code intégré (Monaco Editor)

### 📊 Évaluation et Notes
- Système de notation flexible
- Publication automatique des résultats
- Statistiques et analyses détaillées
- Export des données

### 🔒 Sécurité et Sauvegarde
- Authentification sécurisée
- Sauvegarde automatique chiffrée
- Stockage cloud intégré
- Logs d'audit complets

## Architecture Technique

### Technologies Utilisées
- **Backend**: Python Flask
- **Base de données**: SQLite avec SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap
- **Éditeur de code**: Monaco Editor
- **Exécution de code**: Judge0 API
- **Sauvegarde**: Chiffrement AES-256, stockage cloud

### Structure des Fichiers
```
ULC-ICAM/
├── app.py                 # Application principale Flask
├── code_execution.py      # Module d'exécution de code
├── static/               # Fichiers statiques (CSS, JS, images)
├── templates/            # Templates HTML
├── backup/               # Système de sauvegarde
├── test/                 # Suite de tests
├── docs/                 # Documentation
└── uploads/              # Fichiers téléchargés
```

## Configuration Initiale

Le système est configuré par défaut avec :
- **Faculté**: Faculté des Sciences et Technologies (ULC-ICAM)
- **8 Départements**:
  - Mathématiques & Informatique
  - Génie Mécanique
  - Génie Électrique
  - Physique & Chimie
  - Génie Informatique
  - Maintenance & Génie Industriels
  - Énergie/Environnement/Matériaux
  - Polytechnique Générale

## Support et Contact

Pour toute assistance technique ou question concernant l'utilisation du système :
- **Email**: support@ulc-icam.edu.km
- **Documentation**: Consultez les guides spécifiques par rôle
- **Logs système**: Disponibles dans le tableau de bord administrateur

## Propriété Intellectuelle

© 2024 Université Libre des Comores - Institut Catholique d'Arts et Métiers (ULC-ICAM)
Tous droits réservés. Ce logiciel est la propriété exclusive de ULC-ICAM.

---

**Version**: 1.0  
**Dernière mise à jour**: Décembre 2024