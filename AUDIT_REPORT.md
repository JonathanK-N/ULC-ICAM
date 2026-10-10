# Audit initial confirmé

## Environnement
GitHub `JonathanK-N/ULC-ICAM`, branche principale `develop`. Railway : projet `9f836aa4-d149-49b1-a116-ed43192cbd87`, environnement `production`, service ULC-ICAM. Volume `/app/data`, Redis et domaines `ulc-cognito-web.com` et `cognitoweb.up.railway.app` confirmés via connecteur. Aucun changement de configuration effectué, aucune valeur de secret lue.

## Corrigé dans cette branche
- P0 : `code_execution.py` exécutait du code non fiable via subprocess quand la clé Judge0 était absente. Les méthodes locales sont supprimées.
- P0 : `/test_submit` exécutait du code sans vérifier un utilisateur. Vérification du compte connecté ajoutée.
- P0 : `_DEFAULT_ADMIN_PASSWORD` était fixe et journalisé. Bootstrap uniquement par variable, sans journaliser le secret.
- P1 : création et import des utilisateurs persistaient `temp_password`. Suppression du champ et remise unique des identifiants sans flash contenant le secret.
- P1 : publication globale des soumissions ne vérifiait pas le propriétaire du devoir ; actions GET modifiantes. POST, contrôle de propriété et sauvegarde ajoutés.
- P1 : syllabus et documents de chapitre téléchargeables par tout utilisateur connecté. Contrôle du cours et de l'association du fichier ajouté.
- P1 : rate limiting en mémoire malgré Redis disponible. Redis utilisé lorsqu'il est configuré ; limites spécifiques de connexion ajoutées.

## Restant / risques confirmés
- PWA : le service worker met en cache dashboard et notes ; fuite possible sur terminal partagé. À corriger immédiatement.
- Le fichier JSON reste une source en mémoire : verrou limité à un processus ; un worker Celery écrivant le même JSON peut perdre des mises à jour. Ne pas augmenter le nombre de processus écrivains avant migration.
- `models.py` contient une migration partielle utilisateurs/cours, sans préserver tous les identifiants et relations : ne pas l'utiliser pour la production.
- `seed_data.py`, `reset_system.py`, `populate_data.py` contiennent des comptes de démonstration connus. Route de seed interdite en production ; scripts à sécuriser avant utilisation.
- Export complet admin inclut encore les hashes ; à assainir.
- Permissions sur les autres routes, uploads, correction IA, notes et export : audit exhaustif restant.
- Pas de test réel contre Judge0, Redis ou les comptes de production. Judge0 auto-hébergé HTTP serait volontairement refusé ; config HTTPS à vérifier avant déploiement sans exposer la clé.
- Une installation vide requiert BOOTSTRAP_ADMIN_PASSWORD ; comptes existants préservés. Aucun changement de secret production demandé ou effectué.

## Compléments de l’audit
- Confirmé et corrigé : fallback IA aléatoire (60–90 %), notation par sentiment, note par défaut 75 % quand réponse IA invalide. Les nouvelles évaluations indisponibles n’ont aucune note et restent en attente de validation.
- Confirmé et corrigé : inscriptions/plagiat déclenchés par GET, relance plagiat inter-professeur, analyse de devoir sans inscription, correction manuelle non sauvegardée et repli silencieux vers données vides après erreur JSON.
- Export complet assaini et cache PWA privé corrigé dans le cycle 3.
- Scripts de démonstration : admin initial fourni par environnement et opérations refusées en mode production ; leurs autres comptes de test restent réservés aux démonstrations isolées.
- Voir ROUTE_INVENTORY.md pour l’inventaire statique complet ; cet inventaire n’est pas une preuve de couverture dynamique complète.
- Celery actuel : tâches décorées sur une instance provisoire, fichiers JSON réécrits sans coordination inter-processus. Activation en production bloquée jusqu’à refonte du stockage et tests worker.
- `DATA_FILE` n’apparaît pas dans les noms de variables Railway lus ; le chemin réellement persistant du JSON doit être vérifié avant bascule. Le volume seul ne démontre pas que le JSON se trouve dedans.
- Groupes et certaines configurations restent réinitialisés en mémoire au démarrage ; corrections de persistance et tests de groupes encore nécessaires.
- PostgreSQL, notifications/audit entièrement normalisés, Web Push, UX et architecture complète : non terminés. Aucune déclaration de modernisation complète.

Cycle groupes : persistance/restauration et contrôle des membres corrigés ; création de devoir réservée au cours assigné ; rôle session vérifié sur le compte existant. PostgreSQL staging validé par CI réelle sur données synthétiques. Les autres formats/configurations non persistés et la couche stockage complète restent à auditer.

Cycle stockage des soumissions : code sauvegardé dans UPLOAD_FOLDER configuré avec noms sûrs et uniques ; pièces de devoir/corrections téléchargées en pièce jointe. Dernière vérification locale : 96 tests réussis, 1 PostgreSQL ignoré ; test de stockage sur répertoire temporaire ajouté.


## Protection des tâches de fond
Le worker est maintenant refusé avant import de Flask, et les helpers ne réécrivent plus le JSON. Le nettoyage aveugle des uploads de plus de 30 jours est désactivé et retiré du planning. La couche transactionnelle des résultats existe en isolation ; elle ne remplace pas encore les globals Flask. Ne pas activer les workers avant cette intégration. La première migration Alembic embarque désormais son propre schéma figé.

Soumission classique IA : publication automatique du devoir supprimée, validation professeur conservée. Dates de session invalides ou futures : session invalidée au lieu d’une erreur serveur.
