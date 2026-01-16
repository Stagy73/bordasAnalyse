#!/bin/bash

# 🔧 Script de correction du Dashboard
# Exécuter ce script pour corriger l'erreur d'indentation

echo "🔧 Correction du Dashboard Turf BZH"
echo "===================================="
echo ""

# Aller dans le bon dossier
cd ~/bordasAnalyse || exit 1

# 1. Arrêter Streamlit si actif
echo "1️⃣ Arrêt de Streamlit..."
pkill -f "streamlit run" 2>/dev/null || echo "   (Streamlit n'était pas actif)"
sleep 2

# 2. Nettoyer le cache Streamlit
echo ""
echo "2️⃣ Nettoyage du cache Streamlit..."
rm -rf ~/.streamlit/cache 2>/dev/null
rm -rf .streamlit/cache 2>/dev/null
echo "   ✅ Cache nettoyé"

# 3. Sauvegarder l'ancien fichier
echo ""
echo "3️⃣ Sauvegarde de l'ancien fichier..."
if [ -f "app_turf_dashboard.py" ]; then
    cp app_turf_dashboard.py app_turf_dashboard_BACKUP_$(date +%Y%m%d_%H%M%S).py
    echo "   ✅ Backup créé"
fi

# 4. Vérifier si app_turf_dashboard_db.py existe
echo ""
echo "4️⃣ Vérification des fichiers..."
if [ ! -f "app_turf_dashboard_db.py" ]; then
    echo "   ❌ ERREUR: app_turf_dashboard_db.py non trouvé !"
    echo "   📥 Veuillez télécharger ce fichier depuis les outputs"
    echo "   📍 Et le placer dans ~/bordasAnalyse/"
    exit 1
fi
echo "   ✅ Fichier trouvé"

# 5. Remplacer le fichier
echo ""
echo "5️⃣ Remplacement du fichier..."
cp app_turf_dashboard_db.py app_turf_dashboard.py
echo "   ✅ Fichier remplacé"

# 6. Vérifier le contenu
echo ""
echo "6️⃣ Vérification du nouveau fichier..."
echo "   Ligne 22-24:"
sed -n '22,24p' app_turf_dashboard.py
echo ""

# 7. Vérifier les dépendances
echo "7️⃣ Vérification des modules requis..."
python3 << 'PYEND'
import sys
missing = []
try:
    from streamlit_db_adapter import get_db_adapter
    print("   ✅ streamlit_db_adapter.py présent")
except:
    missing.append("streamlit_db_adapter.py")
    print("   ❌ streamlit_db_adapter.py MANQUANT")

try:
    from turf_database_complete import get_turf_database
    print("   ✅ turf_database_complete.py présent")
except:
    missing.append("turf_database_complete.py")
    print("   ❌ turf_database_complete.py MANQUANT")

if missing:
    print("\n   ⚠️  Fichiers manquants:", ", ".join(missing))
    print("   📥 Téléchargez-les depuis les outputs")
    sys.exit(1)
PYEND

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Des fichiers requis sont manquants !"
    exit 1
fi

# 8. Relancer Streamlit
echo ""
echo "8️⃣ Relancement de Streamlit..."
echo "   Exécutez manuellement:"
echo ""
echo "   streamlit run app_turf_dashboard.py"
echo ""
echo "✅ Correction terminée !"
echo ""
echo "📋 Si l'erreur persiste:"
echo "   1. Fermez TOUS les onglets Streamlit dans votre navigateur"
echo "   2. Arrêtez le terminal Streamlit (Ctrl+C)"
echo "   3. Relancez: streamlit run app_turf_dashboard.py"
