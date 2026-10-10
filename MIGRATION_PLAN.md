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
