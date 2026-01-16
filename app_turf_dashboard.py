import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Turf BZH",
    page_icon="🏇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("🏇 Dashboard Analyse Turf BZH")
st.markdown("---")

@st.cache_data
def load_data(file_path):
    """Charge et prépare les données"""
    df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
    
    # Détecter le type de fichier
    has_borda = any('Borda' in col for col in df.columns)
    
    # Normaliser les noms de colonnes selon le type
    if not has_borda:
        # Fichier historique (converti depuis JSON)
        # Créer des alias pour compatibilité
        if 'course_id' in df.columns and 'Course' not in df.columns:
            df['Course'] = df['course_id']
        if 'ordre_arrivee' in df.columns and 'Rank' not in df.columns:
            df['Rank'] = df['ordre_arrivee']
        if 'cote_direct' in df.columns and 'Cote' not in df.columns:
            df['Cote'] = df['cote_direct']
        if 'nombre_partants' in df.columns and 'nombre_partants' not in df.columns:
            df['nombre_partants'] = df['nombre_partants']
        if 'montant_prix' in df.columns and 'allocation' not in df.columns:
            df['allocation'] = df['montant_prix']
        if 'cheval' in df.columns and 'Cheval' not in df.columns:
            df['Cheval'] = df['cheval']
        if 'driver' in df.columns and 'Driver' not in df.columns:
            df['Driver'] = df['driver']
        if 'entraineur' in df.columns and 'Entraineur' not in df.columns:
            df['Entraineur'] = df['entraineur']
    
    # Conversion des colonnes numériques
    numeric_cols = ['Cote', 'Note_IA_Decimale', 'allocation', 'nombre_partants', 
                    'Popularite', 'Rank', 'cote_direct', 'ordre_arrivee', 'montant_prix']
    
    # Convertir les taux (qui peuvent avoir des virgules au lieu de points)
    taux_cols = ['Taux Victoire', 'Taux Place', 'Taux Incident']
    
    for col in taux_cols:
        if col in df.columns:
            # Remplacer virgules par points et convertir
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Conversion de la date
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Extraction des scores Borda
    borda_cols = [col for col in df.columns if 'Borda' in col]
    
    return df, borda_cols, has_borda

# Fonction pour afficher les statistiques globales
def display_global_stats(df):
    st.header("📊 Statistiques Globales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Course' in df.columns:
            st.metric("Total Courses", df['Course'].nunique())
        elif 'course_id' in df.columns:
            st.metric("Total Courses", df['course_id'].nunique())
        else:
            st.metric("Total Courses", 1)  # Fichier quotidien = 1 course
    
    with col2:
        if 'Cheval' in df.columns:
            st.metric("Total Chevaux", df['Cheval'].nunique())
        elif 'CHEVAL/MUSIQ.' in df.columns:
            st.metric("Total Chevaux", len(df))
        else:
            st.metric("Total Chevaux", len(df))
    
    with col3:
        if 'Driver' in df.columns:
            st.metric("Total Drivers", df['Driver'].nunique())
        elif 'DRIVER/ENTRAINEUR' in df.columns:
            st.metric("Total Drivers", df['DRIVER/ENTRAINEUR'].nunique())
        else:
            st.metric("Total Drivers", "N/A")
    
    with col4:
        if 'hippodrome' in df.columns:
            st.metric("Hippodromes", df['hippodrome'].nunique())
        else:
            st.metric("Hippodromes", 1)  # Fichier quotidien = 1 hippodrome

# Fonction pour analyser les Borda
def analyze_borda_scores(df, borda_cols):
    st.header("🎯 Analyse des Scores Borda")
    
    # Sélection de la colonne Borda
    selected_borda = st.selectbox(
        "Sélectionnez un système Borda:",
        options=borda_cols,
        index=0 if borda_cols else None
    )
    
    if selected_borda:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des scores Borda
            fig = px.histogram(
                df[df[selected_borda].notna()],
                x=selected_borda,
                title=f"Distribution - {selected_borda}",
                color_discrete_sequence=['#1f77b4']
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Top 10 chevaux par score Borda
            top_horses = df.nlargest(10, selected_borda)[['Cheval', selected_borda, 'hippodrome', 'Course']]
            st.subheader("🏆 Top 10 Chevaux")
            st.dataframe(top_horses, width="stretch")

# Fonction pour analyser Favoris vs Outsiders
def analyze_favoris_outsiders(df):
    st.header("🎲 Analyse Favoris vs Outsiders")
    
    # Créer une catégorisation si elle existe
    if 'classement' in df.columns:
        favoris_counts = df['classement'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique en camembert
            fig = px.pie(
                values=favoris_counts.values,
                names=favoris_counts.index,
                title="Répartition Favoris/Possibles/Outsiders",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Taux de réussite par catégorie
            st.subheader("📈 Performance par Catégorie")
            
            perf_data = []
            for cat in df['classement'].unique():
                if pd.notna(cat):
                    cat_df = df[df['classement'] == cat]
                    avg_rank = cat_df['Rank'].mean() if 'Rank' in cat_df.columns else 0
                    avg_cote = cat_df['Cote'].mean() if 'Cote' in cat_df.columns else 0
                    perf_data.append({
                        'Catégorie': cat,
                        'Rang Moyen': round(avg_rank, 2),
                        'Cote Moyenne': round(avg_cote, 2)
                    })
            
            if perf_data:
                perf_df = pd.DataFrame(perf_data)
                st.dataframe(perf_df, width="stretch")

# Fonction pour l'analyse par hippodrome
def analyze_by_hippodrome(df):
    st.header("🏟️ Analyse par Hippodrome")
    
    hippodrome_stats = df.groupby('hippodrome').agg({
        'Course': 'nunique',
        'Cheval': 'nunique',
        'allocation': 'mean'
    }).reset_index()
    
    hippodrome_stats.columns = ['Hippodrome', 'Nb Courses', 'Nb Chevaux', 'Allocation Moyenne']
    hippodrome_stats = hippodrome_stats.sort_values('Nb Courses', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 hippodromes
        fig = px.bar(
            hippodrome_stats.head(10),
            x='Nb Courses',
            y='Hippodrome',
            orientation='h',
            title="Top 10 Hippodromes par Nombre de Courses",
            color='Nb Courses',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.subheader("📊 Détails des Hippodromes")
        st.dataframe(hippodrome_stats, width="stretch", height=400)

# Fonction pour l'analyse des drivers
def analyze_performances(df):
    st.header("📈 Analyse des Performances")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top chevaux par nombre de victoires
        if 'nombre_victoires' in df.columns and 'Cheval' in df.columns:
            top_winners = df.groupby('Cheval')['nombre_victoires'].first().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=top_winners.values,
                y=top_winners.index,
                orientation='h',
                title="Top 15 Chevaux par Victoires",
                labels={'x': 'Nombre de Victoires', 'y': 'Cheval'},
                color=top_winners.values,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, width="stretch")
    
    with col2:
        # Distribution des places
        if 'ordre_arrivee' in df.columns or 'Rank' in df.columns:
            rank_col = 'ordre_arrivee' if 'ordre_arrivee' in df.columns else 'Rank'
            place_counts = df[rank_col].value_counts().sort_index().head(10)
            
            fig = px.bar(
                x=place_counts.index,
                y=place_counts.values,
                title="Distribution des Classements",
                labels={'x': 'Position', 'y': 'Nombre de courses'},
                color=place_counts.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, width="stretch")
    
    # Analyse des gains
    if 'gains_carriere' in df.columns:
        st.subheader("💰 Analyse des Gains")
        
        gains_data = df[df['gains_carriere'].notna()].groupby('Cheval').agg({
            'gains_carriere': 'first',
            'gains_victoires': 'first',
            'nombre_victoires': 'first'
        }).sort_values('gains_carriere', ascending=False).head(20)
        
        st.dataframe(gains_data, width="stretch")

def analyze_drivers(df):
    st.header("👨‍🏫 Analyse des Drivers")
    
    try:
        # Déterminer quelles colonnes sont disponibles
        has_taux = 'Taux Victoire' in df.columns and 'Taux Place' in df.columns
        
        if has_taux:
            # Fichier avec Borda - utiliser les taux
            st.info("📊 Utilisation des taux de victoire pré-calculés")
            
            # Vérifier que les colonnes contiennent des données valides
            valid_taux_victoire = df['Taux Victoire'].notna().sum()
            st.write(f"Lignes avec Taux Victoire valide: {valid_taux_victoire}/{len(df)}")
            
            driver_stats = df.groupby('Driver').agg({
                'Course': 'count',
                'Taux Victoire': 'mean',
                'Taux Place': 'mean',
                'Cote': 'mean'
            }).reset_index()
            
            driver_stats.columns = ['Driver', 'Nb Courses', 'Taux Victoire Moyen', 'Taux Place Moyen', 'Cote Moyenne']
            
            # Filtrer les drivers avec des taux valides
            driver_stats = driver_stats[driver_stats['Taux Victoire Moyen'].notna()]
            driver_stats = driver_stats[driver_stats['Nb Courses'] >= 5]
            driver_stats = driver_stats.sort_values('Taux Victoire Moyen', ascending=False)
            
            metric_col = 'Taux Victoire Moyen'
            metric_title = "Taux de Victoire"
            
        else:
            # Fichier historique - calculer à partir des résultats
            st.info("🔄 Calcul des statistiques depuis les données historiques...")
            
            rank_col = 'ordre_arrivee' if 'ordre_arrivee' in df.columns else 'Rank'
            cote_col = 'Cote' if 'Cote' in df.columns else 'cote_direct'
            
            # Debug info
            st.write(f"Colonne classement: {rank_col}")
            st.write(f"Nombre total de drivers: {df['Driver'].nunique()}")
            
            # Calculer le taux de victoire par driver
            driver_data = []
            for driver in df['Driver'].dropna().unique():
                driver_df = df[df['Driver'] == driver]
                nb_courses = len(driver_df)
                
                # S'assurer que rank_col existe et contient des valeurs numériques
                if rank_col in driver_df.columns:
                    nb_victoires = (pd.to_numeric(driver_df[rank_col], errors='coerce') == 1).sum()
                else:
                    nb_victoires = 0
                
                taux_victoire = nb_victoires / nb_courses if nb_courses > 0 else 0
                
                if cote_col in driver_df.columns:
                    cote_moyenne = pd.to_numeric(driver_df[cote_col], errors='coerce').mean()
                else:
                    cote_moyenne = 0
                
                driver_data.append({
                    'Driver': driver,
                    'Nb Courses': nb_courses,
                    'Nb Victoires': nb_victoires,
                    'Taux Victoire': taux_victoire,
                    'Cote Moyenne': cote_moyenne
                })
            
            driver_stats = pd.DataFrame(driver_data)
            
            st.write(f"Drivers avant filtre: {len(driver_stats)}")
            
            # Réduire le minimum à 5 courses pour avoir plus de résultats
            driver_stats = driver_stats[driver_stats['Nb Courses'] >= 5]
            driver_stats = driver_stats.sort_values('Taux Victoire', ascending=False)
            
            st.write(f"Drivers après filtre (≥5 courses): {len(driver_stats)}")
            
            metric_col = 'Taux Victoire'
            metric_title = "Taux de Victoire"
        
        if len(driver_stats) == 0:
            st.warning("⚠️ Aucun driver trouvé avec suffisamment de courses")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top drivers
            fig = px.bar(
                driver_stats.head(15),
                x=metric_col,
                y='Driver',
                orientation='h',
                title=f"Top 15 Drivers par {metric_title}",
                color=metric_col,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.subheader("📊 Détails des Drivers")
            st.dataframe(driver_stats.head(20), width="stretch", height=400)
    
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse des drivers: {e}")
        import traceback
        st.code(traceback.format_exc())

# Fonction pour la recherche avancée
def advanced_search(df):
    st.header("🔍 Recherche Avancée")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_horse = st.text_input("Rechercher un cheval:")
    
    with col2:
        search_driver = st.selectbox(
            "Filtrer par Driver:",
            options=['Tous'] + sorted(df['Driver'].dropna().unique().tolist())
        )
    
    with col3:
        search_hippodrome = st.selectbox(
            "Filtrer par Hippodrome:",
            options=['Tous'] + sorted(df['hippodrome'].dropna().unique().tolist())
        )
    
    # Appliquer les filtres
    filtered_df = df.copy()
    
    if search_horse:
        filtered_df = filtered_df[filtered_df['Cheval'].str.contains(search_horse, case=False, na=False)]
    
    if search_driver != 'Tous':
        filtered_df = filtered_df[filtered_df['Driver'] == search_driver]
    
    if search_hippodrome != 'Tous':
        filtered_df = filtered_df[filtered_df['hippodrome'] == search_hippodrome]
    
    # Afficher les résultats
    st.subheader(f"📋 Résultats: {len(filtered_df)} courses trouvées")
    
    if len(filtered_df) > 0:
        # Sélection des colonnes à afficher
        display_cols = ['date', 'hippodrome', 'Course', 'Cheval', 'Driver', 'Entraineur', 
                       'Rank', 'Cote', 'Note_IA_Decimale', 'classement']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[available_cols].sort_values('date', ascending=False),
            width="stretch",
            height=400
        )

# Fonction principale
def main():
    # Sidebar
    st.sidebar.title("⚙️ Navigation")
    
    # Upload du fichier ou utilisation du fichier existant
    uploaded_file = st.sidebar.file_uploader("Charger un fichier CSV", type=['csv'])
    
    if uploaded_file is not None:
        df, borda_cols, has_borda = load_data(uploaded_file)
    else:
        # Utiliser le fichier par défaut dans le dossier courant
        try:
            df, borda_cols, has_borda = load_data('export_turfbzh_20260115.csv')
            st.sidebar.success("✅ Fichier chargé: export_turfbzh_20260115.csv")
        except FileNotFoundError:
            st.sidebar.warning("⚠️ Fichier CSV non trouvé")
            
            # Message d'accueil avec instructions
            st.markdown("""
            ## 👋 Bienvenue sur le Dashboard Turf BZH !
            
            ### 📁 Pour commencer :
            
            **Option 1 : Charger un fichier**
            - Utilisez le bouton **"Browse files"** dans la barre latérale ⬅️
            - Sélectionnez votre fichier CSV d'export Turf BZH
            
            **Option 2 : Utiliser le fichier par défaut**
            - Assurez-vous que le fichier `export_turfbzh_20260115.csv` est dans le même dossier
            - Relancez l'application
            
            ### 📋 Format attendu :
            - Fichier CSV avec séparateur `;`
            - Encodage UTF-8
            - Colonnes : date, hippodrome, Course, Cheval, Driver, etc.
            
            ### 🆘 Besoin d'aide ?
            Consultez le fichier **INSTALL_UBUNTU.md** ou **README.md** dans le dossier.
            """)
            return
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement: {e}")
            return
    
    # Filtres de date
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filtres de Date")
    
    if 'date' in df.columns and df['date'].notna().any():
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Période:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[(df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])]
    
    # Menu de navigation
    st.sidebar.markdown("---")
    
    # Adapter le menu selon le type de fichier
    if has_borda:
        menu_options = ["📊 Vue d'ensemble", "🎯 Scores Borda", "🎯 PRONOSTICS GLOBAUX",
                       "🎲 Favoris/Outsiders", "🏟️ Hippodromes", "👨‍🏫 Drivers", 
                       "⭐ Favoris", "💰 Suivi ROI", "⚙️ Config Borda", "🌍 Courses Étrangères", "🔍 Recherche"]
    else:
        # Fichier quotidien - proposer le pronostique intelligent
        menu_options = ["📊 Vue d'ensemble", "🎯 PRONOSTIQUE", "🏟️ Hippodromes", "👨‍🏫 Drivers", 
                       "📈 Performances", "⭐ Favoris", "💰 Suivi ROI", "⚙️ Config Borda", 
                       "🌍 Courses Étrangères", "🔍 Recherche"]
    
    menu = st.sidebar.radio("Sections:", menu_options)
    
    # Afficher le gestionnaire d'exports Borda dans la sidebar
    from borda_manager import display_borda_manager
    borda_manager_result = display_borda_manager()
    
    # Affichage des statistiques globales en haut
    display_global_stats(df)
    
    # Afficher le type de fichier chargé
    if has_borda:
        st.info("📊 **Fichier avec scores Borda** chargé - Toutes les analyses sont disponibles")
    else:
        st.warning("📁 **Fichier historique** chargé - Analyses Borda et Favoris/Outsiders non disponibles")
    
    st.markdown("---")
    
    # Navigation entre les sections
    if menu == "📊 Vue d'ensemble":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Courses par Date")
            if 'date' in df.columns:
                daily_races = df.groupby(df['date'].dt.date).size().reset_index()
                daily_races.columns = ['Date', 'Nombre de Courses']
                fig = px.line(daily_races, x='Date', y='Nombre de Courses', 
                             markers=True, title="Évolution du nombre de courses")
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.subheader("🏆 Distribution des Disciplines")
            if 'discipline' in df.columns:
                disc_counts = df['discipline'].value_counts()
                fig = px.bar(x=disc_counts.index, y=disc_counts.values,
                           title="Courses par Discipline",
                           labels={'x': 'Discipline', 'y': 'Nombre'},
                           color=disc_counts.values,
                           color_continuous_scale='Viridis')
                st.plotly_chart(fig, width="stretch")
    
    elif menu == "🎯 Scores Borda" and has_borda:
        analyze_borda_scores(df, borda_cols)
    
    elif menu == "🎯 PRONOSTICS GLOBAUX" and has_borda:
        from global_predictions import display_global_predictions
        display_global_predictions()
    
    elif menu == "🎲 Favoris/Outsiders" and has_borda:
        analyze_favoris_outsiders(df)
    
    elif menu == "🎯 PRONOSTIQUE" and not has_borda:
        # Module de pronostique intelligent pour fichiers quotidiens
        from smart_prediction_v2 import display_smart_prediction
        display_smart_prediction(df)
    
    elif menu == "🏟️ Hippodromes":
        analyze_by_hippodrome(df)
    
    elif menu == "👨‍🏫 Drivers":
        analyze_drivers(df)
    
    elif menu == "⭐ Favoris":
        from favorites_system import display_favorites_manager
        display_favorites_manager(df)
    
    elif menu == "💰 Suivi ROI":
        from betting_interface import display_roi_analysis
        display_roi_analysis()
    
    elif menu == "⚙️ Config Borda":
        from borda_configuration_interface import display_borda_configuration_interface
        display_borda_configuration_interface(df)
    
    elif menu == "🌍 Courses Étrangères":
        from foreign_races_system import display_foreign_races_manager
        display_foreign_races_manager()
    
    elif menu == "📈 Performances" and not has_borda:
        analyze_performances(df)
    
    elif menu == "🔍 Recherche":
        advanced_search(df)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Turf BZH Dashboard v1.0**")
    st.sidebar.markdown(f"Données: {len(df)} courses analysées")

if __name__ == "__main__":
    main()
