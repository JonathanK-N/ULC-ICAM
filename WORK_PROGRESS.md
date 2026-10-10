# Cognito Web — progression

## État actuel — prêt pour examen de la PR

Travaux livrés : correctifs de sécurité, Blueprints, migration isolée PostgreSQL, liaison transactionnelle Flask/worker, Celery/Redis, propositions IA avec approbation professeur, rapports, Web Push volontaire, PWA privée et tableaux de bord. PR 28 sur codex/cognito-modernisation, sans fusion.

Validation du code b6dc6e8 : CI 38056481365, **139 tests Python réussis**, **10 assertions PWA**, image Docker construite, smoke test réussi et audit complet des dépendances de l'image sans vulnérabilité connue. Tests PostgreSQL et Redis réels ; IA, SMTP et push simulés. La suite locale précédente : 135 réussis, 2 intégrations réservées à la CI ignorées, en 422.33s.

Partiellement terminé : architecture relationnelle encore fondée sur un snapshot avec verrou commun, navigation mobile modifiée mais rendu visuel non validé après délais CUA. Non réalisé : migration réelle, configuration des secrets, intégrations payantes/envois réels, fusion et déploiement. Prochaine étape : revue de la PR et validation visuelle ; activation seulement après accord explicite et vérification du chemin réel des données Railway. Procédure : ACTIVATION_RUNBOOK.md.

Railway relu le 10 octobre : services web et Redis en ligne, déploiement web toujours 92255766-777e-4e33-a61c-c9f23b516a70, aucune opération en attente. Les sections suivantes sont l'historique des cycles, pas une liste des tâches actuelles.

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

Cycle parcours utilisateurs : connexions réelles et rendu des pages essentielles des trois rôles validés avec données synthétiques (dashboard, utilisateurs/cours/devoirs admin, cours/résultats professeur, cours/notes/soumission étudiant). Dernière suite locale : **99 passed, 1 skipped in 25.47s** ; navigateur/mobile réel restant à vérifier. CI sur 6a86d53 réussie : run 38017352179.

Validation finale du code cd5df9e : CI GitHub Actions 38017470818, Linux/Python 3.11/PostgreSQL 16 : **100 passed in 4.19s**, puis **7 assertions PWA réussies**. Logs du job 114110851944 vérifiés. Branche ui contrôlée à nouveau : toujours 7699c614f0c9cdeadf407c232145844ff3b5b33c. Aucun déploiement.

Statut de livraison : lot de sécurité et fondation de migration livré en PR brouillon #28 ; mission globale partiellement réalisée. Prochaine priorité : couche repository PostgreSQL et worker sans écritures JSON concurrentes, puis Web Push et validation navigateur/mobile.


## Cycle repository et protection worker
- Dernière CI précédente : 38017580727 réussie sur 9fb264e.
- Première révision Alembic figée : indépendante des futurs modèles SQLAlchemy ; test de non-régression ajouté.
- SubmissionRepository : lecture des soumissions et mise à jour transactionnelle des propositions/similarités ; verrou de ligne PostgreSQL, correction approuvée protégée. Couche isolée, pas encore branchée dans Flask.
- Worker Celery bloqué explicitement avant import Flask tant que le stockage global reste JSON ; anciennes écritures directes retirées. Aucune activation en production.
- Nettoyage périodique supprimé : conserver les pièces pédagogiques, même anciennes, jusqu’à politique de rétention approuvée.
- Local : 105 passed, 1 skipped (PostgreSQL), 7 assertions PWA. Test PostgreSQL CI étendu au repository.
- Restent : repository Flask complet avec gestion de concurrence des routes, tâches IA sans imports des globals, notifications/audit, Web Push, UX et navigateur/mobile.

CI b9bd569 validée : run 38018904260, job 114115307716, 106 tests réussis en 5.51s et 7 assertions PWA. PostgreSQL réel inclut désormais le repository.

Cycle sessions/publication : dates invalides, incompatibles ou futures entraînent une reconnexion ; la soumission de fichier IA ne publie plus automatiquement le devoir. Tests de régression ajoutés.

Validation CI e3e58b7 : run 38019074383, job 114115813826 réussi (PostgreSQL réel, tests Python et PWA). Railway consulté en lecture : services ULC-ICAM et Redis en ligne ; déploiement ULC-ICAM toujours 92255766-777e-4e33-a61c-c9f23b516a70 ; aucune opération en attente. Prochaine action : intégrer le stockage relationnel aux routes Flask et extraire le calcul IA avant toute activation Celery.

## Reprise du 10 octobre — services et intégration
- Services purs préparés : correction avec grille contrôlée, extraction documentaire, similarité, emails, Web Push et rapports ; aucun import Flask dans le calcul des soumissions.
- Repository de transition : snapshot relationnel, transaction de requête et verrou commun PostgreSQL ; notifications et audit désormais normalisés. Export isolé de rollback sans écrasement.
- Contrôleurs déplacés en Blueprints, URL et endpoints historiques conservés via règles de construction compatibles.
- Intégration Flask et worker en cours de validation : JSON reste le mode par défaut, activation relationnelle explicite, worker PostgreSQL uniquement. Aucun changement Railway.
- Validation locale du découpage avant les derniers ajouts : 128 passed, 2 skipped. Les deux tests PostgreSQL/Redis réels attendent la nouvelle CI. Tests grille/dates : 9 passed.
- Navigateur : deux délais d’attente CUA ; serveur local et ressources HTTP répondent 200, mais aucune validation visuelle des trois rôles n’est revendiquée.

Cycle intégration : Flask peut fonctionner en mode relationnel explicite ; routes réparties en Blueprints avec alias historiques ; worker indépendant de Flask et PostgreSQL obligatoire ; file durable des soumissions, emails et notifications ; grille personnalisable et rapports CSV de fond. Local : 133 passed, 2 skipped (les services réels sont réservés à la CI), avant les derniers ajustements de rapports et UI. Rendu visuel toujours non validé à cause des délais CUA.

## État actuel — activation préparée
Routes extraites en Blueprints, stockage relationnel transactionnel branché, worker Celery indépendant, correction structurée avec validation professeur, rapports et notifications durables, Web Push volontaire, résumés par compte et cache Redis. CI 14330c9 : 135 tests réussis avec PostgreSQL/Redis réels et 10 assertions PWA. La transition conserve un verrou global et un remplacement du snapshot : optimisation relationnelle fine restant à planifier. Aucun déploiement ni migration réelle. Voir ACTIVATION_RUNBOOK.md.
