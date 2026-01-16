# 🔄 GUIDE IMPORTEUR UNIVERSEL

## ✨ **NOUVEAU : IMPORT AUTOMATIQUE DE TOUS LES FORMATS**

Votre système détecte maintenant **automatiquement** le format du CSV et adapte l'import !

---

## 📦 **FORMATS SUPPORTÉS**

### **1. Export AVANT les courses**
```
Colonnes: Course, Cheval, Driver, Cote, IA_Gagnant...
Pas de: Rank, Rapport_SG
```
✅ **Import automatique** - Pronostics possibles

### **2. Export APRÈS les courses**
```
Colonnes: Course, Cheval, Driver, Cote, Rank, Rapport_SG...
Avec résultats
```
✅ **Import automatique** - Pronostics + résultats + ROI

### **3. Export historique**
```
Colonnes: course_id, ordre_arrivee, cote_direct...
Format complètement différent
```
✅ **Import automatique** - Historique complet

### **4. Noms de colonnes variables**
- `Course` ou `course_id` ou `code_course`
- `Cote` ou `cote_direct` ou `cote_pmu`
- `Rank` ou `rang_arrivee` ou `ordre_arrivee`

✅ **Détection automatique** de tous les variants !

---

## 🚀 **UTILISATION**

### **Option 1 : Interface Streamlit (recommandé)**

1. Ouvrez le dashboard
2. Sidebar → "📥 Importer un export CSV"
3. Glissez-déposez **n'importe quel** export TurfBZH
4. ✅ Import automatique !

**Pas besoin de se soucier du format !**

### **Option 2 : Ligne de commande**

```fish
cd ~/bordasAnalyse

# Import n'importe quel fichier
python3 universal_importer.py mon_fichier.csv

# Avec date spécifique (si pas dans le CSV)
python3 universal_importer.py mon_fichier.csv 2026-01-16
```

---

## 🎯 **WORKFLOW QUOTIDIEN**

### **Matin (avant les courses) :**

```
1. Export TurfBZH (sans résultats)
2. Import dans Streamlit
3. 🎯 PRONOSTICS GLOBAUX
4. Recalculer Borda
5. Voir les pronostics
6. Sélectionner les paris
```

### **Soir (après les courses) :**

```
1. Export TurfBZH (avec résultats)
2. Import dans Streamlit
3. 💰 SUIVI ROI
4. Calcul automatique gains/pertes
5. Analyse performances
```

**Même fichier, même import - le système s'adapte !**

---

## 🔍 **DÉTECTION AUTOMATIQUE**

L'importeur analyse le CSV et détecte :

### **Format**
- Standard TurfBZH → `import_standard()`
- Historique → `import_historique()`
- Inconnu → Erreur explicite

### **Colonnes disponibles**
- Mappings automatiques pour ~20 types de données
- Chaque champ a 2-5 variantes possibles
- Si absent → `None` (pas d'erreur)

### **Date**
1. Lit la colonne `date` si présente
2. Extrait du nom de fichier si possible
3. Utilise la date du jour sinon

---

## 📋 **EXEMPLES**

### **Fichier du matin (pronostics) :**

```csv
Course;Cheval;Driver;Cote;IA_Gagnant;IA_Couple
R1C1;DADDY JOY;T. Bachelot;18;0.118;0.186
R1C1;FAST WIND;A. Lemaitre;5.2;0.352;0.445
```

✅ Import OK - Pas de `Rank` → Pas grave !

### **Fichier du soir (résultats) :**

```csv
Course;Cheval;Driver;Cote;Rank;Rapport_SG
R1C1;FAST WIND;A. Lemaitre;5.2;1;5.2
R1C1;DADDY JOY;T. Bachelot;18;4;
```

✅ Import OK - Avec `Rank` → ROI calculable !

### **Fichier historique :**

```csv
course_id;cheval;driver;ordre_arrivee;cote_direct
R1C1;CHITCHAT;M. Mottier;1;3.5
R1C2;BELLO;J. Dubois;3;8.2
```

✅ Import OK - Format différent détecté !

---

## ⚙️ **MAPPINGS AUTOMATIQUES**

Chaque donnée a plusieurs noms possibles :

| Donnée | Variantes |
|--------|-----------|
| Course | Course, course_id, code_course |
| Cote | Cote, cote_direct, cote_pmu |
| Rang | Rank, rang_arrivee, ordre_arrivee |
| Cheval | Cheval, cheval, CHEVAL/MUSIQ. |
| Driver | Driver, driver, DRIVER/ENTRAINEUR |
| IA Note | IA_Gagnant, ia_gagnant |
| Date | date, Date |

**+15 autres champs supportés !**

---

## 🔧 **FICHIERS MODIFIÉS**

### **universal_importer.py** (nouveau)
- Détection automatique du format
- Mappings de colonnes
- Import adaptatif

### **streamlit_db_adapter.py** (mis à jour)
- Utilise l'importeur universel
- Plus besoin de spécifier le format

### **turf_database_complete.py** (mis à jour)
- Lit la date depuis le CSV

---

## 📊 **AVANTAGES**

✅ **Zéro configuration** - Détection automatique  
✅ **Tous les exports** - Avant/après/historique  
✅ **Colonnes flexibles** - Variantes supportées  
✅ **Pas d'erreur** - Colonnes manquantes = NULL  
✅ **Même workflow** - Un seul bouton import  

---

## 🎉 **RÉSULTAT**

**Vous n'avez plus à vous soucier du format !**

Tous les exports TurfBZH fonctionnent :
- ✅ Pronostics du matin
- ✅ Résultats du soir
- ✅ Historiques complets
- ✅ Formats variables

**Un seul bouton "Import" pour tout ! 🚀**

---

## 🔍 **TEST**

```fish
cd ~/bordasAnalyse

# Télécharger universal_importer.py
# Télécharger streamlit_db_adapter.py (mis à jour)

# Tester avec votre fichier du 16/01
python3 universal_importer.py export_turfbzh_20260116.csv

# Résultat attendu :
# 🔍 Format détecté: sans_resultats
# ✅ Courses: 55
# ✅ Partants: 633
```

**Plus jamais de problème d'import ! ✨**
