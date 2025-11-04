# Guide Professeur - Système ULC-ICAM

## Table des Matières
1. [Première Connexion](#première-connexion)
2. [Tableau de Bord Professeur](#tableau-de-bord-professeur)
3. [Gestion des Cours](#gestion-des-cours)
4. [Création de Devoirs](#création-de-devoirs)
5. [Devoirs de Programmation](#devoirs-de-programmation)
6. [Correction et Évaluation](#correction-et-évaluation)
7. [Gestion des Notes](#gestion-des-notes)
8. [Communication](#communication)
9. [Outils Avancés](#outils-avancés)

## Première Connexion

### Accès au Système
- **URL** : `http://localhost:5000/login`
- **Identifiants** : Fournis par l'administrateur
- **Format email** : `prenom.nom@ulc-icam.edu.km`

### Configuration Initiale
1. Connectez-vous avec vos identifiants
2. **Changez votre mot de passe** immédiatement
3. Complétez votre profil :
   - Photo de profil (optionnelle)
   - Spécialité
   - Bureau
   - Heures de consultation
4. Vérifiez vos cours assignés

## Tableau de Bord Professeur

### Vue d'Ensemble
Votre tableau de bord affiche :
- **Mes Cours** : Liste de vos cours avec nombre d'étudiants
- **Devoirs Récents** : Derniers devoirs créés
- **Soumissions en Attente** : Travaux à corriger
- **Statistiques** : Performance de vos étudiants
- **Calendrier** : Échéances importantes

### Navigation Rapide
- **Créer un Devoir** : Bouton d'accès rapide
- **Mes Cours** : Gestion de tous vos cours
- **Corrections** : Travaux en attente de correction
- **Notes** : Gestion des évaluations

## Gestion des Cours

### Accéder à un Cours
1. Cliquez sur le cours dans votre tableau de bord
2. Ou utilisez "Mes Cours" → Sélectionner le cours

### Interface du Cours
- **Informations générales** : Code, nom, crédits, semestre
- **Étudiants inscrits** : Liste complète avec statuts
- **Devoirs** : Tous les devoirs du cours
- **Statistiques** : Performance globale de la classe

### Gérer les Étudiants
- **Voir la liste** : Tous les étudiants inscrits
- **Statistiques individuelles** : Performance par étudiant
- **Historique des soumissions** : Travaux rendus
- **Notes** : Évaluations attribuées

## Création de Devoirs

### Devoir Traditionnel
1. **Accédez à votre cours**
2. **Cliquez "Créer un Devoir"**
3. **Remplissez les informations** :
   - **Titre** : Nom du devoir
   - **Description** : Consignes détaillées
   - **Type** : "Devoir traditionnel"
   - **Date limite** : Date et heure de remise
   - **Note maximale** : Points attribuables
   - **Instructions** : Consignes spécifiques

4. **Options avancées** :
   - **Soumissions multiples** : Autoriser plusieurs tentatives
   - **Affichage des notes** : Immédiat ou différé
   - **Fichiers autorisés** : Types de fichiers acceptés
   - **Taille maximale** : Limite de taille des fichiers

### Paramètres de Soumission
- **Types de fichiers acceptés** :
  - Documents : PDF, DOC, DOCX
  - Images : JPG, PNG, GIF
  - Archives : ZIP, RAR
  - Code : TXT, PY, JAVA, CPP, etc.
- **Taille maximale** : 50 MB par fichier
- **Nombre de fichiers** : Jusqu'à 10 fichiers par soumission

## Devoirs de Programmation

### Création d'un Devoir de Code
1. **Sélectionnez "Devoir de programmation"**
2. **Configurez les paramètres** :
   - **Langage** : Python, Java, C++, C, JavaScript
   - **Environnement** : Version du langage
   - **Limite de temps** : Temps d'exécution maximum (10s max)
   - **Limite mémoire** : Mémoire allouée

### Configuration des Tests
1. **Tests automatiques** :
   - **Entrée** : Données d'entrée du test
   - **Sortie attendue** : Résultat correct
   - **Points** : Valeur du test
   - **Visible** : Test visible par l'étudiant ou caché

2. **Exemple de configuration** :
   ```
   Test 1 (Visible):
   Entrée: 5 3
   Sortie: 8
   Points: 2
   
   Test 2 (Caché):
   Entrée: 10 -2
   Sortie: 8
   Points: 3
   ```

### Langages Supportés

#### Python
- **Version** : 3.8+
- **Modules disponibles** : math, random, sys, os
- **Format d'entrée** : input() ou sys.stdin
- **Format de sortie** : print()

#### Java
- **Version** : OpenJDK 11
- **Classe principale** : Main
- **Entrée** : Scanner ou System.in
- **Sortie** : System.out.println()

#### C++
- **Compilateur** : GCC 9.4
- **Standard** : C++17
- **Entrée** : cin
- **Sortie** : cout

#### C
- **Compilateur** : GCC 9.4
- **Standard** : C11
- **Entrée** : scanf
- **Sortie** : printf

#### JavaScript
- **Runtime** : Node.js 14
- **Entrée** : readline ou process.stdin
- **Sortie** : console.log()

## Correction et Évaluation

### Accéder aux Soumissions
1. **Depuis le cours** : Cliquez sur le devoir
2. **Ou depuis le tableau de bord** : "Corrections en attente"

### Interface de Correction

#### Devoirs Traditionnels
- **Fichiers soumis** : Téléchargement et visualisation
- **Zone de commentaires** : Feedback détaillé
- **Attribution de note** : Sur la note maximale définie
- **Statut** : Brouillon, Corrigé, Publié

#### Devoirs de Programmation
- **Code soumis** : Visualisation avec coloration syntaxique
- **Résultats des tests** : Automatiques et détaillés
- **Exécution manuelle** : Tester avec vos propres entrées
- **Correction hybride** : Note automatique + ajustement manuel

### Outils de Correction

#### Détection de Plagiat
- **Activation automatique** pour tous les devoirs
- **Rapport de similarité** : Pourcentage et sources
- **Comparaison** : Entre étudiants et bases de données
- **Actions** : Signalement et investigation

#### Commentaires et Feedback
- **Commentaires généraux** : Feedback global
- **Annotations** : Commentaires sur parties spécifiques
- **Suggestions d'amélioration** : Conseils personnalisés
- **Ressources** : Liens vers documentation/cours

### Grille d'Évaluation
Créez des grilles personnalisées :
- **Critères** : Fonctionnalité, style, documentation
- **Barème** : Points par critère
- **Commentaires** : Feedback par critère
- **Total automatique** : Calcul de la note finale

## Gestion des Notes

### Attribution des Notes
1. **Note numérique** : Sur la note maximale définie
2. **Commentaires** : Justification de la note
3. **Statut** : Brouillon (non visible) ou Publié (visible)

### Publication des Résultats
- **Publication individuelle** : Note par note
- **Publication groupée** : Toutes les notes d'un devoir
- **Notification automatique** : Email aux étudiants
- **Statistiques** : Moyenne, médiane, distribution

### Export des Notes
- **Format CSV** : Pour tableurs
- **Format PDF** : Relevés de notes
- **Intégration** : Systèmes de gestion scolaire

## Communication

### Annonces
1. **Créer une annonce** dans le cours
2. **Titre et contenu** : Message aux étudiants
3. **Priorité** : Normale, Importante, Urgente
4. **Notification** : Email automatique

### Messages Individuels
- **Répondre aux questions** des étudiants
- **Feedback personnalisé** sur les travaux
- **Suivi individuel** des difficultés

### Forum de Discussion
- **Questions/Réponses** : Espace d'échange
- **Modération** : Contrôle des messages
- **FAQ** : Questions fréquentes

## Outils Avancés

### Statistiques et Analyses

#### Performance de la Classe
- **Moyenne générale** : Note moyenne du cours
- **Distribution des notes** : Histogramme
- **Taux de réussite** : Pourcentage de réussite
- **Évolution** : Progression dans le temps

#### Analyse Individuelle
- **Profil étudiant** : Historique complet
- **Points forts/faibles** : Analyse des compétences
- **Recommandations** : Suggestions d'amélioration
- **Suivi personnalisé** : Évolution individuelle

### Outils de Programmation

#### Éditeur de Code Intégré
- **Monaco Editor** : Éditeur professionnel
- **Coloration syntaxique** : Support multi-langages
- **Auto-complétion** : Suggestions de code
- **Détection d'erreurs** : Erreurs de syntaxe

#### Tests et Débogage
- **Exécution en temps réel** : Test immédiat du code
- **Débogage** : Points d'arrêt et inspection
- **Profiling** : Analyse des performances
- **Logs d'exécution** : Historique détaillé

### Réutilisation et Templates

#### Bibliothèque de Devoirs
- **Sauvegarde** : Devoirs comme templates
- **Partage** : Avec d'autres professeurs
- **Modification** : Adaptation aux besoins
- **Historique** : Versions précédentes

#### Banque de Tests
- **Tests réutilisables** : Pour différents devoirs
- **Catégorisation** : Par difficulté/concept
- **Import/Export** : Partage entre cours

## Bonnes Pratiques

### Création de Devoirs
- **Consignes claires** : Instructions précises
- **Exemples** : Cas d'usage concrets
- **Critères d'évaluation** : Barème transparent
- **Ressources** : Documentation et aide

### Correction Efficace
- **Feedback constructif** : Commentaires utiles
- **Cohérence** : Barème uniforme
- **Rapidité** : Correction dans les délais
- **Suivi** : Vérification de la compréhension

### Gestion de Classe
- **Communication régulière** : Annonces fréquentes
- **Disponibilité** : Réponses rapides aux questions
- **Encouragement** : Motivation des étudiants
- **Adaptation** : Ajustement selon les besoins

## Résolution de Problèmes

### Problèmes Techniques
- **Code qui ne s'exécute pas** : Vérifiez la syntaxe et les limites
- **Tests qui échouent** : Vérifiez les entrées/sorties
- **Fichiers non téléchargeables** : Vérifiez les permissions
- **Notes non sauvegardées** : Vérifiez la connexion

### Support
- **Documentation** : Guides détaillés disponibles
- **Support technique** : admin@ulc-icam.edu.km
- **Formation** : Sessions de formation disponibles
- **Communauté** : Forum des enseignants

---

**Support Professeurs** : teachers@ulc-icam.edu.km  
**Documentation mise à jour** : Décembre 2024