"""
🎯 INTERFACE DE CONFIGURATION BORDA AVANCÉE
Création, modification et recommandations automatiques de systèmes Borda
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class BordaConfigurationSystem:
    """Système de configuration avancée des Borda"""
    
    def __init__(self):
        self.config_dir = Path.home() / "bordasAnalyse" / "borda_configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.configs_file = self.config_dir / "custom_bordas.json"
        self.load_configs()
        
        # Critères disponibles avec poids min/max
        self.available_criteria = {
            'ELO Cheval': {'min': 0, 'max': 100, 'default': 30, 'unit': 'points'},
            'ELO Jockey': {'min': 0, 'max': 100, 'default': 25, 'unit': 'points'},
            'ELO Entraineur': {'min': 0, 'max': 100, 'default': 20, 'unit': 'points'},
            'Age': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'ELO Propriétaire': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'ELO Éleveur': {'min': 0, 'max': 50, 'default': 5, 'unit': 'points'},
            'Sigma': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Turf Points': {'min': 0, 'max': 100, 'default': 30, 'unit': 'points'},
            'Gains Course': {'min': 0, 'max': 100, 'default': 25, 'unit': 'points'},
            'Gains Totaux': {'min': 0, 'max': 100, 'default': 20, 'unit': 'points'},
            'Moyenne Alloc': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Chrono Record': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'Top 1 IA': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'Top 2 IA': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Top 3 IA': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'Top 4 IA': {'min': 0, 'max': 50, 'default': 8, 'unit': 'points'},
            'Top 5 IA': {'min': 0, 'max': 50, 'default': 5, 'unit': 'points'},
            'Nb Courses': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'Repos': {'min': 0, 'max': 30, 'default': 10, 'unit': 'points'},
            'Cote dernière course': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Taux de Victoire': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'Taux de Place': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            "Taux d'Incident": {'min': 0, 'max': 30, 'default': 5, 'unit': 'points'},
            'Popularité': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Note IA': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'Cote PMU': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Cote BZH': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'Rang J': {'min': 0, 'max': 30, 'default': 10, 'unit': 'points'},
            'TPJ 365': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'TPJ 90': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'Moy TPJ 365': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Moy TPJ 90': {'min': 0, 'max': 50, 'default': 20, 'unit': 'points'},
            'TPch 90': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Moy TPch 365': {'min': 0, 'max': 50, 'default': 10, 'unit': 'points'},
            'Moy TPch 90': {'min': 0, 'max': 50, 'default': 15, 'unit': 'points'},
            'Synergie Jch': {'min': 0, 'max': 30, 'default': 10, 'unit': 'points'},
        }
    
    def load_configs(self):
        """Charge les configurations personnalisées"""
        if self.configs_file.exists():
            with open(self.configs_file, 'r') as f:
                self.custom_configs = json.load(f)
        else:
            self.custom_configs = {}
    
    def save_configs(self):
        """Sauvegarde les configurations"""
        with open(self.configs_file, 'w') as f:
            json.dump(self.custom_configs, f, indent=2)
    
    def get_hippodrome_recommendations(self, hippodrome, discipline):
        """
        Génère des recommandations de critères Borda pour un hippodrome/discipline
        
        Returns:
            Dict avec critères recommandés et leurs poids
        """
        hippo_lower = hippodrome.lower() if hippodrome else ''
        disc = discipline.upper() if discipline else 'A'
        
        # Recommandations par hippodrome
        if 'vincennes' in hippo_lower or 'vincenne' in hippo_lower:
            if disc == 'A':  # Attelé
                return {
                    'name': f'Vincennes Attelé Recommandé',
                    'criteria': {
                        'ELO Cheval': 35,
                        'ELO Jockey': 30,
                        'ELO Entraineur': 25,
                        'Turf Points': 30,
                        'Top 1 IA': 25,
                        'Top 2 IA': 20,
                        'Cote BZH': 25,
                        'Taux de Victoire': 25,
                        'Gains Totaux': 20,
                        'Popularité': 15,
                        'Repos': 10,
                        'TPJ 90': 20,
                        'Synergie Jch': 15,
                    },
                    'total': 300
                }
            elif disc == 'M':  # Monté
                return {
                    'name': f'Vincennes Monté Recommandé',
                    'criteria': {
                        'ELO Cheval': 30,
                        'ELO Jockey': 35,
                        'ELO Entraineur': 25,
                        'Turf Points': 30,
                        'Top 1 IA': 25,
                        'Cote BZH': 20,
                        'Taux de Victoire': 20,
                        'Gains Course': 25,
                        'Popularité': 20,
                        'Age': 15,
                        'TPJ 90': 25,
                        'Chrono Record': 10,
                    },
                    'total': 300
                }
        
        elif 'pau' in hippo_lower:
            return {
                'name': f'Pau {disc} Recommandé',
                'criteria': {
                    'ELO Cheval': 30,
                    'ELO Jockey': 25,
                    'ELO Entraineur': 20,
                    'Turf Points': 35,
                    'Top 1 IA': 20,
                    'Top 2 IA': 15,
                    'Cote BZH': 20,
                    'Taux de Place': 20,
                    'Gains Course': 30,
                    'Repos': 15,
                    'TPJ 365': 20,
                    'Moyenne Alloc': 15,
                    'Popularité': 10,
                },
                'total': 300
            }
        
        elif 'cagne' in hippo_lower:
            return {
                'name': f'Cagnes-sur-Mer {disc} Recommandé',
                'criteria': {
                    'ELO Cheval': 30,
                    'ELO Jockey': 30,
                    'ELO Entraineur': 25,
                    'Turf Points': 30,
                    'Top 1 IA': 25,
                    'Cote BZH': 25,
                    'Taux de Victoire': 20,
                    'Gains Totaux': 25,
                    'TPJ 90': 20,
                    'Sigma': 15,
                    'Popularité': 15,
                    'Note IA': 20,
                },
                'total': 300
            }
        
        elif 'deauville' in hippo_lower:
            return {
                'name': f'Deauville Galop Recommandé',
                'criteria': {
                    'ELO Cheval': 35,
                    'ELO Jockey': 30,
                    'ELO Entraineur': 25,
                    'ELO Propriétaire': 15,
                    'Turf Points': 30,
                    'Top 1 IA': 25,
                    'Cote BZH': 20,
                    'Gains Totaux': 30,
                    'Taux de Victoire': 20,
                    'Age': 15,
                    'Chrono Record': 15,
                    'TPJ 365': 20,
                },
                'total': 300
            }
        
        elif any(x in hippo_lower for x in ['bousc', 'bouscat']):
            return {
                'name': f'Le Bouscat Recommandé',
                'criteria': {
                    'ELO Cheval': 30,
                    'ELO Jockey': 25,
                    'ELO Entraineur': 20,
                    'Turf Points': 30,
                    'Top 1 IA': 20,
                    'Cote BZH': 25,
                    'Taux de Place': 25,
                    'Gains Course': 25,
                    'Repos': 15,
                    'TPJ 90': 25,
                    'Popularité': 15,
                    'Moyenne Alloc': 15,
                    'Nb Courses': 10,
                },
                'total': 300
            }
        
        else:
            # Configuration par défaut
            return {
                'name': f'Borda par Défaut',
                'criteria': {
                    'ELO Cheval': 30,
                    'ELO Jockey': 25,
                    'ELO Entraineur': 20,
                    'Turf Points': 30,
                    'Top 1 IA': 20,
                    'Top 2 IA': 15,
                    'Cote BZH': 20,
                    'Taux de Victoire': 20,
                    'Gains Course': 25,
                    'Popularité': 15,
                    'TPJ 90': 20,
                    'Repos': 10,
                    'Sigma': 15,
                    'Note IA': 15,
                },
                'total': 300
            }
    
    def create_or_update_config(self, name, criteria_weights, hippodrome=None, discipline=None, nb_partants_range=None):
        """Crée ou met à jour une configuration Borda"""
        
        config_id = name.lower().replace(' ', '_')
        
        self.custom_configs[config_id] = {
            'name': name,
            'criteria': criteria_weights,
            'hippodrome': hippodrome,
            'discipline': discipline,
            'nb_partants_range': nb_partants_range,
            'created_at': datetime.now().isoformat(),
            'total_points': sum(criteria_weights.values())
        }
        
        self.save_configs()
        
        return config_id
    
    def delete_config(self, config_id):
        """Supprime une configuration"""
        if config_id in self.custom_configs:
            del self.custom_configs[config_id]
            self.save_configs()
            return True
        return False
    
    def detect_missing_bordas(self, df):
        """
        Détecte les combinaisons hippodrome/discipline sans Borda correspondant
        
        Returns:
            List[Dict] avec les configurations manquantes
        """
        missing = []
        
        if 'hippodrome' not in df.columns or 'discipline' not in df.columns:
            return missing
        
        # Grouper par hippodrome et discipline
        unique_combos = df.groupby(['hippodrome', 'discipline']).size().reset_index(name='count')
        
        for _, row in unique_combos.iterrows():
            hippo = row['hippodrome']
            disc = row['discipline']
            count = row['count']
            
            # Vérifier si un Borda existe pour cette combo
            config_name = f"{hippo}_{disc}".lower().replace(' ', '_')
            
            if config_name not in self.custom_configs:
                missing.append({
                    'hippodrome': hippo,
                    'discipline': disc,
                    'nb_courses': count,
                    'config_name': config_name
                })
        
        return missing


def display_borda_configuration_interface(df=None):
    """Interface complète de configuration Borda"""
    
    st.header("🎯 Configuration Avancée des Systèmes Borda")
    
    # Initialiser le système
    if 'borda_config_system' not in st.session_state:
        st.session_state.borda_config_system = BordaConfigurationSystem()
    
    config_system = st.session_state.borda_config_system
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Mes Configurations",
        "➕ Créer/Modifier",
        "🔍 Détection Manquants",
        "💡 Recommandations"
    ])
    
    with tab1:
        st.subheader("📋 Configurations Borda Existantes")
        
        if len(config_system.custom_configs) == 0:
            st.info("💡 Aucune configuration personnalisée. Créez-en une dans l'onglet 'Créer/Modifier' !")
        else:
            for config_id, config in config_system.custom_configs.items():
                with st.expander(f"⚙️ {config['name']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Hippodrome:** {config.get('hippodrome', 'Tous')}")
                        st.write(f"**Discipline:** {config.get('discipline', 'Toutes')}")
                        st.write(f"**Partants:** {config.get('nb_partants_range', 'Tous')}")
                        st.write(f"**Total points:** {config['total_points']}")
                        
                        # Afficher les critères
                        st.markdown("**Critères actifs:**")
                        criteria_df = pd.DataFrame([
                            {'Critère': k, 'Points': v}
                            for k, v in config['criteria'].items()
                        ]).sort_values('Points', ascending=False)
                        
                        st.dataframe(criteria_df, hide_index=True)
                    
                    with col2:
                        if st.button("✏️ Modifier", key=f"edit_{config_id}"):
                            st.session_state.editing_config = config_id
                            st.rerun()
                        
                        if st.button("🗑️ Supprimer", key=f"del_{config_id}"):
                            config_system.delete_config(config_id)
                            st.success(f"✅ Configuration '{config['name']}' supprimée")
                            st.rerun()
    
    with tab2:
        st.subheader("➕ Créer ou Modifier une Configuration")
        
        # Formulaire
        col1, col2, col3 = st.columns(3)
        
        with col1:
            config_name = st.text_input("Nom de la configuration *", 
                                       placeholder="Ex: Vincennes Attelé 12-14",
                                       key="config_name_input")
        
        with col2:
            hippo_input = st.text_input("Hippodrome", 
                                       placeholder="Ex: Paris-Vincennes",
                                       key="hippo_config_input")
        
        with col3:
            disc_input = st.selectbox("Discipline", ['Tous', 'A', 'M', 'P'], key="disc_config_input")
        
        st.markdown("### 🎛️ Sélection des Critères")
        
        st.info("""
        💡 **Instructions:**
        - Cochez les critères que vous voulez utiliser
        - Ajustez les points pour chaque critère
        - Le total doit être proche de 300 points pour un Borda standard
        """)
        
        # Initialiser la sélection
        if 'borda_criteria_selection' not in st.session_state:
            st.session_state.borda_criteria_selection = {}
        
        # Afficher les critères par catégories
        categories = {
            'ELO': ['ELO Cheval', 'ELO Jockey', 'ELO Entraineur', 'ELO Propriétaire', 'ELO Éleveur'],
            'Performance': ['Turf Points', 'Gains Course', 'Gains Totaux', 'Taux de Victoire', 'Taux de Place'],
            'IA': ['Top 1 IA', 'Top 2 IA', 'Top 3 IA', 'Top 4 IA', 'Top 5 IA', 'Note IA'],
            'Cotes': ['Cote BZH', 'Cote PMU', 'Popularité'],
            'Forme': ['Repos', 'Nb Courses', 'Chrono Record', 'Age'],
            'TPJ/TPch': ['TPJ 365', 'TPJ 90', 'Moy TPJ 365', 'Moy TPJ 90', 'TPch 90', 'Moy TPch 365', 'Moy TPch 90'],
            'Autres': ['Sigma', 'Moyenne Alloc', 'Rang J', 'Synergie Jch', "Taux d'Incident", 'Cote dernière course']
        }
        
        selected_criteria = {}
        total_points = 0
        
        for category, criteria_list in categories.items():
            with st.expander(f"📊 {category}", expanded=(category in ['ELO', 'Performance'])):
                cols = st.columns(2)
                
                for idx, criterion in enumerate(criteria_list):
                    if criterion in config_system.available_criteria:
                        info = config_system.available_criteria[criterion]
                        
                        with cols[idx % 2]:
                            use_criterion = st.checkbox(
                                criterion,
                                key=f"use_{criterion}",
                                value=criterion in st.session_state.borda_criteria_selection
                            )
                            
                            if use_criterion:
                                points = st.slider(
                                    f"Points pour {criterion}",
                                    min_value=info['min'],
                                    max_value=info['max'],
                                    value=st.session_state.borda_criteria_selection.get(criterion, info['default']),
                                    step=5,
                                    key=f"points_{criterion}",
                                    label_visibility="collapsed"
                                )
                                
                                selected_criteria[criterion] = points
                                total_points += points
        
        # Afficher le total
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Points", f"{total_points}/300")
        
        with col2:
            st.metric("Critères Sélectionnés", len(selected_criteria))
        
        with col3:
            if total_points < 250:
                st.warning("⚠️ Total faible")
            elif total_points > 350:
                st.warning("⚠️ Total élevé")
            else:
                st.success("✅ Total OK")
        
        # Bouton de sauvegarde
        if st.button("💾 SAUVEGARDER LA CONFIGURATION", type="primary", use_container_width=True):
            if config_name and len(selected_criteria) > 0:
                config_id = config_system.create_or_update_config(
                    name=config_name,
                    criteria_weights=selected_criteria,
                    hippodrome=hippo_input if hippo_input else None,
                    discipline=disc_input if disc_input != 'Tous' else None
                )
                
                st.success(f"✅ Configuration '{config_name}' sauvegardée !")
                st.session_state.borda_criteria_selection = {}
                st.rerun()
            else:
                st.error("❌ Veuillez renseigner un nom et sélectionner au moins un critère")
    
    with tab3:
        st.subheader("🔍 Détection des Borda Manquants")
        
        if df is None or len(df) == 0:
            st.warning("⚠️ Aucun fichier chargé. Chargez un export pour détecter les Borda manquants.")
        else:
            missing = config_system.detect_missing_bordas(df)
            
            if len(missing) == 0:
                st.success("✅ Tous les hippodromes/disciplines ont un Borda correspondant !")
            else:
                st.warning(f"⚠️ {len(missing)} configuration(s) manquante(s) détectée(s)")
                
                for item in missing:
                    with st.container():
                        st.markdown(f"""
                        <div style='border: 2px solid orange; border-radius: 10px; padding: 15px; margin-bottom: 10px;'>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### 🏟️ {item['hippodrome']} - {item['discipline']}")
                            st.write(f"**Courses concernées:** {item['nb_courses']}")
                        
                        with col2:
                            if st.button("🚀 Créer Borda", key=f"create_{item['config_name']}"):
                                # Générer la recommandation
                                reco = config_system.get_hippodrome_recommendations(
                                    item['hippodrome'],
                                    item['discipline']
                                )
                                
                                # Créer la config
                                config_system.create_or_update_config(
                                    name=reco['name'],
                                    criteria_weights=reco['criteria'],
                                    hippodrome=item['hippodrome'],
                                    discipline=item['discipline']
                                )
                                
                                st.success(f"✅ Borda créé : {reco['name']}")
                                st.rerun()
    
    with tab4:
        st.subheader("💡 Recommandations par Hippodrome")
        
        st.info("""
        Cette section vous permet de voir les recommandations de critères Borda optimisés
        pour chaque hippodrome et discipline.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            hippo_search = st.text_input("Hippodrome", placeholder="Ex: Paris-Vincennes", key="hippo_reco_search")
        
        with col2:
            disc_search = st.selectbox("Discipline", ['A', 'M', 'P'], key="disc_reco_search")
        
        if st.button("🔍 Voir les Recommandations", type="primary", key="btn_view_reco"):
            if hippo_search:
                reco = config_system.get_hippodrome_recommendations(hippo_search, disc_search)
                
                st.success(f"✅ Recommandations pour **{reco['name']}**")
                
                # Afficher les critères recommandés
                st.markdown("### 📊 Critères Recommandés")
                
                reco_df = pd.DataFrame([
                    {'Critère': k, 'Points': v}
                    for k, v in reco['criteria'].items()
                ]).sort_values('Points', ascending=False)
                
                st.dataframe(reco_df, hide_index=True, use_container_width=True)
                
                st.metric("Total Points", reco['total'])
                
                # Bouton pour créer directement
                if st.button("💾 Créer cette Configuration", type="secondary"):
                    config_system.create_or_update_config(
                        name=reco['name'],
                        criteria_weights=reco['criteria'],
                        hippodrome=hippo_search,
                        discipline=disc_search
                    )
                    st.success(f"✅ Configuration créée : {reco['name']}")
                    st.rerun()
