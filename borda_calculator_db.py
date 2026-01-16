"""
🎯 SYSTÈME DE CALCUL BORDA DEPUIS LA BASE DE DONNÉES
Calcule et stocke les scores Borda pour toutes les courses
"""

from turf_database_complete import get_turf_database
import pandas as pd
from datetime import date
import json


class BordaCalculator:
    """Calcule les scores Borda depuis la DB"""
    
    def __init__(self):
        self.db = get_turf_database()
        # Créer config par défaut si elle n'existe pas
        self._ensure_default_config()
    
    def _ensure_default_config(self):
        """S'assure que la config 'default' existe"""
        self.db.cursor.execute("SELECT id FROM borda_configs WHERE config_id = 'default'")
        if not self.db.cursor.fetchone():
            self.db.cursor.execute("""
                INSERT INTO borda_configs
                (config_id, nom, description, is_active)
                VALUES ('default', 'Configuration par défaut', 'Config générique pour toutes les courses', 1)
            """)
            self.db.conn.commit()
    
    def _get_config_db_id(self, config_id: str) -> int:
        """Convertit config_id (string) en ID de la DB (integer)"""
        self.db.cursor.execute("SELECT id FROM borda_configs WHERE config_id = ?", (config_id,))
        result = self.db.cursor.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"Config '{config_id}' n'existe pas dans borda_configs")
    
    def get_default_criteria(self):
        """Critères Borda par défaut"""
        return {
            'IA_Gagnant': 30,
            'ia_couple': 15,
            'ia_trio': 10,
            'Cote BZH': 20,
            'ELO_Cheval': 15,
            'ELO_Jockey': 10
        }
    
    def calculate_borda_for_course(self, course_code: str, criteria: dict = None, date_course: date = None):
        """
        Calcule les scores Borda pour une course
        
        Args:
            course_code: Code de la course (ex: R1C1)
            criteria: Dict des critères et leurs poids
            date_course: Date de la course (pour éviter les doublons de code)
        
        Returns:
            DataFrame avec scores calculés
        """
        
        if criteria is None:
            criteria = self.get_default_criteria()
        
        # Si pas de date fournie, prendre la plus récente
        if date_course is None:
            self.db.cursor.execute("""
                SELECT MAX(r.date) FROM courses c
                JOIN reunions r ON c.reunion_id = r.id
                WHERE c.course_code = ?
            """, (course_code,))
            result = self.db.cursor.fetchone()
            if result and result[0]:
                date_course = result[0]
        
        # Récupérer les partants de la course
        query = """
            SELECT 
                p.id as partant_id,
                p.numero,
                ch.nom as cheval,
                d.nom as driver,
                p.cote_pmu,
                p.cote_bzh,
                p.ia_gagnant,
                p.ia_couple,
                p.ia_trio,
                ch.elo as elo_cheval,
                d.elo as elo_jockey,
                p.turf_points,
                p.tpch_90
            FROM partants p
            JOIN courses c ON p.course_id = c.id
            JOIN reunions r ON c.reunion_id = r.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            WHERE c.course_code = ?
            AND r.date = ?
            AND p.non_partant = 0
            ORDER BY p.numero
        """
        
        df = pd.read_sql_query(query, self.db.conn, params=[course_code, date_course])
        
        if df.empty:
            return None
        
        # Calculer le score total
        df['score_borda'] = 0.0
        details = {}
        
        total_points = sum(criteria.values())
        
        for critere, points in criteria.items():
            col_name = critere.replace(' ', '_').lower()
            
            # Mapper les noms de colonnes
            if col_name == 'ia_gagnant':
                col_name = 'ia_gagnant'
            elif col_name == 'cote_bzh':
                col_name = 'cote_bzh'
            elif col_name == 'elo_cheval':
                col_name = 'elo_cheval'
            elif col_name == 'elo_jockey':
                col_name = 'elo_jockey'
            
            if col_name in df.columns:
                # Calculer le score pour ce critère
                values = df[col_name].fillna(0)
                
                # Pour les cotes : inverse (meilleure cote = meilleur score)
                if 'cote' in col_name:
                    # Inverser : cote basse = score élevé
                    max_val = values.max()
                    if max_val > 0:
                        normalized = (max_val - values) / max_val
                    else:
                        normalized = 0
                else:
                    # Pour les autres : valeur haute = score élevé
                    max_val = values.max()
                    if max_val > 0:
                        normalized = values / max_val
                    else:
                        normalized = 0
                
                score_critere = normalized * points
                df['score_borda'] += score_critere
                details[critere] = score_critere.tolist()
        
        # Normaliser sur le total des points
        if total_points > 0:
            df['score_borda'] = (df['score_borda'] / total_points) * 100
        
        # Ajouter le rang
        df['rang_borda'] = df['score_borda'].rank(ascending=False, method='min').astype(int)
        
        # Stocker les détails
        df['details'] = df.apply(lambda row: json.dumps({
            'criteres': {k: v[row.name] for k, v in details.items()},
            'score_final': row['score_borda']
        }), axis=1)
        
        return df
    
    def save_borda_scores(self, course_code: str, df: pd.DataFrame, config_id: str = 'default', date_course: date = None):
        """
        Sauvegarde les scores Borda dans la DB
        
        Args:
            course_code: Code de la course
            df: DataFrame avec les scores calculés
            config_id: ID de la configuration (string, ex: 'default')
            date_course: Date de la course (pour éviter les doublons)
        """
        
        # Convertir config_id string en ID integer
        config_db_id = self._get_config_db_id(config_id)
        
        # Si pas de date, prendre la plus récente
        if date_course is None:
            self.db.cursor.execute("""
                SELECT MAX(r.date) FROM courses c
                JOIN reunions r ON c.reunion_id = r.id
                WHERE c.course_code = ?
            """, (course_code,))
            result = self.db.cursor.fetchone()
            if result and result[0]:
                date_course = result[0]
        
        for _, row in df.iterrows():
            # Récupérer le vrai partant_id depuis la DB avec la date
            self.db.cursor.execute("""
                SELECT p.id FROM partants p
                JOIN courses c ON p.course_id = c.id
                JOIN reunions r ON c.reunion_id = r.id
                WHERE c.course_code = ? 
                AND p.numero = ?
                AND r.date = ?
            """, (course_code, row['numero'], date_course))
            
            result = self.db.cursor.fetchone()
            if not result:
                continue
            
            partant_id = result[0]
            
            self.db.cursor.execute("""
                INSERT OR REPLACE INTO borda_scores
                (partant_id, config_id, score_total, rang, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                partant_id,
                config_db_id,  # Utiliser l'ID integer
                row['score_borda'],
                row['rang_borda'],
                row['details']
            ))
        
        self.db.conn.commit()
    
    def calculate_all_today(self, target_date: date = None):
        """
        Calcule les scores Borda pour toutes les courses d'une date
        
        Args:
            target_date: Date cible (défaut: aujourd'hui)
        
        Returns:
            Dict avec stats de calcul
        """
        
        if target_date is None:
            from datetime import datetime
            target_date = datetime.now().date()
        
        # Récupérer toutes les courses de la date
        query = """
            SELECT DISTINCT c.course_code, c.nombre_partants, h.nom as hippodrome
            FROM courses c
            JOIN reunions r ON c.reunion_id = r.id
            JOIN hippodromes h ON r.hippodrome_id = h.id
            WHERE r.date = ?
            ORDER BY c.course_code
        """
        
        courses = pd.read_sql_query(query, self.db.conn, params=[target_date])
        
        stats = {
            'courses_calculees': 0,
            'partants_analyses': 0,
            'erreurs': []
        }
        
        criteria = self.get_default_criteria()
        
        for _, course in courses.iterrows():
            try:
                print(f"📊 Calcul Borda pour {course['course_code']} ({course['hippodrome']})...")
                
                df = self.calculate_borda_for_course(course['course_code'], criteria, target_date)
                
                if df is not None and not df.empty:
                    self.save_borda_scores(course['course_code'], df, 'default', target_date)
                    stats['courses_calculees'] += 1
                    stats['partants_analyses'] += len(df)
                    print(f"   ✅ {len(df)} partants analysés")
                else:
                    print(f"   ⚠️  Aucun partant trouvé")
            
            except Exception as e:
                stats['erreurs'].append(f"{course['course_code']}: {e}")
                print(f"   ❌ Erreur: {e}")
        
        return stats
    
    def get_borda_scores_for_course(self, course_code: str, config_id: str = 'default', date_course: date = None):
        """
        Récupère les scores Borda stockés pour une course
        
        Args:
            course_code: Code de la course
            config_id: ID de la configuration (string, ex: 'default')
            date_course: Date de la course (pour éviter les doublons)
        
        Returns:
            DataFrame avec les scores
        """
        
        # Convertir config_id string en ID integer
        config_db_id = self._get_config_db_id(config_id)
        
        # Si pas de date, prendre la plus récente
        if date_course is None:
            self.db.cursor.execute("""
                SELECT MAX(r.date) FROM courses c
                JOIN reunions r ON c.reunion_id = r.id
                WHERE c.course_code = ?
            """, (course_code,))
            result = self.db.cursor.fetchone()
            if result and result[0]:
                date_course = result[0]
        
        query = """
            SELECT 
                p.numero,
                ch.nom as cheval,
                d.nom as driver,
                bs.score_total,
                bs.rang,
                bs.details,
                p.cote_pmu,
                p.cote_bzh
            FROM borda_scores bs
            JOIN partants p ON bs.partant_id = p.id
            JOIN courses c ON p.course_id = c.id
            JOIN reunions r ON c.reunion_id = r.id
            JOIN chevaux ch ON p.cheval_id = ch.id
            LEFT JOIN drivers d ON p.driver_id = d.id
            WHERE c.course_code = ?
            AND bs.config_id = ?
            AND r.date = ?
            ORDER BY bs.rang
        """
        
        return pd.read_sql_query(query, self.db.conn, params=[course_code, config_db_id, date_course])


def calculate_borda_for_date(target_date: date = None):
    """
    Fonction utilitaire pour calculer les scores du jour
    """
    calculator = BordaCalculator()
    return calculator.calculate_all_today(target_date)


if __name__ == "__main__":
    from datetime import datetime
    
    print("🎯 CALCUL DES SCORES BORDA")
    print("="*60)
    
    calculator = BordaCalculator()
    
    # Calculer pour aujourd'hui
    stats = calculator.calculate_all_today()
    
    print("\n" + "="*60)
    print("📊 RÉSULTAT")
    print("="*60)
    print(f"✅ Courses calculées: {stats['courses_calculees']}")
    print(f"✅ Partants analysés: {stats['partants_analyses']}")
    
    if stats['erreurs']:
        print(f"\n⚠️  Erreurs: {len(stats['erreurs'])}")
        for err in stats['erreurs'][:5]:
            print(f"  - {err}")
    
    print("\n✅ Calcul terminé!")
