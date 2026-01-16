"""
🔄 ADAPTATEUR BASE DE DONNÉES POUR STREAMLIT
Remplace le chargement CSV par des requêtes DB
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from turf_database_complete import get_turf_database


class StreamlitDatabaseAdapter:
    """Adaptateur pour utiliser la DB dans Streamlit au lieu des CSV"""
    
    def __init__(self):
        self.db = self._get_cached_db()
    
    @staticmethod
    @st.cache_resource
    def _get_cached_db():
        """Instance DB cachée pour Streamlit"""
        return get_turf_database()
    
    # ==================== CHARGEMENT DES DONNÉES ====================
    
    def load_courses_by_date_range(self, date_debut: date, date_fin: date) -> pd.DataFrame:
        """
        Remplace le chargement CSV par une requête DB
        Équivalent au load_data() de l'ancien système
        """
        
        query = """
            SELECT 
                c.course_code as Course,
                c.heure as heure,
                h.nom as hippodrome,
                c.discipline,
                c.distance,
                c.allocation,
                c.nombre_partants,
                r.date,
                r.reunion_code
            FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            WHERE r.date BETWEEN ? AND ?
            ORDER BY r.date, c.numero_course
        """
        
        return pd.read_sql_query(
            query, 
            self.db.conn, 
            params=[date_debut, date_fin]
        )
    
    def load_partants_for_predictions(self, date_debut: date, date_fin: date) -> pd.DataFrame:
        """
        Charge tous les partants avec leurs données pour les pronostics
        Format compatible avec l'ancien système CSV
        """
        
        query = """
            SELECT 
                c.course_code as Course,
                r.date,
                h.nom as hippodrome,
                c.heure,
                c.discipline,
                c.distance,
                c.allocation,
                c.nombre_partants,
                
                p.numero as Numero,
                ch.nom as Cheval,
                ch.age,
                ch.sexe as Sexe,
                p.musique as Musique,
                
                d.nom as Driver,
                e.nom as Entraineur,
                
                p.cote_pmu as Cote,
                p.cote_bzh as "Cote BZH",
                
                ch.elo as ELO_Cheval,
                d.elo as ELO_Jockey,
                e.elo as ELO_Entraineur,
                
                p.ia_gagnant as IA_Gagnant,
                p.ia_couple as IA_Couple,
                p.ia_trio as IA_Trio,
                p.ia_multi as IA_Multi,
                p.note_ia as Note_IA_Decimale,
                
                p.turf_points as "Turf Points",
                p.tpch_90 as "TPch 90",
                p.tpj_365 as "TPJ 365",
                p.tpj_90 as "TPJ 90",
                
                p.rang_arrivee as Rang,
                p.rapport_simple_gagnant as Rapport_SG,
                p.rapport_simple_place as Rapport_SP
                
            FROM partants p
            JOIN courses c ON p.course_id = c.id
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            LEFT JOIN entraineurs e ON p.entraineur_id = e.id
            
            WHERE r.date BETWEEN ? AND ?
            AND p.non_partant = 0
            
            ORDER BY r.date, c.numero_course, p.numero
        """
        
        df = pd.read_sql_query(
            query,
            self.db.conn,
            params=[date_debut, date_fin]
        )
        
        # Conversion des types pour compatibilité
        if not df.empty:
            df['Numero'] = df['Numero'].astype(int)
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_course_detail(self, course_code: str) -> pd.DataFrame:
        """
        Récupère le détail d'une course avec tous ses partants
        """
        
        query = """
            SELECT 
                p.numero as Numero,
                ch.nom as Cheval,
                ch.age,
                ch.sexe as Sexe,
                p.musique as Musique,
                d.nom as Driver,
                e.nom as Entraineur,
                p.cote_pmu as Cote,
                p.cote_bzh as "Cote BZH",
                ch.elo as ELO_Cheval,
                d.elo as ELO_Jockey,
                e.elo as ELO_Entraineur,
                p.ia_gagnant as IA_Gagnant,
                p.note_ia as Note_IA,
                p.turf_points as "Turf Points",
                p.rang_arrivee as Rang
            FROM partants p
            JOIN courses c ON p.course_id = c.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            LEFT JOIN entraineurs e ON p.entraineur_id = e.id
            WHERE c.course_code = ?
            AND p.non_partant = 0
            ORDER BY p.numero
        """
        
        return pd.read_sql_query(query, self.db.conn, params=[course_code])
    
    # ==================== STATISTIQUES ====================
    
    def get_global_stats(self) -> dict:
        """Statistiques globales pour le dashboard"""
        
        stats = {}
        
        # Nombre de courses
        self.db.cursor.execute("SELECT COUNT(*) FROM courses")
        stats['total_courses'] = self.db.cursor.fetchone()[0]
        
        # Nombre de chevaux
        self.db.cursor.execute("SELECT COUNT(*) FROM chevaux")
        stats['total_chevaux'] = self.db.cursor.fetchone()[0]
        
        # Nombre de drivers
        self.db.cursor.execute("SELECT COUNT(*) FROM drivers")
        stats['total_drivers'] = self.db.cursor.fetchone()[0]
        
        # Nombre d'hippodromes
        self.db.cursor.execute("SELECT COUNT(*) FROM hippodromes")
        stats['total_hippodromes'] = self.db.cursor.fetchone()[0]
        
        # Période couverte
        self.db.cursor.execute("""
            SELECT MIN(date), MAX(date) 
            FROM reunions
        """)
        min_date, max_date = self.db.cursor.fetchone()
        stats['date_debut'] = min_date
        stats['date_fin'] = max_date
        
        return stats
    
    def get_hippodrome_stats(self) -> pd.DataFrame:
        """Statistiques par hippodrome"""
        
        query = """
            SELECT 
                h.nom as Hippodrome,
                COUNT(DISTINCT r.id) as Nb_Reunions,
                COUNT(c.id) as Nb_Courses,
                COUNT(p.id) as Nb_Partants
            FROM hippodromes h
            LEFT JOIN reunions r ON h.id = r.hippodrome_id
            LEFT JOIN courses c ON r.id = c.reunion_id
            LEFT JOIN partants p ON c.id = p.course_id
            GROUP BY h.id
            ORDER BY Nb_Courses DESC
        """
        
        return pd.read_sql_query(query, self.db.conn)
    
    # ==================== FAVORIS ====================
    
    def get_favorite_horses(self) -> pd.DataFrame:
        """Liste des chevaux favoris avec leurs stats"""
        
        query = """
            SELECT 
                ch.nom as Cheval,
                ch.age as Age,
                ch.elo as ELO,
                ch.nb_courses as "Nb Courses",
                ch.nb_victoires as Victoires,
                ch.gains_total as "Gains Totaux",
                fc.notes as Notes,
                fc.date_ajout as "Date Ajout"
            FROM favoris_chevaux fc
            JOIN chevaux ch ON fc.cheval_id = ch.id
            ORDER BY fc.date_ajout DESC
        """
        
        return pd.read_sql_query(query, self.db.conn)
    
    def add_favorite_horse(self, nom_cheval: str, notes: str = None) -> bool:
        """Ajoute un cheval aux favoris"""
        
        # Trouver le cheval
        self.db.cursor.execute(
            "SELECT id FROM chevaux WHERE nom = ?",
            (nom_cheval,)
        )
        row = self.db.cursor.fetchone()
        
        if not row:
            return False
        
        cheval_id = row[0]
        
        try:
            self.db.cursor.execute(
                "INSERT INTO favoris_chevaux (cheval_id, notes) VALUES (?, ?)",
                (cheval_id, notes)
            )
            self.db.conn.commit()
            return True
        except:
            return False
    
    def remove_favorite_horse(self, nom_cheval: str) -> bool:
        """Retire un cheval des favoris"""
        
        query = """
            DELETE FROM favoris_chevaux
            WHERE cheval_id IN (
                SELECT id FROM chevaux WHERE nom = ?
            )
        """
        
        self.db.cursor.execute(query, (nom_cheval,))
        self.db.conn.commit()
        return self.db.cursor.rowcount > 0
    
    # ==================== HISTORIQUE CHEVAUX ====================
    
    def get_horse_history(self, nom_cheval: str, limit: int = 20) -> pd.DataFrame:
        """Historique des courses d'un cheval"""
        
        query = """
            SELECT 
                r.date as Date,
                c.course_code as Course,
                h.nom as Hippodrome,
                c.discipline as Discipline,
                c.distance as Distance,
                p.numero as "N°",
                p.cote_pmu as Cote,
                d.nom as Driver,
                p.rang_arrivee as Rang,
                CASE 
                    WHEN p.rang_arrivee = 1 THEN '🥇'
                    WHEN p.rang_arrivee = 2 THEN '🥈'
                    WHEN p.rang_arrivee = 3 THEN '🥉'
                    WHEN p.rang_arrivee <= 5 THEN '✅'
                    ELSE ''
                END as Resultat
            FROM partants p
            JOIN courses c ON p.course_id = c.id
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            WHERE ch.nom = ?
            ORDER BY r.date DESC
            LIMIT ?
        """
        
        return pd.read_sql_query(query, self.db.conn, params=[nom_cheval, limit])
    
    # ==================== RECHERCHE ====================
    
    def search_horses(self, search_term: str, limit: int = 20) -> pd.DataFrame:
        """Recherche de chevaux par nom"""
        
        query = """
            SELECT 
                nom as Cheval,
                age as Age,
                sexe as Sexe,
                elo as ELO,
                nb_courses as "Nb Courses",
                nb_victoires as Victoires,
                ROUND(nb_victoires * 100.0 / NULLIF(nb_courses, 0), 1) as "Taux %"
            FROM chevaux
            WHERE nom LIKE ?
            ORDER BY elo DESC
            LIMIT ?
        """
        
        return pd.read_sql_query(
            query, 
            self.db.conn, 
            params=[f"%{search_term}%", limit]
        )
    
    def search_drivers(self, search_term: str, limit: int = 20) -> pd.DataFrame:
        """Recherche de drivers par nom"""
        
        query = """
            SELECT 
                nom as Driver,
                elo as ELO,
                nb_courses as "Nb Courses",
                nb_victoires as Victoires,
                ROUND(taux_victoire, 1) as "Taux Victoire %",
                ROUND(taux_place, 1) as "Taux Place %"
            FROM drivers
            WHERE nom LIKE ?
            ORDER BY elo DESC
            LIMIT ?
        """
        
        return pd.read_sql_query(
            query,
            self.db.conn,
            params=[f"%{search_term}%", limit]
        )
    
    # ==================== IMPORT AUTOMATIQUE ====================
    
    def import_csv_file(self, uploaded_file, date_reunion: date = None) -> dict:
        """
        Import d'un fichier CSV uploadé dans Streamlit
        Utilise l'importeur universel qui gère tous les formats
        
        Args:
            uploaded_file: Fichier UploadedFile de Streamlit
            date_reunion: Date de la réunion (auto-détection si None)
        
        Returns:
            Dict avec statistiques d'import
        """
        
        # Sauvegarder temporairement
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        
        # Utiliser l'importeur universel
        from universal_importer import import_any_csv
        stats = import_any_csv(tmp_path, date_reunion)
        
        # Nettoyer
        import os
        os.unlink(tmp_path)
        
        return stats


# Instance globale pour Streamlit
@st.cache_resource
def get_db_adapter():
    """Récupère l'adaptateur DB pour Streamlit"""
    return StreamlitDatabaseAdapter()
