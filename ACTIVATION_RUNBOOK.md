# Activation Cognito Web

La branche prépare une activation ; elle ne migre et ne déploie rien en production automatiquement.

## État vérifié

La CI du commit b6dc6e8 (run 38056481365) a réussi : 139 tests Python avec PostgreSQL 16 et Redis 7 réels, puis 10 assertions du service worker, construction Docker, smoke test et audit complet des dépendances sans vulnérabilité connue. Le parcours couvre dépôt étudiant, worker, relecture professeur et publication. Les appels IA, SMTP et Web Push sont simulés. Le navigateur CUA a dépassé ses délais : la validation visuelle mobile reste à réaliser.

## Environnement de validation

1. Créer, après autorisation si nécessaire, un environnement indépendant avec PostgreSQL, Redis et stockage de fichiers. Ne jamais utiliser les identifiants ou volumes de production pour les tests.
2. Importer uniquement un snapshot synthétique avec `migrate_isolated.py --confirm-isolated`. Les outils actuels refusent les bases distantes de production.
3. Configurer `COGNITO_STORAGE=relational`, `DATABASE_URL`, `FLASK_SECRET_KEY`, `UPLOAD_FOLDER`, `CELERY_BROKER_URL` et `CELERY_RESULT_BACKEND`. Utiliser la même base et le même espace de fichiers pour le web et le worker.
4. Démarrer le web, `celery -A celery_worker.celery worker`, puis une seule instance `celery -A celery_worker.celery beat`. Les profils Compose `relational-worker` et `worker-monitoring` sont explicites ; ils ne démarrent pas par défaut.
5. Pour les propositions IA, définir explicitement `OPENAI_MODEL` et `OPENAI_API_KEY`. Sans configuration, la correction reste manuelle. Les propositions doivent être approuvées par le professeur avant publication.
6. Pour les notifications, configurer les variables `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT`, puis faire souscrire chaque utilisateur depuis ses préférences. Pour SMTP, configurer les variables MAIL et activer `NOTIFICATIONS_ENABLED` volontairement. Tester avec destinataires de validation autorisés.
7. Vérifier les trois rôles, propriétaires des téléchargements, soumission répétée, panne Redis, correction simultanée, export et restauration. Vérifier visuellement téléphone, clavier et accessibilité.

## Bascule réelle : approbation obligatoire

Avant toute migration, identifier le chemin réellement utilisé par `DATA_FILE` et les fichiers sur Railway. La présence du volume `/app/data` ne prouve pas que le JSON y est enregistré. Sauvegarder les données et fichiers de manière cohérente, avec manifeste SHA-256, et démontrer une restauration isolée. Les scripts isolés doivent être adaptés et revus pour une opération réelle approuvée ; ne pas contourner leur protection d'hôte.

Geler les écritures, arrêter les traitements, importer la copie finale, comparer comptes, IDs, relations, notes et fichiers, puis seulement activer le mode relationnel et les services approuvés. Ne pas fusionner ou déployer sans accord explicite. Ne pas créer de ressources facturées ni modifier les secrets sans cet accord.

Le montage Compose actuel du JSON comme fichier individuel n'est pas compatible avec un remplacement atomique sur tous les systèmes. Avant une activation JSON sous Docker, préparer un montage de répertoire et copier le fichier existant après vérification ; ne pas déplacer les données automatiquement.

## Retour arrière et limites

Après de nouvelles écritures relationnelles, un ancien JSON est périmé. Arrêter web et workers, exporter un snapshot frais et vérifier son intégrité avant une reprise approuvée. `export_isolated.py` prépare cette répétition uniquement sur base locale et refuse l'écrasement d'un fichier existant.

Le repository de transition conserve les formats historiques et verrouille une transaction commune ; il reconstruit et remplace le snapshot relationnel. Il protège la cohérence mais sérialise les requêtes et ne constitue pas encore une architecture à grande échelle. Le mode JSON reste limité à un processus web. Redis accélère les résumés par compte avec une durée de 60 secondes et un repli sans cache.

Les traitements et notifications sont livrés au moins une fois. Les soumissions utilisent des identifiants et des baux pour éviter une correction doublonnée ; un envoi SMTP interrompu après livraison peut être répété. Aucun dépôt hors connexion n'est rejoué automatiquement. Les pages et notes privées ne sont pas mises en cache par le service worker.
