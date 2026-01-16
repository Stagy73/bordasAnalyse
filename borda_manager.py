"""
📁 GESTIONNAIRE D'EXPORTS BORDA  
Système de gestion intégré pour sauvegarder et sélectionner les exports Borda
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import shutil


class BordaExportManager:
    """Gestionnaire d'exports Borda avec interface intégrée"""
    
    def __init__(self, storage_dir="borda_exports"):
        self.storage_dir = Path.home() / "bordasAnalyse" / storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.storage_dir / "config.json"
        self.load_config()
    
    def load_config(self):
        """Charge la configuration des exports"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'exports': [],
                'default': None
            }
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_export(self, file_path, name=None, set_as_default=False):
        """Ajoute un export Borda au gestionnaire"""
        try:
            # Lire le fichier pour vérifier qu'il contient des Borda
            df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig', nrows=5)
            borda_cols = [col for col in df.columns if 'Borda' in col]
            
            if len(borda_cols) == 0:
                return False, "❌ Ce fichier ne contient pas de colonnes Borda"
            
            # Générer un identifiant unique
            export_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Nom par défaut si non fourni
            if name is None:
                name = Path(file_path).stem if isinstance(file_path, str) else file_path.name.replace('.csv', '')
            
            # Copier le fichier dans le dossier de stockage
            dest_path = self.storage_dir / f"{export_id}.csv"
            
            if isinstance(file_path, str):
                shutil.copy2(file_path, dest_path)
            else:
                # C'est un objet UploadedFile de Streamlit
                with open(dest_path, 'wb') as f:
                    f.write(file_path.getvalue())
            
            # Ajouter à la configuration
            export_info = {
                'id': export_id,
                'name': name,
                'path': str(dest_path),
                'date_added': datetime.now().isoformat(),
                'num_borda': len(borda_cols),
                'size_kb': dest_path.stat().st_size / 1024
            }
            
            self.config['exports'].append(export_info)
            
            if set_as_default or self.config['default'] is None:
                self.config['default'] = export_id
            
            self.save_config()
            
            return True, f"✅ Export '{name}' ajouté ({len(borda_cols)} systèmes Borda)"
        
        except Exception as e:
            return False, f"❌ Erreur: {str(e)}"
    
    def get_export(self, export_id):
        """Récupère un export par son ID"""
        for exp in self.config['exports']:
            if exp['id'] == export_id:
                return exp
        return None
    
    def load_export_data(self, export_id):
        """Charge les données d'un export"""
        export = self.get_export(export_id)
        if export is None:
            return None, "Export non trouvé"
        
        try:
            df = pd.read_csv(export['path'], sep=';', encoding='utf-8-sig')
            return df, f"✅ {len(df)} lignes chargées"
        except Exception as e:
            return None, f"❌ Erreur: {str(e)}"
    
    def delete_export(self, export_id):
        """Supprime un export"""
        export = self.get_export(export_id)
        if export is None:
            return False, "Export non trouvé"
        
        try:
            # Supprimer le fichier
            Path(export['path']).unlink(missing_ok=True)
            
            # Retirer de la config
            self.config['exports'] = [e for e in self.config['exports'] if e['id'] != export_id]
            
            # Si c'était le défaut, choisir un autre
            if self.config['default'] == export_id:
                self.config['default'] = self.config['exports'][0]['id'] if self.config['exports'] else None
            
            self.save_config()
            
            return True, f"✅ Export '{export['name']}' supprimé"
        except Exception as e:
            return False, f"❌ Erreur: {str(e)}"
    
    def update_export_name(self, export_id, new_name):
        """Renomme un export"""
        for exp in self.config['exports']:
            if exp['id'] == export_id:
                exp['name'] = new_name
                self.save_config()
                return True, f"✅ Renommé en '{new_name}'"
        return False, "Export non trouvé"
    
    def set_default(self, export_id):
        """Définit un export comme défaut"""
        if self.get_export(export_id):
            self.config['default'] = export_id
            self.save_config()
            return True, "✅ Export par défaut mis à jour"
        return False, "Export non trouvé"
    
    def get_default_export(self):
        """Récupère l'export par défaut"""
        if self.config['default']:
            return self.get_export(self.config['default'])
        return None
    
    def list_exports(self):
        """Liste tous les exports"""
        return self.config['exports']


def display_borda_manager():
    """Interface de gestion des exports Borda dans la sidebar"""
    
    # Initialiser le gestionnaire
    if 'borda_manager' not in st.session_state:
        st.session_state.borda_manager = BordaExportManager()
    
    manager = st.session_state.borda_manager
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Exports Borda")
    
    exports = manager.list_exports()
    
    if len(exports) == 0:
        st.sidebar.info("💡 Aucun export Borda sauvegardé")
        
        # Bouton pour ajouter le premier
        with st.sidebar.expander("➕ Ajouter un export", expanded=True):
            uploaded = st.file_uploader(
                "Charger export Borda (CSV)",
                type=['csv'],
                key='borda_upload_initial'
            )
            
            if uploaded:
                col1, col2 = st.columns(2)
                
                with col1:
                    custom_name = st.text_input("Nom", value=uploaded.name.replace('.csv', ''))
                
                with col2:
                    if st.button("💾 Sauvegarder", type="primary"):
                        success, msg = manager.add_export(uploaded, custom_name, set_as_default=True)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        # Sélection de l'export
        export_names = {exp['name']: exp['id'] for exp in exports}
        default_export = manager.get_default_export()
        default_name = default_export['name'] if default_export else list(export_names.keys())[0]
        
        selected_name = st.sidebar.selectbox(
            "Sélectionner un export:",
            options=list(export_names.keys()),
            index=list(export_names.keys()).index(default_name) if default_name in export_names else 0,
            key='borda_export_selector'
        )
        
        selected_id = export_names[selected_name]
        selected_export = manager.get_export(selected_id)
        
        # Afficher les infos
        st.sidebar.markdown(f"""
        **📅 Ajouté:** {selected_export['date_added'][:10]}  
        **🎯 Systèmes Borda:** {selected_export['num_borda']}  
        **💾 Taille:** {selected_export['size_kb']:.1f} KB
        """)
        
        # Actions sur l'export sélectionné
        col1, col2, col3 = st.sidebar.columns(3)
        
        with col1:
            if st.button("⭐", help="Définir par défaut"):
                manager.set_default(selected_id)
                st.success("✅")
                st.rerun()
        
        with col2:
            if st.button("✏️", help="Renommer"):
                st.session_state.editing_export = selected_id
        
        with col3:
            if st.button("🗑️", help="Supprimer"):
                if st.session_state.get('confirm_delete') == selected_id:
                    success, msg = manager.delete_export(selected_id)
                    if success:
                        st.success(msg)
                        st.session_state.pop('confirm_delete', None)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.session_state.confirm_delete = selected_id
                    st.warning("⚠️ Cliquer à nouveau pour confirmer")
        
        # Interface de renommage
        if st.session_state.get('editing_export') == selected_id:
            new_name = st.sidebar.text_input("Nouveau nom:", value=selected_export['name'])
            if st.sidebar.button("💾 Enregistrer"):
                manager.update_export_name(selected_id, new_name)
                st.session_state.pop('editing_export', None)
                st.rerun()
        
        # Ajouter un nouvel export
        with st.sidebar.expander("➕ Ajouter un export"):
            uploaded = st.file_uploader(
                "Charger CSV",
                type=['csv'],
                key='borda_upload_additional'
            )
            
            if uploaded:
                custom_name = st.text_input("Nom", value=uploaded.name.replace('.csv', ''))
                
                if st.button("💾 Ajouter", type="primary"):
                    success, msg = manager.add_export(uploaded, custom_name)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
        
        # Stocker l'export sélectionné dans session_state
        st.session_state.selected_borda_export_id = selected_id
        
        return selected_id, selected_export


def get_selected_borda_data():
    """Récupère les données de l'export Borda sélectionné"""
    if 'borda_manager' not in st.session_state:
        return None, "Gestionnaire non initialisé"
    
    if 'selected_borda_export_id' not in st.session_state:
        return None, "Aucun export sélectionné"
    
    manager = st.session_state.borda_manager
    export_id = st.session_state.selected_borda_export_id
    
    return manager.load_export_data(export_id)
