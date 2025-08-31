# Tests Manuels - Cognito Web

## 🚀 Démarrage de l'application
```bash
cd "c:\Users\Twice As Nice\Desktop\ULC-ICAM\ulc-turnin-web"
python app.py
```

## 📋 Liste de vérification des fonctionnalités

### ✅ 1. AUTHENTIFICATION
- [ ] Page d'accueil accessible (http://localhost:5000)
- [ ] Sélection des portails de connexion
- [ ] Connexion Admin (admin/admin123)
- [ ] Connexion Professeur (prof001/prof1pass)
- [ ] Connexion Étudiant (etud001/etud1pass)
- [ ] Déconnexion fonctionne

### ✅ 2. TABLEAU DE BORD ADMINISTRATEUR
- [ ] Statistiques cliquables (Utilisateurs, Devoirs, Soumissions, Étudiants)
- [ ] Navigation vers toutes les pages admin
- [ ] Gestion des utilisateurs
- [ ] Gestion des cours
- [ ] Configuration système
- [ ] Pages dédiées (professeurs, étudiants)

### ✅ 3. GESTION DES UTILISATEURS
- [ ] Ajout étudiant avec formulaire complet
- [ ] Ajout professeur avec formulaire complet
- [ ] Import CSV fonctionne
- [ ] Profils détaillés avec photos
- [ ] Modification des profils
- [ ] Suppression d'utilisateurs

### ✅ 4. GESTION DES COURS
- [ ] Création de cours par admin
- [ ] Attribution aux professeurs
- [ ] Désassignation des professeurs
- [ ] Vue des cours assignés (professeur)

### ✅ 5. TABLEAU DE BORD PROFESSEUR
- [ ] Statistiques cliquables (Devoirs, Soumissions, Étudiants, Cours)
- [ ] Liste des devoirs avec statistiques
- [ ] Accès aux soumissions par devoir
- [ ] Liste des étudiants inscrits
- [ ] Navigation fluide

### ✅ 6. CRÉATION DE DEVOIRS
- [ ] Formulaire de création complet
- [ ] Upload de fichiers joints
- [ ] Options de correction automatique
- [ ] Détection de plagiat
- [ ] Travail de groupe (manuel/automatique)
- [ ] Sélection des cours assignés

### ✅ 7. TRAVAIL DE GROUPE
- [ ] Création devoir de groupe
- [ ] Formation manuelle des groupes
- [ ] Formation automatique des groupes
- [ ] Sélection des coéquipiers
- [ ] Gestion des groupes (professeur)
- [ ] Affichage statut groupe (étudiant)

### ✅ 8. SOUMISSIONS
- [ ] Page de soumission avec fichiers joints
- [ ] Information sur les groupes
- [ ] Téléchargement des ressources
- [ ] Alertes pour travail de groupe
- [ ] Historique des soumissions

### ✅ 9. GESTION DES SOUMISSIONS (PROFESSEUR)
- [ ] Vue globale des soumissions
- [ ] Soumissions par devoir
- [ ] Statistiques détaillées
- [ ] Liste "Ont soumis" vs "N'ont pas soumis"
- [ ] Téléchargement des fichiers
- [ ] Taux de participation

### ✅ 10. CORRECTION ET PLAGIAT
- [ ] Simulation correction automatique
- [ ] Simulation détection plagiat
- [ ] Résultats avec scores
- [ ] Feedback automatique
- [ ] Statuts de correction

### ✅ 11. CONFIGURATION SYSTÈME
- [ ] Gestion des promotions
- [ ] Gestion des facultés
- [ ] Gestion des départements
- [ ] Gestion des grades
- [ ] Ajout/suppression d'éléments

### ✅ 12. DONNÉES DE TEST
- [ ] 50 professeurs chargés
- [ ] 100 étudiants chargés
- [ ] 60 cours créés
- [ ] 95 devoirs générés
- [ ] Inscriptions automatiques
- [ ] Noms congolais réalistes

## 🧪 Tests Spécifiques

### Test 1: Workflow Administrateur
1. Connexion admin
2. Créer un cours
3. Assigner un professeur
4. Voir les statistiques
5. Gérer la configuration

### Test 2: Workflow Professeur
1. Connexion professeur
2. Voir ses cours assignés
3. Créer un devoir normal
4. Créer un devoir de groupe
5. Voir les soumissions
6. Gérer les groupes

### Test 3: Workflow Étudiant
1. Connexion étudiant
2. Voir les devoirs disponibles
3. Former un groupe (si applicable)
4. Soumettre un devoir
5. Changer son mot de passe

### Test 4: Travail de Groupe
1. Professeur crée devoir de groupe
2. Étudiant 1 forme un groupe
3. Sélectionne des coéquipiers
4. Professeur vérifie les groupes
5. Soumission en groupe

### Test 5: Gestion des Fichiers
1. Professeur joint des fichiers au devoir
2. Étudiant télécharge les ressources
3. Étudiant soumet son travail
4. Professeur télécharge les soumissions

## 🔍 Points de Vérification Critiques

### Sécurité
- [ ] Accès restreint selon les rôles
- [ ] Redirection si non authentifié
- [ ] Changement mot de passe obligatoire

### Interface
- [ ] Design responsive
- [ ] Navigation intuitive
- [ ] Messages d'erreur clairs
- [ ] Badges et statuts visuels

### Données
- [ ] Cohérence entre facultés/départements
- [ ] Statistiques correctes
- [ ] Inscriptions automatiques
- [ ] Groupes bien formés

### Performance
- [ ] Pages se chargent rapidement
- [ ] Upload de fichiers fonctionne
- [ ] Pas d'erreurs JavaScript
- [ ] Navigation fluide

## 🚨 Problèmes Potentiels à Vérifier

1. **Erreurs 404/500** sur certaines pages
2. **Données manquantes** dans les formulaires
3. **Problèmes d'upload** de fichiers
4. **Groupes mal formés** automatiquement
5. **Statistiques incorrectes** dans les tableaux de bord
6. **Navigation cassée** entre les pages
7. **Problèmes de session** lors de la déconnexion

## 📊 Critères de Réussite

- ✅ **100% des pages** accessibles sans erreur
- ✅ **Tous les formulaires** fonctionnent
- ✅ **Upload/download** de fichiers opérationnel
- ✅ **Système de groupes** complet
- ✅ **Statistiques** correctes et à jour
- ✅ **Navigation** fluide entre toutes les sections
- ✅ **Données de test** complètes et cohérentes

## 🎯 Commandes de Test

```bash
# Test automatique
python test_functionality.py

# Vérification des données
python generate_test_data.py

# Démarrage application
python app.py
```