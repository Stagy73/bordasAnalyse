#!/usr/bin/env python3
"""
🔄 TEST IMPORT AVEC LOGS
"""

from turf_database_complete import get_turf_database
from universal_importer import import_any_csv

print("🔄 NETTOYAGE + RÉIMPORT 16/01")
print("="*60)

# 1. Nettoyage
print("\n1️⃣ Nettoyage des données du 16/01...")
db = get_turf_database()

db.cursor.execute('''
    DELETE FROM partants WHERE course_id IN (
        SELECT c.id FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        WHERE r.date = "2026-01-16"
    )
''')

db.cursor.execute('''
    DELETE FROM courses WHERE id IN (
        SELECT c.id FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        WHERE r.date = "2026-01-16"
    )
''')

db.cursor.execute('DELETE FROM reunions WHERE date = "2026-01-16"')
db.conn.commit()

print("   ✅ Nettoyage terminé")

# 2. Import
print("\n2️⃣ Import avec logs détaillés...")
print("-"*60)

stats = import_any_csv('export_turfbzh_20260116.csv')

print("\n" + "-"*60)
print(f"   Stats retournées: {stats['courses']} courses, {stats['partants']} partants")

# 3. Vérification
print("\n3️⃣ Vérification dans la DB...")

db.cursor.execute('''
    SELECT COUNT(*) FROM courses c
    JOIN reunions r ON c.reunion_id = r.id
    WHERE r.date = "2026-01-16"
''')
courses = db.cursor.fetchone()[0]

db.cursor.execute('''
    SELECT COUNT(*) FROM partants p
    JOIN courses c ON p.course_id = c.id
    JOIN reunions r ON c.reunion_id = r.id
    WHERE r.date = "2026-01-16"
''')
partants = db.cursor.fetchone()[0]

print(f"   📊 DB réelle: {courses} courses, {partants} partants")

if partants == 0:
    print("\n❌ ÉCHEC: Aucun partant dans la DB!")
elif partants == stats['partants']:
    print("\n✅ SUCCÈS TOTAL!")
else:
    print(f"\n⚠️  PARTIEL: {partants}/{stats['partants']} partants")

print("\n" + "="*60)
