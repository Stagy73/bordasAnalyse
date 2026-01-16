# 🐧 Installation Ubuntu - Dashboard Turf BZH

## ⚡ Installation Rapide (Méthode Recommandée)

### Option 1: Script Automatique (Le Plus Simple)

1. **Ouvrez un terminal dans le dossier où sont les fichiers**
   ```bash
   cd ~/bordasAnalyse
   ```

2. **Lancez le script**
   ```bash
   ./lancer_dashboard.sh
   ```
   
   Le script va automatiquement:
   - Créer un environnement virtuel Python
   - Installer toutes les dépendances
   - Lancer le dashboard

3. **C'est tout ! 🎉** Le dashboard s'ouvre dans votre navigateur

### Option 2: Installation Manuelle (Si le script ne marche pas)

1. **Installer les prérequis système**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```

2. **Créer un environnement virtuel**
   ```bash
   cd ~/bordasAnalyse
   python3 -m venv venv
   ```

3. **Activer l'environnement virtuel**
   ```bash
   source venv/bin/activate
   ```
   
   ⚠️ Votre terminal devrait maintenant afficher `(venv)` au début de la ligne

4. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

5. **Lancer l'application**
   ```bash
   streamlit run app_turf_dashboard.py
   ```

## 🔄 Utilisation Quotidienne

### Pour relancer l'application plus tard:

**Méthode 1 (Recommandée):**
```bash
cd ~/bordasAnalyse
./lancer_dashboard.sh
```

**Méthode 2 (Manuelle):**
```bash
cd ~/bordasAnalyse
source venv/bin/activate
streamlit run app_turf_dashboard.py
```

## 🛑 Arrêter l'Application

Dans le terminal où l'application tourne:
- Appuyez sur `Ctrl+C`

## 🆘 Résolution des Problèmes Ubuntu

### Erreur: "python3-venv not found"
```bash
sudo apt install python3-venv
```

### Erreur: "pip not found"
```bash
sudo apt install python3-pip
```

### Erreur: "Permission denied" sur le script
```bash
chmod +x lancer_dashboard.sh
```

### L'application ne s'ouvre pas dans le navigateur
Ouvrez manuellement: http://localhost:8501

### Erreur: "ModuleNotFoundError"
Assurez-vous d'avoir activé l'environnement virtuel:
```bash
source venv/bin/activate
```

## 💡 Créer un Raccourci Bureau Ubuntu

1. **Créez un fichier `turf-dashboard.desktop`**
   ```bash
   nano ~/Bureau/turf-dashboard.desktop
   ```

2. **Copiez ce contenu** (ajustez le chemin):
   ```ini
   [Desktop Entry]
   Version=1.0
   Type=Application
   Name=Dashboard Turf BZH
   Comment=Analyse des courses hippiques
   Exec=gnome-terminal -- bash -c "cd ~/bordasAnalyse && ./lancer_dashboard.sh; exec bash"
   Icon=applications-games
   Terminal=true
   Categories=Application;
   ```

3. **Rendez-le exécutable**
   ```bash
   chmod +x ~/Bureau/turf-dashboard.desktop
   ```

4. **Double-cliquez** sur l'icône pour lancer !

## 📱 Rendre le Script Exécutable Partout

Pour lancer depuis n'importe où:

```bash
echo 'alias turf="cd ~/bordasAnalyse && ./lancer_dashboard.sh"' >> ~/.bashrc
source ~/.bashrc
```

Maintenant tapez juste `turf` dans n'importe quel terminal !

## 🔧 Mettre à Jour les Dépendances

Si vous voulez mettre à jour Streamlit et les autres packages:

```bash
cd ~/bordasAnalyse
source venv/bin/activate
pip install --upgrade streamlit pandas plotly
```

## ❓ FAQ Ubuntu

**Q: Pourquoi créer un environnement virtuel?**
R: Ubuntu 22.04+ protège le Python système. Le venv isole vos packages.

**Q: Le venv prend-il beaucoup d'espace?**
R: Environ 200-300 MB. C'est normal et recommandé.

**Q: Puis-je supprimer le venv?**
R: Oui, supprimez le dossier `venv/`. Le script le recréera automatiquement.

**Q: L'application est-elle sécurisée?**
R: Oui, tout reste local sur votre machine Ubuntu.

**Q: Puis-je utiliser conda au lieu de venv?**
R: Oui, si vous préférez conda:
```bash
conda create -n turf python=3.10
conda activate turf
pip install -r requirements.txt
streamlit run app_turf_dashboard.py
```

## 🚀 Optimisation Ubuntu

### Pour de meilleures performances:

1. **Augmenter la mémoire cache de Streamlit**
   ```bash
   mkdir -p ~/.streamlit
   echo "[server]
maxUploadSize = 500
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false" > ~/.streamlit/config.toml
   ```

2. **Utiliser une version Python récente**
   ```bash
   python3 --version  # Devrait être 3.8 ou plus
   ```

---

**Bon analyse avec Ubuntu ! 🐧🏇**
