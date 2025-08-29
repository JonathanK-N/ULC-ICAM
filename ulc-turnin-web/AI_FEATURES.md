# 🤖 Fonctionnalités IA - ULC-ICAM Turnin

## 🔍 Détection de Plagiat Avancée

### Fonctionnalités
- **Comparaison locale** : Compare avec toutes les soumissions existantes
- **Détection web** : Recherche de contenu similaire sur Internet (Google API)
- **Support multi-formats** : PDF, DOCX, TXT, et autres formats texte
- **Analyse en temps réel** : Traitement asynchrone lors de la soumission

### Algorithmes utilisés
- `SequenceMatcher` pour comparaison de similarité textuelle
- Google Custom Search API pour détection web
- Extraction de texte multi-format (PyPDF2, docx2txt)

### Résultats
- **Pourcentage de similarité** : 0-100%
- **Sources détectées** : Liste des documents/sites similaires
- **Statut** : 
  - `acceptable` (< 30%)
  - `attention` (30-50%)
  - `suspect` (> 50%)

## 🧠 Correction Automatique avec IA

### Modèles supportés

#### 1. OpenAI GPT-3.5/4 (Recommandé)
- **Avantages** : Correction contextuelle avancée, feedback détaillé
- **Configuration** : Nécessite `OPENAI_API_KEY`
- **Coût** : Payant selon usage

#### 2. Hugging Face Transformers (Local)
- **Avantages** : Gratuit, fonctionne hors ligne
- **Modèle** : BERT multilingue pour analyse de sentiment/qualité
- **Performance** : Correction basique mais efficace

#### 3. Fallback (Secours)
- **Utilisation** : Si les autres modèles échouent
- **Méthode** : Analyse statistique basique

### Critères d'évaluation
- **Longueur du contenu** : Vérification du nombre de mots
- **Structure** : Analyse des paragraphes et organisation
- **Qualité linguistique** : Sentiment et cohérence (IA)
- **Pertinence** : Correspondance avec les consignes du devoir

### Feedback automatique
- **Note numérique** : Sur la base maximale définie
- **Commentaires détaillés** : 3-5 points d'amélioration
- **Suggestions** : Recommandations personnalisées

## 🚀 Installation et Configuration

### 1. Installation automatique
```bash
python setup_ai.py
```

### 2. Installation manuelle
```bash
pip install -r requirements.txt
```

### 3. Configuration des API (Optionnel)
Créez un fichier `.env` :
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
GOOGLE_SEARCH_ENGINE_ID=your_search_id
```

## 📊 Utilisation

### Pour les Professeurs
1. **Créer un devoir** avec options :
   - ☑️ Détection de plagiat
   - ☑️ Correction automatique
2. **Consulter les résultats** dans l'interface de gestion
3. **Modifier les notes** si nécessaire (correction manuelle)

### Pour les Étudiants
1. **Soumettre le devoir** normalement
2. **Attendre le traitement** (quelques secondes à minutes)
3. **Consulter les résultats** une fois publiés

## 🔧 Formats de fichiers supportés

### Détection de plagiat
- ✅ PDF (.pdf)
- ✅ Word (.docx)
- ✅ Texte (.txt)
- ✅ Code source (.py, .java, .cpp, etc.)
- ✅ Markdown (.md)

### Correction automatique
- ✅ Tous les formats texte
- ✅ Extraction automatique du contenu
- ✅ Analyse multilingue (français prioritaire)

## ⚡ Performance

### Temps de traitement
- **Plagiat local** : 1-5 secondes
- **Plagiat web** : 5-15 secondes
- **Correction IA** : 10-30 secondes
- **Traitement total** : Asynchrone, n'affecte pas l'UX

### Limitations
- **Taille de fichier** : 16MB maximum
- **API quotas** : Selon les limites des services externes
- **Langues** : Optimisé pour le français, support multilingue

## 🛡️ Sécurité et Confidentialité

### Protection des données
- **Traitement local** : Texte extrait temporairement
- **APIs externes** : Seulement extraits courts pour recherche
- **Stockage** : Aucune donnée sensible conservée par les APIs
- **Chiffrement** : Communications HTTPS uniquement

### Conformité
- **RGPD** : Traitement minimal des données personnelles
- **Académique** : Respect de l'intégrité académique
- **Transparence** : Résultats explicites pour étudiants/professeurs

## 🔄 Maintenance

### Mise à jour des modèles
```bash
pip install --upgrade transformers torch
```

### Monitoring
- Logs automatiques des erreurs
- Statistiques d'utilisation
- Performance des modèles IA

### Dépannage
1. **Vérifier les dépendances** : `python setup_ai.py`
2. **Tester les APIs** : Vérifier les clés dans `.env`
3. **Logs d'erreur** : Consulter la console Flask

## 📈 Métriques et Statistiques

### Tableau de bord admin
- **Taux de plagiat détecté** par cours
- **Distribution des notes** automatiques
- **Temps de traitement** moyen
- **Utilisation des APIs** externes

### Rapports professeurs
- **Comparaison** correction manuelle vs automatique
- **Tendances** par étudiant/classe
- **Efficacité** de la détection de plagiat