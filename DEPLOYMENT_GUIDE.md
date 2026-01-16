# 🚀 GUIDE DE DÉPLOIEMENT - Streamlit Cloud + SQLite

## ✅ **ARCHITECTURE CHOISIE**

- **Frontend :** Streamlit Cloud (gratuit)
- **Base de données :** SQLite locale
- **Stockage :** Volume persistant Streamlit
- **Déploiement :** Git push automatique

---

## 📦 **PRÉPARATION DU DÉPÔT GITHUB**

### **1. Structure des fichiers**

```
votre-repo/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.template
├── turf_database_complete.py
├── streamlit_db_adapter.py
├── app_turf_dashboard.py
├── global_predictions.py
├── betting_system_v2.py
├── betting_interface.py
├── favorites_system.py
├── borda_configuration_interface.py
├── foreign_races_system.py
├── migrate_csv_to_db.py
├── create_sql_views.py
├── requirements.txt
├── .gitignore
└── README.md
```

### **2. Créer .gitignore**

```gitignore
# Base de données locale
*.db
*.db-journal
*.db-wal
turf_complete.db
betting_data.db

# Données temporaires
bordasAnalyse/
uploads/
__pycache__/
*.pyc
.DS_Store

# Secrets locaux
.streamlit/secrets.toml

# Environnement virtuel
venv/
env/
.venv/
```

### **3. Commiter et pusher**

```bash
cd ~/bordasAnalyse

# Initialiser Git (si pas déjà fait)
git init

# Ajouter remote
git remote add origin https://github.com/VOTRE-USERNAME/turf-bzh.git

# Ajouter les fichiers
git add .
git commit -m "🗄️ Système complet avec base de données SQLite"

# Pusher
git push -u origin main
```

---

## 🌐 **DÉPLOIEMENT SUR STREAMLIT CLOUD**

### **1. Se connecter à Streamlit Cloud**

1. Allez sur : https://share.streamlit.io/
2. Connectez-vous avec GitHub
3. Cliquez sur **"New app"**

### **2. Configuration de l'app**

```
Repository : votre-username/turf-bzh
Branch : main
Main file path : app_turf_dashboard.py
App URL (custom) : turf-bzh-dashboard (optionnel)
```

### **3. Secrets (optionnel)**

Dans les paramètres de l'app, section "Secrets" :

```toml
[database]
path = "/mount/data/turf_complete.db"

[general]
debug = false
auto_import = true
```

### **4. Déployer**

Cliquez sur **"Deploy!"** → L'app démarre automatiquement !

---

## 📊 **UTILISATION APRÈS DÉPLOIEMENT**

### **Premier lancement :**

1. ✅ L'app démarre avec une DB vide
2. 📥 Utilisez le bouton "Importer un export CSV"
3. ✅ Les données sont importées dans la DB
4. 🗄️ La DB persiste entre les redémarrages

### **Imports suivants :**

- Chaque nouveau CSV est ajouté à la DB
- Pas de doublons grâce aux clés uniques
- Historique complet conservé

---

## 🔄 **MISE À JOUR DU CODE**

### **Workflow simple :**

```bash
# Modifier votre code localement
git add .
git commit -m "✨ Nouvelle fonctionnalité"
git push

# Streamlit Cloud redéploie automatiquement ! 🚀
```

---

## 💾 **BACKUP DE LA BASE DE DONNÉES**

### **Option 1 : Depuis l'interface**

Ajoutez un bouton de backup dans votre app :

```python
import streamlit as st

if st.sidebar.button("💾 Télécharger DB"):
    with open("turf_complete.db", "rb") as f:
        st.sidebar.download_button(
            "📥 Sauvegarder la base",
            f,
            file_name=f"turf_backup_{datetime.now().strftime('%Y%m%d')}.db",
            mime="application/octet-stream"
        )
```

### **Option 2 : Export CSV automatique**

```python
if st.sidebar.button("📤 Export CSV"):
    df = pd.read_sql_query("SELECT * FROM partants", db.conn)
    csv = df.to_csv(index=False, sep=';')
    st.sidebar.download_button(
        "📥 Télécharger CSV",
        csv,
        file_name=f"export_complet_{datetime.now().strftime('%Y%m%d')}.csv"
    )
```

---

## 🔍 **DEBUGGING**

### **Logs Streamlit Cloud :**

1. Allez dans votre app sur Streamlit Cloud
2. Menu ⋮ → **"Manage app"**
3. Onglet **"Logs"** → Voir les erreurs en temps réel

### **Tester localement avant déploiement :**

```bash
# Activer l'environnement virtuel
cd ~/bordasAnalyse
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'app
streamlit run app_turf_dashboard.py

# Tester sur http://localhost:8501
```

---

## 📈 **LIMITES STREAMLIT CLOUD (Gratuit)**

| Ressource | Limite | Impact |
|-----------|--------|--------|
| RAM | 1 GB | ✅ Suffisant pour SQLite |
| CPU | Partagé | ✅ OK pour usage personnel |
| Storage | 1 GB | ✅ ~2 ans de courses |
| Bandwidth | Illimité | ✅ Pas de souci |
| Apps | 3 apps | ✅ Largement suffisant |

---

## 🚀 **OPTIMISATIONS POUR PRODUCTION**

### **1. Vacuum régulier de la DB**

Ajoutez dans votre code :

```python
# Une fois par semaine
if datetime.now().weekday() == 0:  # Lundi
    db.cursor.execute("VACUUM")
    db.conn.commit()
```

### **2. Index automatiques**

Au démarrage de l'app :

```python
from create_sql_views import create_performance_indexes

@st.cache_resource
def setup_database():
    db = get_turf_database()
    create_performance_indexes(db)
    return db
```

### **3. Cache des requêtes lentes**

```python
@st.cache_data(ttl=3600)  # Cache 1 heure
def get_statistics():
    return db.get_global_stats()
```

---

## ✅ **CHECKLIST FINALE**

Avant de déployer :

- [ ] `.gitignore` créé (exclure *.db)
- [ ] `requirements.txt` à jour
- [ ] Code testé localement
- [ ] README.md écrit
- [ ] Code pushé sur GitHub
- [ ] App créée sur Streamlit Cloud
- [ ] Premier CSV importé avec succès
- [ ] Backup testé

---

## 🎯 **RÉSULTAT FINAL**

Votre app sera accessible à :
```
https://VOTRE-APP-NAME.streamlit.app
```

**Caractéristiques :**
- ✅ Déploiement automatique sur Git push
- ✅ Base de données persistante
- ✅ Backup simple (download button)
- ✅ 100% gratuit
- ✅ Zéro maintenance serveur
- ✅ HTTPS automatique
- ✅ URL personnalisée

---

## 🆘 **SUPPORT**

En cas de problème :

1. Vérifier les logs Streamlit Cloud
2. Tester localement d'abord
3. Vérifier les requirements.txt
4. S'assurer que .gitignore exclut *.db
5. Vérifier la structure des fichiers

**Votre système est maintenant 100% cloud-ready ! 🚀☁️**
