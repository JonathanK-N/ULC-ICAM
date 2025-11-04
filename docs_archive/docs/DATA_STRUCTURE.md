# Structure des Données ULC-ICAM Turnin

**Développeur:** Jonathan Kakesa  
**Date:** 2024-12-19  
**Description:** Documentation de la structure des données JSON  
**Fichier:** ulc_icam_data.json  

## Structure du fichier ulc_icam_data.json

### 1. Users (Utilisateurs)
```json
"users": {
  "username": {
    "password": "mot_de_passe",
    "role": "admin|teacher|student",
    "name": "Nom complet",
    "email": "email@ulc-icam.cd"
  }
}
```

### 2. Admin Courses (Cours administratifs)
```json
"admin_courses": [
  {
    "id": 1,
    "name": "Nom du cours",
    "code": "CODE123"
  }
]
```

### 3. Course Enrollments (Inscriptions aux cours)
```json
"course_enrollments": {
  "course_id": ["username1", "username2"]
}
```

### 4. Assignments (Devoirs)
```json
"assignments": [
  {
    "id": 1,
    "title": "Titre du devoir",
    "description": "Description",
    "course_id": 1,
    "due_date": "2024-12-31",
    "max_score": 100
  }
]
```

### 5. Submissions (Soumissions)
```json
"submissions": [
  {
    "id": 1,
    "assignment_id": 1,
    "student": "username",
    "filename": "fichier.pdf",
    "submitted_at": "2024-12-19 10:30:00"
  }
]
```

## Comptes de test par défaut

- **Admin:** admin / admin123
- **Professeur:** prof_mukendi / prof123  
- **Étudiant 1:** etudiant_marie / etud123
- **Étudiant 2:** etudiant_paul / etud123

## Notes importantes

- Les IDs sont auto-incrémentés
- Les emails sont requis pour les notifications
- Les mots de passe sont en texte clair (à changer en production)
- La structure est extensible pour de nouvelles fonctionnalités