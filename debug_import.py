#!/usr/bin/env python3
"""
🔍 DEBUG IMPORT - Trouve où ça plante
"""

from universal_importer import UniversalCSVImporter
from datetime import date
import traceback

print("🔍 DEBUG IMPORT DU 16/01")
print("="*60)

importer = UniversalCSVImporter()

# Import avec debug complet
import pandas as pd

csv_path = 'export_turfbzh_20260116.csv'
df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig', decimal=',')

print(f"📊 {len(df)} lignes dans le CSV")
print(f"📋 Colonnes: {list(df.columns)[:10]}...")

# Test sur UNE SEULE course
test_course = df[df['Course'] == 'R1C1'].copy()
print(f"\n🧪 TEST sur R1C1 : {len(test_course)} partants")

try:
    # Hippodrome
    hippodrome_nom = test_course['hippodrome'].iloc[0]
    print(f"   Hippodrome: {hippodrome_nom}")
    
    hippodrome_id = importer.db.get_or_create_hippodrome(hippodrome_nom)
    print(f"   ✅ Hippodrome ID: {hippodrome_id}")
    
    # Date
    date_str = test_course['date'].iloc[0]
    date_course = pd.to_datetime(date_str).date()
    print(f"   Date: {date_course}")
    
    # Réunion
    reunion_code = 'R1'
    reunion_id = importer.db.get_or_create_reunion(reunion_code, date_course, hippodrome_id)
    print(f"   ✅ Réunion ID: {reunion_id}")
    
    # Course
    course_code = 'R1C1'
    
    # Vérifier si course existe déjà
    importer.db.cursor.execute("SELECT id FROM courses WHERE course_code = ? AND reunion_id = ?", (course_code, reunion_id))
    existing = importer.db.cursor.fetchone()
    
    if existing:
        print(f"   ⚠️  Course existe déjà : ID {existing[0]}")
        course_id = existing[0]
    else:
        discipline = test_course['discipline'].iloc[0]
        distance = int(test_course['distance'].iloc[0])
        heure = test_course['heure'].iloc[0]
        
        course_id = importer.db.create_course(
            course_code=course_code,
            reunion_id=reunion_id,
            numero_course=1,
            heure=heure,
            discipline=discipline,
            distance=distance,
            nombre_partants=len(test_course)
        )
        print(f"   ✅ Course créée : ID {course_id}")
    
    # Partants - UN PAR UN
    print(f"\n🐴 Création des partants:")
    for idx, row in test_course.iterrows():
        try:
            numero = int(row['Numero'])
            cheval_nom = row['Cheval']
            
            print(f"   Partant {numero} - {cheval_nom}...")
            
            # Cheval
            cheval_id = importer.db.get_or_create_cheval(cheval_nom)
            print(f"      Cheval ID: {cheval_id}")
            
            # Driver
            driver_nom = row.get('Driver')
            driver_id = None
            if pd.notna(driver_nom):
                driver_id = importer.db.get_or_create_driver(driver_nom)
                print(f"      Driver ID: {driver_id}")
            
            # Créer partant
            partant_id = importer.db.create_partant(
                course_id=course_id,
                cheval_id=cheval_id,
                driver_id=driver_id,
                numero=numero,
                cote_pmu=importer.safe_float(row.get('Cote')),
                cote_bzh=importer.safe_float(row.get('Cote BZH'))
            )
            
            print(f"      ✅ Partant créé : ID {partant_id}")
            
        except Exception as e:
            print(f"      ❌ ERREUR : {e}")
            traceback.print_exc()
            break
    
    importer.db.conn.commit()
    print(f"\n✅ Commit réussi")
    
    # Vérifier
    importer.db.cursor.execute("""
        SELECT COUNT(*) FROM partants p
        WHERE p.course_id = ?
    """, (course_id,))
    
    nb_partants = importer.db.cursor.fetchone()[0]
    print(f"\n📊 Partants créés dans la DB: {nb_partants}")
    
except Exception as e:
    print(f"\n❌ ERREUR GLOBALE : {e}")
    traceback.print_exc()

print("\n" + "="*60)
