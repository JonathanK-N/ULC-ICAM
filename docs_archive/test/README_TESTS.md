# 🧪 Suite de Tests ULC-ICAM Turnin System

## 📋 Vue d'ensemble

Cette suite de tests complète vérifie toutes les fonctionnalités du système ULC-ICAM Turnin, incluant la gestion des utilisateurs, des cours, des devoirs, des soumissions, de la détection de plagiat, et de la correction automatique.

## 🏗️ Structure des Tests

### 📁 Fichiers de Test

1. **`test_complete_system.py`** - Tests système complets
   - Démarrage du système
   - Connexions utilisateurs
   - Fonctionnalités principales

2. **`test_user_management.py`** - Gestion des utilisateurs
   - Création d'étudiants et professeurs
   - Import CSV
   - Gestion des profils
   - Authentification

3. **`test_course_assignment.py`** - Gestion des cours
   - Création de cours par faculté
   - Assignation des professeurs
   - Inscription des étudiants
   - Validation des critères

4. **`test_submission_workflow.py`** - Workflow de soumission
   - Soumission de fichiers
   - Détection de plagiat
   - Correction automatique IA
   - Publication des notes

5. **`run_all_tests.py`** - Orchestrateur principal
   - Exécution de toutes les suites
   - Génération de rapports
   - Sauvegarde des résultats

## 🚀 Exécution des Tests

### Prérequis

1. **Serveur en cours d'exécution**
   ```bash
   python app.py
   ```

2. **Dépendances installées**
   ```bash
   pip install -r requirements.txt
   ```

### Exécution Complète

```bash
# Exécuter tous les tests
python test/run_all_tests.py
```

### Exécution Individuelle

```bash
# Tests système
python test/test_complete_system.py

# Tests utilisateurs
python test/test_user_management.py

# Tests cours
python test/test_course_assignment.py

# Tests soumissions
python test/test_submission_workflow.py
```

## 📊 Types de Tests

### 1. Tests Système (15 tests)
- ✅ Démarrage du système
- ✅ Connexion administrateur
- ✅ Création d'utilisateurs
- ✅ Création et assignation de cours
- ✅ Inscription des étudiants
- ✅ Création de devoirs
- ✅ Processus de soumission
- ✅ Détection de plagiat
- ✅ Correction automatique
- ✅ Publication des notes
- ✅ Configuration système
- ✅ Rapports et exports
- ✅ Opérations sur fichiers
- ✅ Gestion des groupes
- ✅ Notifications email

### 2. Tests Gestion Utilisateurs (8 tests)
- ✅ Création complète d'étudiants
- ✅ Création complète de professeurs
- ✅ Import CSV
- ✅ Gestion des profils
- ✅ Authentification
- ✅ Gestion des mots de passe
- ✅ Rôles et permissions
- ✅ Validation des données

### 3. Tests Gestion Cours (8 tests)
- ✅ Création de cours par faculté
- ✅ Assignation des professeurs
- ✅ Inscription selon critères
- ✅ Création de devoirs
- ✅ Gestion du contenu
- ✅ Validation des inscriptions
- ✅ Statistiques des cours
- ✅ Gestion des prérequis

### 4. Tests Workflow Soumission (7 tests)
- ✅ Soumission de différents formats
- ✅ Scénarios de plagiat
- ✅ Correction automatique IA
- ✅ Soumissions en groupe
- ✅ Publication des notes
- ✅ Validation des soumissions
- ✅ Gestion des retards

## 🎯 Scénarios de Test

### Création d'Utilisateurs
```python
# Étudiants avec profils complets
students = [
    {
        'username': 'etudiant_001',
        'cip': 'E2024001',
        'nom': 'Mukendi',
        'prenom': 'Jean',
        'promotion': 'L1',
        'faculte': 'Sciences'
    }
]

# Professeurs avec spécialisations
teachers = [
    {
        'username': 'prof_001',
        'cip': 'P2024001',
        'nom': 'Kasongo',
        'grade': 'Prof. Ordinaire',
        'departement': 'Mathématiques-Informatique'
    }
]
```

### Création de Cours
```python
# Cours par faculté avec critères d'inscription
courses = [
    {
        'name': 'Mathématiques Générales I',
        'code': 'MATH101',
        'faculte': 'Sciences',
        'promotions': ['L1'],
        'credits': 4
    }
]
```

### Tests de Plagiat
```python
# Différents niveaux de similarité
plagiarism_scenarios = [
    {'content': 'original', 'similarity': 0, 'status': 'acceptable'},
    {'content': 'paraphrasé', 'similarity': 75, 'status': 'suspect'},
    {'content': 'identique', 'similarity': 100, 'status': 'plagiat'}
]
```

### Correction Automatique
```python
# Tests par matière
subjects = ['Mathématiques', 'Programmation', 'Physique']
# Évaluation basée sur le contenu et la structure
```

## 📈 Rapports de Test

### Rapport en Temps Réel
- Statut de chaque test (PASS/FAIL/ERROR)
- Messages détaillés
- Temps d'exécution

### Rapport Final
- Statistiques globales
- Taux de réussite par suite
- Recommandations
- Informations de performance

### Fichiers Générés
- `test_results_YYYYMMDD_HHMMSS.json` - Résultats détaillés
- `test_summary_YYYYMMDD_HHMMSS.txt` - Résumé textuel

## 🔧 Configuration des Tests

### Variables d'Environnement
```bash
# URL du serveur de test
TEST_BASE_URL=http://localhost:5000

# Timeout des requêtes
TEST_TIMEOUT=30

# Mode debug
TEST_DEBUG=true
```

### Données de Test
- Utilisateurs de test créés automatiquement
- Cours de test pour toutes les facultés
- Fichiers de soumission simulés
- Scénarios de plagiat prédéfinis

## 🚨 Gestion des Erreurs

### Types d'Erreurs Gérées
- Serveur non disponible
- Timeouts de requête
- Erreurs de validation
- Problèmes de permissions
- Erreurs de base de données

### Récupération Automatique
- Retry automatique pour les erreurs temporaires
- Nettoyage des données de test
- Restauration de l'état initial

## 📋 Checklist de Validation

### ✅ Fonctionnalités Testées

#### Administration
- [x] Connexion administrateur
- [x] Création d'utilisateurs (étudiants/professeurs)
- [x] Import CSV d'utilisateurs
- [x] Gestion des profils utilisateurs
- [x] Configuration du système
- [x] Génération de rapports

#### Gestion des Cours
- [x] Création de cours par faculté
- [x] Assignation des professeurs aux cours
- [x] Inscription automatique des étudiants selon critères
- [x] Gestion du contenu des cours
- [x] Validation des prérequis

#### Devoirs et Soumissions
- [x] Création de devoirs par les professeurs
- [x] Soumission de fichiers (txt, py, pdf, docx)
- [x] Validation des formats et tailles
- [x] Gestion des soumissions tardives
- [x] Travail en groupe (formation manuelle/automatique)

#### Détection de Plagiat
- [x] Comparaison avec soumissions existantes
- [x] Détection de contenu web
- [x] Calcul de pourcentage de similarité
- [x] Classification (acceptable/suspect/plagiat)

#### Correction Automatique
- [x] Correction IA pour mathématiques
- [x] Correction IA pour programmation
- [x] Correction IA pour physique
- [x] Génération de feedback automatique
- [x] Attribution de scores

#### Publication des Notes
- [x] Correction manuelle par professeurs
- [x] Publication immédiate des notes
- [x] Publication programmée
- [x] Notification des étudiants
- [x] Consultation des notes par étudiants

## 🎯 Métriques de Performance

### Temps d'Exécution Cibles
- Tests système complets: < 60 secondes
- Tests utilisateurs: < 30 secondes
- Tests cours: < 45 secondes
- Tests soumissions: < 40 secondes

### Taux de Réussite Attendus
- Production: 100% des tests doivent passer
- Développement: > 95% des tests doivent passer
- Tests critiques: 100% (authentification, sécurité)

## 🔍 Débogage

### Logs de Test
```bash
# Activer les logs détaillés
export TEST_VERBOSE=true
python test/run_all_tests.py
```

### Tests Individuels
```bash
# Tester une fonctionnalité spécifique
python -c "
from test_user_management import TestUserManagement
tester = TestUserManagement()
tester.login_as_admin()
tester.test_student_creation_complete()
"
```

### Vérification Manuelle
1. Vérifier que le serveur répond sur http://localhost:5000
2. Tester la connexion admin (admin/admin123)
3. Vérifier la création d'utilisateurs via l'interface
4. Contrôler les logs du serveur pour les erreurs

## 📞 Support

### En cas de Problème
1. Vérifier que le serveur est démarré
2. Contrôler les logs d'erreur
3. Vérifier les permissions de fichiers
4. Tester manuellement les fonctionnalités qui échouent

### Contact
- Développeur: Jonathan Kakesa
- Email: jonathan.kakesa@ulc-icam.cd
- Date: 19 décembre 2024

---

**🎓 Université Loyola du Congo - Institut Catholique d'Art et Métier**  
**💻 Système ULC-ICAM Turnin - Suite de Tests Complète**