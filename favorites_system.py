"""
⭐ SYSTÈME DE GESTION DES FAVORIS
Chevaux + Drivers + Analyse des performances combinées
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class FavoritesManager:
    """Gestionnaire de favoris (chevaux et drivers)"""
    
    def __init__(self, storage_dir="favoris"):
        self.storage_dir = Path.home() / "bordasAnalyse" / storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.favorites_file = self.storage_dir / "favoris.json"
        self.load_favorites()
    
    def load_favorites(self):
        """Charge les favoris"""
        if self.favorites_file.exists():
            with open(self.favorites_file, 'r') as f:
                data = json.load(f)
                self.horses = data.get('horses', [])
                self.drivers = data.get('drivers', [])
        else:
            self.horses = []
            self.drivers = []
    
    def save_favorites(self):
        """Sauvegarde les favoris"""
        with open(self.favorites_file, 'w') as f:
            json.dump({
                'horses': self.horses,
                'drivers': self.drivers
            }, f, indent=2)
    
    def add_horse(self, nom, proprietaire=None, entraineur=None, notes=""):
        """Ajoute un cheval aux favoris"""
        horse_id = nom.lower().strip()
        
        if horse_id not in [h['id'] for h in self.horses]:
            self.horses.append({
                'id': horse_id,
                'nom': nom,
                'proprietaire': proprietaire,
                'entraineur': entraineur,
                'notes': notes,
                'date_ajout': datetime.now().isoformat()
            })
            self.save_favorites()
            return True, f"✅ {nom} ajouté aux favoris"
        
        return False, f"⚠️ {nom} est déjà dans les favoris"
    
    def remove_horse(self, horse_id):
        """Retire un cheval des favoris"""
        self.horses = [h for h in self.horses if h['id'] != horse_id]
        self.save_favorites()
    
    def add_driver(self, nom, type_driver='jockey', specialite=None, notes=""):
        """Ajoute un driver aux favoris"""
        driver_id = nom.lower().strip()
        
        if driver_id not in [d['id'] for d in self.drivers]:
            self.drivers.append({
                'id': driver_id,
                'nom': nom,
                'type': type_driver,  # 'jockey' ou 'entraineur'
                'specialite': specialite,
                'notes': notes,
                'date_ajout': datetime.now().isoformat()
            })
            self.save_favorites()
            return True, f"✅ {nom} ajouté aux favoris"
        
        return False, f"⚠️ {nom} est déjà dans les favoris"
    
    def remove_driver(self, driver_id):
        """Retire un driver des favoris"""
        self.drivers = [d for d in self.drivers if d['id'] != driver_id]
        self.save_favorites()
    
    def is_favorite_horse(self, nom):
        """Vérifie si un cheval est favori"""
        return nom.lower().strip() in [h['id'] for h in self.horses]
    
    def is_favorite_driver(self, nom):
        """Vérifie si un driver est favori"""
        return nom.lower().strip() in [d['id'] for d in self.drivers]


class PerformanceAnalyzer:
    """Analyseur de performances Driver+Cheval"""
    
    def __init__(self, historical_data=None):
        """
        Args:
            historical_data: DataFrame avec l'historique des courses
        """
        self.data = historical_data
    
    def analyze_driver_horse_combo(self, driver_name, horse_name):
        """
        Analyse les performances d'une combinaison Driver+Cheval
        
        Returns:
            Dict avec statistiques détaillées
        """
        if self.data is None or len(self.data) == 0:
            return None
        
        # Normaliser les noms
        driver_norm = driver_name.lower().strip()
        horse_norm = horse_name.lower().strip()
        
        # Filtrer les courses où le duo a couru ensemble
        mask = (
            (self.data['Driver'].str.lower().str.strip() == driver_norm) &
            (self.data['Cheval'].str.lower().str.strip() == horse_norm)
        )
        
        combo_races = self.data[mask]
        
        if len(combo_races) == 0:
            return {
                'found': False,
                'message': f"Aucune course trouvée pour {driver_name} + {horse_name}"
            }
        
        # Calculer les statistiques
        total_courses = len(combo_races)
        
        # Victoires (ordre_arrivee == 1)
        if 'ordre_arrivee' in combo_races.columns:
            victoires = len(combo_races[combo_races['ordre_arrivee'] == 1])
            places = len(combo_races[combo_races['ordre_arrivee'] <= 3])
        else:
            # Fallback si pas d'ordre d'arrivée
            victoires = 0
            places = 0
        
        taux_victoire = (victoires / total_courses * 100) if total_courses > 0 else 0
        taux_place = (places / total_courses * 100) if total_courses > 0 else 0
        
        # Gains moyens
        if 'Gains Course' in combo_races.columns:
            gains_moyen = combo_races['Gains Course'].mean()
            gains_total = combo_races['Gains Course'].sum()
        else:
            gains_moyen = 0
            gains_total = 0
        
        # Dernières courses
        recent_races = combo_races.tail(5)
        
        return {
            'found': True,
            'driver': driver_name,
            'horse': horse_name,
            'total_courses': total_courses,
            'victoires': victoires,
            'places': places,
            'taux_victoire': round(taux_victoire, 1),
            'taux_place': round(taux_place, 1),
            'gains_moyen': round(gains_moyen, 2),
            'gains_total': round(gains_total, 2),
            'recent_races': recent_races.to_dict('records') if len(recent_races) > 0 else []
        }
    
    def get_driver_best_horses(self, driver_name, top_n=10):
        """Retourne les meilleurs chevaux d'un driver"""
        if self.data is None:
            return None
        
        driver_norm = driver_name.lower().strip()
        driver_races = self.data[self.data['Driver'].str.lower().str.strip() == driver_norm]
        
        if len(driver_races) == 0:
            return None
        
        # Grouper par cheval
        horse_stats = driver_races.groupby('Cheval').agg({
            'ordre_arrivee': lambda x: (x == 1).sum() if 'ordre_arrivee' in driver_races.columns else 0,
            'Gains Course': 'sum' if 'Gains Course' in driver_races.columns else lambda x: 0
        }).reset_index()
        
        horse_stats.columns = ['Cheval', 'Victoires', 'Gains_Total']
        horse_stats = horse_stats.sort_values('Victoires', ascending=False).head(top_n)
        
        return horse_stats
    
    def get_horse_best_drivers(self, horse_name, top_n=10):
        """Retourne les meilleurs drivers d'un cheval"""
        if self.data is None:
            return None
        
        horse_norm = horse_name.lower().strip()
        horse_races = self.data[self.data['Cheval'].str.lower().str.strip() == horse_norm]
        
        if len(horse_races) == 0:
            return None
        
        # Grouper par driver
        driver_stats = horse_races.groupby('Driver').agg({
            'ordre_arrivee': lambda x: (x == 1).sum() if 'ordre_arrivee' in horse_races.columns else 0,
            'Gains Course': 'sum' if 'Gains Course' in horse_races.columns else lambda x: 0
        }).reset_index()
        
        driver_stats.columns = ['Driver', 'Victoires', 'Gains_Total']
        driver_stats = driver_stats.sort_values('Victoires', ascending=False).head(top_n)
        
        return driver_stats


def display_favorites_manager(historical_data=None):
    """Interface de gestion des favoris"""
    
    st.header("⭐ Gestion des Favoris")
    
    # Initialiser le gestionnaire
    if 'favorites_manager' not in st.session_state:
        st.session_state.favorites_manager = FavoritesManager()
    
    manager = st.session_state.favorites_manager
    
    # Onglets
    tab1, tab2, tab3 = st.tabs([
        "🐴 Chevaux Favoris",
        "👨‍🏫 Drivers Favoris",
        "🔍 Analyse Combinaisons"
    ])
    
    with tab1:
        st.subheader("🐴 Mes Chevaux Favoris")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Liste des favoris
            if len(manager.horses) == 0:
                st.info("💡 Aucun cheval favori. Ajoutez-en un ci-dessous !")
            else:
                for horse in manager.horses:
                    with st.expander(f"⭐ {horse['nom']}", expanded=False):
                        st.write(f"**Propriétaire:** {horse.get('proprietaire', 'N/A')}")
                        st.write(f"**Entraîneur:** {horse.get('entraineur', 'N/A')}")
                        st.write(f"**Notes:** {horse.get('notes', 'Aucune note')}")
                        st.caption(f"Ajouté le: {horse['date_ajout'][:10]}")
                        
                        if st.button(f"🗑️ Retirer", key=f"remove_horse_{horse['id']}"):
                            manager.remove_horse(horse['id'])
                            st.success(f"✅ {horse['nom']} retiré des favoris")
                            st.rerun()
        
        with col2:
            # Ajouter un cheval
            st.markdown("### ➕ Ajouter un Cheval")
            
            with st.form("add_horse_form"):
                nom = st.text_input("Nom du cheval *")
                proprietaire = st.text_input("Propriétaire")
                entraineur = st.text_input("Entraîneur")
                notes = st.text_area("Notes")
                
                if st.form_submit_button("➕ Ajouter"):
                    if nom:
                        success, msg = manager.add_horse(nom, proprietaire, entraineur, notes)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                    else:
                        st.error("❌ Le nom est obligatoire")
    
    with tab2:
        st.subheader("👨‍🏫 Mes Drivers Favoris")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Liste des favoris
            if len(manager.drivers) == 0:
                st.info("💡 Aucun driver favori. Ajoutez-en un ci-dessous !")
            else:
                for driver in manager.drivers:
                    emoji = "🏇" if driver['type'] == 'jockey' else "👨‍🏫"
                    
                    with st.expander(f"{emoji} {driver['nom']}", expanded=False):
                        st.write(f"**Type:** {driver['type'].capitalize()}")
                        st.write(f"**Spécialité:** {driver.get('specialite', 'N/A')}")
                        st.write(f"**Notes:** {driver.get('notes', 'Aucune note')}")
                        st.caption(f"Ajouté le: {driver['date_ajout'][:10]}")
                        
                        if st.button(f"🗑️ Retirer", key=f"remove_driver_{driver['id']}"):
                            manager.remove_driver(driver['id'])
                            st.success(f"✅ {driver['nom']} retiré des favoris")
                            st.rerun()
        
        with col2:
            # Ajouter un driver
            st.markdown("### ➕ Ajouter un Driver")
            
            with st.form("add_driver_form"):
                nom = st.text_input("Nom *")
                type_driver = st.selectbox("Type", ['jockey', 'entraineur'])
                specialite = st.text_input("Spécialité")
                notes = st.text_area("Notes")
                
                if st.form_submit_button("➕ Ajouter"):
                    if nom:
                        success, msg = manager.add_driver(nom, type_driver, specialite, notes)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.warning(msg)
                    else:
                        st.error("❌ Le nom est obligatoire")
    
    with tab3:
        st.subheader("🔍 Analyse des Combinaisons Driver + Cheval")
        
        if historical_data is None or len(historical_data) == 0:
            st.warning("⚠️ Aucune donnée historique disponible pour l'analyse")
            return
        
        analyzer = PerformanceAnalyzer(historical_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            driver_name = st.text_input("Nom du Driver")
        
        with col2:
            horse_name = st.text_input("Nom du Cheval")
        
        if st.button("🔍 Analyser la Combinaison", type="primary"):
            if driver_name and horse_name:
                with st.spinner("Analyse en cours..."):
                    results = analyzer.analyze_driver_horse_combo(driver_name, horse_name)
                    
                    if results and results['found']:
                        st.success(f"✅ {results['total_courses']} courses trouvées pour ce duo")
                        
                        # Statistiques
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Courses", results['total_courses'])
                        with col2:
                            st.metric("Victoires", f"{results['victoires']} ({results['taux_victoire']}%)")
                        with col3:
                            st.metric("Top 3", f"{results['places']} ({results['taux_place']}%)")
                        with col4:
                            st.metric("Gains Moyen", f"{results['gains_moyen']:.0f}€")
                        
                        st.markdown("---")
                        
                        # Dernières courses
                        if results['recent_races']:
                            st.markdown("### 📋 5 Dernières Courses Ensemble")
                            
                            recent_df = pd.DataFrame(results['recent_races'])
                            display_cols = ['date', 'Course', 'hippodrome', 'ordre_arrivee', 'Gains Course']
                            available_cols = [col for col in display_cols if col in recent_df.columns]
                            
                            st.dataframe(recent_df[available_cols], width="stretch")
                    else:
                        st.warning(results['message'] if results else "❌ Aucune donnée trouvée")
            else:
                st.error("❌ Veuillez renseigner les deux noms")
        
        st.markdown("---")
        
        # Meilleurs chevaux d'un driver
        st.markdown("### 🏆 Top Chevaux par Driver")
        
        driver_search = st.text_input("Nom du Driver à analyser", key="driver_search")
        
        if st.button("🔍 Voir les meilleurs chevaux"):
            if driver_search:
                best_horses = analyzer.get_driver_best_horses(driver_search)
                
                if best_horses is not None and len(best_horses) > 0:
                    st.dataframe(best_horses, width="stretch")
                else:
                    st.warning("❌ Aucune donnée trouvée pour ce driver")
