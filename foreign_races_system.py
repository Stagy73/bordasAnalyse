"""
🌍 SYSTÈME D'IMPORT COURSES ÉTRANGÈRES + AUTO-BORDA
Import de toutes les courses + Création automatique de systèmes Borda optimisés
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime


class ForeignRaceImporter:
    """Importateur de courses étrangères"""
    
    def __init__(self):
        self.supported_countries = [
            'France', 'Belgique', 'Allemagne', 'Espagne', 'Italie', 
            'Angleterre', 'Irlande', 'Suède', 'Norvège', 'USA', 
            'Dubai', 'Japon', 'Australie', 'Afrique du Sud'
        ]
    
    def detect_race_origin(self, hippodrome_name):
        """Détecte le pays d'origine d'une course"""
        if not hippodrome_name or pd.isna(hippodrome_name):
            return 'France'
        
        hippo_lower = hippodrome_name.lower()
        
        # Mapping des hippodromes connus
        foreign_hippodromes = {
            'Belgique': ['mons', 'ostende', 'sterrebeek', 'waregem', 'tournai'],
            'Allemagne': ['hamburg', 'düsseldorf', 'cologne', 'munich', 'berlin'],
            'Espagne': ['madrid', 'san sebastian', 'dos hermanas'],
            'Italie': ['rome', 'milan', 'naples', 'turin', 'agnano'],
            'Angleterre': ['ascot', 'epsom', 'newmarket', 'cheltenham', 'kempton'],
            'Irlande': ['curragh', 'leopardstown', 'fairyhouse', 'punchestown'],
            'Suède': ['solvalla', 'jägersro', 'aby', 'bergsaker'],
            'USA': ['churchill', 'belmont', 'santa anita', 'gulfstream'],
            'Dubai': ['meydan'],
            'Japon': ['tokyo', 'hanshin', 'kyoto'],
            'Australie': ['flemington', 'randwick', 'moonee'],
        }
        
        for country, hippos in foreign_hippodromes.items():
            if any(h in hippo_lower for h in hippos):
                return country
        
        return 'France'
    
    def enrich_data_with_country(self, df):
        """Ajoute la colonne pays au DataFrame"""
        if 'hippodrome' in df.columns:
            df['pays'] = df['hippodrome'].apply(self.detect_race_origin)
        return df


class AutoBordaGenerator:
    """Générateur automatique de systèmes Borda optimisés"""
    
    def __init__(self):
        self.borda_systems = {}
        self.config_file = Path.home() / "bordasAnalyse" / "auto_borda_systems.json"
        self.load_systems()
    
    def load_systems(self):
        """Charge les systèmes Borda existants"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.borda_systems = json.load(f)
    
    def save_systems(self):
        """Sauvegarde les systèmes Borda"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.borda_systems, f, indent=2)
    
    def generate_borda_key(self, hippodrome, discipline, nb_partants_range):
        """Génère une clé unique pour un système Borda"""
        hippo_norm = hippodrome.lower().strip() if hippodrome else 'default'
        disc_norm = discipline.upper() if discipline else 'X'
        return f"{hippo_norm}_{disc_norm}_{nb_partants_range}"
    
    def calculate_optimal_borda(self, historical_races):
        """
        Calcule le système Borda optimal pour un ensemble de courses
        
        Args:
            historical_races: DataFrame avec les courses historiques
        
        Returns:
            Dict avec les poids optimaux par critère
        """
        if len(historical_races) < 10:
            # Pas assez de données, utiliser les poids par défaut
            return self._get_default_weights()
        
        # Analyser les corrélations entre différents critères et le résultat
        weights = {}
        
        # 1. Popularité
        if 'Popularite' in historical_races.columns and 'ordre_arrivee' in historical_races.columns:
            corr_pop = historical_races['Popularite'].corr(historical_races['ordre_arrivee'])
            weights['popularite'] = max(0.1, min(0.3, abs(corr_pop)))
        else:
            weights['popularite'] = 0.2
        
        # 2. Cote
        if 'Cote' in historical_races.columns and 'ordre_arrivee' in historical_races.columns:
            # Cote optimale entre 3 et 15
            optimal_cotes = historical_races[
                (historical_races['Cote'] >= 3) & 
                (historical_races['Cote'] <= 15) &
                (historical_races['ordre_arrivee'] <= 3)
            ]
            
            if len(optimal_cotes) > len(historical_races) * 0.3:
                weights['cote'] = 0.25
            else:
                weights['cote'] = 0.15
        else:
            weights['cote'] = 0.2
        
        # 3. Gains historiques
        if 'Gains Totaux' in historical_races.columns:
            weights['gains'] = 0.2
        else:
            weights['gains'] = 0.15
        
        # 4. Place à la corde
        if 'place_corde' in historical_races.columns or 'Numero' in historical_races.columns:
            weights['corde'] = 0.15
        else:
            weights['corde'] = 0.1
        
        # 5. Forme récente (musique)
        weights['forme'] = 0.2
        
        # Normaliser pour que la somme = 1
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        return weights
    
    def _get_default_weights(self):
        """Retourne les poids par défaut"""
        return {
            'popularite': 0.20,
            'cote': 0.20,
            'gains': 0.20,
            'corde': 0.15,
            'forme': 0.25
        }
    
    def create_borda_system(self, hippodrome, discipline, nb_partants_range, historical_data=None):
        """
        Crée un nouveau système Borda pour un hippodrome/discipline
        
        Args:
            hippodrome: Nom de l'hippodrome
            discipline: A, M ou P
            nb_partants_range: Ex: "8-10", "10-12", etc.
            historical_data: DataFrame optionnel avec données historiques
        
        Returns:
            system_key, weights
        """
        system_key = self.generate_borda_key(hippodrome, discipline, nb_partants_range)
        
        # Calculer les poids optimaux
        if historical_data is not None and len(historical_data) > 0:
            weights = self.calculate_optimal_borda(historical_data)
        else:
            weights = self._get_default_weights()
        
        # Sauvegarder le système
        self.borda_systems[system_key] = {
            'hippodrome': hippodrome,
            'discipline': discipline,
            'nb_partants_range': nb_partants_range,
            'weights': weights,
            'created_at': datetime.now().isoformat(),
            'nb_races_analyzed': len(historical_data) if historical_data is not None else 0
        }
        
        self.save_systems()
        
        return system_key, weights
    
    def get_or_create_borda(self, hippodrome, discipline, nb_partants, historical_data=None):
        """
        Récupère un système Borda existant ou en crée un nouveau
        
        Args:
            nb_partants: Nombre exact de partants (sera converti en range)
        """
        # Déterminer la tranche de partants
        if nb_partants < 8:
            range_str = "0-8"
        elif nb_partants < 10:
            range_str = "8-10"
        elif nb_partants < 12:
            range_str = "10-12"
        elif nb_partants < 14:
            range_str = "12-14"
        elif nb_partants < 16:
            range_str = "14-16"
        else:
            range_str = "16+"
        
        system_key = self.generate_borda_key(hippodrome, discipline, range_str)
        
        # Vérifier si le système existe
        if system_key in self.borda_systems:
            return system_key, self.borda_systems[system_key]['weights'], False
        
        # Créer un nouveau système
        system_key, weights = self.create_borda_system(
            hippodrome, discipline, range_str, historical_data
        )
        
        return system_key, weights, True
    
    def calculate_borda_score(self, horse_data, weights):
        """
        Calcule le score Borda pour un cheval selon les poids
        
        Args:
            horse_data: Series avec les données du cheval
            weights: Dict avec les poids par critère
        """
        score = 0
        
        # 1. Popularité (inversé: 1 = meilleur)
        if 'Popularite' in horse_data.index and pd.notna(horse_data['Popularite']):
            pop_score = (20 - min(horse_data['Popularite'], 20)) / 20 * 100
            score += pop_score * weights.get('popularite', 0.2)
        
        # 2. Cote (optimal 3-15)
        if 'Cote' in horse_data.index and pd.notna(horse_data['Cote']):
            cote = horse_data['Cote']
            if 3 <= cote <= 15:
                cote_score = 100
            elif cote < 3:
                cote_score = 70
            else:
                cote_score = 50
            score += cote_score * weights.get('cote', 0.2)
        
        # 3. Gains historiques
        if 'Gains Totaux' in horse_data.index and pd.notna(horse_data['Gains Totaux']):
            # Normaliser sur 100000€
            gains_score = min(horse_data['Gains Totaux'] / 100000, 1) * 100
            score += gains_score * weights.get('gains', 0.2)
        
        # 4. Place à la corde (numéro bas = avantage)
        if 'Numero' in horse_data.index and pd.notna(horse_data['Numero']):
            corde_score = max(0, 100 - (horse_data['Numero'] * 5))
            score += corde_score * weights.get('corde', 0.15)
        
        # 5. Forme récente (musique)
        if 'Musique' in horse_data.index and pd.notna(horse_data['Musique']):
            musique = str(horse_data['Musique'])
            # Compter les bonnes places (1, 2, 3) dans les 5 dernières courses
            recent = musique[:10]  # 5 dernières courses environ
            bonnes_places = sum(1 for c in recent if c in ['1', '2', '3'])
            forme_score = (bonnes_places / 5) * 100 if len(recent) >= 5 else 50
            score += forme_score * weights.get('forme', 0.25)
        
        return min(score, 300)  # Score Borda max = 300


def display_foreign_races_manager():
    """Interface de gestion des courses étrangères"""
    
    st.header("🌍 Gestion des Courses Étrangères")
    
    # Initialiser les systèmes
    if 'foreign_importer' not in st.session_state:
        st.session_state.foreign_importer = ForeignRaceImporter()
    
    if 'auto_borda' not in st.session_state:
        st.session_state.auto_borda = AutoBordaGenerator()
    
    importer = st.session_state.foreign_importer
    auto_borda = st.session_state.auto_borda
    
    st.info("""
    💡 **Ce module permet de :**
    - Importer des courses de tous les pays
    - Créer automatiquement des systèmes Borda optimisés
    - Analyser les performances par hippodrome/discipline
    """)
    
    # Afficher les systèmes Borda existants
    st.subheader("📊 Systèmes Borda Créés")
    
    if len(auto_borda.borda_systems) == 0:
        st.info("💡 Aucun système Borda auto-généré pour le moment")
    else:
        systems_df = pd.DataFrame([
            {
                'Système': key,
                'Hippodrome': sys['hippodrome'],
                'Discipline': sys['discipline'],
                'Partants': sys['nb_partants_range'],
                'Courses Analysées': sys['nb_races_analyzed'],
                'Date Création': sys['created_at'][:10]
            }
            for key, sys in auto_borda.borda_systems.items()
        ])
        
        st.dataframe(systems_df, width="stretch", height=400)
    
    st.markdown("---")
    
    # Créer un nouveau système manuellement
    st.subheader("➕ Créer un Système Borda")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hippo_input = st.text_input("Hippodrome")
    
    with col2:
        disc_input = st.selectbox("Discipline", ['A', 'M', 'P'])
    
    with col3:
        range_input = st.selectbox("Nb Partants", ['0-8', '8-10', '10-12', '12-14', '14-16', '16+'])
    
    if st.button("🚀 Créer le Système", type="primary"):
        if hippo_input:
            system_key, weights = auto_borda.create_borda_system(
                hippo_input, disc_input, range_input
            )
            
            st.success(f"✅ Système créé: {system_key}")
            
            # Afficher les poids
            st.json(weights)
            
            st.rerun()
        else:
            st.error("❌ Veuillez renseigner l'hippodrome")
