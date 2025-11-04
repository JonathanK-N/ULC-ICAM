# 🎓 ULC-ICAM Cognito Web - Mode Test

## 🔑 Connexion Simplifiée pour les Tests

Votre application est maintenant configurée en **mode test** avec une authentification simplifiée.

### 📋 Instructions de Connexion

#### Pour les Étudiants :
1. Allez sur `/login/student`
2. **Entrez seulement le CIP** (ex: `ETUD001`)
3. **Laissez le champ mot de passe VIDE**
4. Cliquez sur "Se connecter"

#### Pour les Professeurs :
1. Allez sur `/login/teacher`
2. **Entrez seulement le CIP** (ex: `PROF001`)
3. **Laissez le champ mot de passe VIDE**
4. Cliquez sur "Se connecter"

#### Pour l'Administrateur :
- Username: `admin`
- Mot de passe: `admin123`
- (L'admin garde son authentification normale)

### 👥 Utilisateurs de Test Disponibles

#### Quelques Professeurs :
- `PROF001` - Prof. Ordinaire Jean-Baptiste Mukendi (Sciences)
- `PROF002` - Prof. Ordinaire Therese Mbuyi (Sciences)
- `PROF003` - CT Andre Katanga (Sciences)
- `PROF009` - Ass. Pierre Kasongo (Médecine)
- `PROF015` - CT Bernadette Luboya (Droit)

#### Quelques Étudiants :
- `ETUD001` - David Tshisekedi (L1 Sciences)
- `ETUD002` - Elie Mbayo (L1 Sciences)
- `ETUD010` - Grace Mukendi (L2 Sciences)
- `ETUD053` - Priscille Mwilambwe (L1 Médecine)
- `ETUD097` - Ruth Kasongo (L1 Droit)

### 📊 Données Chargées
- **342 utilisateurs** au total
- **38 professeurs** répartis dans toutes les facultés
- **303 étudiants** de L1 à M2
- **109 cours** disponibles
- **Inscriptions automatiques** déjà configurées

### 🏫 Facultés Disponibles
- Sciences
- Médecine
- Droit
- Sciences Économiques
- Polytechnique
- Lettres et Sciences Humaines

### 🔧 Pour Voir Tous les Utilisateurs
Exécutez le script :
```bash
python show_test_users.py
```

### ⚠️ Important
Ce mode est **uniquement pour les tests**. En production, vous devrez :
1. Supprimer les conditions `if not password or` dans les fonctions de connexion
2. Remettre l'authentification normale avec mot de passe obligatoire

### 🚀 Démarrer l'Application
```bash
python app.py
```

Puis allez sur `http://localhost:5000`