# Politique de sécurité — Cognito Web

Projet maintenu par Cognito Inc. Les résultats vérifiables et les limites de l'audit figurent dans AUDIT_REPORT.md et TEST_REPORT.md. Ce dépôt ne fournit pas de preuve de certification ISO 27001, SOC 2 ou de conformité réglementaire complète.

## Contrôles implémentés

- Authentification, mots de passe hachés, sessions liées au rôle courant et refus des comptes désactivés. Aucun mot de passe administrateur par défaut ; bootstrap explicite pour une installation vide.
- CSRF sur les mutations, limites de connexion et autorisations par rôle et propriétaire pour cours, publications, rapports et téléchargements.
- Exécution de code étudiant uniquement via une sandbox distante configurée ; aucun compilateur ou sous-processus local ne lance le code étudiant.
- Fichiers enregistrés sous noms uniques, limites de taille et téléchargement en pièce jointe. Le traitement automatique des documents possède des limites et peut demander une relecture manuelle.
- Correction IA structurée et contrôlée localement. Le texte étudiant est une entrée non fiable. Une proposition ne publie pas de note : approbation du professeur obligatoire.
- Pages et résultats privés exclus du cache PWA. Messages Web Push génériques et abonnements limités au compte propriétaire, avec consentement explicite depuis les préférences.
- Transactions communes web/worker en mode relationnel, baux de traitement et protection des corrections approuvées. Les sauvegardes et exports ne doivent pas être accessibles publiquement.

## Dépendances et validation

La CI exécute les tests avec PostgreSQL et Redis isolés, construit l'image et contrôle ses dépendances Python avec pip-audit. Un résultat sans vulnérabilité connue dépend des avis disponibles à la date d'exécution ; il ne constitue pas une garantie générale de sécurité. Les intégrations payantes et les envois externes sont simulés dans les tests.

Le repository de transition sérialise les transactions et remplace un snapshot ; le mode JSON utilise un processus web. Ces limites et le contrôle des volumes doivent être traités avant une activation à grande échelle. La configuration effective de production doit être examinée indépendamment des fichiers d'exemple.

## Signalement

Contacter les mainteneurs par le canal privé de sécurité du dépôt lorsqu'il est disponible. Ne pas publier de secrets, mots de passe, travaux étudiants ou exploit permettant l'accès aux données dans une issue publique. Fournir une reproduction synthétique, les versions affectées et les conséquences observées.

## Opérations de production

Ne jamais fusionner vers ui, déployer, migrer les données réelles, modifier les secrets, réinitialiser un volume ou créer une ressource payante sans l'approbation explicite du propriétaire. Préparer une sauvegarde cohérente et une restauration vérifiée. Voir ACTIVATION_RUNBOOK.md et MIGRATION_PLAN.md pour les conditions de bascule et de retour arrière.
