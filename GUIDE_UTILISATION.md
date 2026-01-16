# 🎯 Guide d'Utilisation - Dashboard Turf BZH

## 📸 Aperçu des Fonctionnalités

### 1. Page d'Accueil - Vue d'Ensemble
**Ce que vous verrez:**
- 4 cartes en haut affichant:
  - Nombre total de courses
  - Nombre de chevaux uniques
  - Nombre de drivers
  - Nombre d'hippodromes
- Graphique de l'évolution des courses dans le temps
- Distribution des disciplines (Attelé, Monté, Plat)

**Comment l'utiliser:**
- Les graphiques sont interactifs: survolez pour voir les détails
- Zoomez en sélectionnant une zone avec la souris
- Double-cliquez pour réinitialiser le zoom

### 2. Scores Borda
**Ce que vous verrez:**
- Menu déroulant pour choisir parmi tous vos systèmes Borda
- Histogramme montrant la distribution des scores
- Tableau des 10 meilleurs chevaux pour le système sélectionné

**Comment l'utiliser:**
- Sélectionnez un système Borda dans le menu déroulant
- Comparez les performances entre différents systèmes
- Identifiez les chevaux avec les meilleurs scores

**Systèmes Borda disponibles dans vos données:**
- Borda par Défaut
- Deauville galot pcf
- Pau attelé / monté / plat
- Cagne sur mer attelé / monté
- Le Boucast
- Vincennes (plusieurs variantes selon nombre de chevaux)

### 3. Favoris vs Outsiders
**Ce que vous verrez:**
- Graphique circulaire montrant la répartition:
  - FAVORIS (en vert)
  - POSSIBLE (en orange)
  - OUTSIDERS (en bleu)
- Tableau de performance par catégorie avec:
  - Rang moyen
  - Cote moyenne

**Comment interpréter:**
- Un rang moyen bas = meilleure performance
- Compare si vos favoris arrivent bien dans les premiers
- Identifie les outsiders qui surprennent

### 4. Analyse par Hippodrome
**Ce que vous verrez:**
- Graphique horizontal des 10 hippodromes les plus actifs
- Tableau détaillé avec:
  - Nombre de courses
  - Nombre de chevaux
  - Allocation moyenne

**Utilisation pratique:**
- Identifiez vos hippodromes favoris
- Comparez les allocations (courses plus riches)
- Analysez où vous avez le plus de données

### 5. Analyse des Drivers
**Ce que vous verrez:**
- Top 15 des meilleurs drivers par taux de victoire
- Tableau avec statistiques complètes:
  - Nombre de courses
  - Taux de victoire moyen
  - Taux de place moyen
  - Cote moyenne

**Comment l'utiliser:**
- Identifiez les drivers les plus performants
- Filtrez ceux ayant au minimum 5 courses (pour données fiables)
- Comparez avec les cotes moyennes

### 6. Recherche Avancée
**Ce que vous verrez:**
- 3 zones de filtrage:
  - Barre de recherche pour le nom du cheval
  - Menu déroulant pour le driver
  - Menu déroulant pour l'hippodrome
- Tableau des résultats avec toutes les informations importantes

**Comment l'utiliser:**
- Tapez quelques lettres du nom du cheval (pas besoin du nom complet)
- Combinez les filtres (ex: "CHI" + "Paris-Vincennes" + "B. Rochard")
- Cliquez sur les en-têtes de colonnes pour trier

## 🎨 Filtres Globaux (Barre Latérale)

### Filtre de Date
- Sélectionnez une période spécifique
- Par défaut: toutes les dates disponibles
- Utile pour analyser une semaine ou un mois précis

### Charger un Nouveau Fichier
- Bouton en haut de la barre latérale
- Accepte les fichiers CSV au format Turf BZH
- Le nouveau fichier remplace temporairement les données

## 💡 Astuces d'Utilisation

### Navigation Rapide
- Utilisez le menu latéral pour passer d'une section à l'autre
- Les données sont mises en cache: navigation ultra-rapide après le premier chargement

### Export de Données
Pour exporter un graphique:
1. Survolez le graphique
2. Cliquez sur l'icône 📷 en haut à droite
3. Choisissez "Download plot as png"

### Actualisation des Données
- Ajoutez votre nouveau export dans le dossier
- Utilisez le bouton "Charger un fichier CSV"
- Ou remplacez directement le fichier existant et actualisez la page (R)

### Performance
- L'application charge les données en mémoire (très rapide)
- Pas de limite de taille de fichier (testé jusqu'à 10 000 courses)
- Si lent: réduisez la période via le filtre de date

## 🔍 Exemples d'Analyses Possibles

### Analyse 1: Meilleur Système Borda
1. Allez dans "Scores Borda"
2. Testez chaque système
3. Notez quel système place le plus de chevaux dans le top 10

### Analyse 2: Performance des Favoris
1. Section "Favoris/Outsiders"
2. Regardez le rang moyen des FAVORIS
3. Si < 4: vos favoris sont bien choisis !

### Analyse 3: Meilleur Couple Driver/Hippodrome
1. Section "Drivers"
2. Notez les meilleurs drivers
3. Section "Recherche" → filtrez par ce driver
4. Analysez ses hippodromes de prédilection

### Analyse 4: Suivi d'un Cheval
1. Section "Recherche"
2. Tapez le nom du cheval
3. Voyez son historique complet
4. Analysez l'évolution de ses performances

## 🚀 Améliorations Futures Possibles

Vous pourriez demander d'ajouter:
- Export Excel des résultats filtrés
- Graphiques de corrélation entre différents scores
- Prédictions basées sur l'historique
- Alertes pour les chevaux à forte probabilité
- Analyse de rentabilité (gains vs mises)
- Comparaison de plusieurs périodes
- Dashboard temps réel (si données live)

## 📊 Interprétation des Métriques

### Taux de Victoire
- 0.20 = 20% de victoires
- > 0.25 = Excellent
- 0.15-0.25 = Bon
- < 0.15 = Moyen

### Taux de Place
- Place = Top 3 généralement
- 0.50 = 50% dans les 3 premiers
- > 0.60 = Excellent
- < 0.40 = Faible

### Cote
- < 5 = Grand favori
- 5-15 = Possible
- > 15 = Outsider
- > 50 = Très grosse cote

### Note IA
- Échelle généralement de 0 à 20
- > 15 = Très bon pronostic
- 10-15 = Bon
- < 10 = Faible probabilité

## ❓ FAQ

**Q: Puis-je utiliser l'application sans connexion Internet?**
R: Oui! Une fois installée, l'application fonctionne 100% en local.

**Q: Combien de données puis-je charger?**
R: Aucune limite pratique. Testé avec 10 000+ courses sans problème.

**Q: Puis-je modifier les couleurs?**
R: Oui, modifiez le fichier Python (section "Personnalisation" du README).

**Q: L'application est-elle sécurisée?**
R: Oui, toutes vos données restent sur votre ordinateur.

**Q: Puis-je partager mon dashboard?**
R: Oui, déployez sur Streamlit Cloud (gratuit) pour un accès web.

**Q: Comment sauvegarder mes filtres?**
R: Actuellement non disponible, mais peut être ajouté facilement.

---

**Bon pronostic avec votre Dashboard Turf BZH ! 🏇**
