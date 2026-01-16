"""
🔄 IMPORTEUR UNIVERSEL CSV
S'adapte automatiquement à tous les formats TurfBZH
"""

import pandas as pd
from datetime import datetime, date
from turf_database_complete import get_turf_database


class UniversalCSVImporter:
    """Importe n'importe quel format de CSV TurfBZH"""
    
    def __init__(self):
        self.db = get_turf_database()
        
        # Mappings possibles pour chaque type de donnée
        self.column_mappings = {
            'course_code': ['Course', 'course_id', 'code_course'],
            'date': ['date', 'Date'],
            'hippodrome': ['hippodrome', 'Hippodrome'],
            'heure': ['heure', 'Heure'],
            'discipline': ['discipline', 'Discipline'],
            'distance': ['distance', 'Distance'],
            'allocation': ['allocation', 'montant_prix', 'Allocation'],
            'nombre_partants': ['nombre_partants', 'Nombre_Partants'],
            
            'numero': ['Numero', 'numero', 'N°'],
            'cheval': ['Cheval', 'cheval', 'CHEVAL/MUSIQ.'],
            'driver': ['Driver', 'driver', 'DRIVER/ENTRAINEUR'],
            'entraineur': ['Entraineur', 'entraineur'],
            'age': ['age', 'Age'],
            'sexe': ['Sexe', 'sexe'],
            'musique': ['Musique', 'musique'],
            
            'cote_pmu': ['Cote', 'cote_direct', 'cote_pmu'],
            'cote_bzh': ['Cote BZH', 'cote_bzh', 'cote_reference'],
            
            'ia_gagnant': ['IA_Gagnant', 'ia_gagnant'],
            'ia_couple': ['IA_Couple', 'ia_couple'],
            'ia_trio': ['IA_Trio', 'ia_trio'],
            'note_ia': ['Note_IA_Decimale', 'note_ia'],
            
            'turf_points': ['Turf Points', 'turf_points'],
            'tpch_90': ['TPch 90', 'tpch_90'],
            'tpj_365': ['TPJ 365', 'tpj_365'],
            
            'elo_cheval': ['ELO_Cheval', 'elo_cheval'],
            'elo_jockey': ['ELO_Jockey', 'elo_jockey'],
            'elo_entraineur': ['ELO_Entraineur', 'elo_entraineur'],
            
            'rang_arrivee': ['Rank', 'rang_arrivee', 'ordre_arrivee', 'Rang'],
            'rapport_sg': ['Rapport_SG', 'rapport_simple_gagnant']
        }
    
    def find_column(self, df, field_name):
        """Trouve la colonne correspondante dans le DataFrame"""
        possible_names = self.column_mappings.get(field_name, [])
        
        for col_name in possible_names:
            if col_name in df.columns:
                return col_name
        
        return None
    
    def get_value(self, row, field_name, default=None):
        """Récupère une valeur avec le bon nom de colonne"""
        col_name = self.find_column(row.to_frame().T, field_name)
        
        if col_name and col_name in row.index:
            value = row[col_name]
            if pd.notna(value):
                return value
        
        return default
    
    def safe_float(self, value):
        """Convertit en float, gère virgules françaises"""
        if pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            value = value.replace(',', '.').strip()
            if value == '' or value == 'None':
                return None
            try:
                return float(value)
            except:
                return None
        return None
    
    def detect_format(self, df):
        """Détecte le type de fichier"""
        
        # Format historique
        if 'course_id' in df.columns and 'ordre_arrivee' in df.columns:
            return 'historique'
        
        # Format standard TurfBZH
        if 'Course' in df.columns:
            # Avec résultats
            if 'Rank' in df.columns or 'Rapport_SG' in df.columns:
                return 'avec_resultats'
            # Sans résultats (avant courses)
            else:
                return 'sans_resultats'
        
        return 'inconnu'
    
    def import_csv(self, csv_path, date_reunion=None):
        """
        Importe n'importe quel format de CSV TurfBZH
        
        Args:
            csv_path: Chemin du fichier
            date_reunion: Date par défaut si absent du CSV
        
        Returns:
            Dict avec stats d'import
        """
        
        print(f"📥 Import: {csv_path}")
        
        # Lire avec format français
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig', decimal=',')
        
        print(f"📊 {len(df)} lignes")
        
        # Détecter le format
        format_type = self.detect_format(df)
        print(f"🔍 Format détecté: {format_type}")
        
        if format_type == 'historique':
            return self.import_historique(df)
        else:
            return self.import_standard(df, date_reunion)
    
    def import_standard(self, df, date_reunion=None):
        """Import format standard TurfBZH"""
        
        stats = {
            'courses': 0,
            'partants': 0,
            'chevaux': 0,
            'errors': []
        }
        
        # Trouver la colonne course
        course_col = self.find_column(df, 'course_code')
        if not course_col:
            stats['errors'].append("Colonne Course non trouvée")
            return stats
        
        try:
            for course_code in df[course_col].unique():
                if pd.isna(course_code):
                    continue
                
                course_df = df[df[course_col] == course_code]
                
                # Date
                date_col = self.find_column(course_df, 'date')
                if date_col and pd.notna(course_df[date_col].iloc[0]):
                    date_str = course_df[date_col].iloc[0]
                    try:
                        date_course = pd.to_datetime(date_str).date()
                    except:
                        date_course = date_reunion or datetime.now().date()
                else:
                    date_course = date_reunion or datetime.now().date()
                
                # Hippodrome
                hippo_col = self.find_column(course_df, 'hippodrome')
                hippodrome_nom = course_df[hippo_col].iloc[0] if hippo_col else "Inconnu"
                hippodrome_id = self.db.get_or_create_hippodrome(hippodrome_nom)
                
                # Réunion
                reunion_code = course_code[:2]
                reunion_id = self.db.get_or_create_reunion(
                    reunion_code, date_course, hippodrome_id
                )
                
                # Course
                disc_col = self.find_column(course_df, 'discipline')
                discipline = course_df[disc_col].iloc[0] if disc_col else None
                
                dist_col = self.find_column(course_df, 'distance')
                distance = None
                if dist_col:
                    distance = int(self.safe_float(course_df[dist_col].iloc[0]) or 0)
                
                alloc_col = self.find_column(course_df, 'allocation')
                allocation = None
                if alloc_col:
                    allocation = self.safe_float(course_df[alloc_col].iloc[0])
                
                heure_col = self.find_column(course_df, 'heure')
                heure = course_df[heure_col].iloc[0] if heure_col else None
                
                course_id = self.db.create_course(
                    course_code=course_code,
                    reunion_id=reunion_id,
                    numero_course=int(course_code[3:]) if len(course_code) > 3 else 1,
                    heure=heure,
                    discipline=discipline,
                    distance=distance,
                    allocation=allocation,
                    nombre_partants=len(course_df)
                )
                
                stats['courses'] += 1
                
                # Partants
                for idx, (_, row) in enumerate(course_df.iterrows()):
                    # Cheval
                    cheval_nom = self.get_value(row, 'cheval')
                    if pd.isna(cheval_nom):
                        continue
                    
                    if idx == 0:  # Log premier partant
                        print(f"      🐴 Création partants pour {course_code}...")
                    
                    age = self.get_value(row, 'age')
                    sexe = self.get_value(row, 'sexe')
                    
                    cheval_id = self.db.get_or_create_cheval(
                        cheval_nom,
                        age=int(age) if age and pd.notna(age) else None,
                        sexe=sexe
                    )
                    stats['chevaux'] += 1
                    
                    # Driver
                    driver_nom = self.get_value(row, 'driver')
                    driver_id = None
                    if driver_nom:
                        driver_id = self.db.get_or_create_driver(driver_nom)
                    
                    # Entraîneur
                    entraineur_nom = self.get_value(row, 'entraineur')
                    entraineur_id = None
                    if entraineur_nom:
                        entraineur_id = self.db.get_or_create_entraineur(entraineur_nom)
                    
                    # Numéro
                    numero = self.get_value(row, 'numero', 0)
                    
                    # Rang (si disponible)
                    rang = self.get_value(row, 'rang_arrivee')
                    if rang:
                        try:
                            rang = int(rang)
                        except:
                            rang = None
                    
                    # Créer partant
                    partant_id = self.db.create_partant(
                        course_id=course_id,
                        cheval_id=cheval_id,
                        driver_id=driver_id,
                        entraineur_id=entraineur_id,
                        numero=int(numero),
                        cote_pmu=self.safe_float(self.get_value(row, 'cote_pmu')),
                        cote_bzh=self.safe_float(self.get_value(row, 'cote_bzh')),
                        musique=self.get_value(row, 'musique'),
                        ia_data={
                            'ia_gagnant': self.safe_float(self.get_value(row, 'ia_gagnant')),
                            'ia_couple': self.safe_float(self.get_value(row, 'ia_couple')),
                            'ia_trio': self.safe_float(self.get_value(row, 'ia_trio')),
                            'note_ia': self.safe_float(self.get_value(row, 'note_ia'))
                        },
                        performance_data={
                            'turf_points': self.safe_float(self.get_value(row, 'turf_points')),
                            'tpch_90': self.safe_float(self.get_value(row, 'tpch_90')),
                            'tpj_365': self.safe_float(self.get_value(row, 'tpj_365'))
                        }
                    )
                    
                    # Mettre à jour le rang si disponible
                    if rang:
                        self.db.cursor.execute(
                            "UPDATE partants SET rang_arrivee = ? WHERE id = ?",
                            (rang, partant_id)
                        )
                    
                    stats['partants'] += 1
                
                if stats['partants'] % 100 == 0:  # Log tous les 100 partants
                    print(f"      📊 {stats['partants']} partants créés...")
            
            print(f"   💾 Commit des données...")
            self.db.conn.commit()
            print(f"   ✅ Commit réussi - {stats['courses']} courses, {stats['partants']} partants")
            
        except Exception as e:
            self.db.conn.rollback()
            stats['errors'].append(str(e))
            import traceback
            traceback.print_exc()
        
        return stats
    
    def import_historique(self, df):
        """Import format historique (déjà implémenté dans import_historique.py)"""
        from import_historique import import_historique_csv
        # Sauvegarder temporairement et importer
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df.to_csv(f, sep=';', index=False)
            temp_path = f.name
        
        stats = import_historique_csv(temp_path)
        
        import os
        os.unlink(temp_path)
        
        return stats


def import_any_csv(csv_path, date_reunion=None):
    """Fonction utilitaire pour import universel"""
    importer = UniversalCSVImporter()
    return importer.import_csv(csv_path, date_reunion)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 universal_importer.py fichier.csv [date]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    date_param = None
    
    if len(sys.argv) > 2:
        date_str = sys.argv[2]
        date_param = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    stats = import_any_csv(csv_file, date_param)
    
    print("\n" + "="*60)
    print("📊 RÉSULTAT")
    print("="*60)
    print(f"✅ Courses: {stats['courses']}")
    print(f"✅ Partants: {stats['partants']}")
    print(f"✅ Chevaux: {stats['chevaux']}")
    
    if stats['errors']:
        print(f"\n⚠️ Erreurs: {len(stats['errors'])}")
        for err in stats['errors'][:5]:
            print(f"  - {err}")
