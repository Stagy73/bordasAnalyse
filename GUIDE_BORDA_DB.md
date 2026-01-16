# 🎯 GUIDE COMPLET - SYSTÈME BORDA AVEC BASE DE DONNÉES

## ✨ **NOUVEAUTÉS**

Votre système calcule maintenant les scores Borda **directement depuis la base de données** et les stocke pour réutilisation !

---

## 📦 **FICHIERS À TÉLÉCHARGER**

Depuis les outputs, téléchargez ces 3 fichiers dans `~/bordasAnalyse/` :

1. ✅ **borda_calculator_db.py** - Moteur de calcul Borda
2. ✅ **global_predictions_db.py** - Interface pronostics mise à jour
3. ✅ **app_turf_dashboard_db.py** - Dashboard mis à jour

---

## 🚀 **INSTALLATION**

```fish
cd ~/bordasAnalyse

# Téléchargez les 3 fichiers ci-dessus
# Puis remplacez le dashboard :

mv app_turf_dashboard.py app_turf_dashboard_OLD.py
mv app_turf_dashboard_db.py app_turf_dashboard.py

# Relancer Streamlit
streamlit run app_turf_dashboard.py
```

---

## 🎯 **UTILISATION**

### **1. Calculer les scores Borda**

#### **Option A : Depuis le Dashboard**

1. Ouvrez **🎯 PRONOSTICS GLOBAUX**
2. Sélectionnez la date
3. Cliquez sur **🔄 Recalculer les scores Borda**
4. ✅ Les scores sont calculés et stockés dans la DB !

#### **Option B : En ligne de commande**

```fish
cd ~/bordasAnalyse

# Calculer pour aujourd'hui
python3 borda_calculator_db.py

# Ou pour une date spécifique
python3 -c "
from borda_calculator_db import BordaCalculator
from datetime import date
calc = BordaCalculator()
stats = calc.calculate_all_today(date(2026, 1, 16))
print(f'Courses: {stats[\"courses_calculees\"]}')
"
```

---

### **2. Voir les pronostics**

Dans le dashboard :

1. Menu **🎯 PRONOSTICS GLOBAUX**
2. Sélectionnez la date
3. 📊 Les courses s'affichent avec TOP 5, scores, cotes
4. 💾 Export CSV disponible

---

### **3. Personnaliser les critères Borda**

Par défaut :
- IA Gagnant : 30 points
- IA Couplé : 15 points
- IA Trio : 10 points
- Cote BZH : 20 points
- ELO Cheval : 15 points
- ELO Jockey : 10 points

**Total : 100 points**

Pour modifier, éditez `borda_calculator_db.py`, ligne 18 :

```python
def get_default_criteria(self):
    return {
        'IA_Gagnant': 35,      # Augmenter
        'ia_couple': 15,
        'ia_trio': 10,
        'Cote BZH': 25,        # Augmenter
        'ELO_Cheval': 10,      # Diminuer
        'ELO_Jockey': 5        # Diminuer
    }
```

---

## 📊 **STRUCTURE DES DONNÉES**

### **Table `borda_scores` :**

```
partant_id    | config_id | score_total | rang | details
------------- | --------- | ----------- | ---- | -------
123           | default   | 87.5        | 1    | {...}
124           | default   | 72.3        | 2    | {...}
```

### **Avantages :**

✅ **Réutilisation** - Scores calculés une fois, utilisables partout  
✅ **Historique** - Conservation des scores passés  
✅ **Comparaison** - Plusieurs configs Borda possibles  
✅ **Performance** - Pas besoin de recalculer à chaque affichage  

---

## 🔧 **WORKFLOW QUOTIDIEN**

### **Matin :**

```fish
cd ~/bordasAnalyse

# 1. Import du CSV du jour
python3 test_import.py  # ou via interface Streamlit

# 2. Calcul des scores Borda
python3 borda_calculator_db.py

# 3. Lancer le dashboard
streamlit run app_turf_dashboard.py
```

### **Dans le dashboard :**

1. 📊 Vue d'ensemble - Stats globales
2. 🎯 PRONOSTICS GLOBAUX - Voir tous les pronostics
3. 💰 Betting interface - Sélectionner les paris
4. ⭐ Favoris - Vérifier si vos chevaux courent

---

## 📈 **FONCTIONNALITÉS AVANCÉES**

### **Calcul sélectif :**

```python
from borda_calculator_db import BordaCalculator

calc = BordaCalculator()

# Calculer une seule course
df = calc.calculate_borda_for_course('R1C1')
calc.save_borda_scores('R1C1', df)

# Récupérer les scores stockés
scores = calc.get_borda_scores_for_course('R1C1')
print(scores)
```

### **Critères personnalisés par course :**

```python
# Critères pour trot
criteria_trot = {
    'IA_Gagnant': 40,
    'ELO_Cheval': 30,
    'Cote BZH': 30
}

# Critères pour plat
criteria_plat = {
    'IA_Gagnant': 35,
    'ELO_Jockey': 30,
    'Cote BZH': 35
}

df_trot = calc.calculate_borda_for_course('R1C1', criteria_trot)
df_plat = calc.calculate_borda_for_course('R2C1', criteria_plat)
```

---

## 🎯 **EXPORT DES PRONOSTICS**

Dans **PRONOSTICS GLOBAUX** :

1. Cliquez sur **💾 Télécharger tous les pronostics (CSV)**
2. Fichier généré : `pronostics_2026-01-16.csv`

Format :
```
Course;Hippodrome;Heure;Pronostic;Confiance
R1C1;Deauville;16:03;1-10-6-8-15;87.5
R1C2;Deauville;16:35;3-7-12-1-9;82.3
```

---

## ⚙️ **CONFIGURATIONS MULTIPLES**

Créez plusieurs configs Borda :

```python
# Config 1 : Conservatrice (favoris)
calc.save_borda_scores('R1C1', df, config_id='conservateur')

# Config 2 : Risquée (outsiders)
calc.save_borda_scores('R1C1', df, config_id='risque')

# Récupérer une config spécifique
scores = calc.get_borda_scores_for_course('R1C1', 'conservateur')
```

---

## 🔍 **DEBUGGING**

### **Vérifier les scores stockés :**

```fish
python3 -c "
from turf_database_complete import get_turf_database
db = get_turf_database()

db.cursor.execute('SELECT COUNT(*) FROM borda_scores')
print(f'Scores stockés: {db.cursor.fetchone()[0]}')

db.cursor.execute('SELECT DISTINCT config_id FROM borda_scores')
print(f'Configs: {[r[0] for r in db.cursor.fetchall()]}')
"
```

### **Recalculer tout :**

```fish
# Supprimer les anciens scores
python3 -c "
from turf_database_complete import get_turf_database
db = get_turf_database()
db.cursor.execute('DELETE FROM borda_scores')
db.conn.commit()
print('✅ Scores effacés')
"

# Recalculer
python3 borda_calculator_db.py
```

---

## ✅ **RÉSUMÉ**

### **Ce que vous avez maintenant :**

1. ✅ Calcul Borda depuis la DB
2. ✅ Stockage des scores
3. ✅ Interface pronostics mise à jour
4. ✅ Export CSV des pronostics
5. ✅ Personnalisation des critères
6. ✅ Configurations multiples

### **Workflow simplifié :**

```
Import CSV → Calcul Borda → Pronostics → Paris → ROI
     ↓            ↓             ↓          ↓       ↓
    DB  →     borda_scores → Interface → Suivi → Stats
```

**Votre système est maintenant 100% base de données ! 🎉**
