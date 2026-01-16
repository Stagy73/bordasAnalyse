# 🎯 GUIDE WORKFLOW QUOTIDIEN - RÉPONSES À VOS QUESTIONS

## ❓ VOS 3 QUESTIONS :

1. **Comment mettre à jour avec mon fichier tous les jours ?**
2. **Où sont passés les Jockey et Cheval dans le menu ?**
3. **Comment choisir un pari et le sauvegarder pour faire des tests ?**

---

# ✅ RÉPONSE 1 : IMPORT QUOTIDIEN

## 🚀 **MÉTHODE 1 : IMPORT AUTOMATIQUE (RECOMMANDÉ)**

### **Script d'import rapide : `import_today.py`**

```bash
cd ~/bordasAnalyse

# 1. Téléchargez votre export TurfBZH du jour
# 2. Nommez-le : export_turfbzh_YYYYMMDD.csv
#    Exemple : export_turfbzh_20260116.csv

# 3. Lancez l'import
python3 import_today.py
```

**Le script :**
- ✅ Trouve automatiquement le fichier du jour
- ✅ Importe les courses et partants
- ✅ Affiche les statistiques
- ✅ Vous dit quoi faire ensuite

**Sortie attendue :**
```
============================================================
✅ IMPORT RÉUSSI !
============================================================
📊 Courses importées: 55
🐴 Partants importés: 633
🐎 Chevaux ajoutés: 633

📊 ÉTAT DE LA BASE DE DONNÉES:
   Total courses: 190
   Total partants: 3,061

🎯 PROCHAINE ÉTAPE:
   Lancez le dashboard: streamlit run app_turf_dashboard.py
```

---

## 🖥️ **MÉTHODE 2 : IMPORT PAR INTERFACE (NOUVEAU)**

### **Directement dans le Dashboard !**

```bash
streamlit run app_turf_dashboard.py
```

1. Allez dans **📊 Vue d'ensemble**
2. En haut de la page : **📥 Importer un nouveau fichier CSV**
3. Cliquez **Browse files** ou glissez-déposez votre CSV
4. Cliquez **⬆️ Importer**
5. ✅ Import en direct + page se rafraîchit !

---

## 📋 **WORKFLOW QUOTIDIEN COMPLET**

### **MATIN (avant les courses) :**

```bash
cd ~/bordasAnalyse

# 1. Import du fichier du jour
python3 import_today.py

# 2. Lancer le dashboard
streamlit run app_turf_dashboard.py
```

**Dans le dashboard :**
1. Menu **🎯 PRONOSTICS GLOBAUX**
2. Sélectionner la **date du jour**
3. Cliquer **"🔄 Recalculer les scores Borda"** (attend 10-30 sec)
4. ✅ Tous les pronostics sont calculés !

5. Menu **💰 Interface de Paris**
6. Onglet **"📝 Sélectionner mes paris"**
7. Pour chaque course qui vous intéresse :
   - Cocher les paris souhaités ✅
   - Saisir les mises
   - Cliquer **"💾 Sauvegarder ces paris"**

8. Onglet **"📊 Mes paris du jour"**
9. Vérifier le total des mises
10. Prendre note ou faire une capture d'écran

### **SOIR (après les courses) :**

1. Menu **💰 Interface de Paris**
2. Onglet **"📊 Mes paris du jour"**
3. Consulter vos paris
4. (Futur) Import résultats pour mise à jour auto

---

# ✅ RÉPONSE 2 : MENU JOCKEY & CHEVAL

## 🎯 **ILS SONT DE RETOUR !**

Le nouveau dashboard a **6 sections** :

1. **📊 Vue d'ensemble**
   - Statistiques DB
   - Import de fichiers (NOUVEAU)
   - Courses récentes

2. **🎯 PRONOSTICS GLOBAUX**
   - Filtrage par date et réunion
   - Calcul des scores Borda
   - Affichage des pronostics

3. **💰 Interface de Paris**
   - Sélection des paris
   - Sauvegarde dans la DB
   - Suivi du jour

4. **🐴 Analyse Chevaux** (NOUVEAU)
   - Recherche par nom
   - Statistiques détaillées (ELO, nb courses, victoires)
   - Top 20 chevaux par ELO

5. **👨‍🏫 Analyse Drivers** (NOUVEAU)
   - Recherche par nom
   - Statistiques détaillées (ELO, taux de victoire)
   - Top 20 drivers par ELO

6. **⚙️ Config Borda**
   - Configurations existantes
   - Critères par défaut
   - (Futur) Créer des configs personnalisées

---

## 📊 **EXEMPLE : CHERCHER UN CHEVAL**

1. Menu **🐴 Analyse Chevaux**
2. Taper "DADDY JOY" dans la recherche
3. Voir :
   - Âge, Sexe, ELO
   - Nombre de courses
   - Nombre de victoires
   - Nombre de places
   - Cote moyenne

---

# ✅ RÉPONSE 3 : SAUVEGARDER VOS PARIS

## 💰 **LA FONCTIONNALITÉ EXISTE DÉJÀ !**

### **Menu : 💰 Interface de Paris**

#### **Onglet 1 : 📝 Sélectionner mes paris**

Pour **chaque course**, vous voyez :
- Le **TOP 5 Borda**
- **4 colonnes de paris** (Simple Gagnant, Simple Placé, Couplé, Trio)

**Exemple pour R1C1 Deauville :**

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ 🎯 Simple G.    │ 📍 Simple P.    │ 👥 Couplé       │ 🎲 Trio         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ ☑ Checkbox      │ ☐ Checkbox      │ ☑ Checkbox      │ ☐ Checkbox      │
│ Mise: 2.00€     │                 │ Mise: 3.00€     │                 │
│ N°4 - Cote: 5.2 │                 │ Type: Gagnant   │                 │
│                 │                 │ N°4-7           │                 │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘

💰 Total des mises : 5.00 €

                    [ 💾 Sauvegarder ces paris ]
```

**IMPORTANT : Vous devez :**
1. ✅ **COCHER** les checkboxes des paris que vous voulez
2. ✅ Saisir vos **mises**
3. ✅ Cliquer **"💾 Sauvegarder ces paris"**

**→ Les paris sont sauvegardés dans la table `paris` de la DB !**

---

#### **Onglet 2 : 📊 Mes paris du jour**

Affiche **TOUS vos paris sauvegardés** :

```
💰 Vos Paris du Jour

🏇 R1C1 - Deauville (16:03)
  Simple Gagnant    N°4        2.00€    ⏳
  Couplé Gagnant    N°4-7      3.00€    ⏳

🏇 R1C2 - Deauville (16:38)
  Trio Ordre        N°3-5-8    5.00€    ⏳

────────────────────────────────────────
💰 Total misé:  10.00 €
💵 Gains:        0.00 €
📊 Bilan:        0.00 € (0.0%)
```

**Statuts possibles :**
- ⏳ = En attente (avant la course)
- ✅ = Gagnant (après la course)
- ❌ = Perdant (après la course)

---

## 🧪 **FAIRE DES TESTS DE PARIS**

Vous pouvez :

### **Test 1 : Parier conservateur**
```
R1C1 : ✅ Simple Gagnant N°4 (2€)
R1C1 : ✅ Simple Placé N°4 (2€)
Total : 4€
```

### **Test 2 : Parier agressif**
```
R1C1 : ✅ Couplé Gagnant 4-7 (5€)
R1C1 : ✅ Trio Ordre 4-7-10 (10€)
Total : 15€
```

### **Test 3 : Spread sur plusieurs courses**
```
R1C1 : ✅ Simple Gagnant 4 (2€)
R1C2 : ✅ Simple Gagnant 3 (2€)
R1C3 : ✅ Couplé Placé 5-8 (3€)
R1C4 : ✅ Trio Désordre 2-6-9 (5€)
Total : 12€
```

**Tous vos tests sont sauvegardés et consultables dans "Mes paris du jour" !**

---

# 📥 FICHIERS À TÉLÉCHARGER

## **Nouveaux fichiers :**

1. **app_turf_dashboard_db_simple.py** → Remplacer `app_turf_dashboard.py`
   - ✅ Menu Jockey/Cheval ajouté
   - ✅ Import CSV dans l'interface
   - ✅ Pas d'erreur `has_borda`

2. **import_today.py** (NOUVEAU)
   - Script d'import quotidien rapide
   - Cherche automatiquement le fichier du jour

---

# 🚀 INSTALLATION RAPIDE

```bash
cd ~/bordasAnalyse

# 1. Télécharger les fichiers depuis outputs

# 2. Remplacer l'ancien dashboard
mv app_turf_dashboard.py app_turf_dashboard_OLD.py
mv app_turf_dashboard_db_simple.py app_turf_dashboard.py

# 3. Rendre import_today.py exécutable
chmod +x import_today.py

# 4. Tester l'import
python3 import_today.py

# 5. Lancer le dashboard
streamlit run app_turf_dashboard.py
```

---

# 📊 RÉSUMÉ : VOS 3 RÉPONSES

## 1️⃣ **Import quotidien :**
- ✅ Script `import_today.py` trouve le fichier automatiquement
- ✅ Bouton import dans "📊 Vue d'ensemble"

## 2️⃣ **Menu Jockey/Cheval :**
- ✅ Section **🐴 Analyse Chevaux** ajoutée
- ✅ Section **👨‍🏫 Analyse Drivers** ajoutée
- ✅ Recherche + Top 20 par ELO

## 3️⃣ **Sauvegarder les paris :**
- ✅ Menu **💰 Interface de Paris** existe déjà
- ✅ Cochez les checkboxes
- ✅ Cliquez "💾 Sauvegarder"
- ✅ Consultez dans "Mes paris du jour"

---

# 🎯 WORKFLOW RÉSUMÉ EN 5 MINUTES

```bash
# MATIN
cd ~/bordasAnalyse
python3 import_today.py                    # 1. Import CSV
streamlit run app_turf_dashboard.py        # 2. Dashboard

# Dans le dashboard:
# 3. PRONOSTICS GLOBAUX → Recalculer Borda
# 4. Interface de Paris → Cocher vos paris → Sauvegarder
# 5. Mes paris du jour → Vérifier le total

# SOIR
# 6. Mes paris du jour → Consulter les résultats
```

**Vous avez maintenant TOUT pour parier et tester quotidiennement ! 🎉**

---

# ❓ QUESTIONS FRÉQUENTES

**Q : Dois-je supprimer l'ancienne DB avant d'importer ?**
R : NON ! Le système ajoute les nouvelles courses automatiquement.

**Q : Si j'importe 2 fois le même fichier ?**
R : Pas de doublon grâce à `UNIQUE(course_code, reunion_id)`.

**Q : Comment voir mes anciens paris ?**
R : Actuellement, seuls les paris du jour sont affichés. Prochaine version : historique complet.

**Q : Les gains sont calculés automatiquement ?**
R : Pas encore. Il faut importer les résultats (prochaine version).

---

**BON TURF ! 🏇✨**
