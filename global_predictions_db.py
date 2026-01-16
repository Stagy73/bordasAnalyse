"""
🎯 PRONOSTICS GLOBAUX - VERSION BASE DE DONNÉES
Utilise les scores Borda calculés et stockés dans la DB
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_db_adapter import get_db_adapter
from borda_calculator_db import BordaCalculator


def display_global_predictions():
    """Affiche les pronostics globaux depuis la DB"""
    
    st.header("🎯 Pronostics Globaux - Toutes les Courses")
    
    db_adapter = get_db_adapter()
    calculator = BordaCalculator()
    
    # Sélection de date et réunion
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        target_date = st.date_input(
            "Date des courses",
            value=datetime.now().date(),
            help="Sélectionnez la date pour laquelle générer les pronostics"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Recalculer tous les scores", type="primary"):
            with st.spinner("Calcul en cours..."):
                stats = calculator.calculate_all_today(target_date)
                
                if stats['courses_calculees'] > 0:
                    st.success(f"✅ {stats['courses_calculees']} courses calculées!")
                    st.info(f"📊 {stats['partants_analyses']} partants analysés")
                else:
                    st.warning("Aucune course trouvée pour cette date")
                
                if stats['erreurs']:
                    st.error(f"⚠️ {len(stats['erreurs'])} erreurs")
    
    with col3:
        # Filtre par réunion
        reunions_query = f"""
            SELECT DISTINCT SUBSTR(c.course_code, 1, 2) as reunion_code
            FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            WHERE r.date = '{target_date}'
            ORDER BY reunion_code
        """
        reunions_df = pd.read_sql_query(reunions_query, calculator.db.conn)
        
        reunion_options = ['Toutes'] + reunions_df['reunion_code'].tolist()
        selected_reunion = st.selectbox("Réunion", reunion_options)
    
    st.markdown("---")
    
    # Récupérer les courses de la date
    query = f"""
        SELECT 
            c.course_code,
            c.heure,
            h.nom as hippodrome,
            c.discipline,
            c.distance,
            c.nombre_partants
        FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
        WHERE r.date = '{target_date}'
    """
    
    # Filtre par réunion si sélectionné
    if selected_reunion != 'Toutes':
        query += f" AND c.course_code LIKE '{selected_reunion}%'"
    
    query += " ORDER BY c.course_code"
    
    courses_df = pd.read_sql_query(query, calculator.db.conn)
    
    if courses_df.empty:
        st.warning(f"⚠️ Aucune course trouvée pour le {target_date}")
        st.info("💡 Importez un fichier CSV pour cette date")
        return
    
    st.success(f"📊 {len(courses_df)} courses trouvées pour le {target_date}" + 
               (f" - Réunion {selected_reunion}" if selected_reunion != 'Toutes' else ""))
    
    # Options d'affichage
    with st.expander("⚙️ Options d'affichage", expanded=False):
        show_top = st.slider("Nombre de chevaux par course", 3, 10, 5)
        show_details = st.checkbox("Afficher les détails", value=False)
    
    # Afficher chaque course
    for idx, course in courses_df.iterrows():
        with st.container():
            st.markdown(f"### 🏇 {course['course_code']} - {course['hippodrome']}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("⏰ Heure", course['heure'] or "N/A")
            with col2:
                st.metric("🏁 Discipline", course['discipline'] or "N/A")
            with col3:
                st.metric("📏 Distance", f"{course['distance']}m" if course['distance'] else "N/A")
            with col4:
                st.metric("👥 Partants", course['nombre_partants'])
            
            # Récupérer les scores Borda
            scores_df = calculator.get_borda_scores_for_course(course['course_code'], 'default', target_date)
            
            if scores_df.empty:
                st.warning("⚠️ Scores Borda non calculés pour cette course")
                if st.button(f"Calculer maintenant", key=f"calc_{course['course_code']}"):
                    with st.spinner("Calcul..."):
                        df = calculator.calculate_borda_for_course(course['course_code'], date_course=target_date)
                        if df is not None:
                            calculator.save_borda_scores(course['course_code'], df, 'default', target_date)
                            st.success("✅ Scores calculés!")
                            st.rerun()
                continue
            
            # Afficher le TOP N
            top_horses = scores_df.head(show_top).copy()
            
            # Formater pour l'affichage
            top_horses['Score'] = top_horses['score_total'].round(2)
            top_horses['Cote PMU'] = top_horses['cote_pmu'].fillna(0).round(2)
            top_horses['Cote BZH'] = top_horses['cote_bzh'].fillna(0).round(2)
            
            display_cols = ['rang', 'numero', 'cheval', 'driver', 'Score', 'Cote PMU', 'Cote BZH']
            
            st.dataframe(
                top_horses[display_cols],
                use_container_width=True,
                hide_index=True
            )
            
            # Pronostic formaté
            top_5_numeros = top_horses.head(5)['numero'].tolist()
            prono_str = "-".join(map(str, top_5_numeros))
            
            # Section paris avec checkboxes
            st.markdown("### 💰 Sélectionner vos paris")
            
            col_bet1, col_bet2, col_bet3, col_bet4 = st.columns(4)
            
            with col_bet1:
                simple_gagnant = st.checkbox(
                    f"🎯 Simple Gagnant", 
                    key=f"sg_{course['course_code']}",
                    help=f"Miser sur n°{top_5_numeros[0]} gagnant"
                )
                if simple_gagnant:
                    mise_sg = st.number_input(
                        "Mise (€)", 
                        min_value=1.0, 
                        value=2.0, 
                        step=1.0,
                        key=f"mise_sg_{course['course_code']}"
                    )
                    st.info(f"🎯 **N°{top_5_numeros[0]}** - Cote: {top_horses.iloc[0]['Cote PMU']}")
            
            with col_bet2:
                simple_place = st.checkbox(
                    f"📍 Simple Placé", 
                    key=f"sp_{course['course_code']}",
                    help=f"Miser sur n°{top_5_numeros[0]} placé"
                )
                if simple_place:
                    mise_sp = st.number_input(
                        "Mise (€)", 
                        min_value=1.0, 
                        value=2.0, 
                        step=1.0,
                        key=f"mise_sp_{course['course_code']}"
                    )
                    st.info(f"📍 **N°{top_5_numeros[0]}** placé")
            
            with col_bet3:
                couple = st.checkbox(
                    f"👥 Couplé", 
                    key=f"cp_{course['course_code']}",
                    help=f"Couplé: {top_5_numeros[0]}-{top_5_numeros[1]}"
                )
                if couple:
                    mise_cp = st.number_input(
                        "Mise (€)", 
                        min_value=1.0, 
                        value=3.0, 
                        step=1.0,
                        key=f"mise_cp_{course['course_code']}"
                    )
                    ordre_couple = st.radio(
                        "Type",
                        ["Gagnant", "Placé", "Ordre"],
                        horizontal=True,
                        key=f"ordre_cp_{course['course_code']}"
                    )
                    st.info(f"👥 **{top_5_numeros[0]}-{top_5_numeros[1]}** ({ordre_couple})")
            
            with col_bet4:
                trio = st.checkbox(
                    f"🎲 Trio", 
                    key=f"tr_{course['course_code']}",
                    help=f"Trio: {top_5_numeros[0]}-{top_5_numeros[1]}-{top_5_numeros[2]}"
                )
                if trio:
                    mise_tr = st.number_input(
                        "Mise (€)", 
                        min_value=1.0, 
                        value=5.0, 
                        step=1.0,
                        key=f"mise_tr_{course['course_code']}"
                    )
                    ordre_trio = st.radio(
                        "Type",
                        ["Ordre", "Désordre"],
                        horizontal=True,
                        key=f"ordre_tr_{course['course_code']}"
                    )
                    st.info(f"🎲 **{'-'.join(map(str, top_5_numeros[:3]))}** ({ordre_trio})")
            
            # Bouton sauvegarder les paris
            if simple_gagnant or simple_place or couple or trio:
                if st.button(f"💾 Sauvegarder ces paris", key=f"save_{course['course_code']}"):
                    # TODO: Sauvegarder dans une table paris
                    st.success(f"✅ Paris sauvegardés pour {course['course_code']}")
            
            # Afficher pronostic simple
            st.info(f"🎯 **PRONOSTIC SIMPLE:** {prono_str}")
            
            # Détails
            if show_details:
                with st.expander("📊 Détails des scores"):
                    for _, horse in top_horses.iterrows():
                        st.write(f"**N°{horse['numero']} - {horse['cheval']}**")
                        if pd.notna(horse['details']):
                            import json
                            try:
                                details = json.loads(horse['details'])
                                st.json(details)
                            except:
                                st.write("Détails non disponibles")
            
            st.markdown("---")
    
    # Export des pronostics
    st.markdown("### 📥 Export des pronostics")
    
    if st.button("💾 Télécharger tous les pronostics (CSV)"):
        # Générer CSV avec tous les pronostics
        all_pronos = []
        
        for _, course in courses_df.iterrows():
            scores_df = calculator.get_borda_scores_for_course(course['course_code'], 'default', target_date)
            if not scores_df.empty:
                top_5 = scores_df.head(5)
                prono = "-".join(map(str, top_5['numero'].tolist()))
                
                all_pronos.append({
                    'Course': course['course_code'],
                    'Hippodrome': course['hippodrome'],
                    'Heure': course['heure'],
                    'Pronostic': prono,
                    'Confiance': top_5['score_total'].mean().round(2)
                })
        
        if all_pronos:
            export_df = pd.DataFrame(all_pronos)
            csv = export_df.to_csv(index=False, sep=';')
            
            st.download_button(
                "📥 Télécharger",
                csv,
                f"pronostics_{target_date}.csv",
                "text/csv"
            )


if __name__ == "__main__":
    # Pour test standalone
    st.set_page_config(page_title="Pronostics", layout="wide")
    display_global_predictions()
