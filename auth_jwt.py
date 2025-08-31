"""
Authentification JWT et sécurité avancée
"""

from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import timedelta
import hashlib
import secrets

def init_jwt(app):
    """Initialise JWT"""
    app.config['JWT_SECRET_KEY'] = app.secret_key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    
    jwt = JWTManager(app)
    print("✅ JWT configuré")
    return jwt

def init_limiter(app):
    """Initialise le rate limiting"""
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    print("✅ Rate limiting configuré")
    return limiter

def hash_password(password):
    """Hash sécurisé du mot de passe"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}:{pwd_hash.hex()}"

def verify_password(password, hashed):
    """Vérifie le mot de passe"""
    try:
        salt, pwd_hash = hashed.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex() == pwd_hash
    except:
        # Fallback pour anciens mots de passe
        return password == hashed

def create_user_token(user_data):
    """Crée un token JWT pour l'utilisateur"""
    return create_access_token(
        identity=user_data['username'],
        additional_claims={
            'role': user_data['role'],
            'name': user_data['name']
        }
    )