from turf_database_complete import get_turf_database
from datetime import date

print("🔍 Test d'import CSV...")
db = get_turf_database()

try:
    stats = db.import_from_csv('export_turfbzh_20260116.csv', date(2026, 1, 16))
    print("✅ Import réussi!")
    print(f"📊 Courses: {stats['courses']}")
    print(f"🐴 Partants: {stats['partants']}")
    print(f"❌ Erreurs: {stats['errors']}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
