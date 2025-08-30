# Guide d'Installation - Système ULC-ICAM

## Table des Matières
1. [Prérequis Système](#prérequis-système)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Démarrage](#démarrage)
5. [Configuration Avancée](#configuration-avancée)
6. [Dépannage](#dépannage)
7. [Mise à Jour](#mise-à-jour)

## Prérequis Système

### Configuration Minimale
- **OS** : Windows 10/11, Linux Ubuntu 18.04+, macOS 10.15+
- **RAM** : 4 GB minimum, 8 GB recommandé
- **Stockage** : 10 GB d'espace libre
- **Réseau** : Connexion internet stable

### Logiciels Requis
- **Python** : 3.8 ou supérieur
- **pip** : Gestionnaire de paquets Python
- **Git** : Pour le téléchargement du code source

### Vérification des Prérequis
```bash
# Vérifier Python
python --version
# ou
python3 --version

# Vérifier pip
pip --version

# Vérifier Git
git --version
```

## Installation

### 1. Téléchargement du Code Source
```bash
# Cloner le repository
git clone https://github.com/ulc-icam/academic-system.git
cd academic-system

# Ou télécharger et extraire l'archive ZIP
```

### 2. Environnement Virtuel Python
```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Linux/macOS)
source venv/bin/activate
```

### 3. Installation des Dépendances
```bash
# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

### 4. Structure des Répertoires
```bash
# Créer les répertoires nécessaires
mkdir uploads
mkdir logs
mkdir backups
mkdir static/images
```

## Configuration

### 1. Configuration de Base
Créez un fichier `config.py` :
```python
import os

class Config:
    SECRET_KEY = 'votre-clé-secrète-très-sécurisée'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ulc_icam.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    
    # Configuration Judge0 API
    JUDGE0_API_URL = 'https://judge0-ce.p.rapidapi.com'
    JUDGE0_API_KEY = 'votre-clé-rapidapi'
    
    # Configuration Email (optionnel)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'votre-email@ulc-icam.edu.km'
    MAIL_PASSWORD = 'votre-mot-de-passe'
```

### 2. Variables d'Environnement
Créez un fichier `.env` :
```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre-clé-secrète-très-sécurisée
JUDGE0_API_KEY=votre-clé-rapidapi
DATABASE_URL=sqlite:///ulc_icam.db
```

### 3. Configuration Judge0 API
1. Inscrivez-vous sur [RapidAPI](https://rapidapi.com)
2. Abonnez-vous à Judge0 CE
3. Récupérez votre clé API
4. Ajoutez-la dans `config.py` et `.env`

### 4. Logos et Images
Placez les logos ULC-ICAM dans `static/images/` :
- `logo.png` : Logo principal
- `favicon.ico` : Icône du site
- `background.jpg` : Image de fond (optionnel)

## Démarrage

### 1. Initialisation de la Base de Données
```bash
# Activer l'environnement virtuel
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Initialiser la base de données
python -c "from app import db; db.create_all()"
```

### 2. Création du Compte Administrateur
```bash
# Lancer l'application une première fois
python app.py

# Le compte admin par défaut sera créé automatiquement :
# Email: admin@ulc-icam.edu.km
# Mot de passe: admin123
```

### 3. Démarrage de l'Application
```bash
# Mode développement
python app.py

# Ou avec Flask
flask run

# L'application sera accessible sur http://localhost:5000
```

### 4. Première Connexion
1. Ouvrez votre navigateur
2. Allez sur `http://localhost:5000`
3. Connectez-vous avec le compte admin
4. Changez immédiatement le mot de passe
5. Configurez le système selon vos besoins

## Configuration Avancée

### 1. Configuration de Production

#### Serveur Web (Nginx)
```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
        alias /chemin/vers/votre/app/static;
    }
}
```

#### WSGI (Gunicorn)
```bash
# Installer Gunicorn
pip install gunicorn

# Lancer avec Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Service Systemd (Linux)
Créez `/etc/systemd/system/ulc-icam.service` :
```ini
[Unit]
Description=ULC-ICAM Academic System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/votre/app
Environment="PATH=/chemin/vers/votre/app/venv/bin"
ExecStart=/chemin/vers/votre/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Base de Données PostgreSQL (Optionnel)
```bash
# Installer PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Créer la base de données
sudo -u postgres createdb ulc_icam

# Modifier config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/ulc_icam'

# Installer le driver
pip install psycopg2-binary
```

### 3. Configuration HTTPS
```bash
# Générer un certificat SSL (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com

# Ou utiliser un certificat auto-signé pour les tests
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### 4. Sauvegarde Automatique
```bash
# Configurer les sauvegardes
cd backup/
python backup_scheduler.py --setup

# Ajouter au crontab
crontab -e
# Ajouter : 0 2 * * * /chemin/vers/votre/app/backup/daily_backup.sh
```

## Dépannage

### Problèmes Courants

#### Erreur de Port
```bash
# Si le port 5000 est occupé
flask run --port 5001

# Ou modifier dans app.py
app.run(port=5001)
```

#### Problèmes de Permissions
```bash
# Linux/macOS
chmod +x backup/*.sh
chown -R www-data:www-data /chemin/vers/app

# Windows
# Exécuter en tant qu'administrateur
```

#### Erreurs de Base de Données
```bash
# Réinitialiser la base de données
rm ulc_icam.db
python -c "from app import db; db.create_all()"
```

#### Problèmes Judge0 API
```bash
# Tester la connexion
curl -X GET "https://judge0-ce.p.rapidapi.com/languages" \
  -H "X-RapidAPI-Key: votre-clé" \
  -H "X-RapidAPI-Host: judge0-ce.p.rapidapi.com"
```

### Logs et Débogage
```bash
# Activer les logs détaillés
export FLASK_ENV=development

# Consulter les logs
tail -f logs/system.log

# Logs d'erreur Python
python app.py 2>&1 | tee logs/error.log
```

## Mise à Jour

### Mise à Jour du Code
```bash
# Sauvegarder la base de données
cp ulc_icam.db ulc_icam.db.backup

# Mettre à jour le code
git pull origin main

# Mettre à jour les dépendances
pip install -r requirements.txt --upgrade

# Migrer la base de données si nécessaire
python migrate.py
```

### Sauvegarde Avant Mise à Jour
```bash
# Sauvegarde complète
python backup/backup_manager.py --full --local

# Vérifier la sauvegarde
python backup/backup_manager.py --verify
```

### Rollback en Cas de Problème
```bash
# Restaurer la base de données
cp ulc_icam.db.backup ulc_icam.db

# Revenir à la version précédente
git checkout HEAD~1

# Redémarrer l'application
python app.py
```

## Monitoring et Maintenance

### Surveillance Système
```bash
# Utilisation des ressources
htop
df -h
free -m

# Logs d'accès
tail -f /var/log/nginx/access.log
```

### Maintenance Régulière
```bash
# Nettoyage des fichiers temporaires
find uploads/ -type f -mtime +30 -delete

# Optimisation de la base de données
sqlite3 ulc_icam.db "VACUUM;"

# Rotation des logs
logrotate /etc/logrotate.d/ulc-icam
```

### Scripts Utiles
```bash
# Script de démarrage
#!/bin/bash
cd /chemin/vers/app
source venv/bin/activate
python app.py

# Script d'arrêt
#!/bin/bash
pkill -f "python app.py"

# Script de redémarrage
#!/bin/bash
./stop.sh
sleep 2
./start.sh
```

## Support

### Documentation
- **Guides utilisateurs** : Disponibles dans `/docs/`
- **API Documentation** : `/api/docs` (si activée)
- **Code source** : Commenté et documenté

### Contact Support
- **Email technique** : admin@ulc-icam.edu.km
- **Issues GitHub** : Pour les bugs et améliorations
- **Documentation** : Wiki du projet

### Formation
- **Sessions d'installation** : Disponibles sur demande
- **Formation administrateurs** : Programme complet
- **Webinaires** : Mises à jour et nouvelles fonctionnalités

---

**Support Technique** : admin@ulc-icam.edu.km  
**Documentation mise à jour** : Décembre 2024