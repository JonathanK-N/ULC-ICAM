# ULC TurnIn - Application Flask

Application web de remise de devoirs développée avec Flask et Bootstrap.

## Installation

1. Installer Python 3.8+ si ce n'est pas déjà fait
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## Lancement

```bash
python app.py
```

L'application sera accessible sur http://localhost:5000

## Comptes de test

### Étudiant
- Utilisateur : `student`
- Mot de passe : `password`

### Enseignant
- Utilisateur : `teacher`
- Mot de passe : `password`

## Fonctionnalités

- **Étudiants** : Consulter les devoirs et soumettre des fichiers
- **Enseignants** : Voir les soumissions et gérer les devoirs
- Interface responsive avec Bootstrap 5
- Upload de fichiers sécurisé
- Gestion des sessions utilisateur

## Structure

```
ulc-turnin-web/
├── app.py              # Application Flask principale
├── app/
│   ├── templates/      # Templates HTML
│   └── static/         # Fichiers CSS/JS
├── uploads/            # Fichiers soumis
└── requirements.txt    # Dépendances Python
```