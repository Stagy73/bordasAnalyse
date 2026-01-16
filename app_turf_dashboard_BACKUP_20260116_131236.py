import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_db_adapter import get_db_adapter

# Configuration
st.set_page_config(
    page_title="Dashboard Turf BZH",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏇 Dashboard Turf BZH - Version Database")
st.markdown("---")

# Instance DB
db_adapter = get_db_adapter()

def main():
    # Sidebar - Import CSV
    st.sidebar.title("⚙️ Navigation")
    
    st.sidebar.markdown("### 📥 Import de données")
    uploaded_file = st.sidebar.file_uploader(
        "Importer un export CSV", 
        type=['csv'],
        help="Import un nouvel export TurfBZH dans la base de données"
    )
    
    if uploaded_file is not None:
        with st.sidebar:
            with st.spinner("Import en cours..."):
                stats = db_adapter.import_csv_file(uploaded_file)
                
                if stats and not stats.get('errors'):
                    st.success(f"✅ Import réussi!")
                    st.info(f"📝 {stats['courses']} courses")
                    st.info(f"🐴 {stats['partants']} partants")
                else:
                    st.error("❌ Erreur lors de l'import")
    
    # Statistiques DB
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Base de données")
    
    global_stats = db_adapter.get_global_stats()
    st.sidebar.metric("Courses", f"{global_stats['total_courses']:,}")
    st.sidebar.metric("Chevaux", f"{global_stats['total_chevaux']:,}")
    st.sidebar.metric("Drivers", f"{global_stats['total_drivers']:,}")
    
    if global_stats.get('date_debut') and global_stats.get('date_fin'):
        st.sidebar.caption(f"📅 {global_stats['date_debut']} → {global_stats['date_fin']}")
    
    # Filtres de date
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filtres de Date")
    
    today = datetime.now().date()
    default_start = today - timedelta(days=7)
    
    date_range = st.sidebar.date_input(
        "Période",
        value=(default_start, today),
        max_value=today
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        date_debut, date_fin = date_range
    else:
        date_debut = date_fin = today
    
    # Charger les données
    df = db_adapter.load_partants_for_predictions(date_debut, date_fin)
    
    if df.empty:
        st.warning(f"⚠️ Aucune donnée pour {date_debut} → {date_fin}")
        st.info("💡 Importez un fichier CSV pour commencer")
        return
    
    # Menu
    st.sidebar.markdown("---")
    menu_options = [
        "📊 Vue d'ensemble",
        "🎯 PRONOSTICS GLOBAUX",
        "⭐ Favoris",
        "💰 Suivi ROI",
        "⚙️ Config Borda",
        "🌍 Courses Étrangères"
    ]
    
    menu = st.sidebar.radio("Sections:", menu_options)
    
    # Affichage
    if menu == "📊 Vue d'ensemble":
        st.header("📊 Statistiques Globales")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Courses", f"{global_stats['total_courses']:,}")
        with col2:
            st.metric("Chevaux", f"{global_stats['total_chevaux']:,}")
        with col3:
            st.metric("Drivers", f"{global_stats['total_drivers']:,}")
        with col4:
            st.metric("Hippodromes", f"{global_stats['total_hippodromes']:,}")
        
        st.markdown("---")
        
        # Stats période sélectionnée
        st.subheader(f"📈 Période : {date_debut} → {date_fin}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Courses période", df['Course'].nunique())
            st.metric("Partants période", len(df))
        
        with col2:
            if 'hippodrome' in df.columns:
                st.metric("Hippodromes actifs", df['hippodrome'].nunique())
            if 'discipline' in df.columns:
                st.metric("Disciplines", df['discipline'].nunique())
        
        st.markdown("---")
        st.subheader("🏟️ Statistiques par Hippodrome")
        hippo_stats = db_adapter.get_hippodrome_stats()
        if not hippo_stats.empty:
            st.dataframe(hippo_stats, use_container_width=True)
    
    elif menu == "🎯 PRONOSTICS GLOBAUX":
        from global_predictions import display_global_predictions
        display_global_predictions()
    
    elif menu == "⭐ Favoris":
        st.header("⭐ Gestion des Favoris")
        
        tab1, tab2 = st.tabs(["🐴 Chevaux", "🏇 Drivers"])
        
        with tab1:
            st.subheader("Chevaux Favoris")
            fav_horses = db_adapter.get_favorite_horses()
            
            if not fav_horses.empty:
                st.dataframe(fav_horses, use_container_width=True)
            else:
                st.info("Aucun cheval favori")
            
            st.markdown("---")
            st.subheader("Ajouter un cheval")
            
            search_term = st.text_input("Rechercher un cheval")
            if search_term:
                results = db_adapter.search_horses(search_term)
                st.dataframe(results)
                
                cheval_nom = st.selectbox("Choisir", results['Cheval'].tolist() if not results.empty else [])
                notes = st.text_area("Notes")
                
                if st.button("⭐ Ajouter aux favoris"):
                    if db_adapter.add_favorite_horse(cheval_nom, notes):
                        st.success(f"✅ {cheval_nom} ajouté !")
                        st.rerun()
        
        with tab2:
            st.subheader("Drivers Favoris")
            st.info("À venir...")
    
    elif menu == "💰 Suivi ROI":
        from betting_interface import display_roi_analysis
        display_roi_analysis()
    
    elif menu == "⚙️ Config Borda":
        from borda_configuration_interface import display_borda_configuration_interface
        display_borda_configuration_interface(df)
    
    elif menu == "🌍 Courses Étrangères":
        from foreign_races_system import display_foreign_races_manager
        display_foreign_races_manager()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Turf BZH Dashboard v2.0**")
    st.sidebar.markdown(f"📊 {len(df)} partants chargés")

if __name__ == "__main__":
    main()
