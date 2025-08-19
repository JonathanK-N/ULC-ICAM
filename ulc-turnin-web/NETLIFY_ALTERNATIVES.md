# ⚠️ Netlify et Cognito Web

## 🚫 Problème
**Netlify ne supporte QUE les sites statiques** (HTML, CSS, JS). 
Cognito Web est une **application Flask (Python)** qui nécessite un serveur backend.

## ✅ Solutions Recommandées

### 1. 🌐 **Vercel** (Équivalent de Netlify pour Python)
```bash
# Installation
npm i -g vercel

# Déploiement
vercel --prod
```

### 2. 🚀 **Railway** (Simple et gratuit)
```bash
# Connexion GitHub et déploiement automatique
# railway.app
```

### 3. 🔥 **Render** (Alternative moderne)
```bash
# Connexion GitHub
# render.com
```

---

## 🌐 Déploiement sur Vercel

### Étape 1: Créer vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "./app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

### Étape 2: Modifier app.py
```python
# Ajouter à la fin de app.py
app.config['UPLOAD_FOLDER'] = '/tmp'
```

### Étape 3: Déployer
```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel --prod
```

---

## 🚀 Déploiement sur Railway

### Étape 1: Connexion
1. Aller sur https://railway.app
2. Se connecter avec GitHub
3. Sélectionner le repository cognito-web

### Étape 2: Configuration automatique
Railway détecte automatiquement Flask et déploie.

### Étape 3: Variables d'environnement
```
FLASK_ENV=production
PORT=5000
```

---

## 🔥 Déploiement sur Render

### Étape 1: Connexion
1. Aller sur https://render.com
2. Connecter GitHub
3. Sélectionner cognito-web

### Étape 2: Configuration
```
Build Command: pip install -r requirements.txt
Start Command: python app.py
```

---

## 💡 Solution Hybride (Netlify + Backend séparé)

Si vous voulez absolument utiliser Netlify:

### Frontend sur Netlify
```html
<!-- Version statique simplifiée -->
<!DOCTYPE html>
<html>
<head>
    <title>Cognito Web</title>
</head>
<body>
    <div id="app">
        <!-- Interface utilisateur en JavaScript -->
    </div>
    <script>
        // Appels API vers le backend
        fetch('https://votre-backend.herokuapp.com/api/login')
    </script>
</body>
</html>
```

### Backend sur Heroku/Railway
- API Flask séparée
- Communication via AJAX/Fetch

---

## 🎯 Recommandation

**Utilisez Railway ou Render** - Plus simples que Heroku et gratuits:

### Railway (Le plus simple):
1. Push sur GitHub
2. Connecter à railway.app
3. Déploiement automatique

### Render:
1. Push sur GitHub  
2. Connecter à render.com
3. Configuration en 2 clics

---

## 🔧 Préparation pour Railway/Render

Votre projet est déjà prêt avec:
- ✅ requirements.txt
- ✅ Procfile
- ✅ app.py configuré
- ✅ Structure correcte

Il suffit de push sur GitHub et connecter à la plateforme choisie!