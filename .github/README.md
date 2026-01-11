# 🧙 Gandalf - GPX Viewer
> **Un visualiseur GPX multi-traces pour analyser vos données sportives**

Gandalf affiche toutes vos données de santé et de performance : calories, dénivelé, distance, temps, BPM... sur une carte satellite interactive. Importez plusieurs fichiers GPX simultanément et comparez vos parcours !

---

## ✨ Fonctionnalités

### 📊 Analyse Multi-traces
- **Import multi-fichiers** : Chargez plusieurs fichiers GPX en une fois
- **Vue globale** : Statistiques cumulées de toutes vos traces
- **Vue individuelle** : Sélectionnez une trace pour voir ses détails
- **Gestion des traces** : Affichez/masquez, supprimez ou effacez toutes les traces
- **Codage couleur** : Chaque trace possède sa propre couleur pour une identification facile

### 🗺️ Carte Interactive
- **Carte satellite** haute résolution (Esri World Imagery)
- **Contrôles de zoom** : Zoom manuel ou ajustement automatique aux traces
- **Centrage automatique** : Vue globale ou centrée sur une trace spécifique
- **Polylines colorées** : Visualisation claire de vos parcours

### 🏃 Détection d'Activité Intelligente
- **Auto-détection** depuis le nom du fichier (Course, Vélo, VTT, Ski, Randonnée, Natation, Marche)
- **Personnalisation** : Définissez une activité par défaut
- **Activités supportées** : Marche, Course à pied, Vélo, VTT, Ski, Randonnée, Natation
- **Icônes visuelles** : 🔍 pour auto-détection, ⚙️ pour activité par défaut

### 💪 Métriques de Santé
- **Calories brûlées** : Calcul précis basé sur le MET (Metabolic Equivalent of Task)
- **Fréquence cardiaque** : FC moyenne et maximale estimées
- **Intensité** : Pourcentage d'effort par rapport à votre FC max
- **Vitesse moyenne** et allure (min/km)
- **Profil personnalisé** : Âge, poids, taille, sexe, niveau sportif

### ⛰️ Données de Parcours
- **Distance** totale en kilomètres
- **Dénivelé positif** (D+) et **négatif** (D-) en mètres
- **Durée** du parcours (heures, minutes, secondes)
- **Estimation automatique** de la durée si absente du fichier GPX
- **Nombre de points GPS** enregistrés

### 🌍 Impact Environnemental
- **CO2 économisé** vs voiture, bus, train
- **Équivalent arbres** : Nombre de jours d'absorption de CO2 par un arbre
- **Affichage dans les exports** JSON et CSV

### 📤 Export de Données
- **Format JSON** : Export structuré avec toutes les métriques
- **Format CSV** : Compatible Excel pour analyses avancées
- **Export sélectif** : Trace unique ou toutes les traces
- **Données incluses** : Stats de santé, impact environnemental, profil utilisateur

---

## 🚀 Installation

### Prérequis
- **Python 3.13+** (testé sur 3.15.5)
- Système d'exploitation : Windows, Linux, macOS

### 1️⃣ Créer un environnement virtuel

**Linux / macOS :**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

> 💡 Plus d'infos sur les environnements virtuels Windows : [W3Schools Guide](https://www.w3schools.com/python/python_virtualenv.asp)

### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

**Dépendances principales :**
- PyQt5 : Interface graphique
- pyqtlet2 : Carte interactive
- gpxpy : Parsing des fichiers GPX

### 3️⃣ Lancer l'application
```bash
python main.py
```
ou
```bash
python3 main.py
```

---

## 📖 Guide d'Utilisation

### Premier Lancement
1. **Configurez votre profil** : Cliquez sur "Setup" pour entrer vos informations (âge, poids, activité préférée...)
2. **Importez vos fichiers GPX** : Cliquez sur "Importer GPX" et sélectionnez un ou plusieurs fichiers
3. **Explorez vos données** : Sélectionnez une trace dans la liste pour voir ses détails

### Astuces
- **Nommez vos fichiers** : Incluez le type d'activité dans le nom (ex: `sortie_COURSE_2024.gpx`) pour une détection automatique
- **Vue globale** : Cliquez sur "Vue globale" pour voir les statistiques cumulées de toutes vos traces
- **Gestion des traces** : Utilisez les checkboxes pour afficher/masquer des traces sans les supprimer
- **Export de données** : Exportez vos statistiques en JSON ou CSV pour les analyser dans d'autres outils

### Mots-clés de Détection d'Activité
- **Course** : COURSE, RUN, RUNNING, FOOTING, JOGGING
- **Vélo** : VELO, VÉLO, BIKE, CYCLING, CYCLISME
- **VTT** : VTT, MTB, MOUNTAIN
- **Ski** : SKI, SKIING
- **Randonnée** : RANDONNEE, RANDONNÉE, RANDO, HIKING, HIKE, TREK
- **Natation** : NATATION, NAT, SWIM, SWIMMING, PISCINE
- **Marche** : MARCHE, WALK

---

## 📦 Release

### ✅ Version v0.1-alpha - Disponible !

La première version alpha de Gandalf est maintenant disponible ! 

**Téléchargements :**
- 🪟 **Windows** : `Gandalf-v0.1-alpha-windows.exe` (à venir)
- 🐧 **Linux** : `Gandalf-v0.1-alpha-linux.AppImage` (à venir)
- 📦 **Source** : Clonez le repository et suivez les instructions d'installation

**Nouveautés v0.1-alpha :**
- ✨ Import multi-fichiers GPX
- 🗺️ Carte satellite interactive
- 🔍 Détection automatique d'activité
- 💪 Calculs de métriques de santé (calories, FC, intensité)
- 🌍 Impact environnemental (CO2 économisé)
- 📤 Export JSON/CSV avec toutes les données
- 🎨 Interface moderne avec gestion des couleurs
- 📊 Vue globale et vue par trace
- ⚙️ Configuration du profil utilisateur

**Note :** Il s'agit d'une version alpha. Des bugs peuvent survenir. Vos retours sont précieux !

---

## 🐛 Bugs Connus & Limitations

- ⏱️ **Estimation de durée** : Pour les fichiers GPX sans timestamps, la durée est estimée selon votre niveau et l'activité
- 🗺️ **Performance** : L'affichage de très nombreux points GPS (>10000) peut ralentir la carte
- 💾 **Sauvegarde du profil** : Les modifications du profil ne sont appliquées qu'après redémarrage de l'application

---

## 💡 Demande de Fonctionnalités

Pour toute demande de feature ou signalement de bug :
- 🐛 Ouvrez une [issue](../../issues) sur GitHub
- 📧 Envoyez un email à : **perso@archibarbu.art**

**Fonctionnalités prévues :**
- 📈 Graphiques d'élévation interactifs
- 🏆 Système de challenges et objectifs
- 📱 Version mobile
- 🔄 Synchronisation cloud
- 🎯 Comparaison de performances entre traces similaires
- 🗓️ Calendrier d'activités

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

**Comment contribuer :**
1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

**Code de conduite :** Soyez respectueux et constructif dans vos échanges.

---

## 🏗️ Architecture du Projet

```
gandalf-gpx-viewer/
├── main.py                 # Point d'entrée de l'application
├── ui/
│   └── map_window.py      # Interface principale avec carte
├── core/
│   ├── gpx.py            # Parsing des fichiers GPX
│   └── user_config.py    # Gestion du profil utilisateur
├── utils/
│   ├── calculator.py     # Calculs de métriques (calories, FC, MET)
│   ├── co2_calculator.py # Calcul d'impact environnemental
│   ├── info_display.py   # Génération du HTML pour l'affichage
│   └── export_data.py    # Export JSON/CSV
└── ressources/
│   ├── temp_files/
│   ├── test_files/
│   ├── gandalf.ico
|   └── user_profile.json # Configuration utilisateur (généré)
```

---

## 📚 Technologies Utilisées

- **PyQt5** : Framework d'interface graphique
- **pyqtlet2** : Intégration de cartes Leaflet dans PyQt
- **gpxpy** : Bibliothèque de parsing GPX
- **Esri World Imagery** : Tuiles satellite haute résolution

---

## 📝 License

**Apache License 2.0**

Copyright 2025 ArchiBarbu

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## 🙏 Remerciements

- **Communauté OpenStreetMap** pour les données cartographiques
- **Esri** pour les tuiles satellite

---

## 📞 Contact

**Développeur :** ArchiBarbu  
**Email :** perso[aroba]archibarbu[dot]art  
**GitHub :** [gandalf-gpx-viewer](https://github.com/archibarbu/gandalf-gpx-viewer)

---

<p align="center">
  Made with ❤️ for outdoor enthusiasts
</p>