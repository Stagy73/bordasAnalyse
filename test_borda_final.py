#!/usr/bin/env python3
"""
🎯 TEST FINAL - CALCUL BORDA
"""

from borda_calculator_db import BordaCalculator
from datetime import date

print("="*60)
print("🎯 TEST CALCUL BORDA POUR LE 16/01/2026")
print("="*60)

calculator = BordaCalculator()

print("\n1️⃣ Vérification config 'default'...")
try:
    config_id = calculator._get_config_db_id('default')
    print(f"   ✅ Config 'default' existe (ID: {config_id})")
except:
    print("   ❌ Config 'default' introuvable!")

print("\n2️⃣ Calcul Borda pour R1C1...")
try:
    df = calculator.calculate_borda_for_course('R1C1', date_course=date(2026, 1, 16))
    
    if df is not None and not df.empty:
        print(f"   ✅ {len(df)} partants calculés")
        print(f"   📊 TOP 3:")
        for _, row in df.head(3).iterrows():
            print(f"      {row['rang_borda']}. N°{row['numero']} {row['cheval']}: {row['score_borda']:.2f}")
    else:
        print("   ⚠️  Aucun partant trouvé")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n3️⃣ Sauvegarde des scores...")
try:
    calculator.save_borda_scores('R1C1', df, 'default', date(2026, 1, 16))
    print("   ✅ Scores sauvegardés")
    
    # Vérifier
    calculator.db.cursor.execute('SELECT COUNT(*) FROM borda_scores')
    nb = calculator.db.cursor.fetchone()[0]
    print(f"   📊 Total borda_scores: {nb}")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n4️⃣ Récupération des scores...")
try:
    scores_df = calculator.get_borda_scores_for_course('R1C1', 'default', date(2026, 1, 16))
    
    if not scores_df.empty:
        print(f"   ✅ {len(scores_df)} scores récupérés")
        print(f"   🏆 PRONOSTIC: {'-'.join(map(str, scores_df.head(5)['numero'].tolist()))}")
    else:
        print("   ⚠️  Aucun score trouvé")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "="*60)
print("✅ TEST TERMINÉ")
print("="*60)
