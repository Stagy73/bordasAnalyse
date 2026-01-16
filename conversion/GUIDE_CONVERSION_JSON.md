# 🔄 Guide - Conversion JSON → CSV

## 📋 Ce que fait le script

Le script `json_to_csv_converter.py` :
1. ✅ Scanne tous vos fichiers JSON (infos, participants, orts, rapports)
2. ✅ Les regroupe par course
3. ✅ Extrait les données importantes
4. ✅ Crée un seul fichier CSV consolidé
5. ✅ Le place dans votre dossier `bordasAnalyse`

## 🚀 Utilisation

### Méthode Simple (Recommandée)

1. **Copiez le script dans le dossier contenant vos JSON**
   ```bash
   # Si vos JSON sont dans ~/Documents/turf_data/2025/
   cp json_to_csv_converter.py ~/Documents/turf_data/2025/
   cd ~/Documents/turf_data/2025/
   ```

2. **Lancez le script**
   ```bash
   python3 json_to_csv_converter.py
   ```

3. **Le script vous demandera le chemin** (appuyez juste sur Entrée s'il est dans le bon dossier)

4. **Attendez la fin** (quelques secondes à minutes selon le nombre de fichiers)

5. **Le CSV est créé** dans `~/bordasAnalyse/historique_turf_YYYYMMDD.csv`

### Méthode avec Chemin Personnalisé

Si vos JSON sont ailleurs, vous pouvez modifier le script :

```bash
nano json_to_csv_converter.py
```

Changez la ligne 15 :
```python
SOURCE_DIR = Path.home() / "Documents/turf_data/2025"  # Votre chemin
```

Puis lancez :
```bash
python3 json_to_csv_converter.py
```

## 📊 Structure du CSV Généré

Le fichier CSV contiendra :
- **date** : Date de la course
- **hippodrome** : Nom de l'hippodrome
- **numero_course** : Numéro de la course (R1C1, R2C3, etc.)
- **discipline** : Attelé, Monté, Plat
- **distance** : Distance en mètres
- **numero** : Numéro du cheval
- **cheval** : Nom du cheval
- **driver** : Driver/Jockey
- **entraineur** : Entraîneur
- **classement** : Position d'arrivée (1, 2, 3...)
- **cote** : Cote du cheval
- **age** : Âge du cheval
- **sexe** : H, F, M
- **musique** : Historique des performances

## 🎯 Exemple d'Utilisation Complète

```bash
# 1. Aller dans votre dossier bordasAnalyse
cd ~/bordasAnalyse

# 2. Lancer le convertisseur
python3 json_to_csv_converter.py

# 3. Quand demandé, indiquer où sont vos JSON
# Par exemple: /home/votre_user/Documents/turf_data/2025

# 4. Attendre la conversion
# ✓ 1234 courses traitées...

# 5. Le fichier CSV est créé automatiquement
# historique_turf_20260115.csv

# 6. Lancer le dashboard
./lancer_dashboard.sh

# 7. Charger le nouveau fichier CSV dans l'interface
```

## 🔧 Personnalisation

### Adapter la Structure JSON

Si vos JSON ont une structure différente, modifiez les fonctions :
- `extract_course_info()` → Ligne 48
- `extract_participants()` → Ligne 68
- `extract_arrivee()` → Ligne 103

### Changer le Séparateur CSV

Par défaut : `;` (point-virgule)

Pour changer en `,` (virgule) :
```python
# Ligne 241
df.to_csv(output_path, index=False, sep=',', encoding='utf-8-sig')
```

### Filtrer par Date

Pour ne convertir qu'une période :
```python
# Après la ligne 223, ajoutez :
if '2025-01' in course_id:  # Seulement janvier 2025
    rows = process_race(...)
```

## 🆘 Résolution des Problèmes

### "ModuleNotFoundError: No module named 'pandas'"

Installez pandas dans votre environnement virtuel :
```bash
source venv/bin/activate
pip install pandas
```

### "Permission denied"

Rendez le script exécutable :
```bash
chmod +x json_to_csv_converter.py
```

### "FileNotFoundError"

Vérifiez le chemin de vos JSON :
```bash
ls -la /chemin/vers/vos/json/
```

### Le CSV est vide

Vérifiez la structure de vos JSON :
```bash
cat un_fichier_infos.json | python3 -m json.tool
```

Puis adaptez les fonctions d'extraction dans le script.

## 💡 Astuces

### Traiter plusieurs dossiers

Si vous avez plusieurs dossiers (2024, 2025, etc.) :
```bash
for year in 2024 2025; do
    python3 json_to_csv_converter.py ~/Documents/turf_data/$year
done
```

### Fusionner plusieurs CSV

Si vous avez créé plusieurs CSV :
```python
import pandas as pd
import glob

all_files = glob.glob("historique_turf_*.csv")
df_list = [pd.read_csv(f, sep=';') for f in all_files]
df_combined = pd.concat(df_list, ignore_index=True)
df_combined.to_csv('historique_complet.csv', index=False, sep=';', encoding='utf-8-sig')
```

### Automatiser la Conversion

Créez un script `update_data.sh` :
```bash
#!/bin/bash
cd ~/bordasAnalyse
python3 json_to_csv_converter.py
./lancer_dashboard.sh
```

## 📈 Performances

- **1000 courses** : ~5-10 secondes
- **5000 courses** (1 an) : ~30-60 secondes
- **10000 courses** : ~2-3 minutes

## ✅ Checklist Avant Conversion

- [ ] Tous les fichiers JSON sont bien présents
- [ ] La structure des JSON est cohérente
- [ ] Python 3 et pandas sont installés
- [ ] Le dossier de destination existe
- [ ] Vous avez l'espace disque nécessaire

---

**Une fois le CSV créé, chargez-le dans votre dashboard Streamlit ! 🏇**
