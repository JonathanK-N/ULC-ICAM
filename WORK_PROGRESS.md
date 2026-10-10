# Cognito Web — progression

Base vérifiée le 9 octobre 2026 : production Railway `92255766-777e-4e33-a61c-c9f23b516a70`, branche `ui`, commit `7699c614f0c9cdeadf407c232145844ff3b5b33c`. Branche de travail : `codex/cognito-modernisation`. Identité Git : Jonathan Kakesa <jkakesa9@gmail.com>.

## Cycle sécurité 1 et 2
- Terminé : suppression de tous les exécuteurs locaux ; Judge0 HTTPS, délais, absence de redirections, réseau étudiant désactivé, résultats normalisés et erreurs contrôlées.
- Terminé : `/test_submit` authentifié, protection CSRF conservée, limitation de débit ; panne de sandbox traitée avant toute notation ou écriture de soumission.
- Terminé : mot de passe admin de démarrage fourni uniquement par environnement ; mots de passe temporaires absents de la persistance et délivrés dans une réponse unique sans cookie de session.
- Terminé : publication des notes réservée au propriétaire du devoir, POST et sauvegarde ; suppression utilisateur POST ; formulaires adaptés.
- Terminé : autorisations syllabus et documents de chapitre ; sessions renouvelées à la connexion ; Redis utilisé pour les limites si configuré.
- Vérification : 65 tests réussis en stockage temporaire. Aucun test ni écriture sur les données de production.

## Suite
- Corriger le cache PWA de pages privées et auditer toutes les routes restantes (voir AUDIT_REPORT.md).
- Préparer une migration PostgreSQL isolée et idempotente, puis Blueprints, tâches Celery, validation professeur, notifications Web Push et UX.
- PostgreSQL en production, fusion vers `ui`, déploiement et ressources payantes restent soumis à approbation explicite.

La mission complète n'est pas terminée. Ne pas déployer ce lot sans revue des risques et tests des parcours réels.

Cycle 3 : cache PWA limité aux ressources publiques, anciens caches privés purgés, export admin sans hashes, téléchargement des pièces de devoir contrôlé. Vérifications : 65 tests réussis (16.65s), test Node du service worker : 7 assertions réussies.

## Cycles 4 à 6 — branche prête pour revue partielle
- PR brouillon : https://github.com/JonathanK-N/ULC-ICAM/pull/28 (base ui ; aucune fusion).
- Commit c362b62 : fondation relationnelle isolée, import idempotent et Alembic ; SQLite validé, PostgreSQL réel à valider par CI.
- Contrôles supplémentaires : actions d’inscription/plagiat POST, analyse réservée aux inscrits, corrections manuelles persistées, démarrage refusé sur JSON illisible, scripts admin sans mot de passe connu, premier Blueprint et validation des notes IA.
- Note aléatoire de secours et notation par sentiment retirées ; nouveaux brouillons IA en attente de validation professeur. Similarité présentée comme indice à examiner.
- Image Web débarrassée des compilateurs étudiants ; logs INFO et contexte Docker excluant données/secrets locaux. Build Docker restant à valider.
- Dernière validation locale : 92 tests réussis, 1 PostgreSQL ignoré ; service worker : 7 assertions.

## Prochaine reprise
1. Lire les derniers commits, ces rapports et la PR ; vérifier le résultat de CI PostgreSQL.
2. Achever l’audit des uploads/groupes, sessions/permissions et les tests navigateur des trois rôles.
3. Compléter les modèles et l’import notifications/audit, figer les révisions Alembic et introduire le repository PostgreSQL dans Flask avec tests de parité.
4. Corriger l’initialisation/enregistrement Celery et supprimer les écritures concurrentes directes JSON avant activation d’un worker. Ne pas lancer le worker actuel en production.
5. Compléter grille IA, persistance des propositions, gestion Web Push et UX/accessibilité.
6. Faire valider toute bascule, migration réelle et déploiement. Mission globale encore partiellement réalisée.

## Validation CI et cycle groupes
- CI Linux/Python 3.11/PostgreSQL 16 réussie sur 354a2f1 : 93 tests réussis en 3.80s et 7 assertions PWA (run 38017055612). La migration de staging a été validée sur PostgreSQL réel avec données synthétiques ; aucune migration production.
- Groupes : contrôle des inscrits, doublons, taille et appartenance unique, persistance JSON et restauration au chargement ; rôle de session relu depuis le compte. Création de devoir réservée aux cours assignés.
- Dernière suite locale : 95 tests réussis, 1 PostgreSQL ignoré (14.29s). Une nouvelle CI doit confirmer le dernier commit.

Cycle stockage des soumissions : code sauvegardé dans UPLOAD_FOLDER configuré avec noms sûrs et uniques ; pièces de devoir/corrections téléchargées en pièce jointe. Dernière vérification locale : 96 tests réussis, 1 PostgreSQL ignoré ; test de stockage sur répertoire temporaire ajouté.
