# 🚀 Life OS - Tableau de Bord Personnel Évolué

**Life OS** est une application web d'auto-hébergement (Self-Hosted) conçue pour centraliser, organiser et automatiser la gestion du quotidien. Développée en Python avec Streamlit, elle combine la légèreté de fichiers Excel et la puissance d'un moteur relationnel SQL pour offrir un suivi fluide et temps réel.

![Status](https://img.shields.io/badge/Status-Stable-green)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Docker](https://img.shields.io/badge/Docker-Compatible-cyan)

---

## 🤖 Développement et Intelligence Artificielle

Ce projet est le fruit d'une méthodologie de développement moderne mêlant compétences humaines et **Intelligence Artificielle (IA)**. L'IA a été activement impliquée dans :
* **L'Architecture Logicielle :** Structuration de l'application en modules indépendants rattachés à un routeur principal (`app.py`).
* **Le Moteur de Données :** Conception du système hybride Excel / SQLite pour les calculs de flux financiers et la gestion comptable.
* **L'Infrastructure :** Rédaction et optimisation du fichier de conteneurisation `Dockerfile` pour un déploiement stable sans dépendances conflictuelles.
* **L'Automatisation :** Scripting de la communication avec l'API Google Drive pour la création de jetons OAuth2 et l'export des sauvegardes.

---

## ✨ Modules de l'Application

* **🎛️ Dashboard Central** : Vue d'ensemble personnalisable avec thèmes visuels (Cyberpunk/Minimalist), météo locale synchronisée par API, suivi d'habitudes quotidiennes, et rappels de tâches rapides.
* **💰 Gestion Comptable & Patrimoine (Moteur SQL)** : Suivi dynamique des revenus et dépenses, graphiques d'analyse des flux mensuels, gestion des virements de compte à compte et suivi de l'évolution de l'épargne ou du remboursement des dettes.
* **💳 Mes Comptes** : Calcul automatisé en temps réel du solde réel de chaque compte financier (Courant, Épargne, Espèces) basé sur l'historique SQL.
* **🔄 Hub Abonnements** : Traqueur de charges fixes (Streaming, Loyer, Forfaits) calculant l'impact financier mensuel/annuel et générant des alertes pour les prélèvements planifiés dans les 7 prochains jours.
* **📝 Notes & Post-its** : Un mur virtuel interactif permettant de rédiger, colorer et épingler des mémos directement sur le tableau de bord principal.
* **🚗 Suivi Voiture & Tâches** : Modules dédiés au suivi kilométrique du véhicule et à la gestion des projets personnels.

---

## 🛠️ Architecture Technique

* **Framework :** Streamlit (Interface utilisateur web réactive)
* **Base de données :** SQLite (Moteur financier) & Pandas / Openpyxl (Stockage des modules secondaires)
* **Sauvegarde :** Intégration automatisée avec Google Drive API via protocoles OAuth2
* **Conteneurisation :** Docker (Image basée sur `python:3.9-slim`)

---

## 📦 Installation & Déploiement

### Option 1 : Déploiement local classique

1. Cloner le projet sur votre espace :
   ```bash
   git clone https://github.com/C-Lucas-Pro/Life-os.git
   cd Life-os
   ```
2. Installer les dépendances :

  ```Bash
  pip install -r requirements.txt
  ```
3. Lancer l'application :

  ```Bash
  streamlit run app.py
  ```
Option 2 : Déploiement via Docker
Générez et lancez le conteneur en une seule commande :

```Bash
docker build -t life-os .
docker run -p 8501:8501 life-os
```

📄 Licence
Ce projet est disponible sous les termes de la licence MIT. Vous êtes entièrement libre de copier, modifier, distribuer et intégrer ce code, y compris dans des projets commerciaux, à l'unique condition d'inclure la mention de copyright originale et de citer l'auteur (C-Lucas-Pro).

Pour consulter l'intégralité du texte légal, veuillez vous référer au fichier `LICENSE` présent à la racine de ce dépôt.
