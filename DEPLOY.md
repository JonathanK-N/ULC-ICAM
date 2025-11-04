# 🚀 Guide de Déploiement Rapide - ULC-ICAM Turnin

## Fichiers Essentiels pour le Déploiement

### ✅ Fichiers Obligatoires
```
app.py                    # Application Flask principale
code_execution.py         # Moteur d'exécution de code
requirements.txt          # Dépendances Python
ulc_icam_data.json       # Base de données
templates/               # Interface utilisateur (tous les fichiers)
static/                  # Ressources web
uploads/                 # Dossiers de stockage (vides au départ)
```

### ❌ Fichiers Non Nécessaires
```
docs_archive/            # Documentation et tests (peut être supprimé)
test_report_*.json       # Rapports de test
.env.example            # Exemple de configuration
```

## 🚀 Déploiement en 3 Étapes

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Créer les dossiers uploads
mkdir uploads\code_submissions uploads\submissions uploads\corrections uploads\assignments uploads\chapters uploads\syllabus uploads\analysis

# Configurer les variables d'environnement (optionnel)
set FLASK_ENV=production
set FLASK_SECRET_KEY=your_secure_key
```

### 3. Lancement
```bash
python app.py
```

## 🌐 Accès
- **URL**: http://localhost:5000
- **Admin**: admin / admin123

## 📞 Support
En cas de problème, consultez `docs_archive/` pour la documentation complète.

---
**✅ Système prêt en moins de 5 minutes !**