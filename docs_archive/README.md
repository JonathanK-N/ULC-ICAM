# 📚 Documentation et Archives - ULC-ICAM Turnin System

Ce dossier contient tous les documents, tests et fichiers non essentiels pour le déploiement du système ULC-ICAM Turnin.

## 📁 Contenu du Dossier

### 📖 Documentation
- `docs/` - Documentation technique complète
- `*.md` - Guides et rapports (DEPLOYMENT_CHECKLIST, RAPPORT_FINAL, etc.)
- `COPYRIGHT.md` - Informations de propriété intellectuelle
- `INTELLECTUAL_PROPERTY.md` - Détails légaux

### 🧪 Tests et Développement
- `test/` - Suite de tests complète
- `test_final_deployment.py` - Script de test de déploiement
- `debug_*.py` - Scripts de débogage
- `pytest.ini` - Configuration des tests

### 🔧 Outils et Utilitaires
- `archive/` - Anciennes versions et outils
- `backup/` - Système de sauvegarde
- `optimization/` - Outils d'optimisation
- `scripts/` - Scripts utilitaires

## 🎯 Utilisation

Ces fichiers ne sont **PAS nécessaires** pour le déploiement en production, mais peuvent être utiles pour :

- **Développement** : Tests, débogage, optimisation
- **Maintenance** : Sauvegardes, scripts utilitaires
- **Documentation** : Guides détaillés, rapports techniques
- **Formation** : Guides utilisateur, manuels

## 🚀 Pour le Déploiement

Pour déployer le système, utilisez uniquement les fichiers dans le dossier parent :
- `app.py` - Application principale
- `code_execution.py` - Moteur d'exécution
- `requirements.txt` - Dépendances
- `templates/` - Interface utilisateur
- `static/` - Ressources web
- `uploads/` - Stockage fichiers
- `ulc_icam_data.json` - Base de données

## 📞 Support

Si vous avez besoin d'accéder à la documentation complète ou aux outils de test, consultez les fichiers dans ce dossier.

---

**Note**: Ce dossier peut être supprimé en production pour réduire la taille du déploiement.