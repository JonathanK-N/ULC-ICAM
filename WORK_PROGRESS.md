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
