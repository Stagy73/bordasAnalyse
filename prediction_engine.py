"""
🎯 MOTEUR DE PRONOSTIQUE INTELLIGENT TURF BZH
Système complet d'analyse multi-critères pour générer des pronostiques optimaux
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class TurfPredictionEngine:
    """Moteur de prédiction intelligent pour courses hippiques"""
    
    def __init__(self):
        self.weights = self._initialize_weights()
        self.min_confidence_threshold = 30  # Seuil de confiance minimum (%)
    
    def _initialize_weights(self) -> Dict[str, float]:
        """
        Poids de chaque indicateur dans le calcul du score final
        Ajustables selon vos retours d'expérience
        """
        return {
            # Systèmes Borda (40% du poids total)
            'borda_score': 0.40,
            
            # Ratings ELO (25% du poids total)
            'elo_cheval': 0.10,
            'elo_jockey': 0.08,
            'elo_entraineur': 0.05,
            'elo_proprio': 0.01,
            'elo_eleveur': 0.01,
            
            # Prédictions IA (15% du poids total)
            'ia_gagnant': 0.06,
            'ia_couple': 0.03,
            'ia_trio': 0.03,
            'ia_multi': 0.02,
            'ia_quinte': 0.01,
            
            # Performance historique (10% du poids total)
            'turf_points': 0.04,
            'taux_victoire': 0.03,
            'taux_place': 0.03,
            
            # Facteurs stratégiques (10% du poids total)
            'popularite': 0.03,
            'cote': 0.03,
            'place_corde': 0.02,
            'repos': 0.02
        }
    
    def normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """Normalise un score entre 0 et 1"""
        if pd.isna(value) or max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)
    
    def calculate_borda_score(self, row: pd.Series, borda_cols: List[str], 
                              hippodrome: str, discipline: str, 
                              nombre_partants: int) -> float:
        """
        Calcule le score Borda en choisissant le système le plus adapté
        """
        # Logique de sélection du meilleur système Borda
        selected_borda = None
        
        # 1. Prioriser les Borda spécifiques à l'hippodrome
        if 'vincenne' in hippodrome.lower():
            # Sélectionner selon le nombre de partants
            if 8 <= nombre_partants < 10:
                selected_borda = 'Borda - trot 8-10 chevaux  vincenne'
            elif 10 <= nombre_partants < 12:
                selected_borda = 'Borda - trot 10-12 chevaux  vincenne'
            elif 12 <= nombre_partants < 14:
                selected_borda = 'Borda - trot 12-14 chevaux  vincenne'
            elif 14 <= nombre_partants < 16:
                selected_borda = 'Borda - trot 14-16 chevaux  vincenne'
            elif nombre_partants >= 12:
                selected_borda = 'Borda - monté 12-16 chevaux  vincenne'
        
        elif 'pau' in hippodrome.lower():
            if discipline == 'A':  # Attelé
                selected_borda = 'Borda - Pau attelé'
            elif discipline == 'M':  # Monté
                selected_borda = 'Borda - Pau monté'
            else:  # Plat
                selected_borda = 'Borda - Pau plat'
        
        elif 'cagne' in hippodrome.lower() or 'cagnes' in hippodrome.lower():
            if discipline == 'A':
                selected_borda = 'Borda - cagne sur mer attelé'
            else:
                selected_borda = 'Borda - cagne sur mer monté'
        
        elif 'deauville' in hippodrome.lower():
            selected_borda = 'Borda - Deauville galot pcf'
        
        elif 'bousc' in hippodrome.lower():
            selected_borda = 'Borda - le boucast'
        
        # Fallback: Borda par défaut
        if not selected_borda:
            selected_borda = 'Borda - Borda par Défaut'
        
        # Récupérer le score du système sélectionné
        if selected_borda in row.index:
            return row[selected_borda] if not pd.isna(row[selected_borda]) else 0
        
        # Si le système n'existe pas, utiliser Borda par défaut
        if 'Borda - Borda par Défaut' in row.index:
            return row['Borda - Borda par Défaut'] if not pd.isna(row['Borda - Borda par Défaut']) else 0
        
        return 0
    
    def calculate_elo_score(self, row: pd.Series) -> float:
        """Calcule le score ELO combiné (normalisé)"""
        elo_cols = {
            'ELO_Cheval': self.weights['elo_cheval'],
            'ELO_Jockey': self.weights['elo_jockey'],
            'ELO_Entraineur': self.weights['elo_entraineur'],
            'ELO_Proprio': self.weights['elo_proprio'],
            'ELO_Eleveur': self.weights['elo_eleveur']
        }
        
        total_score = 0
        total_weight = 0
        
        for col, weight in elo_cols.items():
            if col in row.index and not pd.isna(row[col]):
                # Normaliser ELO (typiquement entre 1200 et 1800)
                normalized = self.normalize_score(row[col], 1200, 1800)
                total_score += normalized * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def calculate_ia_score(self, row: pd.Series) -> float:
        """Calcule le score IA combiné"""
        ia_cols = {
            'IA_Gagnant': self.weights['ia_gagnant'],
            'IA_Couple': self.weights['ia_couple'],
            'IA_Trio': self.weights['ia_trio'],
            'IA_Multi': self.weights['ia_multi'],
            'IA_Quinte': self.weights['ia_quinte']
        }
        
        total_score = 0
        total_weight = 0
        
        for col, weight in ia_cols.items():
            if col in row.index and not pd.isna(row[col]):
                # Les scores IA sont déjà entre 0 et 1
                total_score += row[col] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def calculate_performance_score(self, row: pd.Series) -> float:
        """Calcule le score de performance historique"""
        score = 0
        
        # Turf Points (normalisé)
        if 'Turf Points' in row.index and not pd.isna(row['Turf Points']):
            tp_normalized = self.normalize_score(row['Turf Points'], 0, 2000)
            score += tp_normalized * self.weights['turf_points']
        
        # Taux de victoire
        if 'Taux Victoire' in row.index and not pd.isna(row['Taux Victoire']):
            score += row['Taux Victoire'] * self.weights['taux_victoire']
        
        # Taux de place
        if 'Taux Place' in row.index and not pd.isna(row['Taux Place']):
            score += row['Taux Place'] * self.weights['taux_place']
        
        return score
    
    def calculate_strategic_score(self, row: pd.Series, df: pd.DataFrame) -> float:
        """Calcule les facteurs stratégiques (corde, cote, etc.)"""
        score = 0
        
        # Popularité (inverse car 1 = meilleur)
        if 'Popularite' in row.index and not pd.isna(row['Popularite']):
            pop_max = df['Popularite'].max()
            pop_normalized = 1 - self.normalize_score(row['Popularite'], 1, pop_max)
            score += pop_normalized * self.weights['popularite']
        
        # Cote (valeur inverse - cote élevée = moins favori mais potentiel gain)
        if 'Cote' in row.index and not pd.isna(row['Cote']):
            # Favoriser les cotes moyennes (3-15)
            cote_score = 0
            if 3 <= row['Cote'] <= 15:
                cote_score = 0.8
            elif row['Cote'] < 3:
                cote_score = 0.6  # Trop favori
            else:
                cote_score = 0.4  # Trop outsider
            score += cote_score * self.weights['cote']
        
        # Place à la corde (1 = meilleur)
        if 'Place_Corde' in row.index and not pd.isna(row['Place_Corde']):
            corde_max = df['Place_Corde'].max()
            corde_normalized = 1 - self.normalize_score(row['Place_Corde'], 1, corde_max)
            score += corde_normalized * self.weights['place_corde']
        
        # Repos (optimal entre 14-28 jours)
        if 'Repos' in row.index and not pd.isna(row['Repos']):
            repos_score = 0
            if 14 <= row['Repos'] <= 28:
                repos_score = 1.0
            elif 7 <= row['Repos'] < 14 or 28 < row['Repos'] <= 42:
                repos_score = 0.7
            else:
                repos_score = 0.4
            score += repos_score * self.weights['repos']
        
        return score
    
    def generate_prediction(self, df: pd.DataFrame, race_info: Dict = None) -> pd.DataFrame:
        """
        Génère les prédictions pour une course
        
        Args:
            df: DataFrame avec les données des chevaux
            race_info: Informations sur la course (hippodrome, discipline, etc.)
        
        Returns:
            DataFrame avec scores et recommandations
        """
        if race_info is None:
            race_info = {}
        
        # Identifier les colonnes Borda
        borda_cols = [col for col in df.columns if 'Borda' in col]
        
        hippodrome = race_info.get('hippodrome', '')
        discipline = race_info.get('discipline', '')
        nombre_partants = len(df)
        
        predictions = []
        
        for idx, row in df.iterrows():
            # Calculer chaque composante du score
            borda_score = self.calculate_borda_score(row, borda_cols, hippodrome, 
                                                     discipline, nombre_partants)
            elo_score = self.calculate_elo_score(row)
            ia_score = self.calculate_ia_score(row)
            perf_score = self.calculate_performance_score(row)
            strat_score = self.calculate_strategic_score(row, df)
            
            # Normaliser le score Borda (typiquement entre 0 et 300)
            borda_normalized = self.normalize_score(borda_score, 0, 300) * self.weights['borda_score']
            
            # Score final (sur 100)
            final_score = (borda_normalized + elo_score + ia_score + 
                          perf_score + strat_score) * 100
            
            # Niveau de confiance basé sur la convergence des indicateurs
            confidence = self._calculate_confidence(borda_normalized, elo_score, 
                                                    ia_score, perf_score, strat_score)
            
            # Déterminer le classement suggéré
            classification = self._classify_horse(final_score, confidence)
            
            predictions.append({
                'Numero': row.get('Numero', idx + 1),
                'Cheval': row.get('Cheval', 'N/A'),
                'Score_Final': round(final_score, 2),
                'Confiance': round(confidence, 2),
                'Score_Borda': round(borda_normalized * 100, 2),
                'Score_ELO': round(elo_score * 100, 2),
                'Score_IA': round(ia_score * 100, 2),
                'Score_Perf': round(perf_score * 100, 2),
                'Score_Strat': round(strat_score * 100, 2),
                'Classification': classification,
                'Cote': row.get('Cote', 'N/A'),
                'Driver': row.get('Driver', 'N/A'),
                'Classement_Actuel': row.get('classement', 'N/A')
            })
        
        result_df = pd.DataFrame(predictions)
        result_df = result_df.sort_values('Score_Final', ascending=False).reset_index(drop=True)
        result_df['Rang_Prono'] = range(1, len(result_df) + 1)
        
        return result_df
    
    def _calculate_confidence(self, borda: float, elo: float, ia: float, 
                             perf: float, strat: float) -> float:
        """Calcule le niveau de confiance basé sur la convergence des scores"""
        scores = [borda, elo, ia, perf, strat]
        scores = [s for s in scores if s > 0]  # Ignorer les scores nuls
        
        if len(scores) < 2:
            return 50  # Confiance moyenne par défaut
        
        # Calculer l'écart-type des scores (normalisés)
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Plus l'écart-type est faible, plus la confiance est élevée
        # Convertir en score de confiance (0-100)
        confidence = 100 - (std_score * 200)  # Ajustement empirique
        confidence = max(20, min(100, confidence))  # Borner entre 20 et 100
        
        return confidence
    
    def _classify_horse(self, score: float, confidence: float) -> str:
        """Classifie un cheval selon son score"""
        if score >= 70 and confidence >= 60:
            return "⭐ FAVORI FORT"
        elif score >= 60:
            return "✅ FAVORI"
        elif score >= 50:
            return "🎯 POSSIBLE"
        elif score >= 40:
            return "💎 OUTSIDER VALEUR"
        else:
            return "⚠️ OUTSIDER"
    
    def generate_betting_strategy(self, predictions: pd.DataFrame) -> Dict:
        """Génère une stratégie de paris optimale"""
        top_5 = predictions.head(5)
        top_3 = predictions.head(3)
        
        strategy = {
            'simple_gagnant': {
                'cheval': int(top_5.iloc[0]['Numero']),
                'nom': top_5.iloc[0]['Cheval'],
                'confiance': top_5.iloc[0]['Confiance'],
                'cote_estimee': top_5.iloc[0]['Cote']
            },
            'simple_place': {
                'chevaux': top_3['Numero'].tolist(),
                'confiance_moyenne': top_3['Confiance'].mean()
            },
            'couple_gagnant': {
                'combinaison': f"{int(top_5.iloc[0]['Numero'])}-{int(top_5.iloc[1]['Numero'])}",
                'confiance': (top_5.iloc[0]['Confiance'] + top_5.iloc[1]['Confiance']) / 2
            },
            'trio': {
                'combinaison': f"{int(top_3.iloc[0]['Numero'])}-{int(top_3.iloc[1]['Numero'])}-{int(top_3.iloc[2]['Numero'])}",
                'confiance': top_3['Confiance'].mean()
            },
            'multi': {
                'base': top_3['Numero'].tolist(),
                'complements': top_5.iloc[3:5]['Numero'].tolist()
            },
            'quinte': {
                'ordre': top_5['Numero'].tolist(),
                'desordre': top_5['Numero'].tolist()
            }
        }
        
        return strategy
