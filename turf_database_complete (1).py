"""
🗄️ BASE DE DONNÉES COMPLÈTE TURF BZH
Architecture complète pour remplacer tous les CSV/JSON
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import json


class TurfDatabase:
    """
    Base de données SQLite complète pour le système Turf BZH
    
    Remplace :
    - CSV d'exports quotidiens
    - JSON des paris
    - JSON des favoris
    - JSON des configs Borda
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path.home() / "bordasAnalyse" / "turf_complete.db")
        
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Activer les clés étrangères
        self.cursor.execute("PRAGMA foreign_keys = ON")
        
        self._create_all_tables()
        self._create_indexes()
    
    def _create_all_tables(self):
        """Crée toutes les tables du système"""
        
        # ==================== RÉFÉRENTIELS ====================
        
        # Table Hippodromes
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hippodromes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                pays TEXT,
                type TEXT,
                surface TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table Chevaux
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chevaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                age INTEGER,
                sexe TEXT,
                race TEXT,
                proprietaire_id INTEGER,
                eleveur TEXT,
                elo REAL DEFAULT 1500,
                nb_courses INTEGER DEFAULT 0,
                nb_victoires INTEGER DEFAULT 0,
                nb_places INTEGER DEFAULT 0,
                gains_total REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nom, age)
            )
        """)
        
        # Table Drivers (Jockeys)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                prenom TEXT,
                type TEXT,
                specialite TEXT,
                elo REAL DEFAULT 1500,
                nb_courses INTEGER DEFAULT 0,
                nb_victoires INTEGER DEFAULT 0,
                taux_victoire REAL DEFAULT 0,
                taux_place REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table Entraîneurs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS entraineurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                prenom TEXT,
                elo REAL DEFAULT 1500,
                nb_courses INTEGER DEFAULT 0,
                nb_victoires INTEGER DEFAULT 0,
                taux_victoire REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table Propriétaires
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS proprietaires (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                elo REAL DEFAULT 1500,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ==================== COURSES ET RÉUNIONS ====================
        
        # Table Réunions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reunions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reunion_code TEXT NOT NULL,
                date DATE NOT NULL,
                hippodrome_id INTEGER NOT NULL,
                nb_courses INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hippodrome_id) REFERENCES hippodromes(id),
                UNIQUE(reunion_code, date, hippodrome_id)
            )
        """)
        
        # Table Courses
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL UNIQUE,
                reunion_id INTEGER NOT NULL,
                numero_course INTEGER NOT NULL,
                heure TIME,
                discipline TEXT NOT NULL,
                distance INTEGER,
                allocation REAL,
                nombre_partants INTEGER,
                classe_groupe TEXT,
                conditions TEXT,
                terrain TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reunion_id) REFERENCES reunions(id)
            )
        """)
        
        # Table Partants (Chevaux dans une course)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS partants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                cheval_id INTEGER NOT NULL,
                driver_id INTEGER,
                entraineur_id INTEGER,
                numero INTEGER NOT NULL,
                cote_pmu REAL,
                cote_bzh REAL,
                musique TEXT,
                ferrure TEXT,
                poids REAL,
                place_corde INTEGER,
                repos INTEGER,
                distance_record REAL,
                
                -- Statistiques de performance
                turf_points REAL,
                tpch_90 REAL,
                tpj_365 REAL,
                tpj_90 REAL,
                
                -- Prédictions IA
                ia_gagnant REAL,
                ia_couple REAL,
                ia_trio REAL,
                ia_multi REAL,
                ia_quinte REAL,
                note_ia REAL,
                
                -- Résultat final
                rang_arrivee INTEGER,
                temps_course REAL,
                disqualifie BOOLEAN DEFAULT 0,
                non_partant BOOLEAN DEFAULT 0,
                rapport_simple_gagnant REAL,
                rapport_simple_place REAL,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (cheval_id) REFERENCES chevaux(id),
                FOREIGN KEY (driver_id) REFERENCES drivers(id),
                FOREIGN KEY (entraineur_id) REFERENCES entraineurs(id),
                UNIQUE(course_id, numero)
            )
        """)
        
        # Table Arrivées
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS arrivees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL UNIQUE,
                ordre_arrivee TEXT NOT NULL,
                rapport_simple_gagnant REAL,
                rapport_simple_place TEXT,
                rapport_couple_gagnant REAL,
                rapport_couple_place REAL,
                rapport_trio REAL,
                rapport_2sur4 REAL,
                rapport_multi REAL,
                rapport_quinte_ordre REAL,
                rapport_quinte_desordre REAL,
                non_partants TEXT,
                temps_premier REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        
        # ==================== SYSTÈMES BORDA ====================
        
        # Table Configurations Borda
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS borda_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id TEXT NOT NULL UNIQUE,
                nom TEXT NOT NULL,
                hippodrome_id INTEGER,
                discipline TEXT,
                nb_partants_min INTEGER,
                nb_partants_max INTEGER,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hippodrome_id) REFERENCES hippodromes(id)
            )
        """)
        
        # Table Critères Borda (points par critère)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS borda_criteres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER NOT NULL,
                critere_nom TEXT NOT NULL,
                points INTEGER NOT NULL,
                FOREIGN KEY (config_id) REFERENCES borda_configs(id) ON DELETE CASCADE,
                UNIQUE(config_id, critere_nom)
            )
        """)
        
        # Table Scores Borda calculés
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS borda_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partant_id INTEGER NOT NULL,
                config_id INTEGER NOT NULL,
                score_total REAL NOT NULL,
                rang INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (partant_id) REFERENCES partants(id) ON DELETE CASCADE,
                FOREIGN KEY (config_id) REFERENCES borda_configs(id),
                UNIQUE(partant_id, config_id)
            )
        """)
        
        # ==================== PRONOSTICS ====================
        
        # Table Pronostics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pronostics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                type_prono TEXT NOT NULL,
                source TEXT,
                top5 TEXT NOT NULL,
                confiance REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(course_id, type_prono, source)
            )
        """)
        
        # ==================== PARIS ====================
        
        # Table Paris Joués
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS paris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                type_pari TEXT NOT NULL,
                formule TEXT,
                numeros TEXT NOT NULL,
                bases TEXT,
                complements TEXT,
                nb_combinaisons INTEGER DEFAULT 1,
                mise_unitaire REAL DEFAULT 1.0,
                cout_total REAL NOT NULL,
                confiance REAL,
                statut TEXT DEFAULT 'en_attente',
                rang_arrivee TEXT,
                resultat TEXT,
                gains REAL DEFAULT 0,
                roi REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        
        # ==================== FAVORIS ====================
        
        # Table Favoris Chevaux
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoris_chevaux (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cheval_id INTEGER NOT NULL UNIQUE,
                notes TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cheval_id) REFERENCES chevaux(id)
            )
        """)
        
        # Table Favoris Drivers
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoris_drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER NOT NULL UNIQUE,
                notes TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (driver_id) REFERENCES drivers(id)
            )
        """)
        
        # Table Favoris Entraîneurs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favoris_entraineurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entraineur_id INTEGER NOT NULL UNIQUE,
                notes TEXT,
                date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entraineur_id) REFERENCES entraineurs(id)
            )
        """)
        
        # ==================== STATISTIQUES ====================
        
        # Table Statistiques par Hippodrome
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats_hippodromes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hippodrome_id INTEGER NOT NULL,
                annee INTEGER NOT NULL,
                nb_reunions INTEGER DEFAULT 0,
                nb_courses INTEGER DEFAULT 0,
                allocation_totale REAL DEFAULT 0,
                FOREIGN KEY (hippodrome_id) REFERENCES hippodromes(id),
                UNIQUE(hippodrome_id, annee)
            )
        """)
        
        # Table Performance Chevaux/Drivers
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS synergies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cheval_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                nb_courses INTEGER DEFAULT 0,
                nb_victoires INTEGER DEFAULT 0,
                taux_reussite REAL DEFAULT 0,
                FOREIGN KEY (cheval_id) REFERENCES chevaux(id),
                FOREIGN KEY (driver_id) REFERENCES drivers(id),
                UNIQUE(cheval_id, driver_id)
            )
        """)
        
        self.conn.commit()
    
    def _create_indexes(self):
        """Crée les index pour accélérer les recherches"""
        
        indexes = [
            # Courses
            "CREATE INDEX IF NOT EXISTS idx_courses_date ON courses(reunion_id)",
            "CREATE INDEX IF NOT EXISTS idx_courses_discipline ON courses(discipline)",
            
            # Partants
            "CREATE INDEX IF NOT EXISTS idx_partants_course ON partants(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_partants_cheval ON partants(cheval_id)",
            "CREATE INDEX IF NOT EXISTS idx_partants_driver ON partants(driver_id)",
            
            # Réunions
            "CREATE INDEX IF NOT EXISTS idx_reunions_date ON reunions(date)",
            "CREATE INDEX IF NOT EXISTS idx_reunions_hippodrome ON reunions(hippodrome_id)",
            
            # Scores Borda
            "CREATE INDEX IF NOT EXISTS idx_borda_scores_partant ON borda_scores(partant_id)",
            "CREATE INDEX IF NOT EXISTS idx_borda_scores_config ON borda_scores(config_id)",
            
            # Paris
            "CREATE INDEX IF NOT EXISTS idx_paris_course ON paris(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_paris_statut ON paris(statut)",
            
            # Noms pour recherche rapide
            "CREATE INDEX IF NOT EXISTS idx_chevaux_nom ON chevaux(nom)",
            "CREATE INDEX IF NOT EXISTS idx_drivers_nom ON drivers(nom)",
            "CREATE INDEX IF NOT EXISTS idx_entraineurs_nom ON entraineurs(nom)",
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except sqlite3.OperationalError:
                pass  # Index existe déjà
        
        self.conn.commit()
    
    # ==================== IMPORT CSV COMPLET ====================
    
    def import_from_csv(self, csv_path: str, date_reunion: date = None) -> Dict:
        """
        Importe un export CSV complet dans la base de données
        
        Returns:
            Dict avec statistiques d'import
        """
        
        if date_reunion is None:
            date_reunion = datetime.now().date()
        
        # Lire le CSV avec format français (virgule comme séparateur décimal)
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig', decimal=',')
        
        # Fonction pour convertir les nombres au format français
        def safe_float(value):
            """Convertit une valeur en float, gère virgules et valeurs manquantes"""
            if pd.isna(value):
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Remplacer virgule par point
                value = value.replace(',', '.')
                # Retirer les espaces
                value = value.strip()
                if value == '' or value == 'None':
                    return None
                try:
                    return float(value)
                except:
                    return None
            return None
        
        stats = {
            'hippodromes': 0,
            'courses': 0,
            'chevaux': 0,
            'drivers': 0,
            'entraineurs': 0,
            'partants': 0,
            'errors': []
        }
        
        try:
            # Grouper par course
            for course_code in df['Course'].unique():
                course_df = df[df['Course'] == course_code]
                
                # Lire la date depuis le CSV (pas le paramètre)
                if 'date' in course_df.columns and pd.notna(course_df['date'].iloc[0]):
                    date_str = course_df['date'].iloc[0]
                    try:
                        date_course = pd.to_datetime(date_str).date()
                    except:
                        date_course = date_reunion
                else:
                    date_course = date_reunion
                
                # 1. Hippodrome
                hippodrome_nom = course_df['hippodrome'].iloc[0]
                hippodrome_id = self.get_or_create_hippodrome(hippodrome_nom)
                
                # 2. Réunion
                reunion_code = course_code[:2]  # R1, R2, etc.
                reunion_id = self.get_or_create_reunion(
                    reunion_code, date_course, hippodrome_id
                )
                
                # 3. Course
                course_id = self.create_course(
                    course_code=course_code,
                    reunion_id=reunion_id,
                    numero_course=int(course_code[3:]),
                    heure=course_df['heure'].iloc[0] if 'heure' in course_df.columns else None,
                    discipline=course_df['discipline'].iloc[0],
                    distance=int(safe_float(course_df['distance'].iloc[0]) or 0) if 'distance' in course_df.columns else None,
                    allocation=safe_float(course_df['allocation'].iloc[0]) if 'allocation' in course_df.columns else None,
                    nombre_partants=len(course_df)
                )
                
                stats['courses'] += 1
                
                # 4. Partants
                for _, row in course_df.iterrows():
                    # Cheval
                    cheval_id = self.get_or_create_cheval(
                        row['Cheval'],
                        age=row.get('age'),
                        sexe=row.get('Sexe')
                    )
                    stats['chevaux'] += 1
                    
                    # Driver
                    driver_id = None
                    if 'Driver' in row and pd.notna(row['Driver']):
                        driver_id = self.get_or_create_driver(row['Driver'])
                        stats['drivers'] += 1
                    
                    # Entraîneur
                    entraineur_id = None
                    if 'Entraineur' in row and pd.notna(row['Entraineur']):
                        entraineur_id = self.get_or_create_entraineur(row['Entraineur'])
                        stats['entraineurs'] += 1
                    
                    # Partant
                    self.create_partant(
                        course_id=course_id,
                        cheval_id=cheval_id,
                        driver_id=driver_id,
                        entraineur_id=entraineur_id,
                        numero=int(row['Numero']),
                        cote_pmu=safe_float(row.get('Cote')),
                        cote_bzh=safe_float(row.get('Cote BZH')),
                        musique=row.get('Musique'),
                        ia_data={
                            'ia_gagnant': safe_float(row.get('IA_Gagnant')),
                            'ia_couple': safe_float(row.get('IA_Couple')),
                            'ia_trio': safe_float(row.get('IA_Trio')),
                            'note_ia': safe_float(row.get('Note_IA_Decimale'))
                        },
                        performance_data={
                            'turf_points': safe_float(row.get('Turf Points')),
                            'tpch_90': safe_float(row.get('TPch 90')),
                            'tpj_365': safe_float(row.get('TPJ 365'))
                        }
                    )
                    stats['partants'] += 1
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            stats['errors'].append(str(e))
        
        return stats

    # ==================== MÉTHODES UTILITAIRES ====================
    
    def get_or_create_hippodrome(self, nom: str, pays: str = 'France') -> int:
        """Récupère ou crée un hippodrome"""
        self.cursor.execute("SELECT id FROM hippodromes WHERE nom = ?", (nom,))
        row = self.cursor.fetchone()
        
        if row:
            return row[0]
        
        self.cursor.execute(
            "INSERT INTO hippodromes (nom, pays) VALUES (?, ?)",
            (nom, pays)
        )
        return self.cursor.lastrowid
    
    def get_or_create_cheval(self, nom: str, age: int = None, sexe: str = None) -> int:
        """Récupère ou crée un cheval"""
        self.cursor.execute(
            "SELECT id FROM chevaux WHERE nom = ? AND (age = ? OR age IS NULL)",
            (nom, age)
        )
        row = self.cursor.fetchone()
        
        if row:
            return row[0]
        
        self.cursor.execute(
            "INSERT INTO chevaux (nom, age, sexe) VALUES (?, ?, ?)",
            (nom, age, sexe)
        )
        return self.cursor.lastrowid
    
    def get_or_create_driver(self, nom: str) -> int:
        """Récupère ou crée un driver"""
        self.cursor.execute("SELECT id FROM drivers WHERE nom = ?", (nom,))
        row = self.cursor.fetchone()
        
        if row:
            return row[0]
        
        self.cursor.execute("INSERT INTO drivers (nom) VALUES (?)", (nom,))
        return self.cursor.lastrowid
    
    def get_or_create_entraineur(self, nom: str) -> int:
        """Récupère ou crée un entraîneur"""
        self.cursor.execute("SELECT id FROM entraineurs WHERE nom = ?", (nom,))
        row = self.cursor.fetchone()
        
        if row:
            return row[0]
        
        self.cursor.execute("INSERT INTO entraineurs (nom) VALUES (?)", (nom,))
        return self.cursor.lastrowid
    
    def get_or_create_reunion(self, reunion_code: str, date: date, hippodrome_id: int) -> int:
        """Récupère ou crée une réunion"""
        self.cursor.execute(
            "SELECT id FROM reunions WHERE reunion_code = ? AND date = ? AND hippodrome_id = ?",
            (reunion_code, date, hippodrome_id)
        )
        row = self.cursor.fetchone()
        
        if row:
            return row[0]
        
        self.cursor.execute(
            "INSERT INTO reunions (reunion_code, date, hippodrome_id) VALUES (?, ?, ?)",
            (reunion_code, date, hippodrome_id)
        )
        return self.cursor.lastrowid
    
    def create_course(self, course_code: str, reunion_id: int, numero_course: int,
                     heure: str = None, discipline: str = None, distance: int = None,
                     allocation: float = None, nombre_partants: int = None) -> int:
        """Crée une course"""
        self.cursor.execute("""
            INSERT OR IGNORE INTO courses 
            (course_code, reunion_id, numero_course, heure, discipline, distance, allocation, nombre_partants)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (course_code, reunion_id, numero_course, heure, discipline, distance, allocation, nombre_partants))
        
        self.cursor.execute("SELECT id FROM courses WHERE course_code = ?", (course_code,))
        return self.cursor.fetchone()[0]
    
    def create_partant(self, course_id: int, cheval_id: int, numero: int,
                      driver_id: int = None, entraineur_id: int = None,
                      cote_pmu: float = None, cote_bzh: float = None,
                      musique: str = None, ia_data: Dict = None,
                      performance_data: Dict = None) -> int:
        """Crée un partant"""
        
        ia_data = ia_data or {}
        performance_data = performance_data or {}
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO partants
            (course_id, cheval_id, driver_id, entraineur_id, numero,
             cote_pmu, cote_bzh, musique, ia_gagnant, ia_couple, ia_trio,
             note_ia, turf_points, tpch_90, tpj_365)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            course_id, cheval_id, driver_id, entraineur_id, numero,
            cote_pmu, cote_bzh, musique,
            ia_data.get('ia_gagnant'), ia_data.get('ia_couple'), ia_data.get('ia_trio'),
            ia_data.get('note_ia'),
            performance_data.get('turf_points'), performance_data.get('tpch_90'),
            performance_data.get('tpj_365')
        ))
        
        return self.cursor.lastrowid
    
    # ==================== REQUÊTES ====================
    
    def get_courses_by_date(self, date: date) -> pd.DataFrame:
        """Récupère toutes les courses d'une date"""
        query = """
            SELECT c.*, r.reunion_code, h.nom as hippodrome
            FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            WHERE r.date = ?
            ORDER BY c.numero_course
        """
        return pd.read_sql_query(query, self.conn, params=[date])
    
    def get_partants_by_course(self, course_code: str) -> pd.DataFrame:
        """Récupère tous les partants d'une course"""
        query = """
            SELECT 
                p.*,
                ch.nom as cheval_nom,
                d.nom as driver_nom,
                e.nom as entraineur_nom
            FROM partants p
            JOIN courses c ON p.course_id = c.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            LEFT JOIN entraineurs e ON p.entraineur_id = e.id
            WHERE c.course_code = ?
            ORDER BY p.numero
        """
        return pd.read_sql_query(query, self.conn, params=[course_code])
    
    def close(self):
        """Ferme la connexion"""
        self.conn.close()


# Instance globale
_db_instance = None

def get_turf_database() -> TurfDatabase:
    """Récupère l'instance globale de la base de données"""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = TurfDatabase()
    
    return _db_instance
