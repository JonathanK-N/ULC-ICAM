# Test Rapide - Résolution du Problème

## Modifications Appliquées

1. **Route de test ajoutée** : `/test_submit` sans authentification
2. **Template modifié** : Utilise temporairement la route de test
3. **Debug ajouté** : Logs détaillés dans le JavaScript

## Comment Tester

1. **Démarrer le serveur :**
   ```bash
   cd ulc-turnin-web
   python app.py
   ```

2. **Se connecter comme étudiant :**
   - URL: http://localhost:5000/login/student
   - Identifiant: etud01
   - Mot de passe: student123

3. **Tester la soumission :**
   - Cliquer sur un devoir de code
   - Saisir : `print("Hello, World!")`
   - Cliquer "Soumettre et Exécuter"
   - **Ouvrir la console du navigateur (F12)** pour voir les logs

## Résultats Attendus

### Si ça fonctionne :
- Console : "Response status: 200"
- Console : "Parsed data: {success: true, execution_result: {...}}"
- Interface : Affichage des résultats d'exécution

### Si ça ne fonctionne pas :
- Console : Détails de l'erreur
- Interface : Message d'erreur spécifique

## Prochaines Étapes

Une fois que la route de test fonctionne :
1. Identifier pourquoi la route originale ne fonctionne pas
2. Corriger le problème d'authentification/accès
3. Restaurer la route originale

## Commandes de Debug

```bash
# Vérifier que le serveur fonctionne
curl http://localhost:5000/

# Tester directement la route
curl -X POST http://localhost:5000/test_submit -d "code_content=print('test')&language=python"
```

Ce test permettra d'isoler le problème et de le résoudre rapidement.