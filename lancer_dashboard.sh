#!/bin/bash

echo "========================================"
echo "  Dashboard Turf BZH"
echo "  Démarrage en cours..."
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null
then
    echo "ERREUR: Python 3 n'est pas installé"
    echo "Installez Python 3: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Nom de l'environnement virtuel
VENV_DIR="venv"

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "ERREUR: Impossible de créer l'environnement virtuel"
        echo "Installez python3-venv: sudo apt install python3-venv"
        exit 1
    fi
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source $VENV_DIR/bin/activate

# Vérifier si Streamlit est installé dans le venv
if ! python -c "import streamlit" &> /dev/null
then
    echo "📦 Installation des dépendances..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERREUR: Impossible d'installer les dépendances"
        deactivate
        exit 1
    fi
    echo "✅ Installation terminée!"
fi

echo ""
echo "🚀 Lancement du dashboard..."
echo ""
echo "📌 Le dashboard va s'ouvrir dans votre navigateur"
echo "⚠️  Pour arrêter l'application, appuyez sur Ctrl+C"
echo ""

streamlit run app_turf_dashboard.py

# Désactiver l'environnement virtuel à la fin
deactivate
