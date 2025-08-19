@echo off
echo ========================================
echo    COGNITO WEB - SUITE DE TESTS
echo ========================================
echo.

echo 1. Verification des donnees de test...
python generate_test_data.py
echo.

echo 2. Demarrage de l'application en arriere-plan...
start /B python app.py
echo Application demarree sur http://localhost:5000
echo.

echo 3. Attente du demarrage (5 secondes)...
timeout /t 5 /nobreak > nul
echo.

echo 4. Execution des tests automatiques...
python test_functionality.py
echo.

echo 5. Tests termines !
echo.
echo INSTRUCTIONS POUR TESTS MANUELS:
echo - Ouvrez http://localhost:5000 dans votre navigateur
echo - Consultez le fichier test_manual.md pour la liste complete
echo - Testez les comptes: admin/admin123, prof001/prof1pass, etud001/etud1pass
echo.

pause