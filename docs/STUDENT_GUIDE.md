# Guide Étudiant - Système ULC-ICAM

## Table des Matières
1. [Première Connexion](#première-connexion)
2. [Tableau de Bord Étudiant](#tableau-de-bord-étudiant)
3. [Mes Cours](#mes-cours)
4. [Devoirs et Soumissions](#devoirs-et-soumissions)
5. [Devoirs de Programmation](#devoirs-de-programmation)
6. [Consultation des Notes](#consultation-des-notes)
7. [Communication](#communication)
8. [Profil et Paramètres](#profil-et-paramètres)
9. [Conseils et Bonnes Pratiques](#conseils-et-bonnes-pratiques)

## Première Connexion

### Accès au Système
- **URL** : `http://localhost:5000/login`
- **Identifiants** : Fournis par l'administration
- **Format email** : `prenom.nom@ulc-icam.edu.km`
- **Mot de passe initial** : Fourni par email

### Configuration Initiale
1. **Connectez-vous** avec vos identifiants
2. **Changez votre mot de passe** immédiatement
3. **Complétez votre profil** :
   - Photo de profil (optionnelle)
   - Informations personnelles
   - Préférences de notification
4. **Vérifiez vos cours** inscrits

### Récupération de Mot de Passe
Si vous oubliez votre mot de passe :
1. Cliquez sur "Mot de passe oublié ?"
2. Saisissez votre email étudiant
3. Suivez les instructions reçues par email
4. Ou contactez l'administration : admin@ulc-icam.edu.km

## Tableau de Bord Étudiant

### Vue d'Ensemble
Votre tableau de bord affiche :
- **Mes Cours** : Liste de vos cours avec professeurs
- **Devoirs à Rendre** : Échéances importantes
- **Notes Récentes** : Dernières évaluations
- **Annonces** : Messages des professeurs
- **Calendrier** : Planning des échéances

### Informations Personnelles
- **Nom complet** : Votre identité
- **Numéro étudiant** : Identifiant unique
- **Faculté** : Faculté des Sciences et Technologies (ULC-ICAM)
- **Département** : Votre spécialisation
- **Promotion** : Votre niveau d'études (L1, L2, L3, M1, M2)
- **Grade** : Licence, Master, etc.

### Navigation Rapide
- **Mes Cours** : Accès direct à vos cours
- **Devoirs** : Travaux en cours et à venir
- **Notes** : Consultez vos évaluations
- **Profil** : Gérez vos informations

## Mes Cours

### Accéder à un Cours
1. Cliquez sur le cours dans votre tableau de bord
2. Ou utilisez "Mes Cours" → Sélectionner le cours

### Interface du Cours
- **Informations générales** :
  - Code du cours (ex: INFO101)
  - Nom complet du cours
  - Professeur responsable
  - Crédits ECTS
  - Semestre

- **Contenu du cours** :
  - **Devoirs** : Tous les travaux assignés
  - **Annonces** : Messages du professeur
  - **Ressources** : Documents et liens utiles
  - **Notes** : Vos évaluations

### Statut d'Inscription
- **Inscrit** : Vous pouvez participer activement
- **Auditeur** : Accès en lecture seule
- **Suspendu** : Accès temporairement restreint

## Devoirs et Soumissions

### Types de Devoirs
1. **Devoirs traditionnels** : Documents, rapports, exercices
2. **Devoirs de programmation** : Code à développer et tester

### Consulter un Devoir
1. **Accédez au cours** concerné
2. **Cliquez sur le devoir** dans la liste
3. **Lisez attentivement** :
   - **Consignes** : Instructions détaillées
   - **Date limite** : Échéance de remise
   - **Note maximale** : Points attribuables
   - **Critères d'évaluation** : Barème de notation
   - **Ressources** : Documents d'aide

### Soumettre un Devoir Traditionnel

#### Préparation
1. **Lisez les consignes** complètement
2. **Vérifiez les formats** acceptés :
   - Documents : PDF, DOC, DOCX
   - Images : JPG, PNG, GIF
   - Archives : ZIP, RAR
3. **Respectez la taille maximale** : 50 MB par fichier

#### Soumission
1. **Cliquez "Soumettre"** sur le devoir
2. **Sélectionnez vos fichiers** :
   - Glissez-déposez ou parcourez
   - Jusqu'à 10 fichiers maximum
   - Vérifiez les noms de fichiers
3. **Ajoutez un commentaire** (optionnel)
4. **Vérifiez votre soumission** avant validation
5. **Cliquez "Envoyer"** pour finaliser

#### Après Soumission
- **Confirmation** : Message de succès affiché
- **Email de confirmation** : Reçu automatiquement
- **Statut** : "Soumis" visible dans le devoir
- **Modification** : Possible si autorisée par le professeur

## Devoirs de Programmation

### Interface de Programmation
- **Éditeur de code intégré** : Monaco Editor professionnel
- **Coloration syntaxique** : Support multi-langages
- **Auto-complétion** : Suggestions automatiques
- **Numérotation des lignes** : Navigation facilitée
- **Détection d'erreurs** : Erreurs de syntaxe signalées

### Langages Supportés

#### Python (3.8+)
```python
# Exemple de structure
def main():
    # Lecture des entrées
    a = int(input())
    b = int(input())
    
    # Traitement
    result = a + b
    
    # Affichage du résultat
    print(result)

if __name__ == "__main__":
    main()
```

#### Java (OpenJDK 11)
```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        // Lecture des entrées
        int a = scanner.nextInt();
        int b = scanner.nextInt();
        
        // Traitement et affichage
        System.out.println(a + b);
        
        scanner.close();
    }
}
```

#### C++ (GCC 9.4)
```cpp
#include <iostream>
using namespace std;

int main() {
    // Lecture des entrées
    int a, b;
    cin >> a >> b;
    
    // Traitement et affichage
    cout << a + b << endl;
    
    return 0;
}
```

#### C (GCC 9.4)
```c
#include <stdio.h>

int main() {
    // Lecture des entrées
    int a, b;
    scanf("%d %d", &a, &b);
    
    // Traitement et affichage
    printf("%d\n", a + b);
    
    return 0;
}
```

#### JavaScript (Node.js 14)
```javascript
const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (input) => {
    // Traitement de l'entrée
    const numbers = input.split(' ').map(Number);
    const result = numbers[0] + numbers[1];
    
    // Affichage du résultat
    console.log(result);
    
    rl.close();
});
```

### Développement et Test

#### Écriture du Code
1. **Sélectionnez le langage** approprié
2. **Écrivez votre code** dans l'éditeur
3. **Respectez les conventions** :
   - Indentation correcte
   - Noms de variables explicites
   - Commentaires si nécessaire
4. **Gérez les entrées/sorties** selon le format demandé

#### Test en Temps Réel
1. **Bouton "Exécuter"** : Test immédiat
2. **Saisissez les entrées** de test
3. **Vérifiez la sortie** produite
4. **Corrigez les erreurs** si nécessaire
5. **Testez plusieurs cas** avant soumission

#### Tests Automatiques
- **Tests visibles** : Vous voyez les entrées/sorties
- **Tests cachés** : Évaluation finale par le professeur
- **Résultats en temps réel** : Score partiel affiché
- **Feedback détaillé** : Messages d'erreur explicites

### Soumission du Code
1. **Testez votre code** complètement
2. **Vérifiez tous les cas** de test visibles
3. **Cliquez "Soumettre"** quand satisfait
4. **Confirmation** : Code envoyé pour évaluation
5. **Résultats** : Score et feedback disponibles

### Limites et Contraintes
- **Temps d'exécution** : 10 secondes maximum
- **Mémoire** : Limite selon le langage
- **Taille du code** : Raisonnable (pas de limite stricte)
- **Bibliothèques** : Seules les bibliothèques standard

## Consultation des Notes

### Accéder aux Notes
1. **Depuis le tableau de bord** : Section "Notes"
2. **Depuis un cours** : Onglet "Mes Notes"
3. **Depuis un devoir** : Note individuelle

### Informations Disponibles
- **Note obtenue** : Sur la note maximale
- **Moyenne de la classe** : Comparaison
- **Rang** : Position dans la classe (si activé)
- **Commentaires** : Feedback du professeur
- **Date de correction** : Quand la note a été attribuée

### Historique des Notes
- **Toutes les évaluations** : Chronologique
- **Par cours** : Notes d'un cours spécifique
- **Statistiques personnelles** : Évolution des performances
- **Export** : Téléchargement en PDF

### Contestation de Note
Si vous n'êtes pas d'accord avec une note :
1. **Relisez les critères** d'évaluation
2. **Contactez le professeur** directement
3. **Demandez des explications** détaillées
4. **Procédure formelle** si nécessaire (via administration)

## Communication

### Annonces des Professeurs
- **Notifications automatiques** : Email et dans l'application
- **Priorités** : Normale, Importante, Urgente
- **Historique** : Toutes les annonces archivées
- **Réponses** : Possibilité de poser des questions

### Messages Directs
- **Contacter un professeur** : Via l'interface du cours
- **Réponses rapides** : Notifications en temps réel
- **Historique** : Conversation sauvegardée
- **Pièces jointes** : Envoi de fichiers possible

### Forum de Discussion
- **Questions publiques** : Visibles par tous les étudiants
- **Réponses partagées** : Bénéficient à tous
- **Modération** : Contrôlée par le professeur
- **Recherche** : Trouvez des réponses existantes

## Profil et Paramètres

### Informations Personnelles
- **Nom et prénom** : Non modifiables
- **Email** : Adresse institutionnelle
- **Photo de profil** : Optionnelle, formats JPG/PNG
- **Numéro de téléphone** : Pour urgences
- **Adresse** : Informations de contact

### Préférences
- **Notifications email** : Activées/désactivées
- **Langue** : Français par défaut
- **Fuseau horaire** : Ajustement automatique
- **Thème** : Clair ou sombre (si disponible)

### Sécurité
- **Changement de mot de passe** : Régulièrement recommandé
- **Historique de connexion** : Dernières connexions
- **Sessions actives** : Appareils connectés
- **Déconnexion** : Fermeture sécurisée

## Conseils et Bonnes Pratiques

### Gestion du Temps
- **Consultez régulièrement** le tableau de bord
- **Notez les échéances** importantes
- **Commencez tôt** les devoirs
- **Planifiez votre travail** selon les priorités

### Qualité du Travail
- **Lisez attentivement** les consignes
- **Respectez les formats** demandés
- **Vérifiez votre travail** avant soumission
- **Demandez de l'aide** si nécessaire

### Programmation
- **Testez votre code** avec plusieurs cas
- **Commentez** les parties complexes
- **Respectez les bonnes pratiques** de codage
- **Gérez les cas d'erreur** possibles

### Communication
- **Soyez respectueux** dans vos messages
- **Posez des questions précises** et claires
- **Participez** aux discussions de cours
- **Répondez rapidement** aux demandes des professeurs

### Sécurité
- **Ne partagez jamais** vos identifiants
- **Déconnectez-vous** des ordinateurs publics
- **Utilisez un mot de passe fort** et unique
- **Signalez** tout problème de sécurité

## Résolution de Problèmes

### Problèmes de Connexion
- **Vérifiez vos identifiants** : Email et mot de passe corrects
- **Réinitialisez le mot de passe** si oublié
- **Vérifiez la connexion internet** : Stable et rapide
- **Contactez l'administration** : Si problème persistant

### Problèmes de Soumission
- **Vérifiez la taille** des fichiers (50 MB max)
- **Formats acceptés** : Selon les consignes
- **Connexion stable** : Évitez les interruptions
- **Sauvegardez localement** : Avant soumission

### Problèmes de Code
- **Erreurs de syntaxe** : Vérifiez la coloration
- **Erreurs d'exécution** : Testez avec des cas simples
- **Timeout** : Optimisez votre algorithme
- **Mauvaise sortie** : Vérifiez le format exact

### Support Technique
- **Documentation** : Guides détaillés disponibles
- **Email support** : students@ulc-icam.edu.km
- **Heures d'ouverture** : Lundi-Vendredi 8h-17h
- **Urgences** : Procédure spéciale pour les échéances

## Ressources Utiles

### Aide à la Programmation
- **Tutoriels en ligne** : Liens fournis par les professeurs
- **Documentation officielle** : Pour chaque langage
- **Exemples de code** : Dans les devoirs
- **Forums d'aide** : Stack Overflow, etc.

### Outils Recommandés
- **Éditeurs locaux** : VS Code, PyCharm, etc.
- **Gestionnaires de version** : Git pour vos projets
- **Outils de test** : Pour valider votre code
- **Calculatrices** : Pour les cours de mathématiques

---

**Support Étudiants** : students@ulc-icam.edu.km  
**Documentation mise à jour** : Décembre 2024