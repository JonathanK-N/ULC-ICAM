# Changements

## Branche de modernisation — 9 octobre 2026
- Exécution distante seule pour le code étudiant, panne sans note ni soumission artificielle.
- Contrôle du compte, CSRF et limites pour les essais de code.
- Bootstrap admin sans mot de passe connu ; suppression des mots de passe temporaires persistés et des secrets dans les flashes.
- POST, droits de propriété et persistance pour publication/masquage des notes ; suppression utilisateur POST.
- Contrôles d'accès aux syllabus et documents de chapitre.
- Redis pour rate limiting lorsqu'il est configuré, limites de connexion et renouvellement des sessions.
- Réponses privées non mises en cache, seed interdit en production et exigences de clé session/CSRF au démarrage production.
- Tests isolés et documents de suivi.

Cycle 3 : cache PWA limité aux ressources publiques, anciens caches privés purgés, export admin sans hashes, téléchargement des pièces de devoir contrôlé. Vérifications : 65 tests réussis (16.65s), test Node du service worker : 7 assertions réussies.

- Fondation SQLAlchemy/Alembic et import isolé transactionnel, idempotent et contrôlé.
- Premier Blueprint pour l’exécution ; autres actions modifiantes POST ; vérifications complémentaires des inscrits et des corrections.
- JSON illisible : arrêt du démarrage pour prévenir un écrasement ; aucune réécriture de mots de passe au chargement.
- Évaluations IA non disponibles sans score inventé ; nouvelles propositions publiables après validation manuelle uniquement.
- Scripts de démonstration sans mot de passe admin connu ; image Web et logs simplifiés ; CI isolée PostgreSQL proposée.

- Groupes persistés/restaurés ; validation des inscrits, doublons, taille et appartenance unique. Rôle de session relu depuis le compte et contrôle du cours lors de création de devoir.
- Migration de staging vérifiée sur PostgreSQL 16 en CI synthétique isolée.

Cycle stockage des soumissions : code sauvegardé dans UPLOAD_FOLDER configuré avec noms sûrs et uniques ; pièces de devoir/corrections téléchargées en pièce jointe. Dernière vérification locale : 96 tests réussis, 1 PostgreSQL ignoré ; test de stockage sur répertoire temporaire ajouté.

Cycle parcours utilisateurs : connexions réelles et rendu des pages essentielles des trois rôles validés avec données synthétiques (dashboard, utilisateurs/cours/devoirs admin, cours/résultats professeur, cours/notes/soumission étudiant). Dernière suite locale : **99 passed, 1 skipped in 25.47s** ; navigateur/mobile réel restant à vérifier. CI sur 6a86d53 réussie : run 38017352179.


- Révision Alembic initiale figée ; repository transactionnel des résultats préparé en isolation, protection des corrections approuvées.
- Worker JSON bloqué ; réécritures concurrentes retirées ; nettoyage destructif des uploads anciens désactivé.

- Reconnexion sur date de session invalide ou future ; publication automatique des devoirs lors des uploads IA supprimée.
