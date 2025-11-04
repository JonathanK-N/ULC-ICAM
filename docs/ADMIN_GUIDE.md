# Guide Administrateur - Système ULC-ICAM

## Table des Matières
1. [Accès Administrateur](#accès-administrateur)
2. [Tableau de Bord](#tableau-de-bord)
3. [Gestion des Utilisateurs](#gestion-des-utilisateurs)
4. [Configuration Système](#configuration-système)
5. [Gestion des Cours](#gestion-des-cours)
6. [Import CSV](#import-csv)
7. [Sauvegarde et Restauration](#sauvegarde-et-restauration)
8. [Surveillance et Logs](#surveillance-et-logs)
9. [Maintenance](#maintenance)

## Accès Administrateur

### Connexion Initiale
- **URL**: `http://localhost:5000/login`
- **Compte par défaut**: 
  - Email: `admin@ulc-icam.edu.km`
  - Mot de passe: `admin123` (à changer immédiatement)

### Première Configuration
1. Connectez-vous avec le compte administrateur par défaut
2. Changez immédiatement le mot de passe administrateur
3. Configurez les paramètres système de base
4. Créez les comptes utilisateurs initiaux

## Tableau de Bord

### Vue d'Ensemble
Le tableau de bord administrateur affiche :
- **Statistiques en temps réel** :
  - Nombre total d'utilisateurs
  - Nombre de devoirs actifs
  - Nombre de soumissions
  - Répartition étudiants/professeurs
  - Nombre de cours

### Cartes de Navigation Rapide
- **Gestion des Utilisateurs** : Ajouter/modifier utilisateurs
- **Configuration Système** : Paramètres globaux
- **Gestion des Cours** : Administration des cours
- **Import CSV** : Import en masse d'utilisateurs

## Gestion des Utilisateurs

### Ajouter un Étudiant
1. Cliquez sur "Ajouter Étudiant"
2. Remplissez les champs obligatoires :
   - **Nom complet**
   - **Email** (format : prenom.nom@ulc-icam.edu.km)
   - **Numéro étudiant** (unique)
   - **Faculté** : Faculté des Sciences et Technologies (ULC-ICAM)
   - **Département** : Sélectionnez parmi les 8 départements
   - **Promotion** : Année d'études
   - **Grade** : Niveau académique
3. Le mot de passe par défaut sera généré automatiquement
4. L'étudiant recevra ses identifiants par email

### Ajouter un Professeur
1. Cliquez sur "Ajouter Enseignant"
2. Remplissez les informations :
   - **Nom complet**
   - **Email** (format : prenom.nom@ulc-icam.edu.km)
   - **Spécialité** : Domaine d'expertise
   - **Département** : Département d'affectation
   - **Titre** : Professeur, Maître de conférences, etc.
3. Assignez les cours si nécessaire
4. Définissez les permissions spécifiques

### Modifier un Utilisateur
1. Accédez à "Voir tous" dans la section utilisateurs
2. Cliquez sur "Modifier" à côté de l'utilisateur
3. Modifiez les informations nécessaires
4. **Important** : Pour les administrateurs, assurez-vous de maintenir le rôle "admin"
5. Sauvegardez les modifications

### Supprimer un Utilisateur
1. Sélectionnez l'utilisateur à supprimer
2. Cliquez sur "Supprimer"
3. **Attention** : Cette action est irréversible
4. Toutes les soumissions et données associées seront supprimées

## Configuration Système

### Gestion des Facultés
- **Ajouter une Faculté** :
  1. Accédez à "Configurer le Système"
  2. Section "Facultés"
  3. Cliquez "Ajouter Faculté"
  4. Saisissez le nom complet
  
- **Modifier/Supprimer** :
  - Utilisez les boutons d'action à côté de chaque faculté
  - **Attention** : La suppression d'une faculté supprime tous ses départements

### Gestion des Départements
- **Ajouter un Département** :
  1. Sélectionnez la faculté parente
  2. Cliquez "Ajouter Département"
  3. Saisissez le nom du département
  
- **Départements par défaut** (ULC-ICAM) :
  - Mathématiques & Informatique
  - Génie Mécanique
  - Génie Électrique
  - Physique & Chimie
  - Génie Informatique
  - Maintenance & Génie Industriels
  - Énergie/Environnement/Matériaux
  - Polytechnique Générale

### Gestion des Promotions et Grades
- **Promotions** : L1, L2, L3, M1, M2
- **Grades** : Licence, Master, Doctorat
- Ajoutez/modifiez selon les besoins institutionnels

### Paramètres Système
- **Taille maximale des fichiers** : 50 MB par défaut
- **Langages de programmation supportés** :
  - Python (3.8+)
  - Java (OpenJDK 11)
  - C++ (GCC 9.4)
  - C (GCC 9.4)
  - JavaScript (Node.js 14)
- **Délai d'exécution** : 10 secondes maximum
- **Détection de plagiat** : Activée par défaut

## Gestion des Cours

### Créer un Cours
1. Accédez à "Gérer les Cours"
2. Cliquez "Créer un Cours"
3. Remplissez les informations :
   - **Nom du cours**
   - **Code du cours** (ex: INFO101)
   - **Description**
   - **Crédits ECTS**
   - **Département**
   - **Semestre**
4. Assignez un professeur responsable
5. Définissez les étudiants inscrits

### Assigner des Professeurs
- Un cours peut avoir plusieurs professeurs
- Le professeur principal a tous les droits
- Les professeurs secondaires peuvent corriger et noter

### Gérer les Inscriptions
- **Inscription individuelle** : Ajoutez des étudiants un par un
- **Inscription par promotion** : Inscrivez toute une promotion
- **Import CSV** : Utilisez l'import en masse

## Import CSV

### Format des Fichiers CSV

#### Étudiants (students_template.csv)
```csv
nom_complet,email,numero_etudiant,faculte,departement,promotion,grade
Jean Dupont,jean.dupont@ulc-icam.edu.km,20240001,Faculté des Sciences et Technologies (ULC-ICAM),Mathématiques & Informatique,L1,Licence
```

#### Professeurs (teachers_template.csv)
```csv
nom_complet,email,specialite,departement,titre
Dr. Marie Martin,marie.martin@ulc-icam.edu.km,Informatique,Mathématiques & Informatique,Professeur
```

### Procédure d'Import
1. Téléchargez le template approprié
2. Remplissez le fichier CSV avec vos données
3. Respectez exactement les noms de colonnes
4. Utilisez les valeurs exactes pour faculté/département
5. Uploadez le fichier via l'interface
6. Vérifiez les erreurs éventuelles
7. Confirmez l'import

### Gestion des Erreurs
- **Emails en double** : L'import s'arrêtera
- **Départements inexistants** : Créez-les d'abord
- **Format invalide** : Vérifiez les colonnes obligatoires

## Sauvegarde et Restauration

### Configuration de la Sauvegarde
1. Accédez aux paramètres de sauvegarde
2. Configurez les fournisseurs cloud :
   - **AWS S3** : Clés d'accès, région, bucket
   - **Google Cloud** : Fichier de service, bucket
   - **Azure** : Chaîne de connexion, conteneur
3. Définissez la planification :
   - **Sauvegarde complète** : Hebdomadaire (dimanche 2h00)
   - **Sauvegarde incrémentale** : Quotidienne (2h00)
4. Configurez la rétention : 30 jours par défaut

### Sauvegarde Manuelle
1. Tableau de bord → "Sauvegarde"
2. Sélectionnez le type :
   - **Complète** : Toute la base de données
   - **Incrémentale** : Modifications récentes
3. Choisissez la destination
4. Lancez la sauvegarde
5. Surveillez le statut

### Restauration
1. Accédez à l'interface de restauration
2. Sélectionnez le point de restauration
3. **Attention** : Arrêtez l'application avant restauration
4. Lancez la restauration
5. Redémarrez l'application
6. Vérifiez l'intégrité des données

## Surveillance et Logs

### Logs Système
- **Emplacement** : `/logs/system.log`
- **Rotation** : Quotidienne, 30 jours de rétention
- **Niveaux** : ERROR, WARNING, INFO, DEBUG

### Logs d'Audit
- **Connexions utilisateurs**
- **Modifications de données**
- **Actions administratives**
- **Tentatives d'accès non autorisées**

### Monitoring
- **Performance** : Temps de réponse, utilisation CPU/RAM
- **Sécurité** : Tentatives de connexion, accès suspects
- **Utilisation** : Statistiques d'usage par utilisateur

## Maintenance

### Maintenance Préventive
- **Nettoyage des fichiers temporaires** : Hebdomadaire
- **Optimisation base de données** : Mensuelle
- **Mise à jour des dépendances** : Trimestrielle
- **Test des sauvegardes** : Mensuel

### Résolution de Problèmes

#### Problèmes de Performance
1. Vérifiez l'utilisation des ressources
2. Optimisez la base de données
3. Nettoyez les fichiers temporaires
4. Redémarrez l'application si nécessaire

#### Problèmes de Connexion
1. Vérifiez les logs d'erreur
2. Testez la connectivité réseau
3. Vérifiez la configuration des ports
4. Redémarrez les services

#### Problèmes d'Exécution de Code
1. Vérifiez la connexion à Judge0 API
2. Testez les langages individuellement
3. Vérifiez les limites de ressources
4. Consultez les logs d'exécution

### Commandes Utiles
```bash
# Redémarrer l'application
python app.py

# Vérifier les logs
tail -f logs/system.log

# Sauvegarde manuelle
python backup/backup_manager.py --full

# Test de connectivité Judge0
curl -X GET "https://judge0-ce.p.rapidapi.com/languages"
```

## Sécurité

### Bonnes Pratiques
- Changez régulièrement les mots de passe administrateur
- Activez l'authentification à deux facteurs si disponible
- Surveillez les logs d'accès
- Maintenez le système à jour
- Limitez les accès administrateur au strict nécessaire

### Gestion des Permissions
- **Administrateur** : Accès complet
- **Professeur** : Gestion des cours assignés
- **Étudiant** : Accès aux cours inscrits uniquement

### Chiffrement
- **Base de données** : Chiffrement au repos
- **Sauvegardes** : Chiffrement AES-256
- **Communications** : HTTPS obligatoire en production

---

**Support Technique** : admin@ulc-icam.edu.km  
**Documentation mise à jour** : Décembre 2024