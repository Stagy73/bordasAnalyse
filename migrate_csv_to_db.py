"""
🔄 SCRIPT DE MIGRATION CSV → BASE DE DONNÉES
Import automatique de tous les exports historiques
"""

import glob
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from turf_database_complete import get_turf_database


def extract_date_from_filename(filename: str):
    """Extrait la date du nom de fichier"""
    # Format: export_turfbzh_20260116.csv
    try:
        date_str = filename.split('_')[-1].replace('.csv', '')
        return datetime.strptime(date_str, '%Y%m%d').date()
    except:
        return None


def migrate_csv_to_database(csv_directory: str = None, db_path: str = None):
    """
    Migre tous les CSV vers la base de données
    
    Args:
        csv_directory: Dossier contenant les CSV (défaut: dossier courant)
        db_path: Chemin de la DB (défaut: ~/bordasAnalyse/turf_complete.db)
    """
    
    if csv_directory is None:
        csv_directory = os.getcwd()
    
    print("🔄 MIGRATION CSV → BASE DE DONNÉES")
    print("=" * 60)
    
    # Connexion à la base
    db = get_turf_database() if db_path is None else TurfDatabase(db_path)
    
    # Trouver tous les CSV
    csv_pattern = os.path.join(csv_directory, "export_*.csv")
    csv_files = sorted(glob.glob(csv_pattern))
    
    if not csv_files:
        print(f"❌ Aucun fichier CSV trouvé dans {csv_directory}")
        print(f"   Pattern recherché: export_*.csv")
        return
    
    print(f"📁 {len(csv_files)} fichiers CSV trouvés\n")
    
    total_stats = {
        'files_processed': 0,
        'files_success': 0,
        'files_error': 0,
        'total_courses': 0,
        'total_partants': 0,
        'total_chevaux': 0,
        'errors': []
    }
    
    for idx, csv_file in enumerate(csv_files, 1):
        filename = os.path.basename(csv_file)
        date_reunion = extract_date_from_filename(filename)
        
        if date_reunion is None:
            print(f"⚠️  [{idx}/{len(csv_files)}] {filename} - Format date invalide")
            total_stats['files_error'] += 1
            continue
        
        print(f"📥 [{idx}/{len(csv_files)}] {filename} ({date_reunion})")
        
        try:
            # Import du fichier
            stats = db.import_from_csv(csv_file, date_reunion)
            
            # Affichage des stats
            print(f"   ✅ {stats['courses']} courses")
            print(f"   ✅ {stats['partants']} partants")
            print(f"   ✅ {stats['chevaux']} chevaux")
            
            if stats['errors']:
                print(f"   ⚠️  {len(stats['errors'])} erreurs")
                for error in stats['errors'][:3]:  # Max 3 premières erreurs
                    print(f"      - {error}")
            
            # Mise à jour des totaux
            total_stats['files_success'] += 1
            total_stats['total_courses'] += stats['courses']
            total_stats['total_partants'] += stats['partants']
            total_stats['total_chevaux'] += stats['chevaux']
            
        except Exception as e:
            print(f"   ❌ ERREUR: {e}")
            total_stats['files_error'] += 1
            total_stats['errors'].append(f"{filename}: {e}")
        
        total_stats['files_processed'] += 1
        print()
    
    # Résumé final
    print("=" * 60)
    print("📊 RÉSUMÉ DE LA MIGRATION")
    print("=" * 60)
    print(f"✅ Fichiers traités avec succès : {total_stats['files_success']}")
    print(f"❌ Fichiers en erreur         : {total_stats['files_error']}")
    print(f"📝 Total courses importées    : {total_stats['total_courses']}")
    print(f"🐴 Total partants importés    : {total_stats['total_partants']}")
    print(f"🏇 Chevaux créés/mis à jour   : {total_stats['total_chevaux']}")
    
    if total_stats['errors']:
        print(f"\n⚠️  Erreurs détectées:")
        for error in total_stats['errors'][:10]:  # Max 10 erreurs
            print(f"   - {error}")
    
    # Statistiques de la base
    print("\n📈 STATISTIQUES DE LA BASE DE DONNÉES")
    print("=" * 60)
    
    stats_queries = {
        'Hippodromes': "SELECT COUNT(*) FROM hippodromes",
        'Chevaux': "SELECT COUNT(*) FROM chevaux",
        'Drivers': "SELECT COUNT(*) FROM drivers",
        'Entraîneurs': "SELECT COUNT(*) FROM entraineurs",
        'Réunions': "SELECT COUNT(*) FROM reunions",
        'Courses': "SELECT COUNT(*) FROM courses",
        'Partants': "SELECT COUNT(*) FROM partants"
    }
    
    for label, query in stats_queries.items():
        db.cursor.execute(query)
        count = db.cursor.fetchone()[0]
        print(f"   {label:15} : {count:>8,}")
    
    # Période couverte
    db.cursor.execute("""
        SELECT MIN(date), MAX(date) 
        FROM reunions
    """)
    min_date, max_date = db.cursor.fetchone()
    
    if min_date and max_date:
        print(f"\n📅 Période couverte : {min_date} → {max_date}")
    
    # Taille de la base
    if os.path.exists(db.db_path):
        size_mb = os.path.getsize(db.db_path) / (1024 * 1024)
        print(f"💾 Taille de la base : {size_mb:.2f} MB")
    
    print("\n✅ Migration terminée !")
    
    return total_stats


def migrate_single_csv(csv_file: str, db_path: str = None):
    """
    Migre un seul fichier CSV
    
    Args:
        csv_file: Chemin du fichier CSV
        db_path: Chemin de la DB (optionnel)
    """
    
    if not os.path.exists(csv_file):
        print(f"❌ Fichier non trouvé: {csv_file}")
        return None
    
    filename = os.path.basename(csv_file)
    date_reunion = extract_date_from_filename(filename)
    
    if date_reunion is None:
        # Demander la date manuellement
        date_str = input("Date de la réunion (YYYY-MM-DD): ")
        try:
            date_reunion = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            print("❌ Format de date invalide")
            return None
    
    print(f"📥 Import de {filename} ({date_reunion})")
    
    db = get_turf_database() if db_path is None else TurfDatabase(db_path)
    
    try:
        stats = db.import_from_csv(csv_file, date_reunion)
        
        print(f"✅ {stats['courses']} courses importées")
        print(f"✅ {stats['partants']} partants ajoutés")
        print(f"✅ {stats['chevaux']} chevaux créés/mis à jour")
        
        if stats['errors']:
            print(f"⚠️  {len(stats['errors'])} erreurs:")
            for error in stats['errors']:
                print(f"   - {error}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Mode fichier unique
        csv_file = sys.argv[1]
        db_path = sys.argv[2] if len(sys.argv) > 2 else None
        migrate_single_csv(csv_file, db_path)
    else:
        # Mode migration complète
        csv_dir = input("Dossier contenant les CSV (Enter = dossier courant): ").strip()
        if not csv_dir:
            csv_dir = os.getcwd()
        
        migrate_csv_to_database(csv_dir)
