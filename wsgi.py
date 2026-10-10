"""
Point d'entrée WSGI pour gunicorn / Railway.
Centralise les erreurs de démarrage dans les logs.
"""
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout,
)

logger = logging.getLogger('wsgi')
logger.info("=== Démarrage de l'application ULC-ICAM ===")

try:
    from app import app
    logger.info("=== Application importée avec succès ===")
except Exception as e:
    logger.critical(f"=== ERREUR FATALE AU DÉMARRAGE : {e} ===", exc_info=True)
    raise
