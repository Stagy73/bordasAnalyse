# 🏇 Dashboard Turf BZH - Guide d'Installation

## 📋 Description
Application Streamlit pour analyser vos données de courses hippiques avec visualisations interactives.

## ✨ Fonctionnalités

### 1. Vue d'ensemble
- Statistiques globales (courses, chevaux, drivers, hippodromes)
- Évolution du nombre de courses par date
- Distribution des disciplines

### 2. Analyse des Scores Borda
- Sélection de différents systèmes Borda
- Distribution des scores
- Top 10 des chevaux par score

### 3. Favoris vs Outsiders
- Répartition entre FAVORIS, POSSIBLE, OUTSIDERS
- Performance moyenne par catégorie
- Rang moyen et cote moyenne

### 4. Analyse par Hippodrome
- Top 10 hippodromes
- Nombre de courses et chevaux
- Allocation moyenne

### 5. Analyse des Drivers
- Top 15 drivers par taux de victoire
- Statistiques détaillées (taux de victoire, taux de place, cote moyenne)

### 6. Recherche Avancée
- Recherche par nom de cheval
- Filtres par driver et hippodrome
- Affichage des résultats détaillés

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)

### Étape 1: Installer Python
Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/downloads/)

### Étape 2: Installer les dépendances
Ouvrez un terminal/invite de commandes et exécutez:

```bash
pip install streamlit pandas plotly
```

## 🎯 Utilisation

### Lancer l'application
1. Ouvrez un terminal dans le dossier contenant `app_turf_dashboard.py`
2. Exécutez la commande:

```bash
streamlit run app_turf_dashboard.py
```

3. L'application s'ouvrira automatiquement dans votre navigateur à l'adresse: `http://localhost:8501`

### Charger vos données
- **Option 1**: L'application chargera automatiquement le fichier `export_turfbzh_20260115.csv` s'il est présent
- **Option 2**: Utilisez le bouton "Charger un fichier CSV" dans la barre latérale

### Navigation
- Utilisez le menu latéral pour naviguer entre les différentes sections
- Appliquez des filtres de date pour affiner l'analyse
- Interagissez avec les graphiques (zoom, survol, etc.)

## 📊 Format des Données

Le fichier CSV doit contenir les colonnes suivantes (minimum):
- `date`: Date de la course
- `hippodrome`: Nom de l'hippodrome
- `Course`: Identifiant de la course
- `Cheval`: Nom du cheval
- `Driver`: Nom du driver
- `Cote`: Cote du cheval
- `Rank`: Classement final
- `classement`: FAVORIS/POSSIBLE/OUTSIDERS
- Colonnes Borda: `Borda - *` (tous les systèmes Borda)

## 🛠️ Personnalisation

### Modifier les couleurs
Dans le fichier `app_turf_dashboard.py`, modifiez les paramètres `color_discrete_sequence` et `color_continuous_scale` dans les graphiques Plotly.

### Ajouter de nouvelles analyses
Vous pouvez ajouter de nouvelles fonctions d'analyse en suivant le modèle des fonctions existantes.

## 📱 Utilisation Avancée

### Exporter l'application pour un usage quotidien

#### Option 1: Créer un raccourci (Windows)
1. Créez un fichier `lancer_dashboard.bat`:
```batch
@echo off
cd C:\chemin\vers\votre\dossier
streamlit run app_turf_dashboard.py
```

2. Double-cliquez sur ce fichier pour lancer l'application

#### Option 2: Créer un script (Mac/Linux)
1. Créez un fichier `lancer_dashboard.sh`:
```bash
#!/bin/bash
cd /chemin/vers/votre/dossier
streamlit run app_turf_dashboard.py
```

2. Rendez-le exécutable: `chmod +x lancer_dashboard.sh`
3. Lancez-le: `./lancer_dashboard.sh`

### Déploiement en ligne
Pour rendre l'application accessible en ligne (pour toute votre équipe):
1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre repository GitHub
3. Déployez en un clic

## 🔄 Mise à jour des données

Pour mettre à jour avec vos nouveaux exports:
1. Remplacez le fichier CSV existant
2. Ou utilisez le bouton "Charger un fichier CSV" dans l'application

## ❓ Résolution des problèmes

### L'application ne démarre pas
- Vérifiez que Python est installé: `python --version`
- Vérifiez que Streamlit est installé: `pip list | grep streamlit`
- Réinstallez les packages: `pip install --upgrade streamlit pandas plotly`

### Erreur de chargement des données
- Vérifiez que le fichier CSV est au bon format (séparateur `;`)
- Vérifiez l'encodage (UTF-8 avec BOM)

### Les graphiques ne s'affichent pas
- Actualisez la page du navigateur (F5)
- Videz le cache Streamlit: dans le menu ☰ → "Clear cache"

## 📞 Support
Pour toute question ou amélioration, n'hésitez pas à demander !

---

**Version**: 1.0
**Dernière mise à jour**: 15 janvier 2026
# bordasAnalyse
