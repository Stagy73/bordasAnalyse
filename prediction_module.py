"""
Module de Pronostique Automatique pour le Dashboard Turf BZH
À intégrer dans app_turf_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from prediction_engine import TurfPredictionEngine


def display_prediction_module(df):
    """
    Module de pronostique automatique intégré au dashboard
    """
    st.header("🎯 Pronostiques Automatiques")
    
    # Initialiser le moteur de prédiction
    engine = TurfPredictionEngine()
    
    # Configuration
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration Pronostics")
    
    # Sélection de la course
    if 'Course' in df.columns:
        courses_disponibles = df['Course'].unique()
        selected_course = st.sidebar.selectbox(
            "Sélectionner une course:",
            options=sorted(courses_disponibles)
        )
        
        # Filtrer les données pour la course sélectionnée
        course_df = df[df['Course'] == selected_course].copy()
    else:
        st.warning("⚠️ Veuillez d'abord charger un fichier avec des courses")
        return
    
    # Informations sur la course
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        hippodrome = course_df['hippodrome'].iloc[0] if 'hippodrome' in course_df.columns else 'N/A'
        st.metric("🏟️ Hippodrome", hippodrome)
    
    with col2:
        discipline = course_df['discipline'].iloc[0] if 'discipline' in course_df.columns else 'N/A'
        st.metric("🏇 Discipline", discipline)
    
    with col3:
        distance = course_df['distance'].iloc[0] if 'distance' in course_df.columns else 'N/A'
        st.metric("📏 Distance", f"{distance}m" if distance != 'N/A' else 'N/A')
    
    with col4:
        nb_partants = len(course_df)
        st.metric("👥 Partants", nb_partants)
    
    st.markdown("---")
    
    # Générer les prédictions
    if st.button("🚀 GÉNÉRER LES PRONOSTIQUES", type="primary"):
        with st.spinner("🔄 Analyse en cours..."):
            # Préparer les informations de la course
            race_info = {
                'hippodrome': hippodrome,
                'discipline': discipline,
                'distance': distance,
                'nombre_partants': nb_partants
            }
            
            # Générer les prédictions
            predictions = engine.generate_prediction(course_df, race_info)
            
            # Stocker dans session state
            st.session_state['predictions'] = predictions
            st.session_state['race_info'] = race_info
    
    # Afficher les résultats si disponibles
    if 'predictions' in st.session_state:
        predictions = st.session_state['predictions']
        
        st.success("✅ Analyse terminée !")
        
        # 1. TOP 5 PRONOSTIQUES
        st.subheader("🏆 TOP 5 PRONOSTIQUES")
        
        top_5 = predictions.head(5)
        
        for idx, row in top_5.iterrows():
            with st.expander(
                f"#{int(row['Rang_Prono'])} - N°{int(row['Numero'])} {row['Cheval']} - Score: {row['Score_Final']}/100",
                expanded=(idx == 0)
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Score Final", f"{row['Score_Final']}/100")
                    st.metric("🎯 Confiance", f"{row['Confiance']}%")
                    st.metric("💰 Cote", row['Cote'])
                
                with col2:
                    st.metric("🎲 Borda", f"{row['Score_Borda']}/100")
                    st.metric("⭐ ELO", f"{row['Score_ELO']}/100")
                    st.metric("🤖 IA", f"{row['Score_IA']}/100")
                
                with col3:
                    st.metric("📈 Performance", f"{row['Score_Perf']}/100")
                    st.metric("🎯 Stratégie", f"{row['Score_Strat']}/100")
                    st.write(f"**Classification:** {row['Classification']}")
                
                # Graphique radar des scores
                categories = ['Borda', 'ELO', 'IA', 'Perf.', 'Strat.']
                values = [
                    row['Score_Borda'],
                    row['Score_ELO'],
                    row['Score_IA'],
                    row['Score_Perf'],
                    row['Score_Strat']
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=row['Cheval']
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=False,
                    height=300
                )
                st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # 2. TABLEAU COMPLET
        st.subheader("📋 Classement Complet")
        
        # Formater le tableau
        display_df = predictions[[
            'Rang_Prono', 'Numero', 'Cheval', 'Score_Final', 'Confiance',
            'Classification', 'Cote', 'Classement_Actuel'
        ]].copy()
        
        display_df.columns = ['Rang', 'N°', 'Cheval', 'Score', 'Confiance %',
                             'Classification', 'Cote', 'Class. Actuel']
        
        # Colorier selon le score
        def color_score(val):
            if val >= 70:
                return 'background-color: #90EE90'
            elif val >= 60:
                return 'background-color: #FFD700'
            elif val >= 50:
                return 'background-color: #87CEEB'
            else:
                return ''
        
        styled_df = display_df.style.applymap(color_score, subset=['Score'])
        st.dataframe(styled_df, width="stretch", height=400)
        
        st.markdown("---")
        
        # 3. STRATÉGIE DE PARIS
        st.subheader("💎 Stratégie de Paris Recommandée")
        
        strategy = engine.generate_betting_strategy(predictions)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Paris Simples")
            
            # Simple Gagnant
            st.info(f"""
            **Simple Gagnant:**  
            N° **{strategy['simple_gagnant']['cheval']}** - {strategy['simple_gagnant']['nom']}  
            Confiance: {strategy['simple_gagnant']['confiance']:.1f}%  
            Cote estimée: {strategy['simple_gagnant']['cote_estimee']}
            """)
            
            # Simple Placé
            places = ', '.join([f"N°{int(n)}" for n in strategy['simple_place']['chevaux']])
            st.info(f"""
            **Simple Placé:**  
            {places}  
            Confiance moyenne: {strategy['simple_place']['confiance_moyenne']:.1f}%
            """)
        
        with col2:
            st.markdown("### 🎰 Paris Combinés")
            
            # Couplé
            st.success(f"""
            **Couplé Gagnant:**  
            {strategy['couple_gagnant']['combinaison']}  
            Confiance: {strategy['couple_gagnant']['confiance']:.1f}%
            """)
            
            # Trio
            st.success(f"""
            **Trio:**  
            {strategy['trio']['combinaison']}  
            Confiance: {strategy['trio']['confiance']:.1f}%
            """)
        
        # Multi et Quinté
        st.markdown("### 🎲 Paris Complexes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            base_multi = ', '.join([f"N°{int(n)}" for n in strategy['multi']['base']])
            comp_multi = ', '.join([f"N°{int(n)}" for n in strategy['multi']['complements']])
            st.warning(f"""
            **Multi en 4/5:**  
            Base (Top 3): {base_multi}  
            Compléments: {comp_multi}
            """)
        
        with col2:
            quinte_ordre = ' - '.join([f"N°{int(n)}" for n in strategy['quinte']['ordre']])
            st.warning(f"""
            **Quinté+:**  
            Ordre suggéré: {quinte_ordre}
            """)
        
        st.markdown("---")
        
        # 4. GRAPHIQUES D'ANALYSE
        st.subheader("📊 Analyses Visuelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des scores
            fig = px.bar(
                predictions,
                x='Cheval',
                y='Score_Final',
                color='Confiance',
                title="Scores de tous les chevaux",
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Comparaison Score vs Cote
            fig = px.scatter(
                predictions,
                x='Cote',
                y='Score_Final',
                size='Confiance',
                color='Classification',
                hover_data=['Cheval'],
                title="Score vs Cote (taille = confiance)"
            )
            st.plotly_chart(fig, width="stretch")
        
        # Matrice de corrélation des scores
        st.subheader("🔬 Corrélation des Indicateurs")
        
        corr_cols = ['Score_Borda', 'Score_ELO', 'Score_IA', 'Score_Perf', 'Score_Strat']
        corr_matrix = predictions[corr_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            labels=dict(color="Corrélation"),
            x=['Borda', 'ELO', 'IA', 'Perf.', 'Strat.'],
            y=['Borda', 'ELO', 'IA', 'Perf.', 'Strat.'],
            title="Corrélation entre les différents scores",
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        
        # 5. EXPORT DES RÉSULTATS
        st.subheader("💾 Export des Résultats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export CSV
            csv = predictions.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"pronostics_{selected_course}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export Excel
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                predictions.to_excel(writer, sheet_name='Pronostics', index=False)
            
            st.download_button(
                label="📥 Télécharger Excel",
                data=buffer.getvalue(),
                file_name=f"pronostics_{selected_course}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # Synthèse finale
        st.markdown("---")
        st.success(f"""
        ### ✅ Résumé de l'Analyse
        
        **Course:** {selected_course}  
        **Hippodrome:** {hippodrome}  
        **Partants analysés:** {len(predictions)}  
        
        **Recommandation principale:**  
        Jouer le N°{int(strategy['simple_gagnant']['cheval'])} ({strategy['simple_gagnant']['nom']}) 
        en base avec une confiance de {strategy['simple_gagnant']['confiance']:.1f}%
        
        **Stratégie optimale:** Couplé {strategy['couple_gagnant']['combinaison']} 
        + Trio {strategy['trio']['combinaison']}
        """)

