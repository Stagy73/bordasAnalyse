#!/usr/bin/env python3
"""
💰 MODULE INTERFACE DE BETTING
Permet de sélectionner et sauvegarder les paris
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from turf_database_complete import get_turf_database
from borda_calculator_db import BordaCalculator

class BettingInterface:
    """Interface pour sélectionner et gérer les paris"""
    
    def __init__(self):
        self.db = get_turf_database()
        self.calculator = BordaCalculator()
        self._ensure_paris_table()
    
    def _ensure_paris_table(self):
        """Crée la table paris si elle n'existe pas"""
        self.db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS paris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                type_pari TEXT NOT NULL,
                numeros TEXT NOT NULL,
                mise REAL NOT NULL,
                option TEXT,
                statut TEXT DEFAULT 'en_attente',
                resultat TEXT,
                gain REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)
        self.db.conn.commit()
    
    def save_pari(self, course_code: str, target_date: date, type_pari: str, 
                  numeros: list, mise: float, option: str = None):
        """Sauvegarde un pari dans la DB"""
        
        # Récupérer course_id
        self.db.cursor.execute("""
            SELECT c.id FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            WHERE c.course_code = ? AND r.date = ?
        """, (course_code, target_date))
        
        result = self.db.cursor.fetchone()
        if not result:
            return False
        
        course_id = result[0]
        
        # Sauvegarder le pari
        self.db.cursor.execute("""
            INSERT INTO paris
            (course_id, type_pari, numeros, mise, option)
            VALUES (?, ?, ?, ?, ?)
        """, (course_id, type_pari, ','.join(map(str, numeros)), mise, option))
        
        self.db.conn.commit()
        return True
    
    def get_paris_for_date(self, target_date: date):
        """Récupère tous les paris pour une date"""
        try:
            query = """
                SELECT 
                    c.course_code,
                    c.heure,
                    h.nom as hippodrome,
                    p.type_pari,
                    p.numeros,
                    p.mise,
                    p.option,
                    p.statut,
                    p.gain
                FROM paris p
                JOIN courses c ON p.course_id = c.id
                JOIN reunions r ON c.reunion_id = r.id
                JOIN hippodromes h ON r.hippodrome_id = h.id
                WHERE r.date = ?
                ORDER BY c.course_code, p.type_pari
            """
            
            return pd.read_sql_query(query, self.db.conn, params=[target_date])
        
        except Exception as e:
            # Si erreur de colonne, peut-être que la table est mal formée
            if "no such column" in str(e):
                # Recréer la table
                self.db.cursor.execute("DROP TABLE IF EXISTS paris")
                self.db.conn.commit()
                self._ensure_paris_table()
            # Retourner DataFrame vide
            return pd.DataFrame()
    
    def display_bet_selection(self, course_code: str, target_date: date, top_horses: pd.DataFrame):
        """Affiche les checkboxes de sélection de paris pour une course"""
        
        if top_horses.empty:
            return
        
        st.markdown("### 💰 Sélectionner vos paris")
        
        # Top 5 numéros
        top_5 = top_horses.head(5)['numero'].tolist()
        all_numeros = top_horses['numero'].tolist()
        
        # Conteneur pour tous les paris
        selected_bets = []
        
        # 4 colonnes pour les 4 types de paris
        col1, col2, col3, col4 = st.columns(4)
        
        # SIMPLE GAGNANT
        with col1:
            sg_key = f"sg_{course_code}_{target_date}"
            simple_gagnant = st.checkbox(
                "🎯 Simple Gagnant",
                key=sg_key,
                help="Miser sur un cheval gagnant"
            )
            
            if simple_gagnant:
                # SÉLECTION DU CHEVAL
                num_sg = st.selectbox(
                    "Cheval",
                    all_numeros,
                    key=f"num_{sg_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                mise_sg = st.number_input(
                    "Mise (€)",
                    min_value=1.0,
                    value=2.0,
                    step=0.5,
                    key=f"mise_{sg_key}"
                )
                
                # Trouver la cote de ce cheval
                horse_row = top_horses[top_horses['numero'] == num_sg]
                if not horse_row.empty:
                    cote = horse_row.iloc[0]['cote_pmu'] if pd.notna(horse_row.iloc[0]['cote_pmu']) else 0
                    st.caption(f"N°{num_sg} - Cote: {cote:.1f}")
                
                selected_bets.append({
                    'type': 'Simple Gagnant',
                    'numeros': [num_sg],
                    'mise': mise_sg,
                    'option': None
                })
        
        # SIMPLE PLACÉ
        with col2:
            sp_key = f"sp_{course_code}_{target_date}"
            simple_place = st.checkbox(
                "📍 Simple Placé",
                key=sp_key,
                help="Miser sur un cheval placé (top 3)"
            )
            
            if simple_place:
                # SÉLECTION DU CHEVAL
                num_sp = st.selectbox(
                    "Cheval",
                    all_numeros,
                    key=f"num_{sp_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                mise_sp = st.number_input(
                    "Mise (€)",
                    min_value=1.0,
                    value=2.0,
                    step=0.5,
                    key=f"mise_{sp_key}"
                )
                
                st.caption(f"N°{num_sp} placé")
                
                selected_bets.append({
                    'type': 'Simple Placé',
                    'numeros': [num_sp],
                    'mise': mise_sp,
                    'option': None
                })
        
        # COUPLÉ
        with col3:
            cp_key = f"cp_{course_code}_{target_date}"
            couple = st.checkbox(
                "👥 Couplé",
                key=cp_key,
                help="Couplé 2 chevaux"
            )
            
            if couple:
                # SÉLECTION DES 2 CHEVAUX
                num_cp_1 = st.selectbox(
                    "Cheval 1",
                    all_numeros,
                    key=f"num1_{cp_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                num_cp_2 = st.selectbox(
                    "Cheval 2",
                    [n for n in all_numeros if n != num_cp_1],
                    key=f"num2_{cp_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                mise_cp = st.number_input(
                    "Mise (€)",
                    min_value=1.0,
                    value=3.0,
                    step=0.5,
                    key=f"mise_{cp_key}"
                )
                
                option_cp = st.radio(
                    "Type",
                    ["Gagnant", "Placé", "Ordre"],
                    horizontal=True,
                    key=f"option_{cp_key}"
                )
                
                st.caption(f"{num_cp_1}-{num_cp_2}")
                
                selected_bets.append({
                    'type': 'Couplé',
                    'numeros': [num_cp_1, num_cp_2],
                    'mise': mise_cp,
                    'option': option_cp
                })
        
        # TRIO
        with col4:
            tr_key = f"tr_{course_code}_{target_date}"
            trio = st.checkbox(
                "🎲 Trio",
                key=tr_key,
                help="Trio 3 chevaux"
            )
            
            if trio:
                # SÉLECTION DES 3 CHEVAUX
                num_tr_1 = st.selectbox(
                    "Cheval 1",
                    all_numeros,
                    key=f"num1_{tr_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                num_tr_2 = st.selectbox(
                    "Cheval 2",
                    [n for n in all_numeros if n != num_tr_1],
                    key=f"num2_{tr_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                num_tr_3 = st.selectbox(
                    "Cheval 3",
                    [n for n in all_numeros if n not in [num_tr_1, num_tr_2]],
                    key=f"num3_{tr_key}",
                    format_func=lambda x: f"N°{x}"
                )
                
                mise_tr = st.number_input(
                    "Mise (€)",
                    min_value=1.0,
                    value=5.0,
                    step=0.5,
                    key=f"mise_{tr_key}"
                )
                
                option_tr = st.radio(
                    "Type",
                    ["Ordre", "Désordre"],
                    horizontal=True,
                    key=f"option_{tr_key}"
                )
                
                st.caption(f"{num_tr_1}-{num_tr_2}-{num_tr_3}")
                
                selected_bets.append({
                    'type': 'Trio',
                    'numeros': [num_tr_1, num_tr_2, num_tr_3],
                    'mise': mise_tr,
                    'option': option_tr
                })
        
        # Bouton de sauvegarde si au moins un pari est sélectionné
        if selected_bets:
            st.markdown("---")
            
            col_total, col_save = st.columns([2, 1])
            
            with col_total:
                total_mise = sum(bet['mise'] for bet in selected_bets)
                st.metric("💰 Total des mises", f"{total_mise:.2f} €")
            
            with col_save:
                if st.button(
                    "💾 Sauvegarder ces paris",
                    type="primary",
                    key=f"save_{course_code}_{target_date}"
                ):
                    success_count = 0
                    for bet in selected_bets:
                        if self.save_pari(
                            course_code,
                            target_date,
                            bet['type'],
                            bet['numeros'],
                            bet['mise'],
                            bet['option']
                        ):
                            success_count += 1
                    
                    if success_count == len(selected_bets):
                        st.success(f"✅ {success_count} paris sauvegardés!")
                    else:
                        st.warning(f"⚠️ {success_count}/{len(selected_bets)} paris sauvegardés")
    
    def display_saved_bets(self, target_date: date):
        """Affiche tous les paris sauvegardés pour une date"""
        
        paris_df = self.get_paris_for_date(target_date)
        
        if paris_df.empty:
            st.info("📭 Aucun pari sauvegardé pour cette date")
            return
        
        st.header("💰 Vos Paris du Jour")
        
        # Regrouper par course
        for course_code in paris_df['course_code'].unique():
            course_paris = paris_df[paris_df['course_code'] == course_code]
            
            with st.expander(
                f"🏇 {course_code} - {course_paris.iloc[0]['hippodrome']} "
                f"({course_paris.iloc[0]['heure']})",
                expanded=True
            ):
                for _, pari in course_paris.iterrows():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    
                    with col1:
                        st.write(f"**{pari['type_pari']}**")
                        if pari['option']:
                            st.caption(pari['option'])
                    
                    with col2:
                        st.write(f"N° {pari['numeros']}")
                    
                    with col3:
                        st.write(f"{pari['mise']:.2f} €")
                    
                    with col4:
                        if pari['statut'] == 'gagnant':
                            st.success(f"+{pari['gain']:.2f}€")
                        elif pari['statut'] == 'perdant':
                            st.error("❌")
                        else:
                            st.info("⏳")
        
        # Total des mises
        total_mise = paris_df['mise'].sum()
        total_gain = paris_df[paris_df['statut'] == 'gagnant']['gain'].sum()
        
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 Total misé", f"{total_mise:.2f} €")
        
        with col2:
            st.metric("💵 Gains", f"{total_gain:.2f} €")
        
        with col3:
            bilan = total_gain - total_mise
            st.metric(
                "📊 Bilan",
                f"{bilan:+.2f} €",
                delta=f"{(bilan/total_mise*100 if total_mise > 0 else 0):.1f}%"
            )


def display_betting_interface():
    """Page principale de l'interface de betting"""
    
    st.header("💰 Interface de Paris")
    
    betting = BettingInterface()
    calculator = BordaCalculator()
    
    # Sélection de date
    target_date = st.date_input(
        "Date des courses",
        value=datetime.now().date()
    )
    
    # Onglets
    tab1, tab2 = st.tabs(["📝 Sélectionner mes paris", "📊 Mes paris du jour"])
    
    with tab1:
        st.subheader("🎯 Sélectionner vos paris par course")
        
        # Récupérer les courses
        query = """
            SELECT 
                c.course_code,
                c.heure,
                h.nom as hippodrome,
                c.nombre_partants
            FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            WHERE r.date = ?
            ORDER BY c.course_code
        """
        
        courses_df = pd.read_sql_query(
            query,
            calculator.db.conn,
            params=[target_date]
        )
        
        if courses_df.empty:
            st.warning("Aucune course pour cette date")
            return
        
        # Afficher chaque course
        for _, course in courses_df.iterrows():
            with st.expander(
                f"🏇 {course['course_code']} - {course['hippodrome']} "
                f"({course['heure']}) - {course['nombre_partants']} partants"
            ):
                # Récupérer les scores Borda
                scores_df = calculator.get_borda_scores_for_course(
                    course['course_code'],
                    'default',
                    target_date
                )
                
                if scores_df.empty:
                    st.warning("⚠️ Scores Borda non calculés")
                    continue
                
                # Afficher le top 5
                top_5 = scores_df.head(5)[['numero', 'cheval', 'score_total', 'cote_pmu']]
                st.dataframe(top_5, use_container_width=True, hide_index=True)
                
                # Interface de sélection des paris
                betting.display_bet_selection(
                    course['course_code'],
                    target_date,
                    scores_df
                )
    
    with tab2:
        betting.display_saved_bets(target_date)


if __name__ == "__main__":
    display_betting_interface()
