#!/usr/bin/env python3
"""
Script de conversion JSON → CSV pour données Turf
Convertit tous les fichiers JSON en un seul CSV consolidé
"""

import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Configuration
SOURCE_DIR = Path.home() / "path/to/json/folder"  # À MODIFIER
DESTINATION_DIR = Path.home() / "bordasAnalyse"
OUTPUT_FILENAME = f"historique_turf_{datetime.now().strftime('%Y%m%d')}.csv"

def find_json_files(directory):
    """Trouve tous les fichiers JSON dans le dossier et ses sous-dossiers"""
    json_files = {
        'infos': [],
        'participants': [],
        'rapports': [],
        'orts': []
    }
    
    for file_path in directory.rglob('*.json'):
        filename = file_path.name
        
        if 'infos' in filename:
            json_files['infos'].append(file_path)
        elif 'participants' in filename or 'cipants' in filename:
            json_files['participants'].append(file_path)
        elif 'rapp' in filename:
            json_files['rapports'].append(file_path)
        elif 'orts' in filename:
            json_files['orts'].append(file_path)
    
    return json_files

def load_json_safe(file_path):
    """Charge un fichier JSON de manière sécurisée"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Erreur lecture {file_path.name}: {e}")
        return None

def extract_course_info(infos_data):
    """Extrait les informations de la course"""
    if not infos_data:
        return {}
    
    info = {}
    try:
        # Convertir le timestamp en date
        timestamp = infos_data.get('heureDepart', 0)
        if timestamp:
            date_obj = datetime.fromtimestamp(timestamp / 1000)  # milliseconds to seconds
            info['date'] = date_obj.strftime('%Y-%m-%d')
            info['heure'] = date_obj.strftime('%H:%M')
        else:
            info['date'] = ''
            info['heure'] = ''
        
        # Informations hippodrome
        hippodrome = infos_data.get('hippodrome', {})
        info['code_hippodrome'] = hippodrome.get('codeHippodrome', '')
        info['hippodrome'] = hippodrome.get('libelleLong', '')
        info['hippodrome_court'] = hippodrome.get('libelleCourt', '')
        
        # Informations course
        info['numero_reunion'] = infos_data.get('numReunion', '')
        info['numero_course'] = infos_data.get('numOrdre', '')
        info['course_id'] = f"R{info['numero_reunion']}C{info['numero_course']}"
        info['libelle'] = infos_data.get('libelle', '')
        info['libelle_court'] = infos_data.get('libelleCourt', '')
        
        # Caractéristiques
        info['discipline'] = infos_data.get('discipline', '')
        info['specialite'] = infos_data.get('specialite', '')
        info['distance'] = infos_data.get('distance', '')
        info['parcours'] = infos_data.get('parcours', '')
        info['type_piste'] = infos_data.get('typePiste', '')
        info['corde'] = infos_data.get('corde', '')
        
        # Allocations
        info['montant_prix'] = infos_data.get('montantPrix', '')
        info['montant_total'] = infos_data.get('montantTotalOffert', '')
        
        # Conditions
        info['nombre_partants'] = infos_data.get('nombreDeclaresPartants', '')
        info['categorie_particularite'] = infos_data.get('categorieParticularite', '')
        info['condition_age'] = infos_data.get('conditionAge', '')
        info['condition_sexe'] = infos_data.get('conditionSexe', '')
        
        # Statut
        info['statut'] = infos_data.get('statut', '')
        info['arrivee_definitive'] = infos_data.get('arriveeDefinitive', False)
        
    except Exception as e:
        print(f"⚠️  Erreur extraction info: {e}")
    
    return info

def extract_participants(participants_data):
    """Extrait les informations des participants"""
    if not participants_data:
        return []
    
    participants = []
    try:
        # Les participants sont dans une clé 'participants'
        partants_list = participants_data.get('participants', [])
        
        for cheval in partants_list:
            participant = {
                'numero': cheval.get('numPmu', ''),
                'cheval': cheval.get('nom', ''),
                'driver': cheval.get('driver', ''),
                'entraineur': cheval.get('entraineur', ''),
                'proprietaire': cheval.get('proprietaire', ''),
                'age': cheval.get('age', ''),
                'sexe': cheval.get('sexe', ''),
                'race': cheval.get('race', ''),
                'pays': cheval.get('pays', ''),
                'musique': cheval.get('musique', ''),
                'statut': cheval.get('statut', ''),
                'place_corde': cheval.get('placeCorde', ''),
                'oeilleres': cheval.get('oeilleres', ''),
                
                # Statistiques carrière
                'nombre_courses': cheval.get('nombreCourses', ''),
                'nombre_victoires': cheval.get('nombreVictoires', ''),
                'nombre_places': cheval.get('nombrePlaces', ''),
                
                # Gains
                'gains_carriere': cheval.get('gainsParticipant', {}).get('gainsCarriere', ''),
                'gains_victoires': cheval.get('gainsParticipant', {}).get('gainsVictoires', ''),
                'gains_annee_courante': cheval.get('gainsParticipant', {}).get('gainsAnneeEnCours', ''),
                'gains_annee_precedente': cheval.get('gainsParticipant', {}).get('gainsAnneePrecedente', ''),
                
                # Handicap
                'handicap_valeur': cheval.get('handicapValeur', ''),
                'handicap_poids': cheval.get('handicapPoids', ''),
                
                # Cote
                'cote_direct': cheval.get('dernierRapportDirect', {}).get('rapport', ''),
                'cote_reference': cheval.get('dernierRapportReference', {}).get('rapport', ''),
                'favoris': cheval.get('dernierRapportDirect', {}).get('favoris', False),
                
                # Généalogie
                'nom_pere': cheval.get('nomPere', ''),
                'nom_mere': cheval.get('nomMere', ''),
                'eleveur': cheval.get('eleveur', ''),
                
                # Résultat (peut être vide si pas encore couru)
                'ordre_arrivee': cheval.get('ordreArrivee', ''),
                'distance_precedent': cheval.get('distanceChevalPrecedent', {}).get('libelleCourt', '')
            }
            participants.append(participant)
            
    except Exception as e:
        print(f"⚠️  Erreur extraction participants: {e}")
        import traceback
        traceback.print_exc()
    
    return participants

def extract_rapports(rapports_data):
    """Extrait les rapports (résultats des paris)"""
    if not rapports_data:
        return {}
    
    rapports = {}
    try:
        # rapports_data est une liste de types de paris
        for pari in rapports_data:
            type_pari = pari.get('typePari', '')
            
            # Pour les paris simples, prendre le premier rapport
            if 'rapports' in pari and len(pari['rapports']) > 0:
                premier_rapport = pari['rapports'][0]
                
                if type_pari == 'E_SIMPLE_GAGNANT':
                    rapports['rapport_gagnant'] = premier_rapport.get('dividende', '')
                    rapports['combinaison_gagnant'] = premier_rapport.get('combinaison', '')
                elif type_pari == 'E_SIMPLE_PLACE':
                    # Prendre tous les rapports place
                    places = [r.get('combinaison', '') for r in pari['rapports']]
                    rapports['rapport_place'] = ', '.join(map(str, places))
                elif type_pari == 'E_COUPLE_GAGNANT':
                    rapports['rapport_couple_gagnant'] = premier_rapport.get('dividende', '')
                    rapports['combinaison_couple'] = premier_rapport.get('combinaison', '')
                elif type_pari == 'E_TRIO':
                    rapports['rapport_trio'] = premier_rapport.get('dividende', '')
                    rapports['combinaison_trio'] = premier_rapport.get('combinaison', '')
                    
    except Exception as e:
        print(f"⚠️  Erreur extraction rapports: {e}")
    
    return rapports

def extract_arrivee(infos_data):
    """Extrait l'ordre d'arrivée depuis le fichier infos"""
    if not infos_data:
        return {}
    
    arrivee = {}
    try:
        # L'ordre d'arrivée est dans le fichier infos, pas dans orts
        ordre_arrivee = infos_data.get('ordreArrivee', [])
        
        # ordreArrivee est une liste de listes: [[5], [6], [7], [2], ...]
        # où chaque sous-liste contient le(s) numéro(s) de cheval(aux) pour cette position
        for position, numeros_list in enumerate(ordre_arrivee, 1):
            for numero in numeros_list:
                arrivee[numero] = position
                
    except Exception as e:
        print(f"⚠️  Erreur extraction arrivée: {e}")
    
    return arrivee

def process_race(infos_file, participants_file, orts_file=None, rapports_file=None):
    """Traite une course complète"""
    # Charger les données
    infos_data = load_json_safe(infos_file) if infos_file else None
    participants_data = load_json_safe(participants_file) if participants_file else None
    rapports_data = load_json_safe(rapports_file) if rapports_file else None
    
    # Extraire les infos
    course_info = extract_course_info(infos_data)
    participants = extract_participants(participants_data)
    arrivee = extract_arrivee(infos_data)  # L'arrivée est dans infos, pas orts
    rapports = extract_rapports(rapports_data)
    
    # Créer les lignes du CSV
    rows = []
    for participant in participants:
        row = {**course_info, **participant, **rapports}
        
        # Le classement est déjà dans participant['ordre_arrivee']
        # Mais on peut aussi le vérifier/compléter depuis arrivee
        numero = participant.get('numero', '')
        if not row.get('ordre_arrivee') and numero in arrivee:
            row['ordre_arrivee'] = arrivee.get(numero, '')
        
        rows.append(row)
    
    return rows

def main():
    print("=" * 60)
    print("🏇 Conversion JSON → CSV - Données Turf")
    print("=" * 60)
    print()
    
    # Demander le dossier source si non configuré
    if str(SOURCE_DIR) == str(Path.home() / "path/to/json/folder"):
        print("📁 Où sont vos fichiers JSON ?")
        source_input = input("Chemin complet du dossier (ou appuyez sur Entrée pour le dossier actuel): ").strip()
        
        if source_input:
            source_dir = Path(source_input)
        else:
            source_dir = Path.cwd()
    else:
        source_dir = SOURCE_DIR
    
    if not source_dir.exists():
        print(f"❌ Erreur: Le dossier {source_dir} n'existe pas!")
        return
    
    print(f"📂 Dossier source: {source_dir}")
    print(f"📂 Dossier destination: {DESTINATION_DIR}")
    print()
    
    # Créer le dossier de destination si nécessaire
    DESTINATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Trouver tous les fichiers JSON
    print("🔍 Recherche des fichiers JSON...")
    json_files = find_json_files(source_dir)
    
    total_files = sum(len(files) for files in json_files.values())
    print(f"✅ {total_files} fichiers JSON trouvés:")
    print(f"   - Infos: {len(json_files['infos'])}")
    print(f"   - Participants: {len(json_files['participants'])}")
    print(f"   - Rapports: {len(json_files['rapports'])}")
    print(f"   - Orts: {len(json_files['orts'])}")
    print()
    
    if total_files == 0:
        print("❌ Aucun fichier JSON trouvé!")
        return
    
    # Grouper les fichiers par course
    print("🔄 Traitement des courses...")
    courses = {}
    
    # Utiliser les fichiers infos comme référence
    for infos_file in json_files['infos']:
        # Extraire l'identifiant de la course du nom de fichier
        # Ex: 2025-01-02_R1_C1_infos.json → 2025-01-02_R1_C1
        course_id = infos_file.stem.replace('_infos', '').replace('.json', '')
        
        courses[course_id] = {
            'infos': infos_file,
            'participants': None,
            'orts': None,
            'rapports': None
        }
    
    # Associer les autres fichiers
    for participants_file in json_files['participants']:
        course_id = participants_file.stem.replace('_participants', '').replace('_cipants', '').replace('.json', '')
        if course_id in courses:
            courses[course_id]['participants'] = participants_file
    
    for orts_file in json_files['orts']:
        course_id = orts_file.stem.replace('_orts', '').replace('.json', '')
        if course_id in courses:
            courses[course_id]['orts'] = orts_file
    
    for rapports_file in json_files['rapports']:
        course_id = rapports_file.stem.replace('_rapp', '').replace('_rapports', '').replace('.json', '')
        if course_id in courses:
            courses[course_id]['rapports'] = rapports_file
    
    print(f"📊 {len(courses)} courses identifiées")
    print()
    
    # Traiter chaque course
    all_rows = []
    processed = 0
    errors = 0
    
    for course_id, files in courses.items():
        try:
            rows = process_race(
                files['infos'],
                files['participants'],
                files['orts'],
                files['rapports']
            )
            all_rows.extend(rows)
            processed += 1
            
            if processed % 50 == 0:
                print(f"   ✓ {processed}/{len(courses)} courses traitées...")
        except Exception as e:
            print(f"   ⚠️  Erreur course {course_id}: {e}")
            errors += 1
    
    print(f"✅ {processed} courses traitées avec succès")
    if errors > 0:
        print(f"⚠️  {errors} erreurs")
    print()
    
    # Créer le DataFrame et sauvegarder
    if all_rows:
        print("💾 Création du fichier CSV...")
        df = pd.DataFrame(all_rows)
        
        # Réorganiser les colonnes
        priority_cols = ['date', 'heure', 'hippodrome', 'course_id', 'numero_reunion', 'numero_course',
                        'discipline', 'distance', 'numero', 'cheval', 'driver', 'entraineur', 
                        'ordre_arrivee', 'cote_direct', 'cote_reference', 'favoris', 'age', 'sexe',
                        'nombre_courses', 'nombre_victoires', 'musique']
        other_cols = [col for col in df.columns if col not in priority_cols]
        
        # Ne garder que les colonnes qui existent réellement
        final_cols = [col for col in priority_cols if col in df.columns] + other_cols
        df = df[final_cols]
        
        # Sauvegarder
        output_path = DESTINATION_DIR / OUTPUT_FILENAME
        df.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"✅ Fichier créé: {output_path}")
        print(f"📊 {len(df)} lignes (chevaux)")
        print(f"📊 {len(df['numero_course'].unique())} courses uniques")
        print()
        print("=" * 60)
        print("🎉 Conversion terminée avec succès!")
        print("=" * 60)
        print()
        print(f"👉 Vous pouvez maintenant charger {OUTPUT_FILENAME}")
        print(f"   dans votre dashboard Streamlit!")
    else:
        print("❌ Aucune donnée extraite!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
