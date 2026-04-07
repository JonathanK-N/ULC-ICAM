FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Répertoire de travail
WORKDIR /app

# Dépendances système (gcc/g++ pour compilation de code étudiants)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Créer les dossiers nécessaires
RUN mkdir -p uploads cache logs uploads/assignments uploads/chapters \
    uploads/corrections uploads/code_submissions uploads/analysis uploads/syllabus

# Port d'exposition (Railway injecte PORT=8080)
EXPOSE 8080

# Healthcheck sur le port Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:${PORT:-8080}/ || exit 1

# Commande : gunicorn lit $PORT injecté par Railway
CMD gunicorn \
    --bind 0.0.0.0:${PORT:-8080} \
    --workers 2 \
    --threads 2 \
    --timeout 120 \
    --log-level info \
    app:app
