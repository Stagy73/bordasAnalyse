"""
📥 IMPORT DE FICHIERS HISTORIQUES
Format différent du CSV quotidien TurfBZH
"""

from turf_database_complete import get_turf_database
import pandas as pd
from datetime import datetime


def import_historique_csv(csv_path: str):
    """
    Importe un fichier historique avec format différent
    Colonnes: date, course_id, cheval, driver, ordre_arrivee, etc.
    """
    
    print(f"📥 Import fichier historique: {csv_path}")
    
    db = get_turf_database()
    
    # Lire avec format français
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig', decimal=',')
    
    print(f"📊 {len(df)} lignes trouvées")
    print(f"📋 Colonnes: {list(df.columns)[:10]}...")
    
    stats = {
        'courses': 0,
        'partants': 0,
        'chevaux': 0,
        'errors': []
    }
    
    # Fonction de conversion sécurisée
    def safe_float(value):
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
            if value == '' or value == 'None':
                return None
            try:
                return float(value)
            except:
                return None
        return None
    
    try:
        # Grouper par course
        for course_id in df['course_id'].unique():
            if pd.isna(course_id):
                continue
            
            course_df = df[df['course_id'] == course_id].copy()
            
            # Date de la course
            date_str = course_df['date'].iloc[0]
            try:
                date_course = pd.to_datetime(date_str).date()
            except:
                print(f"⚠️  Date invalide pour {course_id}")
                continue
            
            # Hippodrome
            hippodrome_nom = course_df['hippodrome'].iloc[0]
            hippodrome_id = db.get_or_create_hippodrome(hippodrome_nom)
            
            # Réunion (extraire de course_id: ex R1C2 -> R1)
            try:
                reunion_code = course_id[:2]  # R1, R2, etc.
            except:
                reunion_code = "R1"
            
            reunion_id = db.get_or_create_reunion(
                reunion_code, 
                date_course, 
                hippodrome_id
            )
            
            # Course
            try:
                numero_course = int(course_df['numero_course'].iloc[0])
            except:
                numero_course = int(course_id[3:]) if len(course_id) > 3 else 1
            
            course_id_db = db.create_course(
                course_code=course_id,
                reunion_id=reunion_id,
                numero_course=numero_course,
                heure=course_df['heure'].iloc[0] if 'heure' in course_df.columns else None,
                discipline=course_df['discipline'].iloc[0] if 'discipline' in course_df.columns else None,
                distance=int(safe_float(course_df['distance'].iloc[0]) or 0) if 'distance' in course_df.columns else None,
                allocation=safe_float(course_df['montant_prix'].iloc[0]) if 'montant_prix' in course_df.columns else None,
                nombre_partants=int(course_df['nombre_partants'].iloc[0]) if 'nombre_partants' in course_df.columns else len(course_df)
            )
            
            stats['courses'] += 1
            
            # Partants
            for _, row in course_df.iterrows():
                # Cheval
                cheval_nom = row['cheval']
                if pd.isna(cheval_nom):
                    continue
                
                cheval_id = db.get_or_create_cheval(
                    cheval_nom,
                    age=int(row['age']) if 'age' in row and pd.notna(row['age']) else None,
                    sexe=row['sexe'] if 'sexe' in row else None
                )
                stats['chevaux'] += 1
                
                # Driver
                driver_id = None
                if 'driver' in row and pd.notna(row['driver']):
                    driver_id = db.get_or_create_driver(row['driver'])
                
                # Entraîneur
                entraineur_id = None
                if 'entraineur' in row and pd.notna(row['entraineur']):
                    entraineur_id = db.get_or_create_entraineur(row['entraineur'])
                
                # Rang d'arrivée
                rang_arrivee = None
                if 'ordre_arrivee' in row and pd.notna(row['ordre_arrivee']):
                    try:
                        rang_arrivee = int(row['ordre_arrivee'])
                    except:
                        pass
                
                # Créer le partant
                db.cursor.execute("""
                    INSERT OR REPLACE INTO partants
                    (course_id, cheval_id, driver_id, entraineur_id, numero,
                     cote_pmu, musique, rang_arrivee)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course_id_db,
                    cheval_id,
                    driver_id,
                    entraineur_id,
                    int(row['numero']),
                    safe_float(row.get('cote_direct')),
                    row.get('musique'),
                    rang_arrivee
                ))
                
                stats['partants'] += 1
        
        db.conn.commit()
        
    except Exception as e:
        db.conn.rollback()
        stats['errors'].append(str(e))
        import traceback
        traceback.print_exc()
    
    return stats


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 import_historique.py fichier.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    stats = import_historique_csv(csv_file)
    
    print("\n" + "="*60)
    print("📊 RÉSULTAT DE L'IMPORT")
    print("="*60)
    print(f"✅ Courses importées: {stats['courses']}")
    print(f"✅ Partants ajoutés: {stats['partants']}")
    print(f"✅ Chevaux créés: {stats['chevaux']}")
    
    if stats['errors']:
        print(f"\n⚠️  Erreurs: {len(stats['errors'])}")
        for err in stats['errors'][:5]:
            print(f"  - {err}")
    
    print("\n✅ Import terminé!")
