#!/usr/bin/env python3
"""
🎉 TEST FINAL AVEC BUG FIXÉ
"""

from turf_database_complete import get_turf_database
from universal_importer import import_any_csv

print("="*60)
print("🔧 BUG FIXÉ : create_course() retourne maintenant le bon ID")
print("="*60)

db = get_turf_database()

# 1. Nettoyer TOUT ce qui concerne le 16/01
print("\n1️⃣ Nettoyage complet...")

# Supprimer les partants du 16/01 (qui n'existent pas encore normalement)
db.cursor.execute('''
    DELETE FROM partants WHERE course_id IN (
        SELECT c.id FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        WHERE r.date = "2026-01-16"
    )
''')

# Supprimer les courses du 16/01
db.cursor.execute('''
    DELETE FROM courses WHERE id IN (
        SELECT c.id FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        WHERE r.date = "2026-01-16"
    )
''')

# Supprimer les réunions du 16/01
db.cursor.execute('DELETE FROM reunions WHERE date = "2026-01-16"')

db.conn.commit()
print("   ✅ Nettoyage terminé")

# 2. Import avec version corrigée
print("\n2️⃣ Import avec create_course() corrigé...")
print("-"*60)

stats = import_any_csv('export_turfbzh_20260116.csv')

print("-"*60)
print(f"   📊 Stats: {stats['courses']} courses, {stats['partants']} partants")

# 3. Vérification IMMÉDIATE
print("\n3️⃣ Vérification...")

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

print(f"   📊 DB: {courses} courses, {partants} partants")

# 4. Vérif détaillée
if partants > 0:
    print("\n4️⃣ Vérification détaillée...")
    
    db.cursor.execute('''
        SELECT c.course_code, COUNT(p.id)
        FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        LEFT JOIN partants p ON p.course_id = c.id
        WHERE r.date = "2026-01-16"
        GROUP BY c.course_code
        ORDER BY c.course_code
        LIMIT 10
    ''')
    
    print("   📋 Partants par course:")
    for code, nb in db.cursor.fetchall():
        status = "✅" if nb > 0 else "❌"
        print(f"      {status} {code}: {nb} partants")

# 5. Résultat final
print("\n" + "="*60)
if partants == 633:
    print("✅ ✅ ✅ SUCCÈS TOTAL ! ✅ ✅ ✅")
    print(f"   {courses} courses + {partants} partants pour le 16/01/2026")
elif partants > 0:
    print(f"⚠️  PARTIEL: {partants}/633 partants créés")
else:
    print("❌ ÉCHEC: Aucun partant créé")
print("="*60)
