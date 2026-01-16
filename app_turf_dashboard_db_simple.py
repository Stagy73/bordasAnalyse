#!/usr/bin/env python3
"""
🏇 DASHBOARD TURF BZH - VERSION DATABASE
Version simplifiée utilisant uniquement la base de données
"""

import streamlit as st
from datetime import datetime
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Turf BZH",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Point d'entrée principal du dashboard"""
    
    st.title("🏇 Dashboard Turf BZH - Version Database")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("📊 Navigation")
        
        menu_options = [
            "📊 Vue d'ensemble",
            "🎯 PRONOSTICS GLOBAUX",
            "💰 Interface de Paris",
            "🐴 Analyse Chevaux",
            "👨‍🏫 Analyse Drivers",
            "⚙️ Config Borda",
        ]
        
        menu = st.radio("Menu:", menu_options, label_visibility="collapsed")
    
    # Afficher la section sélectionnée
    if menu == "📊 Vue d'ensemble":
        display_overview()
    
    elif menu == "🎯 PRONOSTICS GLOBAUX":
        from global_predictions_db import display_global_predictions
        display_global_predictions()
    
    elif menu == "💰 Interface de Paris":
        from betting_interface_db import display_betting_interface
        display_betting_interface()
    
    elif menu == "🐴 Analyse Chevaux":
        display_cheval_analysis()
    
    elif menu == "👨‍🏫 Analyse Drivers":
        display_driver_analysis()
    
    elif menu == "⚙️ Config Borda":
        display_config_borda()


def display_overview():
    """Affiche la vue d'ensemble de la base de données"""
    
    from turf_database_complete import get_turf_database
    
    st.header("📊 Vue d'ensemble de la Base de Données")
    
    # Bouton d'import en haut
    col_import1, col_import2 = st.columns([3, 1])
    
    with col_import1:
        uploaded_file = st.file_uploader(
            "📥 Importer un nouveau fichier CSV",
            type=['csv'],
            help="Glissez-déposez votre export TurfBZH quotidien"
        )
    
    with col_import2:
        st.write("")
        st.write("")
        if uploaded_file and st.button("⬆️ Importer", type="primary"):
            import tempfile
            import os
            from universal_importer import import_any_csv
            
            # Sauvegarder temporairement
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                with st.spinner("Import en cours..."):
                    stats = import_any_csv(tmp_path)
                    
                st.success(f"✅ Import réussi !")
                st.info(f"📊 {stats['courses']} courses, {stats['partants']} partants importés")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors de l'import : {e}")
            finally:
                os.unlink(tmp_path)
    
    st.markdown("---")
    
    db = get_turf_database()
    
    # Statistiques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        db.cursor.execute("SELECT COUNT(*) FROM courses")
        nb_courses = db.cursor.fetchone()[0]
        st.metric("🏇 Courses", f"{nb_courses:,}")
    
    with col2:
        db.cursor.execute("SELECT COUNT(*) FROM chevaux")
        nb_chevaux = db.cursor.fetchone()[0]
        st.metric("🐴 Chevaux", f"{nb_chevaux:,}")
    
    with col3:
        db.cursor.execute("SELECT COUNT(*) FROM drivers")
        nb_drivers = db.cursor.fetchone()[0]
        st.metric("👨‍🏫 Drivers", f"{nb_drivers:,}")
    
    with col4:
        db.cursor.execute("SELECT COUNT(*) FROM partants")
        nb_partants = db.cursor.fetchone()[0]
        st.metric("📊 Partants", f"{nb_partants:,}")
    
    st.markdown("---")
    
    # Période couverte
    db.cursor.execute("SELECT MIN(date), MAX(date) FROM reunions")
    date_min, date_max = db.cursor.fetchone()
    
    if date_min and date_max:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **Première course:** {date_min}")
        with col2:
            st.info(f"📅 **Dernière course:** {date_max}")
    
    st.markdown("---")
    
    # Courses par hippodrome (top 10)
    st.subheader("🏟️ Top 10 Hippodromes")
    
    query = """
        SELECT 
            h.nom,
            COUNT(c.id) as nb_courses,
            COUNT(DISTINCT r.date) as nb_jours
        FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
        GROUP BY h.nom
        ORDER BY nb_courses DESC
        LIMIT 10
    """
    
    df_hippo = pd.read_sql_query(query, db.conn)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(df_hippo, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("")
        st.write("")
        st.metric("Total hippodromes", f"{df_hippo['nb_courses'].sum():,} courses")
    
    st.markdown("---")
    
    # Courses récentes
    st.subheader("📅 Courses Récentes")
    
    query = """
        SELECT 
            r.date,
            h.nom as hippodrome,
            COUNT(c.id) as nb_courses,
            COUNT(p.id) as nb_partants
        FROM courses c
        JOIN reunions r ON c.reunion_id = r.id
        JOIN hippodromes h ON r.hippodrome_id = h.id
        LEFT JOIN partants p ON p.course_id = c.id
        GROUP BY r.date, h.nom
        ORDER BY r.date DESC
        LIMIT 20
    """
    
    df_recent = pd.read_sql_query(query, db.conn)
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Scores Borda
    st.subheader("🎯 Scores Borda Calculés")
    
    db.cursor.execute("SELECT COUNT(*) FROM borda_scores")
    nb_borda = db.cursor.fetchone()[0]
    
    if nb_borda > 0:
        st.success(f"✅ {nb_borda:,} scores Borda calculés")
        
        # Derniers scores calculés
        query = """
            SELECT 
                c.course_code,
                r.date,
                COUNT(bs.id) as nb_scores
            FROM borda_scores bs
            JOIN partants p ON bs.partant_id = p.id
            JOIN courses c ON p.course_id = c.id
            JOIN reunions r ON c.reunion_id = r.id
            GROUP BY c.course_code, r.date
            ORDER BY r.date DESC, c.course_code
            LIMIT 10
        """
        
        df_borda = pd.read_sql_query(query, db.conn)
        st.dataframe(df_borda, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Aucun score Borda calculé")
        st.info("💡 Allez dans **🎯 PRONOSTICS GLOBAUX** pour calculer les scores")


def display_config_borda():
    """Affiche la configuration Borda"""
    
    from borda_calculator_db import BordaCalculator
    
    st.header("⚙️ Configuration Borda")
    
    calculator = BordaCalculator()
    
    # Afficher les configurations existantes
    query = "SELECT * FROM borda_configs"
    configs_df = pd.read_sql_query(query, calculator.db.conn)
    
    st.subheader("📋 Configurations Existantes")
    
    if not configs_df.empty:
        st.dataframe(configs_df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune configuration personnalisée")
    
    st.markdown("---")
    
    # Critères par défaut
    st.subheader("🎯 Critères de la Configuration 'default'")
    
    criteria = calculator.get_default_criteria()
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i, (crit, poids) in enumerate(list(criteria.items())[:4]):
            st.metric(crit, f"{poids} points")
    
    with col2:
        for crit, poids in list(criteria.items())[4:]:
            st.metric(crit, f"{poids} points")
    
    total = sum(criteria.values())
    st.info(f"📊 Total: {total} points")


def display_cheval_analysis():
    """Analyse des performances des chevaux"""
    
    from turf_database_complete import get_turf_database
    
    st.header("🐴 Analyse des Chevaux")
    
    db = get_turf_database()
    
    # Recherche de cheval
    cheval_search = st.text_input("🔍 Rechercher un cheval", placeholder="Nom du cheval...")
    
    if cheval_search:
        query = """
            SELECT 
                ch.nom,
                ch.age,
                ch.sexe,
                ch.elo,
                COUNT(DISTINCT p.id) as nb_courses,
                COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) as nb_victoires,
                COUNT(DISTINCT CASE WHEN p.rang_arrivee <= 3 AND p.rang_arrivee > 0 THEN p.id END) as nb_places,
                ROUND(AVG(p.cote_pmu), 2) as cote_moyenne
            FROM chevaux ch
            LEFT JOIN partants p ON ch.id = p.cheval_id
            WHERE LOWER(ch.nom) LIKE LOWER(?)
            GROUP BY ch.id, ch.nom, ch.age, ch.sexe, ch.elo
            ORDER BY nb_courses DESC
            LIMIT 10
        """
        
        df = pd.read_sql_query(query, db.conn, params=[f"%{cheval_search}%"])
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Aucun cheval trouvé pour '{cheval_search}'")
    
    st.markdown("---")
    
    # Top chevaux par nombre de courses
    st.subheader("🏆 Top 20 Chevaux (par nombre de courses)")
    
    query = """
        SELECT 
            ch.nom,
            ch.elo,
            COUNT(DISTINCT p.id) as nb_courses,
            COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) as victoires,
            COUNT(DISTINCT CASE WHEN p.rang_arrivee <= 3 AND p.rang_arrivee > 0 THEN p.id END) as places
        FROM chevaux ch
        LEFT JOIN partants p ON ch.id = p.cheval_id
        GROUP BY ch.id, ch.nom, ch.elo
        HAVING nb_courses > 0
        ORDER BY nb_courses DESC
        LIMIT 20
    """
    
    df_top = pd.read_sql_query(query, db.conn)
    if not df_top.empty:
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée disponible")


def display_driver_analysis():
    """Analyse des performances des drivers"""
    
    from turf_database_complete import get_turf_database
    
    st.header("👨‍🏫 Analyse des Drivers")
    
    db = get_turf_database()
    
    # Recherche de driver
    driver_search = st.text_input("🔍 Rechercher un driver", placeholder="Nom du driver...")
    
    if driver_search:
        query = """
            SELECT 
                d.nom,
                d.elo,
                COUNT(DISTINCT p.id) as nb_courses,
                COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) as nb_victoires,
                COUNT(DISTINCT CASE WHEN p.rang_arrivee <= 3 AND p.rang_arrivee > 0 THEN p.id END) as nb_places,
                ROUND(COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) * 100.0 / NULLIF(COUNT(DISTINCT p.id), 0), 2) as taux_victoire
            FROM drivers d
            LEFT JOIN partants p ON d.id = p.driver_id
            WHERE LOWER(d.nom) LIKE LOWER(?)
            GROUP BY d.id, d.nom, d.elo
            ORDER BY nb_courses DESC
            LIMIT 10
        """
        
        df = pd.read_sql_query(query, db.conn, params=[f"%{driver_search}%"])
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"Aucun driver trouvé pour '{driver_search}'")
    
    st.markdown("---")
    
    # Top drivers par nombre de courses
    st.subheader("🏆 Top 20 Drivers (par nombre de courses)")
    
    query = """
        SELECT 
            d.nom,
            d.elo,
            COUNT(DISTINCT p.id) as nb_courses,
            COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) as victoires,
            ROUND(COUNT(DISTINCT CASE WHEN p.rang_arrivee = 1 THEN p.id END) * 100.0 / NULLIF(COUNT(DISTINCT p.id), 0), 2) as taux_victoire
        FROM drivers d
        LEFT JOIN partants p ON d.id = p.driver_id
        GROUP BY d.id, d.nom, d.elo
        HAVING nb_courses > 0
        ORDER BY nb_courses DESC
        LIMIT 20
    """
    
    df_top = pd.read_sql_query(query, db.conn)
    if not df_top.empty:
        st.dataframe(df_top, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée disponible")


if __name__ == "__main__":
    main()
