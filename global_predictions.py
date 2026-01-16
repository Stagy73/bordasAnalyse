"""
🎯 SYSTÈME DE PRONOSTIQUE GLOBAL
Génère les pronostiques pour TOUTES les courses du jour en une seule fois
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go


class GlobalPredictionEngine:
    """Moteur de pronostique pour toutes les courses"""
    
    def __init__(self):
        self.weights = {
            'borda': 0.40,
            'elo_cheval': 0.10,
            'elo_jockey': 0.08,
            'elo_entraineur': 0.05,
            'ia_gagnant': 0.06,
            'ia_couple': 0.03,
            'turf_points': 0.04,
            'taux_victoire': 0.03,
            'popularite': 0.03,
            'cote': 0.03
        }
    
    def select_best_borda(self, row, hippodrome, discipline, nb_partants):
        """Sélectionne le meilleur système Borda pour cette course"""
        borda_cols = [col for col in row.index if 'Borda' in col]
        
        # Logique de sélection intelligente
        selected = None
        
        hippo_lower = hippodrome.lower() if pd.notna(hippodrome) else ''
        
        if 'vincennes' in hippo_lower or 'vincenne' in hippo_lower:
            if 8 <= nb_partants < 10:
                selected = 'Borda - trot 8-10 chevaux  vincenne'
            elif 10 <= nb_partants < 12:
                selected = 'Borda - trot 10-12 chevaux  vincenne'
            elif 12 <= nb_partants < 14:
                selected = 'Borda - trot 12-14 chevaux  vincenne'
            elif 14 <= nb_partants < 16:
                selected = 'Borda - trot 14-16 chevaux  vincenne'
            elif nb_partants >= 12:
                selected = 'Borda - monté 12-16 chevaux  vincenne'
        
        elif 'pau' in hippo_lower:
            if discipline == 'A':
                selected = 'Borda - Pau attelé'
            elif discipline == 'M':
                selected = 'Borda - Pau monté'
            else:
                selected = 'Borda - Pau plat'
        
        elif 'cagne' in hippo_lower:
            if discipline == 'A':
                selected = 'Borda - cagne sur mer attelé'
            else:
                selected = 'Borda - cagne sur mer monté'
        
        elif 'deauville' in hippo_lower:
            selected = 'Borda - Deauville galot pcf'
        
        elif 'bousc' in hippo_lower:
            selected = 'Borda - le boucast'
        
        # Fallback
        if not selected or selected not in row.index:
            selected = 'Borda - Borda par Défaut'
        
        return row.get(selected, 0) if selected in row.index else 0
    
    def calculate_horse_score(self, row, hippodrome, discipline, nb_partants, forced_borda=None):
        """
        Calcule le score d'un cheval
        
        Args:
            forced_borda: Nom du système Borda à forcer (sans le préfixe "Borda - ")
        """
        score = 0
        components = {}
        
        # 1. Score Borda (40%)
        if forced_borda:
            # Utiliser le Borda forcé
            borda_col = f"Borda - {forced_borda}"
            borda_raw = row.get(borda_col, 0) if borda_col in row.index else 0
        else:
            # Utiliser la sélection automatique
            borda_raw = self.select_best_borda(row, hippodrome, discipline, nb_partants)
        try:
            borda_raw = float(borda_raw) if pd.notna(borda_raw) else 0
        except:
            borda_raw = 0
        
        borda_normalized = (borda_raw / 300) * 40 if borda_raw > 0 else 0
        score += borda_normalized
        components['Borda'] = round(borda_normalized, 2)
        
        # 2. ELO Combiné (23%)
        elo_score = 0
        if 'ELO_Cheval' in row.index and pd.notna(row['ELO_Cheval']):
            try:
                elo_cheval = float(row['ELO_Cheval'])
                elo_score += ((elo_cheval - 1200) / 600) * 10
            except:
                pass
        
        if 'ELO_Jockey' in row.index and pd.notna(row['ELO_Jockey']):
            try:
                elo_jockey = float(row['ELO_Jockey'])
                elo_score += ((elo_jockey - 1200) / 600) * 8
            except:
                pass
        
        if 'ELO_Entraineur' in row.index and pd.notna(row['ELO_Entraineur']):
            try:
                elo_entraineur = float(row['ELO_Entraineur'])
                elo_score += ((elo_entraineur - 1200) / 600) * 5
            except:
                pass
        
        score += elo_score
        components['ELO'] = round(elo_score, 2)
        
        # 3. IA Prédictions (9%)
        ia_score = 0
        if 'IA_Gagnant' in row.index and pd.notna(row['IA_Gagnant']):
            try:
                ia_gagnant = float(row['IA_Gagnant'])
                ia_score += ia_gagnant * 6
            except:
                pass
        
        if 'IA_Couple' in row.index and pd.notna(row['IA_Couple']):
            try:
                ia_couple = float(row['IA_Couple'])
                ia_score += ia_couple * 3
            except:
                pass
        
        score += ia_score
        components['IA'] = round(ia_score, 2)
        
        # 4. Turf Points (4%)
        tp_score = 0
        if 'Turf Points' in row.index and pd.notna(row['Turf Points']):
            try:
                turf_points = float(row['Turf Points'])
                tp_score = (turf_points / 2000) * 4
            except:
                pass
        
        score += tp_score
        components['TP'] = round(tp_score, 2)
        
        # 5. Taux de victoire (3%)
        tv_score = 0
        if 'Taux Victoire' in row.index and pd.notna(row['Taux Victoire']):
            try:
                taux_victoire = float(str(row['Taux Victoire']).replace(',', '.'))
                tv_score = taux_victoire * 3
            except:
                pass
        
        score += tv_score
        components['TxVict'] = round(tv_score, 2)
        
        # 6. Popularité & Cote BZH (6%)
        pop_score = 0
        if 'Popularite' in row.index and pd.notna(row['Popularite']):
            try:
                popularite = float(row['Popularite'])
                pop_normalized = 1 - (min(popularite, 20) / 20)
                pop_score += pop_normalized * 3
            except:
                pass
        
        # UTILISER COTE BZH en priorité, sinon fallback sur Cote PMU
        cote_used = None
        cote_source = None
        
        # Essayer plusieurs variantes de nom pour Cote BZH
        for col_name in ['Cote BZH', 'cote_bzh', 'CoteBZH', 'Cote_BZH']:
            if col_name in row.index and pd.notna(row[col_name]):
                try:
                    cote_used = float(str(row[col_name]).replace(',', '.'))
                    cote_source = 'BZH'
                    break
                except:
                    pass
        
        # Fallback sur Cote PMU si pas de Cote BZH
        if cote_used is None and 'Cote' in row.index and pd.notna(row['Cote']):
            try:
                cote_used = float(str(row['Cote']).replace(',', '.'))
                cote_source = 'PMU'
            except:
                pass
        
        # Calculer le score basé sur la cote (BZH ou PMU)
        if cote_used is not None:
            if 3 <= cote_used <= 15:
                pop_score += 3
            elif cote_used < 3:
                pop_score += 2
            else:
                pop_score += 1
        
        score += pop_score
        components['Pop'] = round(pop_score, 2)
        if cote_source:
            components['Cote_Source'] = cote_source
        
        # Score final sur 100
        return min(score, 100), components
    
    def generate_all_predictions(self, df, race_config=None):
        """
        Génère les pronostiques pour toutes les courses
        
        Args:
            df: DataFrame avec les données
            race_config: Dict optionnel avec la config manuelle par course
                        Format: {course_id: {'discipline': 'A', 'borda': 'trot 10-12...'}}
        """
        
        # Grouper par course
        courses = df['Course'].unique()
        
        all_predictions = []
        course_summaries = []
        
        for course in courses:
            course_df = df[df['Course'] == course].copy()
            
            # Infos de la course
            hippodrome = course_df['hippodrome'].iloc[0]
            heure = course_df['heure'].iloc[0] if 'heure' in course_df.columns else 'N/A'
            distance = course_df['distance'].iloc[0] if 'distance' in course_df.columns else 'N/A'
            nb_partants = len(course_df)
            
            # Utiliser la config manuelle si disponible
            if race_config and course in race_config:
                discipline = race_config[course]['discipline']
                forced_borda = race_config[course]['borda']
            else:
                discipline = course_df['discipline'].iloc[0]
                forced_borda = None
            
            # Déterminer quel Borda sera utilisé (pour info)
            if forced_borda:
                borda_name = forced_borda
            else:
                sample_row = course_df.iloc[0]
                test_borda = self.select_best_borda(sample_row, hippodrome, discipline, nb_partants)
                
                # Trouver le nom du système utilisé
                borda_name = "Borda par Défaut"
                for col in sample_row.index:
                    if 'Borda' in col:
                        try:
                            if float(sample_row[col]) == float(test_borda):
                                borda_name = col.replace('Borda - ', '')
                                break
                        except:
                            pass
            
            # Calculer les scores pour chaque cheval
            predictions = []
            
            for idx, row in course_df.iterrows():
                score, components = self.calculate_horse_score(
                    row, hippodrome, discipline, nb_partants, forced_borda
                )
                
                # Calculer la confiance (basée sur la variance des composantes)
                # Filtrer uniquement les valeurs numériques
                comp_values = []
                for v in components.values():
                    try:
                        if isinstance(v, (int, float)) and v > 0:
                            comp_values.append(float(v))
                    except:
                        pass
                
                confidence = 100 - (np.std(comp_values) * 20) if len(comp_values) > 2 else 50
                confidence = max(30, min(100, confidence))
                
                predictions.append({
                    'Course': course,
                    'Hippodrome': hippodrome,
                    'Heure': heure,
                    'Distance': distance,
                    'Discipline': discipline,
                    'Numero': row.get('Numero', ''),
                    'Cheval': row.get('Cheval', ''),
                    'Driver': row.get('Driver', ''),
                    'Entraineur': row.get('Entraineur', ''),
                    'Cote': row.get('Cote', 'N/A'),
                    'Score': round(score, 2),
                    'Confiance': round(confidence, 1),
                    **components
                })
            
            # Trier par score
            pred_df = pd.DataFrame(predictions)
            pred_df = pred_df.sort_values('Score', ascending=False).reset_index(drop=True)
            pred_df['Rang'] = range(1, len(pred_df) + 1)
            
            all_predictions.extend(predictions)
            
            # Résumé de la course
            top3 = pred_df.head(3)
            course_summaries.append({
                'Course': course,
                'Hippodrome': hippodrome,
                'Heure': heure,
                'Distance': f"{distance}m" if distance != 'N/A' else 'N/A',
                'Discipline': discipline,
                'Nb_Partants': nb_partants,
                'Borda_Utilisé': borda_name,
                'Top1': f"N°{int(top3.iloc[0]['Numero'])} {top3.iloc[0]['Cheval']}",
                'Score_Top1': top3.iloc[0]['Score'],
                'Top2': f"N°{int(top3.iloc[1]['Numero'])} {top3.iloc[1]['Cheval']}",
                'Top3': f"N°{int(top3.iloc[2]['Numero'])} {top3.iloc[2]['Cheval']}",
                'Confiance_Moy': pred_df['Confiance'].mean()
            })
        
        return pd.DataFrame(all_predictions), pd.DataFrame(course_summaries)


def display_global_predictions():
    """Interface pour les pronostiques globaux"""
    
    st.header("🎯 Pronostiques Globaux - Toutes les Courses")
    st.markdown("Générez les pronostiques pour toutes les courses du jour en un clic !")
    
    # Vérifier qu'on a bien un fichier export avec Borda
    from borda_manager import get_selected_borda_data
    
    df, message = get_selected_borda_data()
    
    if df is None:
        st.error("❌ Aucun export Borda sélectionné")
        st.info("💡 Sélectionnez un export Borda dans la sidebar (section 📊 Exports Borda)")
        return
    
    # Vérifier qu'il y a des colonnes Borda
    borda_cols = [col for col in df.columns if 'Borda' in col]
    if len(borda_cols) == 0:
        st.error("❌ Le fichier sélectionné ne contient pas de scores Borda")
        return
    
    st.success(f"✅ Export Borda chargé: {len(df)} chevaux, {df['Course'].nunique()} courses")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Filtre par date
        dates = df['date'].unique() if 'date' in df.columns else []
        if len(dates) > 0:
            selected_date = st.selectbox("📅 Date:", sorted(dates, reverse=True))
            df = df[df['date'] == selected_date]
    
    with col2:
        # Filtre par hippodrome
        hippos = ['Tous'] + sorted(df['hippodrome'].unique().tolist())
        selected_hippo = st.selectbox("🏟️ Hippodrome:", hippos)
        if selected_hippo != 'Tous':
            df = df[df['hippodrome'] == selected_hippo]
    
    with col3:
        # Nombre de courses
        nb_courses = df['Course'].nunique()
        st.metric("📊 Courses à analyser", nb_courses)
    
    st.markdown("### 💎 Utilisation des Cotes")
    
    with st.expander("ℹ️ Comprendre les cotes BZH vs PMU", expanded=False):
        st.info("""
        **🎯 Cotes BZH** : Utilisées pour calculer les scores et classements  
        - Plus précises pour les pronostiques  
        - Reflètent mieux les vraies chances  
        
        **💰 Cotes PMU** : Affichées pour les rapports estimés  
        - Correspondent aux gains réels du PMU  
        - Mises à jour avec l'import des résultats  
        
        **🔄 Priorité** : Le système utilise automatiquement la cote BZH si disponible, sinon la cote PMU.
        """)
    
    st.markdown("---")
    
    # Configuration avancée
    with st.expander("⚙️ Configuration avancée par course", expanded=False):
        st.markdown("### 🎯 Personnaliser le système Borda par course")
        st.caption("Modifiez la discipline ou le système Borda utilisé pour chaque course")
        
        # Initialiser la config dans session state si nécessaire
        if 'race_config' not in st.session_state:
            st.session_state.race_config = {}
        
        # Afficher toutes les courses avec options
        courses_list = sorted(df['Course'].unique())
        
        for course in courses_list:
            course_data = df[df['Course'] == course].iloc[0]
            
            col1, col2, col3, col4 = st.columns([2, 2, 3, 2])
            
            with col1:
                st.write(f"**{course}**")
                st.caption(f"{course_data['hippodrome']}")
            
            with col2:
                # Sélection de la discipline
                default_disc = course_data['discipline'] if 'discipline' in course_data else 'A'
                disciplines = ['A', 'M', 'P']
                
                selected_disc = st.selectbox(
                    "Discipline",
                    options=disciplines,
                    index=disciplines.index(default_disc) if default_disc in disciplines else 0,
                    key=f"disc_{course}",
                    label_visibility="collapsed"
                )
            
            with col3:
                # Déterminer les Borda disponibles
                borda_options = [col.replace('Borda - ', '') for col in df.columns if 'Borda' in col]
                
                # Borda auto-sélectionné
                nb_part = len(df[df['Course'] == course])
                hippo = course_data['hippodrome']
                
                # Logique de sélection auto
                auto_borda = "Borda par Défaut"
                hippo_lower = hippo.lower() if pd.notna(hippo) else ''
                
                if 'vincennes' in hippo_lower or 'vincenne' in hippo_lower:
                    if selected_disc == 'A':
                        if 8 <= nb_part < 10:
                            auto_borda = "trot 8-10 chevaux  vincenne"
                        elif 10 <= nb_part < 12:
                            auto_borda = "trot 10-12 chevaux  vincenne"
                        elif 12 <= nb_part < 14:
                            auto_borda = "trot 12-14 chevaux  vincenne"
                        else:
                            auto_borda = "trot 14-16 chevaux  vincenne"
                    elif selected_disc == 'M':
                        auto_borda = "monté 12-16 chevaux  vincenne"
                
                elif 'pau' in hippo_lower:
                    if selected_disc == 'A':
                        auto_borda = "Pau attelé"
                    elif selected_disc == 'M':
                        auto_borda = "Pau monté"
                    else:
                        auto_borda = "Pau plat"
                
                elif 'cagne' in hippo_lower:
                    if selected_disc == 'A':
                        auto_borda = "cagne sur mer attelé"
                    else:
                        auto_borda = "cagne sur mer monté"
                
                elif 'deauville' in hippo_lower:
                    auto_borda = "Deauville galot pcf"
                
                elif 'bousc' in hippo_lower:
                    auto_borda = "le boucast"
                
                # Trouver l'index du borda auto
                try:
                    auto_index = borda_options.index(auto_borda)
                except:
                    auto_index = borda_options.index("Borda par Défaut") if "Borda par Défaut" in borda_options else 0
                
                selected_borda = st.selectbox(
                    "Système Borda",
                    options=borda_options,
                    index=auto_index,
                    key=f"borda_{course}",
                    label_visibility="collapsed"
                )
            
            with col4:
                st.caption(f"🏇 {nb_part} partants")
            
            # Sauvegarder la config
            st.session_state.race_config[course] = {
                'discipline': selected_disc,
                'borda': selected_borda
            }
        
        if st.button("💾 Appliquer la configuration", type="secondary"):
            st.success("✅ Configuration sauvegardée pour la génération")
    
    st.markdown("---")
    
    # Bouton de génération
    if st.button("🚀 GÉNÉRER TOUS LES PRONOSTIQUES", type="primary", use_container_width=True):
        with st.spinner("🔄 Analyse de toutes les courses en cours..."):
            engine = GlobalPredictionEngine()
            
            # Récupérer la config si elle existe
            race_config = st.session_state.get('race_config', None)
            
            all_preds, course_summaries = engine.generate_all_predictions(df, race_config)
            
            # Stocker dans session state
            st.session_state['global_predictions'] = all_preds
            st.session_state['course_summaries'] = course_summaries
    
    # Affichage des résultats
    if 'global_predictions' in st.session_state and 'course_summaries' in st.session_state:
        all_preds = st.session_state['global_predictions']
        summaries = st.session_state['course_summaries']
        
        st.success(f"✅ {len(summaries)} courses analysées !")
        
        # Onglets
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Vue d'ensemble",
            "🏆 Détails par course",
            "📊 Analyses",
            "💾 Export"
        ])
        
        with tab1:
            st.subheader("📋 Résumé de toutes les courses")
            
            try:
                # Afficher le tableau des courses
                display_summaries = summaries.copy()
                display_summaries = display_summaries[[
                    'Course', 'Hippodrome', 'Heure', 'Distance', 'Discipline', 'Nb_Partants',
                    'Borda_Utilisé', 'Top1', 'Score_Top1', 'Confiance_Moy'
                ]]
                display_summaries.columns = [
                    'Course', 'Hippodrome', 'Heure', 'Dist.', 'Disc.', 'Part.',
                    'Système Borda', 'Favori', 'Score', 'Conf. %'
                ]
                
                st.dataframe(display_summaries, width="stretch", height=400)
            except Exception as e:
                st.error(f"Erreur d'affichage du tableau: {e}")
                # Afficher un tableau simplifié
                simple_summary = summaries[['Course', 'Heure', 'Top1', 'Score_Top1', 'Confiance_Moy']]
                st.dataframe(simple_summary, width="stretch")
            
            # Stats globales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Courses", len(summaries))
            with col2:
                st.metric("Chevaux", len(all_preds))
            with col3:
                avg_conf = summaries['Confiance_Moy'].mean()
                st.metric("Confiance moyenne", f"{avg_conf:.1f}%")
            with col4:
                high_conf = len(summaries[summaries['Confiance_Moy'] >= 70])
                st.metric("Courses haute confiance", high_conf)
            
            st.markdown("---")
            
            # Résumé des paris recommandés
            st.subheader("💎 Résumé des Paris Recommandés")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🌟 Meilleurs Paris Simples")
                
                # Top 5 simples gagnants
                best_sg = summaries.nlargest(5, 'Score_Top1')[['Course', 'Heure', 'Top1', 'Score_Top1', 'Confiance_Moy']]
                
                for idx, row in best_sg.iterrows():
                    conf_emoji = "🟢" if row['Confiance_Moy'] >= 70 else "🟡" if row['Confiance_Moy'] >= 60 else "🟠"
                    st.markdown(f"""
                    **{row['Course']}** à {row['Heure']}  
                    {conf_emoji} {row['Top1']} - Score: {row['Score_Top1']:.1f} - Conf: {row['Confiance_Moy']:.0f}%
                    """)
                    st.caption("---")
            
            with col2:
                st.markdown("### 🎯 Courses à Privilégier")
                
                # Courses avec meilleure confiance
                best_conf = summaries.nlargest(5, 'Confiance_Moy')[['Course', 'Heure', 'Top1', 'Confiance_Moy']]
                
                for idx, row in best_conf.iterrows():
                    st.markdown(f"""
                    **{row['Course']}** à {row['Heure']}  
                    🎯 {row['Top1']}  
                    Confiance globale: {row['Confiance_Moy']:.0f}%
                    """)
                    st.caption("---")
            
            st.markdown("---")
            
            # Plan de jeu global
            st.subheader("📋 Plan de Jeu Suggéré")
            
            plan_data = []
            
            for idx, row in summaries.iterrows():
                conf = row['Confiance_Moy']
                
                # Déterminer quels paris jouer
                paris = []
                if conf >= 70:
                    paris = ["Simple Gagnant 🌟", "Couplé Gagnant", "Trio"]
                elif conf >= 60:
                    paris = ["Simple Gagnant", "Couplé Placé"]
                elif conf >= 50:
                    paris = ["Simple Placé", "2sur4"]
                elif conf >= 40:
                    paris = ["Multi en 4"]
                else:
                    paris = ["⚠️ À éviter"]
                
                plan_data.append({
                    'Course': row['Course'],
                    'Heure': row['Heure'],
                    'Confiance': f"{conf:.0f}%",
                    'Paris Suggérés': ', '.join(paris),
                    'Favori': row['Top1']
                })
            
            plan_df = pd.DataFrame(plan_data)
            st.dataframe(plan_df, width="stretch", height=400)
        
        with tab2:
            st.subheader("🏆 Pronostiques détaillés par course")
            
            # Sélectionner une course
            courses = sorted(all_preds['Course'].unique())
            selected_course = st.selectbox("Choisir une course:", courses)
            
            course_data = all_preds[all_preds['Course'] == selected_course].sort_values('Score', ascending=False).reset_index(drop=True)
            
            # Infos de la course
            info = course_data.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏟️ Hippodrome", info['Hippodrome'])
            with col2:
                st.metric("🕐 Heure", info['Heure'])
            with col3:
                st.metric("📏 Distance", f"{info['Distance']}m")
            with col4:
                st.metric("👥 Partants", len(course_data))
            
            st.markdown("---")
            
            # Top 5
            st.markdown("### 🏆 TOP 5")
            
            top5 = course_data.head(5)
            
            for position, (idx, row) in enumerate(top5.iterrows(), start=1):
                with st.expander(
                    f"#{position} - N°{int(row['Numero'])} {row['Cheval']} - Score: {row['Score']}/100",
                    expanded=(position == 1)
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📊 Score", f"{row['Score']}/100")
                        st.metric("🎯 Confiance", f"{row['Confiance']}%")
                        st.metric("💰 Cote", row['Cote'])
                    
                    with col2:
                        st.metric("🎲 Borda", f"{row['Borda']}/40")
                        st.metric("⭐ ELO", f"{row['ELO']}/23")
                        st.metric("🤖 IA", f"{row['IA']}/9")
                    
                    with col3:
                        st.write(f"**Driver:** {row['Driver']}")
                        st.write(f"**Entraîneur:** {row['Entraineur']}")
            
            st.markdown("---")
            
            # Nouvelle stratégie de paris avec système intelligent
            from betting_interface import display_betting_interface
            
            course_info_dict = {
                'course': selected_course,
                'hippodrome': info['Hippodrome'],
                'discipline': info['Discipline'],
                'heure': info['Heure'],
                'distance': info['Distance']
            }
            
            display_betting_interface(course_data, course_info_dict)
        
        with tab3:
            st.subheader("📊 Analyses visuelles")
            
            # Distribution des scores
            fig = px.box(
                summaries,
                y='Score_Top1',
                title="Distribution des scores des favoris par course",
                labels={'Score_Top1': 'Score du favori'}
            )
            st.plotly_chart(fig, width="stretch")
            
            # Confiance par hippodrome
            if len(summaries['Hippodrome'].unique()) > 1:
                conf_by_hippo = summaries.groupby('Hippodrome')['Confiance_Moy'].mean().sort_values(ascending=False)
                
                fig = px.bar(
                    x=conf_by_hippo.values,
                    y=conf_by_hippo.index,
                    orientation='h',
                    title="Confiance moyenne par hippodrome",
                    labels={'x': 'Confiance moyenne (%)', 'y': 'Hippodrome'}
                )
                st.plotly_chart(fig, width="stretch")
        
        with tab4:
            st.subheader("💾 Exporter les résultats")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export CSV des prédictions
                csv = all_preds.to_csv(index=False, sep=';')
                st.download_button(
                    label="📥 Télécharger toutes les prédictions (CSV)",
                    data=csv,
                    file_name=f"pronostics_global_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export CSV du résumé
                csv_summary = summaries.to_csv(index=False, sep=';')
                st.download_button(
                    label="📥 Télécharger le résumé (CSV)",
                    data=csv_summary,
                    file_name=f"resume_courses_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
