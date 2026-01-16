# 🎯 GUIDE D'INTÉGRATION - MODULE DE PRONOSTIQUE

## 📦 Fichiers créés

1. **prediction_engine.py** - Moteur de prédiction intelligent
2. **prediction_module.py** - Interface Streamlit
3. Ce guide d'intégration

## 🚀 Installation

### Étape 1: Copier les fichiers

```bash
cd ~/bordasAnalyse
# Les 3 fichiers doivent être dans le même dossier que app_turf_dashboard.py
```

### Étape 2: Installer les dépendances supplémentaires

```bash
source venv/bin/activate
pip install openpyxl  # Pour l'export Excel
```

### Étape 3: Intégrer au dashboard

Ouvrez `app_turf_dashboard.py` et ajoutez :

**En haut du fichier (après les imports existants):**

```python
from prediction_module import display_prediction_module
```

**Dans la fonction main(), après la ligne avec les menu_options:**

Remplacez :
```python
if has_borda:
    menu_options = ["📊 Vue d'ensemble", "🎯 Scores Borda", "🎲 Favoris/Outsiders", 
                   "🏟️ Hippodromes", "👨‍🏫 Drivers", "🔍 Recherche"]
else:
    menu_options = ["📊 Vue d'ensemble", "🏟️ Hippodromes", "👨‍🏫 Drivers", 
                   "📈 Performances", "🔍 Recherche"]
```

Par :
```python
if has_borda:
    menu_options = ["📊 Vue d'ensemble", "🎯 Scores Borda", "🎲 Favoris/Outsiders", 
                   "🏟️ Hippodromes", "👨‍🏫 Drivers", "🎲 PRONOSTIQUES", "🔍 Recherche"]
else:
    menu_options = ["📊 Vue d'ensemble", "🏟️ Hippodromes", "👨‍🏫 Drivers", 
                   "📈 Performances", "🔍 Recherche"]
```

**Dans la section de navigation (après les autres elif):**

Ajoutez :
```python
elif menu == "🎲 PRONOSTIQUES" and has_borda:
    display_prediction_module(df)
```

## 🎯 Utilisation

### 1. Lancer le dashboard
```bash
./lancer_dashboard.sh
```

### 2. Charger vos données
- Upload votre fichier CSV avec Borda (export quotidien)

### 3. Aller dans "PRONOSTIQUES"
- Sélectionner une course dans la sidebar
- Cliquer sur "GÉNÉRER LES PRONOSTIQUES"

### 4. Analyser les résultats
Le système vous donne :
- ✅ Top 5 chevaux avec scores détaillés
- ✅ Stratégie de paris optimale
- ✅ Graphiques d'analyse
- ✅ Export CSV/Excel

## ⚙️ Personnalisation des Poids

### Modifier l'importance des indicateurs

Dans `prediction_engine.py`, fonction `_initialize_weights()` :

```python
return {
    # Augmenter l'importance du Borda (par défaut 40%)
    'borda_score': 0.50,  # Passer à 50%
    
    # Réduire l'importance des ELO
    'elo_cheval': 0.08,   # Au lieu de 0.10
    
    # Augmenter l'importance de l'IA
    'ia_gagnant': 0.10,   # Au lieu de 0.06
    
    # etc...
}
```

**Important:** La somme de tous les poids doit faire 1.0 (100%)

## 🎓 Comment ça fonctionne

### Algorithme de scoring

1. **Score Borda (40%)** : Sélection automatique du meilleur système selon :
   - Hippodrome (Vincennes, Pau, Cagnes, Deauville, etc.)
   - Discipline (Attelé, Monté, Plat)
   - Nombre de partants

2. **Scores ELO (25%)** : Combinaison de 5 ELO
   - Cheval (10%)
   - Jockey (8%)
   - Entraîneur (5%)
   - Propriétaire (1%)
   - Éleveur (1%)

3. **Prédictions IA (15%)** : Moyenne pondérée
   - Gagnant (6%)
   - Couplé (3%)
   - Trio (3%)
   - Multi (2%)
   - Quinté (1%)

4. **Performance historique (10%)**
   - Turf Points (4%)
   - Taux victoire (3%)
   - Taux place (3%)

5. **Facteurs stratégiques (10%)**
   - Popularité (3%)
   - Cote (3%)
   - Place à la corde (2%)
   - Repos optimal (2%)

### Calcul de la confiance

La confiance est calculée selon la **convergence des indicateurs** :
- Tous les scores pointent vers le même cheval → Confiance élevée (80-100%)
- Scores divergents → Confiance moyenne (50-70%)
- Grande dispersion → Confiance faible (20-50%)

## 🔧 Dépannage

### Erreur "No module named 'prediction_engine'"
```bash
# Vérifier que les fichiers sont au bon endroit
ls ~/bordasAnalyse/prediction_*.py
```

### Les scores sont tous à 0
- Vérifier que votre CSV contient bien les colonnes Borda
- Vérifier que les colonnes ELO_Cheval, ELO_Jockey, etc. existent

### Erreur lors de l'export Excel
```bash
pip install openpyxl --break-system-packages
# Ou dans le venv :
source venv/bin/activate
pip install openpyxl
```

## 📊 Exemple de workflow quotidien

1. **Matin** : Récupérer l'export Turf BZH du jour
2. **Charger** dans le dashboard
3. **Pour chaque course** :
   - Générer les pronostics
   - Analyser les Top 5
   - Vérifier la confiance
   - Noter la stratégie recommandée
4. **Jouer** selon les recommandations
5. **Soir** : Comparer résultats réels vs prédictions

## 🎯 Optimisation continue

### Ajuster les poids selon vos résultats

Après quelques semaines :

1. **Analyser quels indicateurs performent le mieux**
2. **Augmenter leur poids** dans `_initialize_weights()`
3. **Diminuer ceux qui performent moins**
4. **Tester sur une période**
5. **Itérer**

### Ajouter de nouveaux indicateurs

Dans `prediction_engine.py`, vous pouvez ajouter :
- Météo
- État du terrain
- Historique sur l'hippodrome
- Statistiques driver/cheval
- etc.

## 💡 Conseils d'utilisation

### ✅ À faire
- Toujours vérifier la confiance (>60% recommandé)
- Croiser avec votre propre analyse
- Utiliser pour plusieurs types de paris
- Exporter pour garder un historique

### ❌ À éviter
- Jouer aveuglément sans vérifier
- Ignorer les chevaux à forte confiance
- Parier sur des courses avec confiance <40%
- Ne pas tenir compte de la cote

## 🚀 Améliorations futures possibles

1. **Machine Learning** : Entraîner un modèle sur historique
2. **Backtesting** : Tester les stratégies sur données passées
3. **API temps réel** : Intégration cotes live
4. **Alertes** : Notifications pour opportunités
5. **Multi-courses** : Optimisation de bankroll

---

**🏇 Bon pronostic avec votre système intelligent Turf BZH !**
