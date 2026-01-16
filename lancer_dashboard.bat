@echo off
echo ========================================
echo   Dashboard Turf BZH
echo   Demarrage en cours...
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Telechargez Python sur: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verifier si Streamlit est installe
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer les dependances
        pause
        exit /b 1
    )
)

echo Lancement du dashboard...
echo.
echo Le dashboard va s'ouvrir dans votre navigateur
echo Pour arreter l'application, appuyez sur Ctrl+C
echo.

streamlit run app_turf_dashboard.py

pause
