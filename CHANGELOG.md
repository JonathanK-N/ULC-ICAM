# Changements

## Branche de modernisation — 9 octobre 2026
- Exécution distante seule pour le code étudiant, panne sans note ni soumission artificielle.
- Contrôle du compte, CSRF et limites pour les essais de code.
- Bootstrap admin sans mot de passe connu ; suppression des mots de passe temporaires persistés et des secrets dans les flashes.
- POST, droits de propriété et persistance pour publication/masquage des notes ; suppression utilisateur POST.
- Contrôles d'accès aux syllabus et documents de chapitre.
- Redis pour rate limiting lorsqu'il est configuré, limites de connexion et renouvellement des sessions.
- Réponses privées non mises en cache, seed interdit en production et exigences de clé session/CSRF au démarrage production.
- Tests isolés et documents de suivi.

Cycle 3 : cache PWA limité aux ressources publiques, anciens caches privés purgés, export admin sans hashes, téléchargement des pièces de devoir contrôlé. Vérifications : 65 tests réussis (16.65s), test Node du service worker : 7 assertions réussies.

- Fondation SQLAlchemy/Alembic et import isolé transactionnel, idempotent et contrôlé.
- Premier Blueprint pour l’exécution ; autres actions modifiantes POST ; vérifications complémentaires des inscrits et des corrections.
- JSON illisible : arrêt du démarrage pour prévenir un écrasement ; aucune réécriture de mots de passe au chargement.
- Évaluations IA non disponibles sans score inventé ; nouvelles propositions publiables après validation manuelle uniquement.
- Scripts de démonstration sans mot de passe admin connu ; image Web et logs simplifiés ; CI isolée PostgreSQL proposée.
