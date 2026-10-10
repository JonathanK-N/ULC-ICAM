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
