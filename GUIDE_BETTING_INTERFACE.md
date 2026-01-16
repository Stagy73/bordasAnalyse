# 🎉 NOUVELLES FONCTIONNALITÉS - GUIDE D'UTILISATION

## ✅ CE QUI A ÉTÉ AJOUTÉ

Nous avons restauré deux fonctionnalités essentielles de votre système de pronostics :

### 1️⃣ **FILTRE PAR RÉUNION** (dans PRONOSTICS GLOBAUX)
### 2️⃣ **INTERFACE DE PARIS** (nouveau menu)

---

## 📋 INSTALLATION

```bash
cd ~/bordasAnalyse

# 1. Télécharger les fichiers depuis outputs :
#    - global_predictions_db.py (mis à jour)
#    - betting_interface_db.py (nouveau)
#    - app_turf_dashboard.py (mis à jour)

# 2. Redémarrer Streamlit
streamlit run app_turf_dashboard.py
```

---

## 🎯 FONCTIONNALITÉ 1 : FILTRE PAR RÉUNION

### **Où ?**
Menu : **🎯 PRONOSTICS GLOBAUX**

### **Utilisation :**

1. Sélectionnez une **date** (ex: 2026-01-16)
2. Un **nouveau sélecteur "Réunion"** apparaît :
   - `Toutes` : Affiche toutes les 55 courses
   - `R1 - Deauville` : Affiche uniquement les courses de R1
   - `R2 - Nantes` : Affiche uniquement les courses de R2
   - etc.

3. Cliquez **"🔄 Recalculer les scores Borda"** si besoin

### **Avantages :**
- ✅ Navigation rapide par réunion
- ✅ Focus sur une réunion spécifique
- ✅ Moins de scrolling

---

## 💰 FONCTIONNALITÉ 2 : INTERFACE DE PARIS

### **Où ?**
Nouveau menu : **💰 Interface de Paris**

### **Ce que vous pouvez faire :**

#### **📝 Onglet "Sélectionner mes paris"**

Pour **chaque course**, vous pouvez cocher :

**1. 🎯 Simple Gagnant**
- Mise sur le n°1 du Borda gagnant
- Saisir votre mise (€)
- Voir la cote PMU

**2. 📍 Simple Placé**
- Mise sur le n°1 du Borda placé (top 3)
- Saisir votre mise

**3. 👥 Couplé**
- Mise sur les 2 premiers du Borda
- Choisir : Gagnant / Placé / Ordre
- Saisir votre mise

**4. 🎲 Trio**
- Mise sur les 3 premiers du Borda
- Choisir : Ordre / Désordre
- Saisir votre mise

**💾 Bouton "Sauvegarder ces paris"**
- Calcule le total des mises
- Sauvegarde tous les paris cochés dans la base de données

#### **📊 Onglet "Mes paris du jour"**

Affiche tous vos paris sauvegardés :
- ✅ Par course (R1C1, R1C2, etc.)
- ✅ Type de pari (Simple Gagnant, Couplé, etc.)
- ✅ Numéros joués
- ✅ Mise
- ✅ Statut (en attente ⏳ / gagnant ✅ / perdant ❌)

**Statistiques du jour :**
- 💰 Total misé
- 💵 Gains
- 📊 Bilan (avec %)

---

## 🔄 WORKFLOW COMPLET

### **MATIN - Avant les courses**

1. **Import du CSV**
   ```bash
   python3 universal_importer.py export_turfbzh_YYYYMMDD.csv
   ```

2. **Calcul Borda**
   - Menu **🎯 PRONOSTICS GLOBAUX**
   - Sélectionner la date
   - Cliquer **"🔄 Recalculer"**

3. **Sélection des paris**
   - Menu **💰 Interface de Paris**
   - Onglet **"Sélectionner mes paris"**
   - Pour chaque course :
     - Cocher les paris souhaités (SG, SP, Couplé, Trio)
     - Saisir les mises
     - Cliquer **"💾 Sauvegarder"**

4. **Vérifier vos paris**
   - Onglet **"Mes paris du jour"**
   - Vérifier le total des mises
   - Prendre note ou exporter

### **SOIR - Après les courses**

1. **Consulter vos paris**
   - Menu **💰 Interface de Paris**
   - Onglet **"Mes paris du jour"**

2. **(Futur)** Saisie des résultats
   - Actuellement manuel
   - Prochaine version : auto-update depuis CSV résultats

---

## 📊 STRUCTURE DE LA BASE DE DONNÉES

### **Nouvelle table : `paris`**

```sql
CREATE TABLE paris (
    id INTEGER PRIMARY KEY,
    course_id INTEGER,              -- Lien vers la course
    type_pari TEXT,                 -- 'Simple Gagnant', 'Couplé', etc.
    numeros TEXT,                   -- '4,7,10'
    mise REAL,                      -- Montant de la mise
    option TEXT,                    -- 'Gagnant', 'Placé', 'Ordre', etc.
    statut TEXT,                    -- 'en_attente', 'gagnant', 'perdant'
    resultat TEXT,                  -- Résultat réel de la course
    gain REAL,                      -- Gain éventuel
    created_at TIMESTAMP
)
```

---

## 💡 EXEMPLES D'UTILISATION

### **Exemple 1 : Jouer conservateur**

**Pour R1C1 Deauville :**
- ✅ Simple Gagnant : n°4 (2€)
- ✅ Simple Placé : n°4 (2€)
- Total : **4€**

### **Exemple 2 : Jouer agressif**

**Pour R1C1 Deauville :**
- ✅ Couplé Gagnant : 4-7 (5€)
- ✅ Trio Ordre : 4-7-10 (10€)
- Total : **15€**

### **Exemple 3 : Spread sur plusieurs courses**

**R1C1 :** Simple Gagnant 4 (2€)  
**R1C2 :** Simple Gagnant 3 (2€)  
**R1C3 :** Couplé Placé 5-8 (3€)  
**R1C4 :** Trio Désordre 2-6-9 (5€)  
**Total : 12€**

---

## ⚠️ LIMITES ACTUELLES

### **Ce qui fonctionne :**
- ✅ Sélection de paris
- ✅ Sauvegarde dans la DB
- ✅ Affichage des paris du jour
- ✅ Calcul du total des mises

### **Ce qui manque (prochaines versions) :**
- ❌ Calcul automatique des gains
- ❌ Mise à jour automatique des statuts
- ❌ Recommandations automatiques (BB/XXX, etc.)
- ❌ Configs Borda par hippodrome/discipline
- ❌ Export PDF des paris

---

## 🚀 PROCHAINES ÉTAPES

Pour compléter le système, il faudra ajouter :

### **3️⃣ RECOMMANDATIONS AUTOMATIQUES**
- Formules BB/XXX, BB/XXXX, BBB/XXXX
- Adaptation selon la confiance
- Calcul du nombre optimal de chevaux

### **4️⃣ CONFIGS BORDA AVANCÉES**
- Configs par hippodrome (Deauville-P, Vincennes-T, etc.)
- Configs par discipline (Plat, Trot, Obstacle)
- Pondérations personnalisées

### **5️⃣ IMPORT DES RÉSULTATS**
- Import CSV résultats
- Mise à jour automatique des statuts
- Calcul automatique des gains

### **6️⃣ ANALYSE AVANCÉE**
- ROI par type de pari
- ROI par hippodrome
- Statistiques de réussite

---

## 🎯 RÉSUMÉ

**Aujourd'hui, vous pouvez :**

1. ✅ Filtrer par réunion (R1, R2, R3...)
2. ✅ Sélectionner vos paris avec checkboxes
3. ✅ Sauvegarder vos paris dans la DB
4. ✅ Voir tous vos paris du jour
5. ✅ Calculer votre exposition totale

**C'est un excellent point de départ pour gérer vos paris quotidiens ! 🎉**

---

## 📞 SUPPORT

En cas de problème :

1. Vérifier que tous les fichiers sont bien téléchargés
2. Redémarrer Streamlit
3. Vérifier les erreurs dans le terminal
4. Vérifier que la table `paris` existe :
   ```bash
   python3 -c "from turf_database_complete import get_turf_database; db = get_turf_database(); db.cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\" AND name=\"paris\"'); print('Table paris:', 'OK' if db.cursor.fetchone()[0] == 1 else 'MANQUANTE')"
   ```

**Bon turf ! 🏇✨**
