# 📧 Notifications Email - ULC-ICAM Turnin

## ✅ FONCTIONNALITÉ AJOUTÉE

La fonctionnalité de notifications email automatiques a été ajoutée à votre application ULC-ICAM Turnin.

### 🎯 Fonctionnalités
- **Notification automatique** quand un professeur crée un nouveau devoir
- **Email aux étudiants inscrits** au cours concerné
- **Templates HTML professionnels** aux couleurs ULC-ICAM
- **Envoi asynchrone** (non-bloquant)

## 🚀 UTILISATION

### Pour tester immédiatement :

1. **Démarrer l'application**
   ```bash
   python app.py
   ```

2. **Se connecter comme enseignant**
   - Utilisateur: `prof_mukendi`
   - Mot de passe: `prof123`

3. **Créer un nouveau devoir**
   - Cliquer sur "Créer un devoir" dans le tableau de bord
   - Remplir le formulaire
   - Cliquer sur "Créer et notifier"

4. **Vérifier les logs**
   - Les messages d'envoi d'email apparaissent dans la console
   - Les étudiants `marie` et `paul` recevront l'email

## ⚙️ CONFIGURATION

### Fichiers modifiés :
- `app.py` : Ajout des fonctions de notification
- `.env` : Configuration email
- `ulc_icam_data.json` : Données avec emails des étudiants
- `templates/teacher_dashboard.html` : Bouton de création

### Configuration email (.env) :
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=ulc.icam.system@gmail.com
MAIL_PASSWORD=your_app_password_here
NOTIFICATIONS_ENABLED=true
```

### Pour activer l'envoi réel :
1. Créez un compte Gmail dédié
2. Activez la vérification en 2 étapes
3. Générez un mot de passe d'application
4. Remplacez `your_app_password_here` par ce mot de passe

## 👥 COMPTES DE TEST

- **Enseignant** : `prof_mukendi` / `prof123`
- **Étudiants** : 
  - `etudiant_marie` / `etud123` (m.kabongo@student.ulc-icam.cd)
  - `etudiant_paul` / `etud123` (p.mbuyi@student.ulc-icam.cd)

## 🧪 TEST

```bash
python test_email.py
```

Ce script vérifie :
- Configuration email
- Présence des données
- Emails des étudiants

## 📧 TEMPLATE EMAIL

Les emails envoyés contiennent :
- En-tête ULC-ICAM avec logo
- Titre du devoir
- Nom du cours
- Description
- Date limite
- Design responsive

## 🔧 DÉPANNAGE

### Si les emails ne s'envoient pas :
1. Vérifiez la configuration dans `.env`
2. Testez avec `python test_email.py`
3. Consultez les logs dans la console
4. Vérifiez les paramètres Gmail

### Messages dans les logs :
- `Email envoyé: [titre]` = Succès
- `Erreur envoi email: [erreur]` = Problème de configuration
- `Notification désactivée: [titre]` = NOTIFICATIONS_ENABLED=false

## 🎉 RÉSULTAT

Maintenant, à chaque fois qu'un professeur crée un devoir, tous les étudiants inscrits au cours reçoivent automatiquement un email de notification professionnel !

---
**Développé par Jonathan Kakesa pour l'ULC-ICAM**