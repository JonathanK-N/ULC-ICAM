# Tests exécutés

## Dernière validation complète

Code b6dc6e84f1bb6fac21f41ab2abbbb31a045a693d : [CI 38056481365](https://github.com/JonathanK-N/ULC-ICAM/actions/runs/38056481365), logs vérifiés des jobs 114225940841 et 114225940757 : **139 passed in 8.53s**, **10 assertions service worker**, construction Docker, smoke test et **aucune vulnérabilité connue dans l'audit des dépendances complètes de l'image**. PostgreSQL 16 et Redis 7 réels, données synthétiques isolées. Les nouvelles vérifications PDF couvrent extraction et limites.

Dernière suite locale complète avant migration du lecteur PDF : **135 passed, 2 skipped in 422.33s** ; PostgreSQL/Redis couverts en CI. Les appels IA, SMTP et Web Push sont simulés. Aucun test ni écriture sur données réelles. Le navigateur CUA n'a pas fourni de capture après ses dépassements de délai : contrôle visuel mobile restant. Les résultats suivants sont historiques.

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

Cycle parcours utilisateurs : connexions réelles et rendu des pages essentielles des trois rôles validés avec données synthétiques (dashboard, utilisateurs/cours/devoirs admin, cours/résultats professeur, cours/notes/soumission étudiant). Dernière suite locale : **99 passed, 1 skipped in 25.47s** ; navigateur/mobile réel restant à vérifier. CI sur 6a86d53 réussie : run 38017352179.

Validation finale du code cd5df9e : CI GitHub Actions 38017470818, Linux/Python 3.11/PostgreSQL 16 : **100 passed in 4.19s**, puis **7 assertions PWA réussies**. Logs du job 114110851944 vérifiés. Branche ui contrôlée à nouveau : toujours 7699c614f0c9cdeadf407c232145844ff3b5b33c. Aucun déploiement.


## Cycle repository / worker
Local : 105 tests réussis, 1 PostgreSQL ignoré (36.70s) ; 7 assertions service worker. Vérifications ajoutées : conservation des fichiers anciens, worker refusé, absence d’écriture JSON, migration indépendante des futurs modèles, proposition pending, protection d’une correction approuvée, soumission inconnue refusée. Le test PostgreSQL CI inclut maintenant les mises à jour du repository ; résultat du nouveau commit à vérifier. Aucun Redis réel ni calcul IA testé dans ce cycle.

CI b9bd569 : 106 passed in 5.51s, 7 assertions PWA, PostgreSQL réel ; run 38018904260, logs du job 114115307716 vérifiés. Nouveau cycle : tests de sessions invalides et soumission IA sans publication.

Dernière suite locale sessions/publication : 110 passed, 1 skipped in 32.27s (PostgreSQL réservé à la CI).

Validation CI e3e58b7 : run 38019074383, job 114115813826 réussi (PostgreSQL réel, tests Python et PWA). Railway consulté en lecture : services ULC-ICAM et Redis en ligne ; déploiement ULC-ICAM toujours 92255766-777e-4e33-a61c-c9f23b516a70 ; aucune opération en attente. Prochaine action : intégrer le stockage relationnel aux routes Flask et extraire le calcul IA avant toute activation Celery.

## Lot services et transition
128 tests réussis et 2 ignorés localement avant les derniers ajouts ; 9 tests grille et échéances réussis ensuite. Nouvelle couverture préparée : concurrence PostgreSQL, Flask relationnel sans écriture JSON, worker réel Redis/PostgreSQL jusqu’à validation professeur, idempotence, export de rollback, notifications et emails simulés. Pas d’appel IA payant, pas d’email ni push réel. CUA a dépassé ses délais à deux reprises ; seul le serveur local et ses réponses HTTP ont pu être vérifiés, pas le rendu visuel.

Suite locale intermédiaire : 133 passed, 2 skipped in 469.77s. Cette machine a émis des exceptions Windows de manque de ressources pendant certains imports, mais cette suite a terminé avec succès. Les derniers ajustements et PostgreSQL/Redis restent à confirmer en CI.

## Intégration validée en CI
Commit 14330c9dc1a27a808fc040ff961656af39d5ef5b : run 38054836998, job 114221049787, **135 passed in 11.66s**, puis **10 assertions service worker réussies**. PostgreSQL 16 et Redis 7 réels, worker Celery et parcours étudiant/professeur inclus. Derniers tests ciblés cache/similarité : 2 réussis. Les versions corrigées des dépendances et la construction Docker sont vérifiées dans le prochain run. Appels IA, SMTP et push simulés ; aucun destinataire réel. Validation visuelle navigateur/mobile indisponible après dépassements de délai CUA.

CI feea0b0 : run 38056091227, job 114224818000 : **137 passed in 7.64s**, **10 assertions PWA**. Job image-build 114224817932 : construction des dépendances complètes et smoke test `/health` / `/offline.html` réussis. Audit local après mise à jour : aucune vulnérabilité connue parmi les dépendances installées ; contrôle complet de l'image ajouté dans le prochain run.
