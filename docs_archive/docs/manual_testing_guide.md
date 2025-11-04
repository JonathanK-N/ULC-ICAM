# 🧪 Guide de Tests Manuels - ULC-ICAM Turnin

## 📋 Checklist de Validation Complète

### 🔐 **1. AUTHENTIFICATION ET SÉCURITÉ**

#### Test 1.1: Connexion Administrateur
- [ ] Aller sur `/login/admin`
- [ ] Tenter connexion avec `admin` / `admin123`
- [ ] Vérifier redirection vers dashboard admin
- [ ] Vérifier session établie (nom affiché)
- [ ] Tester déconnexion

#### Test 1.2: Connexion Étudiant
- [ ] Aller sur `/login/student`
- [ ] Tester avec CIP: `ETU001` (avec/sans mot de passe)
- [ ] Vérifier accès dashboard étudiant
- [ ] Tester avec email étudiant
- [ ] Vérifier échec avec mauvais identifiants

#### Test 1.3: Connexion Professeur
- [ ] Aller sur `/login/teacher`
- [ ] Tester avec CIP: `PROF001`
- [ ] Vérifier accès dashboard professeur
- [ ] Tester création de devoir
- [ ] Vérifier gestion des cours

#### Test 1.4: Contrôle d'Accès
- [ ] Sans connexion, tenter `/admin/users` → Redirection
- [ ] Étudiant connecté, tenter `/teacher/assignments` → Refus
- [ ] Professeur connecté, tenter `/admin/users` → Refus

### 👥 **2. GESTION DES UTILISATEURS (ADMIN)**

#### Test 2.1: Liste des Utilisateurs
- [ ] Connexion admin → `/admin/users`
- [ ] Vérifier affichage de tous les utilisateurs
- [ ] Vérifier filtrage par rôle
- [ ] Tester recherche d'utilisateur

#### Test 2.2: Ajout d'Étudiant
- [ ] `/admin/add_student`
- [ ] Remplir tous les champs obligatoires
- [ ] Vérifier validation des données
- [ ] Confirmer création réussie
- [ ] Vérifier dans la liste

#### Test 2.3: Ajout de Professeur
- [ ] `/admin/add_teacher`
- [ ] Remplir informations professeur
- [ ] Tester grades et départements
- [ ] Confirmer création
- [ ] Vérifier assignation possible aux cours

#### Test 2.4: Import CSV
- [ ] `/admin/import_csv`
- [ ] Créer fichier CSV test
- [ ] Importer utilisateurs en lot
- [ ] Vérifier import réussi
- [ ] Contrôler données importées

### 🎓 **3. GESTION DES COURS**

#### Test 3.1: Création de Cours (Admin)
- [ ] `/admin/add_course`
- [ ] Créer cours avec toutes les informations
- [ ] Vérifier facultés et promotions
- [ ] Confirmer création
- [ ] Vérifier dans liste des cours

#### Test 3.2: Assignation Professeur
- [ ] Sélectionner un cours créé
- [ ] Assigner un professeur au cours
- [ ] Vérifier assignation réussie
- [ ] Tester désassignation

#### Test 3.3: Inscription Étudiants
- [ ] Connexion professeur
- [ ] Aller sur cours assigné
- [ ] Inscrire des étudiants éligibles
- [ ] Vérifier critères d'éligibilité
- [ ] Tester désinscription

### 📝 **4. GESTION DES DEVOIRS**

#### Test 4.1: Création de Devoir (Professeur)
- [ ] Connexion professeur → `/teacher/create_assignment`
- [ ] Remplir titre, description, date limite
- [ ] Sélectionner cours
- [ ] Activer options IA (plagiat + correction)
- [ ] Configurer travail de groupe si nécessaire
- [ ] Confirmer création

#### Test 4.2: Configuration Avancée
- [ ] Tester note maximale personnalisée
- [ ] Configurer groupes automatiques
- [ ] Définir date de publication des résultats
- [ ] Ajouter fichiers de consignes
- [ ] Vérifier toutes les options

### 📤 **5. SOUMISSION DE FICHIERS**

#### Test 5.1: Soumission Simple (Étudiant)
- [ ] Connexion étudiant
- [ ] Voir devoir disponible sur dashboard
- [ ] Cliquer "Soumettre" → `/submit/{id}`
- [ ] Sélectionner fichier (PDF, DOCX, TXT)
- [ ] Confirmer soumission
- [ ] Vérifier message de succès

#### Test 5.2: Validation des Fichiers
- [ ] Tester fichier trop volumineux (>16MB)
- [ ] Tester formats non autorisés
- [ ] Vérifier messages d'erreur appropriés
- [ ] Tester caractères spéciaux dans nom

#### Test 5.3: Resoumission
- [ ] Soumettre un premier fichier
- [ ] Soumettre un second fichier
- [ ] Vérifier remplacement ou historique
- [ ] Contrôler horodatage

### 🤖 **6. FONCTIONNALITÉS IA**

#### Test 6.1: Détection de Plagiat
- [ ] Créer devoir avec détection activée
- [ ] Soumettre fichier avec contenu dupliqué
- [ ] Vérifier analyse de plagiat
- [ ] Contrôler pourcentage de similarité
- [ ] Vérifier sources détectées

#### Test 6.2: Correction Automatique
- [ ] Créer devoir avec correction IA
- [ ] Soumettre fichier de qualité variable
- [ ] Vérifier note automatique générée
- [ ] Contrôler feedback détaillé
- [ ] Tester avec différents types de contenu

#### Test 6.3: Traitement Asynchrone
- [ ] Soumettre fichier volumineux
- [ ] Vérifier message "traitement en cours"
- [ ] Attendre fin du traitement
- [ ] Contrôler résultats finaux

### 📊 **7. CORRECTION ET NOTATION**

#### Test 7.1: Correction Manuelle (Professeur)
- [ ] Voir soumissions d'un devoir
- [ ] Ouvrir interface de correction
- [ ] Attribuer note manuelle
- [ ] Ajouter commentaires détaillés
- [ ] Joindre fichier de correction
- [ ] Sauvegarder correction

#### Test 7.2: Publication des Résultats
- [ ] Corriger plusieurs soumissions
- [ ] Publier résultats individuellement
- [ ] Publier tous les résultats d'un coup
- [ ] Vérifier visibilité côté étudiant
- [ ] Tester masquage des résultats

#### Test 7.3: Consultation Notes (Étudiant)
- [ ] Connexion étudiant → `/student/my_grades`
- [ ] Vérifier notes publiées visibles
- [ ] Contrôler notes non publiées masquées
- [ ] Télécharger fichiers de correction
- [ ] Vérifier détails de plagiat si applicable

### 👥 **8. TRAVAIL DE GROUPE**

#### Test 8.1: Formation de Groupes
- [ ] Créer devoir en groupe (formation manuelle)
- [ ] Étudiant: rejoindre/créer groupe
- [ ] Vérifier limitation taille groupe
- [ ] Tester exclusion après formation

#### Test 8.2: Groupes Automatiques
- [ ] Créer devoir avec groupes auto
- [ ] Vérifier formation automatique
- [ ] Contrôler répartition équitable
- [ ] Tester avec nombre impair d'étudiants

#### Test 8.3: Soumission de Groupe
- [ ] Un membre soumet pour le groupe
- [ ] Vérifier visibilité pour tous les membres
- [ ] Tester correction de groupe
- [ ] Contrôler attribution des notes

### 📈 **9. MONITORING ET PERFORMANCE**

#### Test 9.1: Dashboard Performance (Admin)
- [ ] Connexion admin → `/admin/performance`
- [ ] Vérifier métriques temps réel
- [ ] Contrôler utilisation CPU/RAM
- [ ] Tester rafraîchissement automatique
- [ ] Vérifier alertes si surcharge

#### Test 9.2: Statistiques Système
- [ ] `/admin/system_stats`
- [ ] Vérifier compteurs utilisateurs
- [ ] Contrôler statistiques cours/devoirs
- [ ] Tester export des données
- [ ] Vérifier logs d'activité

### 🔧 **10. FONCTIONNALITÉS AVANCÉES**

#### Test 10.1: Contenu de Cours
- [ ] Professeur: ajouter description cours
- [ ] Créer chapitres avec contenu
- [ ] Ajouter exercices et documents
- [ ] Vérifier accès étudiant au contenu
- [ ] Tester téléchargement documents

#### Test 10.2: Configuration Système
- [ ] Admin: modifier promotions/facultés
- [ ] Ajouter nouveaux départements
- [ ] Configurer grades professeurs
- [ ] Tester impact sur formulaires

#### Test 10.3: Gestion des Fichiers
- [ ] Vérifier stockage sécurisé
- [ ] Tester téléchargement par rôle
- [ ] Contrôler noms de fichiers
- [ ] Vérifier nettoyage automatique

## 🎯 **Critères de Validation**

### ✅ **SUCCÈS** si:
- [ ] Toutes les connexions fonctionnent
- [ ] Contrôles d'accès respectés
- [ ] Soumissions traitées correctement
- [ ] IA fonctionne (plagiat + correction)
- [ ] Données persistantes
- [ ] Performance acceptable (<2s par page)
- [ ] Aucune erreur critique

### ⚠️ **ATTENTION** si:
- [ ] Quelques fonctionnalités mineures défaillantes
- [ ] Performance dégradée mais acceptable
- [ ] Erreurs non critiques occasionnelles

### ❌ **ÉCHEC** si:
- [ ] Connexions impossibles
- [ ] Soumissions perdues
- [ ] Erreurs critiques fréquentes
- [ ] Sécurité compromise
- [ ] Performance inacceptable (>5s)

## 📊 **Rapport de Test**

### Modèle de Rapport:
```
RAPPORT DE TEST ULC-ICAM TURNIN
Date: ___________
Testeur: ___________

RÉSULTATS:
✅ Fonctionnalités OK: ___/50
⚠️ Problèmes mineurs: ___
❌ Problèmes critiques: ___

SCORE GLOBAL: ___%

RECOMMANDATIONS:
1. ________________
2. ________________
3. ________________

PRÊT POUR PRODUCTION: OUI/NON
```

## 🚀 **Tests de Charge (Optionnel)**

### Test de Montée en Charge:
1. **10 utilisateurs simultanés** → Performance OK?
2. **50 soumissions en parallèle** → Système stable?
3. **100 connexions/minute** → Rate limiting OK?
4. **Fichiers 15MB multiples** → Stockage OK?

### Outils Recommandés:
- **Apache Bench**: `ab -n 100 -c 10 http://localhost:5000/`
- **Postman** pour tests API
- **Browser DevTools** pour performance frontend