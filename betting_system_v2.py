"""
🎲 SYSTÈME DE PARIS AMÉLIORÉ V2
Recommandations intelligentes + Formules combinées + Tracking ROI
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path


class BettingRecommendationEngine:
    """Moteur de recommandation de paris intelligent"""
    
    def __init__(self):
        # Prix unitaires selon ZEturf
        self.unit_prices = {
            'simple_gagnant': 1.00,
            'simple_place': 1.00,
            'couple_gagnant': 1.00,
            'couple_place': 1.00,
            'trio': 1.00,
            '2sur4': 3.00,  # 6 combinaisons × 0.50€
            'multi_4': 3.00,
            'multi_5': 15.00,
            'quinte': 2.00
        }
        
        # Règles par type d'hippodrome et discipline
        self.betting_rules = self._load_betting_rules()
    
    def _safe_float(self, value, default=0.0):
        """Conversion sécurisée en float"""
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _load_betting_rules(self):
        """Règles de recommandation par hippodrome/discipline"""
        return {
            'vincennes_attele': {
                'priority': ['trio', 'couple_gagnant', 'simple_place', '2sur4'],
                'min_confidence': 35,
                'formulas': {
                    'trio': 'base_2',  # 2 chevaux en base avec compléments
                    'couple': 'base_1',
                    '2sur4': 'base_2'
                }
            },
            'vincennes_monte': {
                'priority': ['couple_place', 'simple_place', 'trio', '2sur4'],
                'min_confidence': 30,
                'formulas': {
                    'trio': 'base_2',
                    'couple': 'base_1'
                }
            },
            'plat_province': {
                'priority': ['simple_place', 'couple_place', 'multi_4'],
                'min_confidence': 25,
                'formulas': {
                    'couple': 'base_1',
                    'multi': 'all_4'
                }
            },
            'default': {
                'priority': ['simple_place', 'couple_place', 'trio'],
                'min_confidence': 30,
                'formulas': {
                    'trio': 'base_2',
                    'couple': 'base_1'
                }
            }
        }
    
    def get_hippodrome_type(self, hippodrome, discipline):
        """Détermine le type d'hippodrome/discipline"""
        hippo_lower = hippodrome.lower() if pd.notna(hippodrome) else ''
        disc = str(discipline).upper() if pd.notna(discipline) else ''
        
        if 'vincennes' in hippo_lower or 'vincenne' in hippo_lower:
            if disc == 'A':
                return 'vincennes_attele'
            elif disc == 'M':
                return 'vincennes_monte'
        
        if disc == 'P':
            return 'plat_province'
        
        return 'default'
    
    def calculate_formula_cost(self, formula_type, nb_base, nb_complements):
        """Calcule le coût d'une formule combinée"""
        if formula_type == 'base_1':
            # 1 base avec X compléments = X paris
            return nb_complements
        elif formula_type == 'base_2':
            # 2 bases avec X compléments = C(2,2) + 2*X = 1 + 2X
            return 1 + (2 * nb_complements)
        elif formula_type == 'base_3':
            # 3 bases avec X compléments
            return 1 + (3 * nb_complements)
        elif formula_type == 'all_4':
            return 1
        else:
            return nb_complements
    
    def generate_betting_recommendations(self, course_data, hippodrome, discipline, confidence):
        """
        Génère des recommandations de paris intelligentes
        TOUJOURS générer Simple, Couplé, Trio, 2sur4 avec formules adaptées
        
        Returns:
            List[Dict] avec recommandations détaillées
        """
        recommendations = []
        
        # Déterminer le type d'hippodrome
        hippo_type = self.get_hippodrome_type(hippodrome, discipline)
        rules = self.betting_rules.get(hippo_type, self.betting_rules['default'])
        
        # Récupérer le top des chevaux TRIÉS PAR SCORE
        nb_partants = len(course_data)
        
        # S'assurer que Confiance est bien une colonne numérique
        if 'Confiance' not in course_data.columns:
            # Si pas de colonne Confiance, la créer à partir du Score
            course_data = course_data.copy()
            course_data['Confiance'] = (course_data['Score'] / 100) * 100
        
        # Déterminer combien de chevaux utiliser selon la confiance
        if confidence >= 70:
            nb_bases = 2
            nb_complements = 2  # Total 4 chevaux
        elif confidence >= 60:
            nb_bases = 2
            nb_complements = 3  # Total 5 chevaux
        elif confidence >= 50:
            nb_bases = 3
            nb_complements = 3  # Total 6 chevaux
        elif confidence >= 40:
            nb_bases = 3
            nb_complements = 4  # Total 7 chevaux
        else:
            nb_bases = 3
            nb_complements = 5  # Total 8 chevaux
        
        total_horses = min(nb_bases + nb_complements, nb_partants)
        
        # Sélectionner les chevaux
        top_horses = course_data.head(total_horses)
        bases = top_horses.head(nb_bases)
        complements = top_horses.iloc[nb_bases:total_horses] if total_horses > nb_bases else pd.DataFrame()
        
        # 1. SIMPLE GAGNANT (toujours le top 1)
        if len(top_horses) >= 1:
            horse = top_horses.iloc[0]
            horse_conf = float(horse['Confiance']) if pd.notna(horse['Confiance']) else confidence
            
            recommendations.append({
                'type': 'Simple Gagnant',
                'priority': 1 if horse_conf >= 50 else 2,
                'formula': 'simple',
                'bases': [int(horse['Numero'])],
                'complements': [],
                'chevaux_details': [{
                    'numero': int(horse['Numero']),
                    'nom': horse['Cheval'],
                    'score': horse['Score'],
                    'role': 'GAGNANT'
                }],
                'nb_combinaisons': 1,
                'mise_unitaire': 1.00,
                'cout_total': 1.00,
                'confiance': round(horse_conf, 1),
                'rapport_estime': f"{self._safe_float(horse.get('Cote', 5)):.1f}€"
            })
        
        # 2. SIMPLE PLACÉ (top 3)
        if len(top_horses) >= 3:
            top3 = top_horses.head(3)
            for i in range(3):
                if i < len(top3):
                    horse = top3.iloc[i]
                    horse_conf = float(horse['Confiance']) if pd.notna(horse['Confiance']) else confidence
                    
                    recommendations.append({
                        'type': f'Simple Placé N°{i+1}',
                        'priority': 2,
                        'formula': 'simple',
                        'bases': [int(horse['Numero'])],
                        'complements': [],
                        'chevaux_details': [{
                            'numero': int(horse['Numero']),
                            'nom': horse['Cheval'],
                            'score': horse['Score'],
                            'role': 'PLACÉ'
                        }],
                        'nb_combinaisons': 1,
                        'mise_unitaire': 1.00,
                        'cout_total': 1.00,
                        'confiance': round(horse_conf, 1),
                        'rapport_estime': f"{self._safe_float(horse.get('Cote', 5)) * 0.3:.1f}€"
                    })
        
        # 3. COUPLÉ GAGNANT (formule champ réduit)
        if len(bases) >= 1 and len(complements) >= 1:
            base_list = [int(bases.iloc[i]['Numero']) for i in range(len(bases))]
            comp_list = [int(complements.iloc[i]['Numero']) for i in range(min(len(complements), 3))]
            
            # Calculer confiance moyenne des bases
            conf_bases = bases['Confiance'].astype(float).mean()
            
            # Formule selon nombre de bases
            if len(bases) == 1:
                formula_str = f"B/{len(comp_list)}X"
                nb_combis = len(comp_list)
            elif len(bases) == 2:
                formula_str = f"BB/{len(comp_list)}X"
                nb_combis = 1 + (2 * len(comp_list))  # BB + B×comp1 + B×comp2...
            else:
                formula_str = f"BBB/{len(comp_list)}X"
                nb_combis = 3 + (3 * len(comp_list))
            
            chevaux_details = [
                {'numero': int(bases.iloc[i]['Numero']), 'nom': bases.iloc[i]['Cheval'], 'role': 'BASE'}
                for i in range(len(bases))
            ] + [
                {'numero': n, 'nom': complements[complements['Numero'] == n]['Cheval'].iloc[0], 'role': 'COMP'}
                for n in comp_list
            ]
            
            recommendations.append({
                'type': 'Couplé Gagnant',
                'priority': 1 if conf_bases >= 55 else 2,
                'formula': formula_str,
                'bases': base_list,
                'complements': comp_list,
                'chevaux_details': chevaux_details,
                'nb_combinaisons': nb_combis,
                'mise_unitaire': 1.00,
                'cout_total': float(nb_combis),
                'confiance': round(conf_bases, 1),
                'rapport_estime': '15-50€'
            })
        
        # 4. COUPLÉ PLACÉ (même formule mais placé)
        if len(bases) >= 1 and len(complements) >= 1:
            base_list = [int(bases.iloc[i]['Numero']) for i in range(len(bases))]
            comp_list = [int(complements.iloc[i]['Numero']) for i in range(min(len(complements), 3))]
            
            conf_bases = bases['Confiance'].astype(float).mean()
            
            if len(bases) == 1:
                formula_str = f"B/{len(comp_list)}X"
                nb_combis = len(comp_list)
            elif len(bases) == 2:
                formula_str = f"BB/{len(comp_list)}X"
                nb_combis = 1 + (2 * len(comp_list))
            else:
                formula_str = f"BBB/{len(comp_list)}X"
                nb_combis = 3 + (3 * len(comp_list))
            
            chevaux_details = [
                {'numero': int(bases.iloc[i]['Numero']), 'nom': bases.iloc[i]['Cheval'], 'role': 'BASE'}
                for i in range(len(bases))
            ] + [
                {'numero': n, 'nom': complements[complements['Numero'] == n]['Cheval'].iloc[0], 'role': 'COMP'}
                for n in comp_list
            ]
            
            recommendations.append({
                'type': 'Couplé Placé',
                'priority': 2,
                'formula': formula_str,
                'bases': base_list,
                'complements': comp_list,
                'chevaux_details': chevaux_details,
                'nb_combinaisons': nb_combis,
                'mise_unitaire': 1.00,
                'cout_total': float(nb_combis),
                'confiance': round(conf_bases, 1),
                'rapport_estime': '8-25€'
            })
        
        # 5. TRIO (formule champ réduit)
        if len(bases) >= 2 and len(complements) >= 2:
            base_list = [int(bases.iloc[i]['Numero']) for i in range(min(len(bases), 3))]
            comp_list = [int(complements.iloc[i]['Numero']) for i in range(min(len(complements), 4))]
            
            # Confiance du trio = moyenne top 3
            conf_trio = top_horses.head(3)['Confiance'].astype(float).mean()
            
            # Formule trio : 2 ou 3 bases avec compléments
            if len(base_list) == 2:
                formula_str = f"BB/{len(comp_list)}X"
                # BB en ordre + BB avec chaque complément
                nb_combis = 1 + (2 * len(comp_list))
            else:
                formula_str = f"BBB/{len(comp_list)}X"
                nb_combis = 1 + (3 * len(comp_list))
            
            chevaux_details = [
                {'numero': int(bases.iloc[i]['Numero']), 'nom': bases.iloc[i]['Cheval'], 'role': 'BASE'}
                for i in range(min(len(bases), 3))
            ] + [
                {'numero': n, 'nom': complements[complements['Numero'] == n]['Cheval'].iloc[0], 'role': 'COMP'}
                for n in comp_list
            ]
            
            recommendations.append({
                'type': 'Trio',
                'priority': 1 if conf_trio >= 50 else 2,
                'formula': formula_str,
                'bases': base_list,
                'complements': comp_list,
                'chevaux_details': chevaux_details,
                'nb_combinaisons': nb_combis,
                'mise_unitaire': 1.00,
                'cout_total': float(nb_combis),
                'confiance': round(conf_trio, 1),
                'rapport_estime': '50-200€'
            })
        
        # 6. 2SUR4 (top 4-6 chevaux en bloc)
        if len(top_horses) >= 4:
            nb_for_2sur4 = min(6, len(top_horses))
            horses_2sur4 = top_horses.head(nb_for_2sur4)
            base_list = [int(horses_2sur4.iloc[i]['Numero']) for i in range(nb_for_2sur4)]
            
            # Confiance 2sur4 = moyenne des chevaux
            conf_2sur4 = horses_2sur4['Confiance'].astype(float).mean()
            
            # Calcul des combinaisons C(n,2)
            from math import comb
            nb_combis = comb(nb_for_2sur4, 2)
            
            chevaux_details = [
                {'numero': int(horses_2sur4.iloc[i]['Numero']), 'nom': horses_2sur4.iloc[i]['Cheval'], 'role': 'BLOC'}
                for i in range(nb_for_2sur4)
            ]
            
            recommendations.append({
                'type': '2sur4',
                'priority': 2,
                'formula': f"Bloc {nb_for_2sur4} chevaux",
                'bases': base_list,
                'complements': [],
                'chevaux_details': chevaux_details,
                'nb_combinaisons': nb_combis,
                'mise_unitaire': 0.50,
                'cout_total': float(nb_combis * 0.50),
                'confiance': round(conf_2sur4, 1),
                'rapport_estime': '10-50€'
            })
        
        return recommendations


class ROITracker:
    """Système de suivi des paris et calcul ROI"""
    
    def __init__(self, storage_dir="paris_joues"):
        self.storage_dir = Path.home() / "bordasAnalyse" / storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.bets_file = self.storage_dir / "paris_historique.json"
        self.load_bets()
    
    def load_bets(self):
        """Charge l'historique des paris"""
        if self.bets_file.exists():
            with open(self.bets_file, 'r') as f:
                self.bets = json.load(f)
        else:
            self.bets = []
    
    def save_bets(self):
        """Sauvegarde l'historique"""
        with open(self.bets_file, 'w') as f:
            json.dump(self.bets, f, indent=2)
    
    def add_bet(self, course, bet_type, horses, cost, date, status='en_attente'):
        """Ajoute un pari à l'historique"""
        bet_id = f"{date}_{course}_{bet_type}_{len(self.bets)}"
        
        self.bets.append({
            'id': bet_id,
            'date': date,
            'course': course,
            'type': bet_type,
            'horses': horses,
            'cout': cost,
            'status': status,
            'resultat': None,
            'gains': 0,
            'roi': 0
        })
        
        self.save_bets()
        return bet_id
    
    def update_bet_result(self, bet_id, resultat, gains):
        """Met à jour le résultat d'un pari"""
        for bet in self.bets:
            if bet['id'] == bet_id:
                bet['status'] = 'termine'
                bet['resultat'] = resultat
                bet['gains'] = gains
                bet['roi'] = ((gains - bet['cout']) / bet['cout']) * 100 if bet['cout'] > 0 else 0
                break
        
        self.save_bets()
    
    def get_statistics(self):
        """Calcule les statistiques globales"""
        if not self.bets:
            return None
        
        total_mise = sum(b['cout'] for b in self.bets)
        total_gains = sum(b['gains'] for b in self.bets)
        roi_global = ((total_gains - total_mise) / total_mise * 100) if total_mise > 0 else 0
        
        termines = [b for b in self.bets if b['status'] == 'termine']
        taux_reussite = (len([b for b in termines if b['gains'] > 0]) / len(termines) * 100) if termines else 0
        
        return {
            'total_paris': len(self.bets),
            'total_mise': total_mise,
            'total_gains': total_gains,
            'roi': roi_global,
            'taux_reussite': taux_reussite
        }
