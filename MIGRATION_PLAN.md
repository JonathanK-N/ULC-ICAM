# Migration PostgreSQL — préparation

Statut : plan initial, aucune migration de production autorisée ou réalisée.

1. Après approbation seulement : sauvegarde cohérente du JSON et des fichiers du volume, manifeste SHA-256, restauration vérifiée sur stockage isolé.
2. Préparer SQLAlchemy et Alembic dans une base isolée. Préserver les identifiants métiers, références, champs additionnels, documents, corrections, groupes et notifications ; aucune perte de champs silencieuse.
3. Import transactionnel idempotent avec clé de source et empreinte. Vérifier doublons, orphelins, cours/enseignants/inscriptions/devoirs/soumissions, compteurs et dates ; échouer sur incohérence.
4. Comparer comptes, relations, hashes des fichiers et résultats avant/après ; relancer l'import et vérifier l'absence de doublons.
5. Introduire une couche stockage et basculer les services progressivement. Tester les trois rôles et les parcours de soumission/correction/export.
6. Soumettre rapport et procédure de bascule à approbation. Définir fenêtre de gel des écritures et sauvegarde finale ; aucune double écriture improvisée.
7. Rollback : remettre la version et la sauvegarde vérifiées avant reprise des écritures. Après nouvelles écritures PostgreSQL, prévoir export différentiel validé ; ne pas restaurer aveuglément un ancien JSON.

Le script `models.migrate_from_json()` actuel est incomplet et ne répond pas à ces critères. Ne pas l'exécuter sur les données réelles.

## Fondation livrée dans cette branche

`migration_schema.py` définit les tables relationnelles de staging et les contraintes. `migrate_isolated.py` valide les références, préserve les IDs et champs supplémentaires en JSON, hash les anciens mots de passe, rejette un snapshot différent sur une base remplie et garde l’empreinte SHA-256 du fichier source. Aucun import automatique depuis Flask.

Tests isolés SQLite : import répété sans doublons, champs préservés, orphelins refusés, source inchangée et upgrade/downgrade Alembic. Un test PostgreSQL dédié est fourni et une CI avec PostgreSQL 16 est préparée. La réussite locale SQLite ne prouve pas la réussite PostgreSQL.

Commande d’essai exclusivement sur une COPIE SYNTHÉTIQUE :
`python migrate_isolated.py tmp/synthetic.json --database-url sqlite:///tmp/migration.sqlite --confirm-isolated`

Alembic exige `ISOLATED_DATABASE_URL`. Le schéma reste une fondation : groupes normalisés ; notifications et audit ont leurs tables mais les formats existants non mappés restent archivés dans application_state. Couche de stockage métier et bascule de Flask non réalisées.

Validation PostgreSQL de la fondation : CI 38017055612 réussie avec PostgreSQL 16, import/relecture/second import d’un snapshot synthétique dans un schéma temporaire puis suppression du seul schéma de test. Aucune copie des données réelles, aucun accès à la base production. Les modèles métier complets et la bascule restent à réaliser.


## Repository des résultats
SubmissionRepository utilise les tables existantes, sans nouvelle migration : résultats séparés des soumissions, transaction et verrou de la soumission en PostgreSQL. Les propositions portent review_status=pending et ne remplacent jamais un enregistrement approved. SQLite valide la logique séquentielle ; il ne valide pas le verrou PostgreSQL. Flask utilise toujours le JSON. Avant activation, intégrer les lectures et toutes les écritures des routes dans une unité transactionnelle, assurer la concurrence avec la validation professeur, extraire le calcul IA des globals et tester le worker avec Redis isolé. Le worker actuel refuse de démarrer durant cette transition.

## Mode de transition préparé
`COGNITO_STORAGE=relational` et `DATABASE_URL` sélectionnent explicitement une base préalablement importée et vérifiée. Aucune création, migration ni bascule automatique au démarrage. JSON reste le défaut. Le worker impose PostgreSQL et utilise le même verrou de transaction que les routes.

Le rollback doit préserver les nouvelles écritures : ne pas remettre simplement l’ancien JSON après utilisation de PostgreSQL. Arrêter les écritures et workers, exporter un snapshot frais, vérifier les comptes, IDs, notes, groupes et empreintes, puis changer le mode selon une procédure approuvée. `export_isolated.py` prépare ce test sur base locale uniquement, avec sortie créée exclusivement et sans écrasement. Les outils de migration et d’export refusent encore les hôtes de production : leur usage réel demande l’approbation et un cycle dédié.

## Mise à jour de la transition
Flask utilise maintenant SnapshotRepository sur sélection explicite relationnelle. Les notifications et événements audit sont normalisés ; les champs historiques supplémentaires restent conservés. Les transactions PostgreSQL concurrentes et le worker Redis réel ont passé la CI 38054836998. Le remplacement du snapshot sous verrou garantit la cohérence mais limite le débit. Les anciennes sections décrivent les étapes historiques. Activation et retour arrière : ACTIVATION_RUNBOOK.md.
