"""
🎯 INTERFACE DE SÉLECTION DES PARIS + ROI TRACKING
Module complet pour sélectionner, sauvegarder et analyser les paris
"""

import streamlit as st
import pandas as pd
from betting_system_v2 import BettingRecommendationEngine, ROITracker
from datetime import datetime


def display_betting_interface(course_data, course_info):
    """
    Interface complète de sélection et suivi des paris
    
    Args:
        course_data: DataFrame avec les prédictions
        course_info: Dict avec infos de la course (course, hippodrome, discipline, etc.)
    """
    
    # Debug
    st.write(f"🔍 DEBUG: Interface appelée pour {course_info['course']}")
    st.write(f"📊 Nombre de chevaux: {len(course_data)}")
    
    # Initialiser les systèmes
    if 'betting_engine' not in st.session_state:
        st.session_state.betting_engine = BettingRecommendationEngine()
    
    if 'roi_tracker' not in st.session_state:
        st.session_state.roi_tracker = ROITracker()
    
    engine = st.session_state.betting_engine
    tracker = st.session_state.roi_tracker
    
    st.markdown("### 💎 Stratégie de Paris Recommandée")
    
    # Générer les recommandations
    confidence = course_data['Confiance'].mean()
    
    st.write(f"🎯 Confiance moyenne: {confidence:.1f}%")
    
    try:
        recommendations = engine.generate_betting_recommendations(
            course_data,
            course_info['hippodrome'],
            course_info['discipline'],
            confidence
        )
        
        st.write(f"✅ {len(recommendations)} recommandations générées")
        
    except Exception as e:
        st.error(f"❌ Erreur génération: {e}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    if len(recommendations) == 0:
        st.warning("⚠️ Confiance insuffisante pour recommander des paris sûrs")
        return
    
    # Afficher les statistiques ROI globales
    with st.expander("📊 Statistiques ROI Globales", expanded=False):
        stats = tracker.get_statistics()
        
        if stats:
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Paris", stats['total_paris'])
            with col2:
                st.metric("Total Misé", f"{stats['total_mise']:.2f}€")
            with col3:
                st.metric("Total Gains", f"{stats['total_gains']:.2f}€")
            with col4:
                roi_color = "🟢" if stats['roi'] > 0 else "🔴"
                st.metric("ROI Global", f"{roi_color} {stats['roi']:.1f}%")
            with col5:
                st.metric("Taux Réussite", f"{stats['taux_reussite']:.1f}%")
        else:
            st.info("💡 Aucun pari enregistré pour le moment")
    
    st.markdown("---")
    
    # Initialiser la sélection des paris
    if 'selected_bets' not in st.session_state:
        st.session_state.selected_bets = {}
    
    course_key = course_info['course']
    
    if course_key not in st.session_state.selected_bets:
        st.session_state.selected_bets[course_key] = []
    
    # Trier par priorité
    recommendations.sort(key=lambda x: x['priority'])
    
    # Afficher les recommandations avec CHECKBOXES TRÈS VISIBLES
    st.success(f"✅ {len(recommendations)} types de paris disponibles pour cette course")
    
    st.markdown("### ☑️ Sélectionnez vos paris :")
    
    for idx, bet in enumerate(recommendations):
        bet_id = f"{course_key}_{bet['type']}_{idx}"
        
        # Container avec border coloré
        border_color = "#28a745" if bet['priority'] == 1 else "#007bff" if bet['priority'] == 2 else "#fd7e14"
        
        st.markdown(f"""
        <div style='border: 3px solid {border_color}; border-radius: 10px; padding: 20px; margin: 15px 0; background-color: rgba(255,255,255,0.05);'>
        </div>
        """, unsafe_allow_html=True)
        
        # CHECKBOX ÉNORME ET VISIBLE
        selected = st.checkbox(
            f"**{bet['type']}** - {bet['formula']} - Coût: {bet['cout_total']:.2f}€",
            key=f"bet_select_{bet_id}",
            value=bet_id in st.session_state.selected_bets[course_key],
            help=f"Confiance: {bet['confiance']:.0f}% | Rapport estimé: {bet['rapport_estime']}"
        )
        
        if selected and bet_id not in st.session_state.selected_bets[course_key]:
            st.session_state.selected_bets[course_key].append(bet_id)
        elif not selected and bet_id in st.session_state.selected_bets[course_key]:
            st.session_state.selected_bets[course_key].remove(bet_id)
        
        # Détails du pari en colonnes
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            # Bases
            bases_str = ', '.join([f"N°{n}" for n in bet['bases']])
            st.write(f"**🔵 Bases :** {bases_str}")
            
            # Compléments
            if bet['complements']:
                comp_str = ', '.join([f"N°{n}" for n in bet['complements']])
                st.write(f"**⚪ Compléments :** {comp_str}")
        
        with col2:
            # Chevaux
            st.write("**🐴 Chevaux :**")
            for h in bet['chevaux_details'][:5]:
                role = h.get('role', '')
                if role:
                    st.caption(f"  {role}: N°{h['numero']} {h['nom'][:25]}")
                else:
                    st.caption(f"  N°{h['numero']} {h['nom'][:25]}")
        
        with col3:
            # Métriques
            conf_color = "🟢" if bet['confiance'] >= 60 else "🟡" if bet['confiance'] >= 45 else "🟠"
            st.metric("Confiance", f"{conf_color} {bet['confiance']:.0f}%")
            if bet['nb_combinaisons'] > 1:
                st.caption(f"📊 {bet['nb_combinaisons']} combis")
        
        st.markdown("---")
    
    # Résumé de la sélection
    if len(st.session_state.selected_bets[course_key]) > 0:
        st.markdown("### 📋 Récapitulatif de votre sélection")
        
        selected_recs = [
            bet for idx, bet in enumerate(recommendations)
            if f"{course_key}_{bet['type']}_{idx}" in st.session_state.selected_bets[course_key]
        ]
        
        total_cost = sum(bet['cout_total'] for bet in selected_recs)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **Paris sélectionnés:** {len(selected_recs)}  
            **Coût total:** {total_cost:.2f}€
            """)
        
        with col2:
            if st.button("💾 ENREGISTRER CES PARIS", type="primary", use_container_width=True):
                # Enregistrer les paris
                date_str = datetime.now().strftime('%Y-%m-%d')
                
                for bet in selected_recs:
                    horses_str = f"B:{'-'.join(map(str, bet['bases']))}"
                    if bet['complements']:
                        horses_str += f" / C:{'-'.join(map(str, bet['complements']))}"
                    
                    tracker.add_bet(
                        course=course_info['course'],
                        bet_type=bet['type'],
                        horses=horses_str,
                        cost=bet['cout_total'],
                        date=date_str
                    )
                
                st.success(f"✅ {len(selected_recs)} paris enregistrés avec succès !")
                st.balloons()
                
                # Réinitialiser la sélection
                st.session_state.selected_bets[course_key] = []


def display_roi_analysis():
    """Affiche l'analyse détaillée du ROI"""
    
    st.header("📊 Analyse ROI Détaillée")
    
    if 'roi_tracker' not in st.session_state:
        st.session_state.roi_tracker = ROITracker()
    
    tracker = st.session_state.roi_tracker
    
    if not tracker.bets:
        st.info("💡 Aucun pari enregistré. Commencez à sélectionner des paris dans les pronostiques !")
        return
    
    # Statistiques globales
    stats = tracker.get_statistics()
    
    st.subheader("🎯 Vue d'ensemble")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Paris", stats['total_paris'])
    with col2:
        st.metric("Total Misé", f"{stats['total_mise']:.2f}€")
    with col3:
        st.metric("Total Gains", f"{stats['total_gains']:.2f}€")
    with col4:
        roi_color = "normal" if stats['roi'] > 0 else "inverse"
        st.metric("ROI Global", f"{stats['roi']:.1f}%", delta_color=roi_color)
    with col5:
        st.metric("Taux Réussite", f"{stats['taux_reussite']:.1f}%")
    
    st.markdown("---")
    
    # Historique des paris
    st.subheader("📋 Historique des Paris")
    
    df_bets = pd.DataFrame(tracker.bets)
    
    if len(df_bets) > 0:
        # Filtres
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Statut",
                options=['en_attente', 'termine'],
                default=['en_attente', 'termine']
            )
        
        with col2:
            type_filter = st.multiselect(
                "Type de pari",
                options=df_bets['type'].unique().tolist(),
                default=df_bets['type'].unique().tolist()
            )
        
        with col3:
            date_filter = st.date_input(
                "Date",
                value=None
            )
        
        # Appliquer les filtres
        df_filtered = df_bets[df_bets['status'].isin(status_filter)]
        df_filtered = df_filtered[df_filtered['type'].isin(type_filter)]
        
        # Afficher le tableau
        display_cols = ['date', 'course', 'type', 'horses', 'cout', 'status', 'gains', 'roi']
        
        st.dataframe(
            df_filtered[display_cols].sort_values('date', ascending=False),
            width="stretch",
            height=400
        )
        
        # Actions
        st.markdown("### ⚙️ Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Mettre à jour un résultat
            bet_ids = df_filtered[df_filtered['status'] == 'en_attente']['id'].tolist()
            
            if bet_ids:
                selected_bet = st.selectbox("Pari à mettre à jour", bet_ids)
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    resultat = st.selectbox("Résultat", ['gagnant', 'perdant'])
                
                with col_b:
                    gains = st.number_input("Gains (€)", min_value=0.0, step=0.5)
                
                if st.button("✅ Mettre à jour"):
                    tracker.update_bet_result(selected_bet, resultat, gains)
                    st.success("✅ Pari mis à jour !")
                    st.rerun()
        
        with col2:
            # Export CSV
            csv = df_filtered.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Exporter en CSV",
                data=csv,
                file_name=f"paris_historique_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col3:
            # Réinitialiser
            if st.button("🗑️ Réinitialiser l'historique", type="secondary"):
                if st.session_state.get('confirm_reset'):
                    tracker.bets = []
                    tracker.save_bets()
                    st.success("✅ Historique réinitialisé")
                    st.session_state.pop('confirm_reset')
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("⚠️ Cliquer à nouveau pour confirmer")
        
        st.markdown("---")
        
        # Analyses par type de pari
        st.subheader("📈 Performance par Type de Pari")
        
        termines = df_filtered[df_filtered['status'] == 'termine']
        
        if len(termines) > 0:
            perf_by_type = termines.groupby('type').agg({
                'cout': 'sum',
                'gains': 'sum',
                'roi': 'mean'
            }).reset_index()
            
            perf_by_type.columns = ['Type', 'Total Misé', 'Total Gains', 'ROI Moyen']
            
            # Ajouter le taux de réussite
            success_by_type = termines.groupby('type').apply(
                lambda x: (x['gains'] > 0).sum() / len(x) * 100
            ).reset_index()
            success_by_type.columns = ['Type', 'Taux Réussite (%)']
            
            perf_by_type = perf_by_type.merge(success_by_type, on='Type')
            
            st.dataframe(perf_by_type, width="stretch")
            
            # Graphiques
            import plotly.express as px
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    perf_by_type,
                    x='Type',
                    y='ROI Moyen',
                    title="ROI Moyen par Type de Pari",
                    labels={'ROI Moyen': 'ROI (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.pie(
                    perf_by_type,
                    names='Type',
                    values='Total Misé',
                    title="Répartition des Mises par Type"
                )
                st.plotly_chart(fig, use_container_width=True)
