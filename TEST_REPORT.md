# Tests exécutés

9 octobre 2026, Windows, Python 3.12 du runtime local, environnement `.venv`.

- `python -m py_compile app.py code_execution.py` : réussi.
- `.venv/Scripts/python.exe -m pytest -q` : **65 passed in 20.73s** après correctifs sécurité et délivrance unique des mots de passe.
- Suite exécutée avec DATA_FILE et UPLOAD_FOLDER temporaires ; aucune donnée production.
- Nouveaux tests : absence d'exécution locale, endpoints Judge0 dangereux refusés, panne réseau assainie, limites HTTP, résultats null normalisés, tests étudiants en erreur non acceptés, authentification/CSRF, propriété des publications, GET refusé, autorisations syllabus, mot de passe temporaire exclu du fichier JSON.
- Tests d'exécution locale historiques retirés car ils imposaient le comportement vulnérable ; résultats distants testés avec doubles HTTP.

Non exécuté : tests navigateur/mobile, sandbox Judge0 réelle, Redis réel, PostgreSQL réel, déploiement Railway et parcours complets IA/email/PWA. Les tests existants ne couvrent pas toutes les fonctionnalités.

Cycle 3 : cache PWA limité aux ressources publiques, anciens caches privés purgés, export admin sans hashes, téléchargement des pièces de devoir contrôlé. Vérifications : 65 tests réussis (16.65s), test Node du service worker : 7 assertions réussies.

## Validation du dernier lot
- `.venv/Scripts/python.exe -m pytest -q` : **92 passed, 1 skipped in 14.44s**. Test PostgreSQL réel explicitement ignoré faute de serveur local ; CI PostgreSQL ajoutée, résultat à suivre.
- Test Node du service worker : **7 assertions réussies**.
- `py_compile` : modules principaux, Blueprint, import relationnel et scripts de démonstration validés.
- Ajouts : aller-retour Alembic SQLite, refus des imports divergents et des orphelins, limites de connexion, stockage corrompu conservé avec démarrage refusé, panne sandbox HTTP 503, note IA invalide/panne sans score, publication des brouillons refusée et validation manuelle suivie de publication.
- Une première vérification Alembic en sous-processus a échoué avec une erreur native du runtime Windows ; le test via l’API Alembic a ensuite validé l’upgrade et le downgrade réels sur SQLite. Des erreurs de montage de tests ont été corrigées avant la dernière suite réussie.
- Image Docker non construite localement (Docker absent). Dépendances optionnelles IA/email/documents et serveur Redis réel non exercés par cette suite minimale.

## CI PostgreSQL réellement exécutée
GitHub Actions run 38017055612, commit 354a2f1 : **93 passed in 3.80s**, PostgreSQL 16 et Python 3.11, puis **7 assertions PWA réussies**. Source : https://github.com/JonathanK-N/ULC-ICAM/actions/runs/38017055612. Le résultat a été vérifié dans les logs du job 114109557356.

Après le cycle groupes et sessions : **95 passed, 1 skipped in 14.29s** localement. Le test PostgreSQL est exécuté par CI, pas localement.

Cycle stockage des soumissions : code sauvegardé dans UPLOAD_FOLDER configuré avec noms sûrs et uniques ; pièces de devoir/corrections téléchargées en pièce jointe. Dernière vérification locale : 96 tests réussis, 1 PostgreSQL ignoré ; test de stockage sur répertoire temporaire ajouté.
