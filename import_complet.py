#!/usr/bin/env python3
"""
📦 IMPORT COMPLET : HISTORIQUE + JOURNALIER
Importe tous vos fichiers dans la même base de données
"""

from universal_importer import import_any_csv
from turf_database_complete import get_turf_database
from datetime import date

print("="*60)
print("📦 IMPORT COMPLET - HISTORIQUE + JOURNALIER")
print("="*60)
print()

# 1. Import historique
print("🔄 ÉTAPE 1/2 : Import de l'historique")
print("-" * 60)

try:
    stats_histo = import_any_csv('historique_turf_20260115.csv')
    
    print(f"\n✅ HISTORIQUE IMPORTÉ")
    print(f"   📊 Courses: {stats_histo['courses']:,}")
    print(f"   🐴 Partants: {stats_histo['partants']:,}")
    print(f"   🏇 Chevaux: {stats_histo['chevaux']:,}")
    
    if stats_histo['errors']:
        print(f"   ⚠️  Erreurs: {len(stats_histo['errors'])}")
        
except Exception as e:
    print(f"❌ Erreur import historique: {e}")
    print("Continuons avec le fichier du jour...")

print()
print("="*60)
print()

# 2. Import du jour
print("🔄 ÉTAPE 2/2 : Import des courses du jour")
print("-" * 60)

try:
    stats_jour = import_any_csv('export_turfbzh_20260116.csv')
    
    print(f"\n✅ COURSES DU JOUR IMPORTÉES")
    print(f"   📊 Courses: {stats_jour['courses']:,}")
    print(f"   🐴 Partants: {stats_jour['partants']:,}")
    print(f"   🏇 Chevaux: {stats_jour['chevaux']:,}")
    
    if stats_jour['errors']:
        print(f"   ⚠️  Erreurs: {len(stats_jour['errors'])}")
        
except Exception as e:
    print(f"❌ Erreur import du jour: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("📊 STATISTIQUES FINALES DE LA BASE")
print("="*60)

# Stats finales
db = get_turf_database()

queries = {
    'Courses': "SELECT COUNT(*) FROM courses",
    'Chevaux': "SELECT COUNT(*) FROM chevaux",
    'Drivers': "SELECT COUNT(*) FROM drivers",
    'Partants': "SELECT COUNT(*) FROM partants",
    'Réunions': "SELECT COUNT(*) FROM reunions"
}

for label, query in queries.items():
    db.cursor.execute(query)
    count = db.cursor.fetchone()[0]
    print(f"   {label:15} : {count:>8,}")

# Période
db.cursor.execute("SELECT MIN(date), MAX(date) FROM reunions")
debut, fin = db.cursor.fetchone()
print(f"\n   📅 Période : {debut} → {fin}")

# Taille DB
import os
if os.path.exists(db.db_path):
    size_mb = os.path.getsize(db.db_path) / (1024 * 1024)
    print(f"   💾 Taille DB : {size_mb:.2f} MB")

print()
print("✅ IMPORT COMPLET TERMINÉ !")
print()
