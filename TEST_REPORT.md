# Tests exécutés

9 octobre 2026, Windows, Python 3.12 du runtime local, environnement `.venv`.

- `python -m py_compile app.py code_execution.py` : réussi.
- `.venv/Scripts/python.exe -m pytest -q` : **65 passed in 20.73s** après correctifs sécurité et délivrance unique des mots de passe.
- Suite exécutée avec DATA_FILE et UPLOAD_FOLDER temporaires ; aucune donnée production.
- Nouveaux tests : absence d'exécution locale, endpoints Judge0 dangereux refusés, panne réseau assainie, limites HTTP, résultats null normalisés, tests étudiants en erreur non acceptés, authentification/CSRF, propriété des publications, GET refusé, autorisations syllabus, mot de passe temporaire exclu du fichier JSON.
- Tests d'exécution locale historiques retirés car ils imposaient le comportement vulnérable ; résultats distants testés avec doubles HTTP.

Non exécuté : tests navigateur/mobile, sandbox Judge0 réelle, Redis réel, PostgreSQL réel, déploiement Railway et parcours complets IA/email/PWA. Les tests existants ne couvrent pas toutes les fonctionnalités.
