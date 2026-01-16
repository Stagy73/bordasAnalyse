#!/usr/bin/env python3
"""
📥 IMPORT QUOTIDIEN RAPIDE
Script pour importer facilement le fichier du jour
"""

import sys
import os
from datetime import datetime
from universal_importer import import_any_csv
from turf_database_complete import get_turf_database

def import_today():
    """Import le fichier du jour"""
    
    print("="*60)
    print("📥 IMPORT QUOTIDIEN TURF BZH")
    print("="*60)
    
    # Trouver le fichier du jour automatiquement
    today = datetime.now().strftime("%Y%m%d")
    filename = f"export_turfbzh_{today}.csv"
    
    # Chercher le fichier dans le répertoire courant
    if not os.path.exists(filename):
        print(f"\n❌ Fichier '{filename}' introuvable dans le répertoire courant")
        print("\n💡 Options:")
        print(f"   1. Téléchargez votre export TurfBZH et nommez-le : {filename}")
        print(f"   2. Ou spécifiez le nom du fichier : python3 import_today.py votre_fichier.csv")
        return False
    
    # Import
    print(f"\n📂 Fichier trouvé: {filename}")
    print("\n🔄 Import en cours...\n")
    
    try:
        stats = import_any_csv(filename)
        
        print("\n" + "="*60)
        print("✅ IMPORT RÉUSSI !")
        print("="*60)
        print(f"📊 Courses importées: {stats['courses']}")
        print(f"🐴 Partants importés: {stats['partants']}")
        print(f"🐎 Chevaux ajoutés: {stats['chevaux']}")
        
        if stats.get('errors'):
            print(f"\n⚠️  {len(stats['errors'])} erreurs:")
            for err in stats['errors'][:5]:
                print(f"  - {err}")
        
        # Vérifier la DB
        db = get_turf_database()
        
        db.cursor.execute("SELECT COUNT(*) FROM courses")
        total_courses = db.cursor.fetchone()[0]
        
        db.cursor.execute("SELECT COUNT(*) FROM partants")
        total_partants = db.cursor.fetchone()[0]
        
        print("\n📊 ÉTAT DE LA BASE DE DONNÉES:")
        print(f"   Total courses: {total_courses:,}")
        print(f"   Total partants: {total_partants:,}")
        
        print("\n🎯 PROCHAINE ÉTAPE:")
        print("   Lancez le dashboard: streamlit run app_turf_dashboard.py")
        print("   Puis allez dans 🎯 PRONOSTICS GLOBAUX pour calculer les scores Borda")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'import: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Si un fichier est spécifié en argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        
        if not os.path.exists(filename):
            print(f"❌ Fichier '{filename}' introuvable")
            sys.exit(1)
        
        print(f"📂 Import du fichier: {filename}\n")
        
        try:
            stats = import_any_csv(filename)
            print(f"\n✅ {stats['courses']} courses et {stats['partants']} partants importés")
        except Exception as e:
            print(f"❌ Erreur: {e}")
            sys.exit(1)
    else:
        # Import automatique du fichier du jour
        success = import_today()
        sys.exit(0 if success else 1)
