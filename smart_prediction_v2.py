"""
🎯 SYSTÈME DE PRONOSTIQUE INTELLIGENT V2
Fusionne fichier quotidien + scores Borda de l'export complet
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class SmartPredictionSystem:
    """Système qui combine fichier quotidien et export Borda"""
    
    def __init__(self):
        self.export_file_path = None
        self.borda_data = None
    
    def load_borda_export(self, file_path):
        """Charge le fichier export avec les scores Borda"""
        try:
            df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
            self.borda_data = df
            self.export_file_path = file_path
            return True, f"✅ Export Borda chargé: {len(df)} lignes"
        except Exception as e:
            return False, f"❌ Erreur: {e}"
    
    def match_horses(self, daily_df, race_info):
        """
        Associe les chevaux du fichier quotidien avec leurs scores Borda
        
        Matching par:
        1. Nom du cheval
        2. Numéro de cheval
        3. Date + hippodrome + course
        """
        if self.borda_data is None:
            return None, "❌ Fichier export Borda non chargé"
        
        # Extraire les informations de matching
        date = race_info.get('date', None)
        hippodrome = race_info.get('hippodrome', None)
        course_num = race_info.get('course', None)
        
        # Filtrer les données Borda pour cette course
        borda_filtered = self.borda_data.copy()
        
        if date:
            borda_filtered = borda_filtered[borda_filtered['date'] == date]
        
        if hippodrome:
            # Matching flexible sur l'hippodrome
            borda_filtered = borda_filtered[
                borda_filtered['hippodrome'].str.contains(hippodrome, case=False, na=False)
            ]
        
        if course_num:
            borda_filtered = borda_filtered[
                borda_filtered['Course'].str.contains(course_num, case=False, na=False)
            ]
        
        # Fusionner les données
        merged_data = []
        
        for idx, daily_row in daily_df.iterrows():
            # Extraire le nom du cheval du fichier quotidien
            cheval_name = daily_row.get('CHEVAL/MUSIQ.', '').split('\n')[0] if 'CHEVAL/MUSIQ.' in daily_row else ''
            numero = daily_row.get('N°', '')
            
            # Chercher le cheval dans les données Borda
            borda_match = None
            
            # Essayer par nom
            if cheval_name:
                potential_matches = borda_filtered[
                    borda_filtered['Cheval'].str.upper() == cheval_name.upper()
                ]
                if len(potential_matches) > 0:
                    borda_match = potential_matches.iloc[0]
            
            # Essayer par numéro si pas trouvé par nom
            if borda_match is None and numero:
                potential_matches = borda_filtered[
                    borda_filtered['Numero'] == numero
                ]
                if len(potential_matches) > 0:
                    borda_match = potential_matches.iloc[0]
            
            # Créer la ligne fusionnée
            merged_row = daily_row.to_dict()
            
            if borda_match is not None:
                # Ajouter tous les scores Borda
                borda_cols = [col for col in borda_match.index if 'Borda' in col]
                for col in borda_cols:
                    merged_row[col] = borda_match[col]
                
                # Ajouter autres infos utiles
                merged_row['_has_borda'] = True
                merged_row['_match_quality'] = 'excellent'
            else:
                merged_row['_has_borda'] = False
                merged_row['_match_quality'] = 'aucun'
            
            merged_data.append(merged_row)
        
        result_df = pd.DataFrame(merged_data)
        
        # Stats de matching
        matched = result_df['_has_borda'].sum()
        total = len(result_df)
        match_rate = (matched / total * 100) if total > 0 else 0
        
        return result_df, f"✅ {matched}/{total} chevaux associés ({match_rate:.0f}%)"
    
    def calculate_smart_score(self, row, race_info):
        """
        Calcule un score intelligent en combinant TOUTES les données disponibles
        """
        score = 0
        confidence = 0
        components = {}
        
        # 1. SCORES BORDA (35% si disponible)
        borda_score = 0
        if row.get('_has_borda', False):
            # Sélectionner le meilleur Borda pour cette course
            borda_cols = [col for col in row.index if 'Borda' in str(col)]
            borda_values = [row[col] for col in borda_cols if not pd.isna(row[col])]
            
            if borda_values:
                borda_score = max(borda_values) / 300 * 35  # Normaliser sur 35
                confidence += 20
        
        components['Borda'] = borda_score
        score += borda_score
        
        # 2. ELO COMBINÉ (25%)
        elo_score = 0
        elo_cols = {
            'CHEVAL': 0.10,
            'JOCKEY': 0.08,
            'COACH': 0.05,
            'PROPRIO': 0.01,
            'ÉLEVEUR': 0.01
        }
        
        for col_name, weight in elo_cols.items():
            if col_name in row.index and not pd.isna(row[col_name]):
                normalized = (row[col_name] - 1200) / 600  # Normaliser ELO
                elo_score += normalized * weight * 100
                confidence += 5
        
        components['ELO'] = elo_score
        score += elo_score
        
        # 3. PRÉDICTIONS IA (20%)
        ia_score = 0
        ia_cols = ['Gagnant', 'Couplé', 'Trio', 'Multi', 'Quinté']
        ia_weights = [0.08, 0.05, 0.04, 0.02, 0.01]
        
        for col_name, weight in zip(ia_cols, ia_weights):
            if col_name in row.index and not pd.isna(row[col_name]):
                ia_score += row[col_name] * weight * 100
                confidence += 3
        
        components['IA'] = ia_score
        score += ia_score
        
        # 4. TURF POINTS (10%)
        tp_score = 0
        if 'TP' in row.index and not pd.isna(row['TP']):
            tp_normalized = row['TP'] / 2000  # Normaliser TP
            tp_score = tp_normalized * 10
            confidence += 10
        
        components['TurfPoints'] = tp_score
        score += tp_score
        
        # 5. POPULARITÉ & COTE (10%)
        pop_score = 0
        if 'Popularité' in row.index and not pd.isna(row['Popularité']):
            # Plus la popularité est basse (1 = meilleur), plus le score est élevé
            pop_normalized = 1 - (row['Popularité'] / 20)  # Normaliser sur 20
            pop_score = pop_normalized * 5
            confidence += 5
        
        if 'COTE' in row.index and not pd.isna(row['COTE']):
            # Favoriser cotes moyennes (3-15)
            cote = row['COTE']
            if 3 <= cote <= 15:
                pop_score += 5
            elif cote < 3:
                pop_score += 3
            else:
                pop_score += 2
            confidence += 5
        
        components['Popularité'] = pop_score
        score += pop_score
        
        # Ajuster la confiance (max 100)
        confidence = min(confidence, 100)
        
        return score, confidence, components


def display_smart_prediction(daily_file, export_file=None):
    """Interface pour le système de pronostique intelligent"""
    
    st.header("🎯 Pronostique Intelligent")
    st.markdown("Combine fichier quotidien + scores Borda de l'export")
    
    # Initialiser le système
    if 'prediction_system' not in st.session_state:
        st.session_state.prediction_system = SmartPredictionSystem()
    
    system = st.session_state.prediction_system
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Fichier Quotidien")
        if daily_file is not None:
            st.success(f"✅ Chargé: {len(daily_file)} chevaux")
        else:
            st.warning("⚠️ Aucun fichier quotidien chargé")
    
    with col2:
        st.subheader("📊 Export Borda")
        
        # Importer le gestionnaire
        from borda_manager import get_selected_borda_data
        
        # Récupérer l'export sélectionné depuis le gestionnaire
        borda_df, message = get_selected_borda_data()
        
        if borda_df is not None:
            system.borda_data = borda_df
            st.success(f"✅ Export Borda chargé: {len(borda_df)} lignes")
        else:
            st.info("💡 Sélectionnez un export Borda dans la sidebar")
            st.caption("Utilisez le gestionnaire d'exports Borda ci-dessous pour ajouter vos fichiers")
    
    st.markdown("---")
    
    # Bouton de génération
    if daily_file is None:
        st.warning("⚠️ Veuillez charger un fichier quotidien")
        return
    
    if system.borda_data is None:
        st.warning("⚠️ Veuillez charger le fichier export Borda")
        return
    
    # Extraire infos de la course depuis le fichier quotidien
    race_info = {
        'date': pd.Timestamp.now().strftime('%Y-%m-%d'),  # À ajuster
        'hippodrome': '',  # À extraire du fichier
        'course': ''  # À extraire du fichier
    }
    
    if st.button("🚀 GÉNÉRER LE PRONOSTIQUE", type="primary"):
        with st.spinner("🔄 Analyse en cours..."):
            # Fusionner les données
            merged_df, match_message = system.match_horses(daily_file, race_info)
            
            st.info(match_message)
            
            if merged_df is None:
                st.error("❌ Impossible de fusionner les données")
                return
            
            # Calculer les scores
            predictions = []
            
            for idx, row in merged_df.iterrows():
                score, confidence, components = system.calculate_smart_score(row, race_info)
                
                cheval = row.get('CHEVAL/MUSIQ.', 'N/A').split('\n')[0] if 'CHEVAL/MUSIQ.' in row else 'N/A'
                numero = row.get('N°', idx + 1)
                cote = row.get('COTE', 'N/A')
                
                predictions.append({
                    'Rang': 0,  # À calculer après tri
                    'N°': numero,
                    'Cheval': cheval,
                    'Score': round(score, 2),
                    'Confiance': round(confidence, 1),
                    'Borda': round(components.get('Borda', 0), 1),
                    'ELO': round(components.get('ELO', 0), 1),
                    'IA': round(components.get('IA', 0), 1),
                    'TP': round(components.get('TurfPoints', 0), 1),
                    'Pop': round(components.get('Popularité', 0), 1),
                    'Cote': cote,
                    'Has_Borda': '✅' if row.get('_has_borda', False) else '❌'
                })
            
            pred_df = pd.DataFrame(predictions)
            pred_df = pred_df.sort_values('Score', ascending=False).reset_index(drop=True)
            pred_df['Rang'] = range(1, len(pred_df) + 1)
            
            # Stocker dans session state
            st.session_state['predictions'] = pred_df
    
    # Afficher les résultats
    if 'predictions' in st.session_state:
        pred_df = st.session_state['predictions']
        
        st.success("✅ Pronostique généré !")
        
        # Top 5
        st.subheader("🏆 TOP 5 PRONOSTIQUES")
        
        top5 = pred_df.head(5)
        
        for idx, row in top5.iterrows():
            with st.expander(
                f"#{int(row['Rang'])} - N°{int(row['N°'])} {row['Cheval']} - Score: {row['Score']}/100",
                expanded=(idx == 0)
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Score Final", f"{row['Score']}/100")
                    st.metric("🎯 Confiance", f"{row['Confiance']}%")
                    st.metric("💰 Cote", row['Cote'])
                
                with col2:
                    st.metric("🎲 Borda", f"{row['Borda']}/35")
                    st.metric("⭐ ELO", f"{row['ELO']}/25")
                    st.metric("🤖 IA", f"{row['IA']}/20")
                
                with col3:
                    st.metric("📈 TP", f"{row['TP']}/10")
                    st.metric("🎯 Pop", f"{row['Pop']}/10")
                    st.write(f"**Borda trouvé:** {row['Has_Borda']}")
        
        st.markdown("---")
        
        # Tableau complet
        st.subheader("📋 Classement Complet")
        st.dataframe(pred_df, width="stretch")
        
        # Stratégie
        st.subheader("💎 Stratégie Recommandée")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Simple Gagnant:**  
            N° **{int(pred_df.iloc[0]['N°'])}** - {pred_df.iloc[0]['Cheval']}  
            Confiance: {pred_df.iloc[0]['Confiance']}%
            """)
        
        with col2:
            st.success(f"""
            **Couplé:**  
            {int(pred_df.iloc[0]['N°'])}-{int(pred_df.iloc[1]['N°'])}  
            Confiance: {(pred_df.iloc[0]['Confiance'] + pred_df.iloc[1]['Confiance']) / 2:.1f}%
            """)
