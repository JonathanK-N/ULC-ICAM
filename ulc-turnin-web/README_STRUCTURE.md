# Structure du Projet ULC-ICAM Turnin

## Fichiers Essentiels (Racine)
- `app.py` - Application Flask principale
- `models.py` - Modèles de base de données
- `config.py` - Configuration de l'application
- `run.py` - Script de lancement principal
- `requirements.txt` - Dépendances Python
- `.env` / `.env.example` - Variables d'environnement

## Dossiers Principaux
- `app/` - Code source de l'application
- `templates/` - Templates HTML
- `uploads/` - Fichiers uploadés
- `instance/` - Base de données et fichiers d'instance
- `test/` - Tests unitaires et d'intégration
- `docs/` - Documentation

## Archive (Fichiers Déplacés)
- `archive/old_versions/` - Anciennes versions d'app et scripts
- `archive/test_scripts/` - Scripts de test divers
- `archive/data_generators/` - Générateurs de données de test
- `archive/optimization_tools/` - Outils d'optimisation

## Utilisation
Pour lancer l'application : `python run.py`
Pour les tests : `python -m pytest test/`