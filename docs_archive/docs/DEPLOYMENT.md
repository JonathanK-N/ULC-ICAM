# 🚀 Guide de Déploiement - Cognito Web

## 📋 Options de Déploiement

### 1. 🌐 **Heroku** (Recommandé - Gratuit)
### 2. ☁️ **PythonAnywhere** (Gratuit avec limitations)
### 3. 🔧 **VPS/Serveur Dédié**
### 4. 🐳 **Docker**

---

## 🌐 Déploiement sur Heroku

### Étape 1: Préparation des fichiers

```bash
# 1. Créer Procfile
echo "web: python app.py" > Procfile

# 2. Modifier app.py pour Heroku
```

### Étape 2: Modifications pour Heroku

```python
# À la fin de app.py, remplacer:
if __name__ == '__main__':
    app.run(debug=True)

# Par:
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Étape 3: Déploiement

```bash
# 1. Installer Heroku CLI
# Télécharger: https://devcenter.heroku.com/articles/heroku-cli

# 2. Se connecter
heroku login

# 3. Créer l'application
heroku create cognito-web-app

# 4. Déployer
git init
git add .
git commit -m "Initial deployment"
git push heroku main
```

---

## ☁️ Déploiement sur PythonAnywhere

### Étape 1: Créer un compte
- Aller sur https://www.pythonanywhere.com
- Créer un compte gratuit

### Étape 2: Upload des fichiers
```bash
# Via l'interface web ou Git
git clone https://github.com/votre-username/cognito-web.git
```

### Étape 3: Configuration
```python
# Dans le fichier WSGI:
import sys
import os

path = '/home/yourusername/cognito-web'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

---

## 🔧 Déploiement sur VPS (Ubuntu)

### Étape 1: Préparation du serveur
```bash
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installation Python et pip
sudo apt install python3 python3-pip python3-venv nginx -y

# Création utilisateur
sudo adduser cognito
sudo usermod -aG sudo cognito
```

### Étape 2: Installation de l'application
```bash
# Se connecter comme cognito
su - cognito

# Cloner le projet
git clone https://github.com/votre-username/cognito-web.git
cd cognito-web

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation dépendances
pip install -r requirements.txt
pip install gunicorn
```

### Étape 3: Configuration Gunicorn
```bash
# Créer gunicorn.service
sudo nano /etc/systemd/system/cognito.service
```

```ini
[Unit]
Description=Cognito Web App
After=network.target

[Service]
User=cognito
Group=www-data
WorkingDirectory=/home/cognito/cognito-web
Environment="PATH=/home/cognito/cognito-web/venv/bin"
ExecStart=/home/cognito/cognito-web/venv/bin/gunicorn --workers 3 --bind unix:cognito.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```

### Étape 4: Configuration Nginx
```bash
sudo nano /etc/nginx/sites-available/cognito
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/cognito/cognito-web/cognito.sock;
    }

    location /static {
        alias /home/cognito/cognito-web/static;
    }

    location /uploads {
        alias /home/cognito/cognito-web/uploads;
    }
}
```

### Étape 5: Activation
```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/cognito /etc/nginx/sites-enabled

# Démarrer les services
sudo systemctl start cognito
sudo systemctl enable cognito
sudo systemctl restart nginx
```

---

## 🐳 Déploiement avec Docker

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  cognito-web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./static:/app/static
    environment:
      - FLASK_ENV=production
```

### Commandes Docker
```bash
# Build et run
docker-compose up --build -d

# Voir les logs
docker-compose logs -f
```

---

## 🔒 Configuration de Production

### 1. Variables d'environnement
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-production-secret-key'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
```

### 2. Sécurité
```python
# Dans app.py
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
```

### 3. Base de données persistante (optionnel)
```python
# Remplacer les dictionnaires par SQLite
import sqlite3

def init_db():
    conn = sqlite3.connect('cognito.db')
    # Créer les tables...
    conn.close()
```

---

## 📊 Monitoring et Maintenance

### 1. Logs
```bash
# Voir les logs Heroku
heroku logs --tail

# Logs VPS
sudo journalctl -u cognito -f
```

### 2. Backup
```bash
# Backup des uploads
tar -czf backup-$(date +%Y%m%d).tar.gz uploads/ static/photos/
```

### 3. Mise à jour
```bash
# Heroku
git add .
git commit -m "Update"
git push heroku main

# VPS
git pull origin main
sudo systemctl restart cognito
```

---

## 🌍 Domaine Personnalisé

### 1. Heroku
```bash
# Ajouter domaine
heroku domains:add www.cognito-web.com

# Configurer DNS
# CNAME: www -> your-app.herokuapp.com
```

### 2. VPS
```bash
# Configurer DNS
# A Record: @ -> IP_DU_SERVEUR
# CNAME: www -> @
```

---

## ✅ Checklist de Déploiement

- [ ] **Code testé** localement
- [ ] **Requirements.txt** à jour
- [ ] **Variables d'environnement** configurées
- [ ] **Secret key** changée
- [ ] **Debug mode** désactivé
- [ ] **HTTPS** configuré (production)
- [ ] **Backup** configuré
- [ ] **Monitoring** en place

---

## 🆘 Dépannage

### Erreurs communes:
```bash
# Port déjà utilisé
sudo lsof -i :5000
sudo kill -9 PID

# Permissions fichiers
sudo chown -R cognito:www-data /home/cognito/cognito-web
sudo chmod -R 755 /home/cognito/cognito-web

# Redémarrer services
sudo systemctl restart cognito nginx
```

### Logs utiles:
```bash
# Nginx
sudo tail -f /var/log/nginx/error.log

# Application
sudo journalctl -u cognito --since "1 hour ago"
```

---

## 📞 Support

Pour toute question sur le déploiement:
- 📧 Email: jonathan.kakesa@example.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: README.md