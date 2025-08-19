FROM python:3.9-slim

WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p uploads/assignments static/photos

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Commande de démarrage
CMD ["python", "app.py"]