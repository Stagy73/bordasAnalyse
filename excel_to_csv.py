#!/usr/bin/env python3
"""
Convertisseur Excel → CSV pour les fichiers Turf BZH quotidiens
"""

import pandas as pd
import sys
from pathlib import Path

def convert_excel_to_csv(excel_file):
    """Convertit un fichier Excel en CSV"""
    try:
        # Lire le fichier Excel
        print(f"📂 Lecture de {excel_file}...")
        df = pd.read_excel(excel_file)
        
        # Générer le nom du fichier CSV
        excel_path = Path(excel_file)
        csv_file = excel_path.with_suffix('.csv')
        
        # Sauvegarder en CSV
        print(f"💾 Conversion en CSV...")
        df.to_csv(csv_file, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"✅ Conversion réussie !")
        print(f"📄 Fichier créé: {csv_file}")
        print(f"📊 {len(df)} lignes, {len(df.columns)} colonnes")
        
        return str(csv_file)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 excel_to_csv.py fichier.xlsx")
        print("\nOu glissez-déposez votre fichier Excel sur ce script")
        
        # Mode interactif
        import os
        files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        
        if files:
            print(f"\n📁 Fichiers Excel trouvés dans le dossier actuel:")
            for i, f in enumerate(files, 1):
                print(f"  {i}. {f}")
            
            choice = input("\nNuméro du fichier à convertir (ou Entrée pour tous): ")
            
            if choice.strip():
                excel_file = files[int(choice) - 1]
                convert_excel_to_csv(excel_file)
            else:
                for f in files:
                    print(f"\n{'='*60}")
                    convert_excel_to_csv(f)
        else:
            print("❌ Aucun fichier Excel trouvé dans le dossier actuel")
    else:
        excel_file = sys.argv[1]
        convert_excel_to_csv(excel_file)
