@echo off
REM ===============================================================================
REM Développeur: Jonathan Kakesa | Date: 19/12/2024 | Heure: 21:15
REM Description: Script batch pour exécuter les tests sur Windows
REM Fonctionnalités: Démarrage serveur, exécution tests, rapport final
REM ===============================================================================

echo.
echo ========================================================================
echo   UNIVERSITE LOYOLA DU CONGO - INSTITUT CATHOLIQUE D'ART ET METIER
echo   SYSTEME ULC-ICAM TURNIN - SUITE DE TESTS COMPLETE
echo   Developpe par: Jonathan Kakesa
echo   Date: 19 decembre 2024
echo ========================================================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python et reessayer
    pause
    exit /b 1
)

REM Aller dans le répertoire du projet
cd /d "%~dp0.."

REM Vérifier si le fichier app.py existe
if not exist "app.py" (
    echo ERREUR: Fichier app.py non trouve
    echo Assurez-vous d'etre dans le bon repertoire
    pause
    exit /b 1
)

echo 🔍 Verification des dependances...
pip install -r requirements.txt >nul 2>&1

echo.
echo 🚀 Demarrage du serveur ULC-ICAM Turnin...
echo.

REM Démarrer le serveur en arrière-plan
start /b python app.py

REM Attendre que le serveur démarre
echo Attente du demarrage du serveur...
timeout /t 8 /nobreak >nul

REM Vérifier si le serveur répond
echo 🔍 Verification du serveur...
python -c "import requests; requests.get('http://localhost:5000', timeout=5)" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Le serveur ne repond pas
    echo.
    echo 📋 INSTRUCTIONS MANUELLES:
    echo 1. Ouvrez un autre terminal
    echo 2. Executez: python app.py
    echo 3. Attendez que le serveur demarre sur http://localhost:5000
    echo 4. Relancez ce script
    echo.
    pause
    exit /b 1
)

echo ✅ Serveur demarre avec succes
echo.

REM Exécuter les tests
echo 🧪 EXECUTION DES TESTS...
echo.

cd test
python run_all_tests.py

REM Capturer le code de retour
set TEST_RESULT=%errorlevel%

echo.
echo ========================================================================

if %TEST_RESULT% equ 0 (
    echo 🎉 TOUS LES TESTS SONT PASSES AVEC SUCCES!
    echo ✅ Le systeme ULC-ICAM Turnin est pret pour la production.
) else (
    echo ⚠️  CERTAINS TESTS ONT ECHOUE
    echo 🔧 Consultez le rapport detaille ci-dessus pour les corrections necessaires.
)

echo.
echo 📄 Les rapports de test ont ete sauvegardes dans le dossier test/
echo.
echo ========================================================================

REM Arrêter le serveur (optionnel)
echo.
set /p STOP_SERVER="Voulez-vous arreter le serveur? (o/N): "
if /i "%STOP_SERVER%"=="o" (
    echo Arret du serveur...
    taskkill /f /im python.exe >nul 2>&1
    echo Serveur arrete.
)

echo.
echo Appuyez sur une touche pour fermer...
pause >nul

exit /b %TEST_RESULT%