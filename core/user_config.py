from os import getcwd
import os.path
from json import load, dump
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
                             QGroupBox, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt

RESSOURCES_FOLDER = os.path.join(getcwd(), "ressources")
CONFIG_FILE = RESSOURCES_FOLDER + '/user_profile.json'

class UserConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Utilisateur")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("Profil Sportif")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # === Informations personnelles ===
        perso_group = QGroupBox("Informations personnelles")
        perso_layout = QVBoxLayout()
        
        # Âge
        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Âge :"))
        self.age_spinbox = QSpinBox()
        self.age_spinbox.setRange(10, 120)
        self.age_spinbox.setValue(30)
        self.age_spinbox.setSuffix(" ans")
        age_layout.addWidget(self.age_spinbox)
        age_layout.addStretch()
        perso_layout.addLayout(age_layout)
        
        # Poids
        poids_layout = QHBoxLayout()
        poids_layout.addWidget(QLabel("Poids :"))
        self.poids_spinbox = QDoubleSpinBox()
        self.poids_spinbox.setRange(30.0, 200.0)
        self.poids_spinbox.setValue(70.0)
        self.poids_spinbox.setSuffix(" kg")
        self.poids_spinbox.setDecimals(1)
        poids_layout.addWidget(self.poids_spinbox)
        poids_layout.addStretch()
        perso_layout.addLayout(poids_layout)
        
        # Taille
        taille_layout = QHBoxLayout()
        taille_layout.addWidget(QLabel("Taille :"))
        self.taille_spinbox = QSpinBox()
        self.taille_spinbox.setRange(100, 250)
        self.taille_spinbox.setValue(170)
        self.taille_spinbox.setSuffix(" cm")
        taille_layout.addWidget(self.taille_spinbox)
        taille_layout.addStretch()
        perso_layout.addLayout(taille_layout)
        
        # Sexe
        sexe_layout = QHBoxLayout()
        sexe_layout.addWidget(QLabel("Sexe :"))
        self.sexe_combo = QComboBox()
        self.sexe_combo.addItems(["Homme", "Femme"])
        sexe_layout.addWidget(self.sexe_combo)
        sexe_layout.addStretch()
        perso_layout.addLayout(sexe_layout)
        
        perso_group.setLayout(perso_layout)
        main_layout.addWidget(perso_group)
        
        # === Activités sportives ===
        sport_group = QGroupBox("Activités préférées")
        sport_layout = QVBoxLayout()
        
        # Type d'activité par défaut
        activite_layout = QHBoxLayout()
        activite_layout.addWidget(QLabel("Activité par défaut :"))
        self.activite_combo = QComboBox()
        self.activite_combo.addItems([
            "Marche", 
            "Course à pied", 
            "Vélo", 
            "VTT", 
            "Ski", 
            "Randonnée",
            "Natation"
        ])
        activite_layout.addWidget(self.activite_combo)
        activite_layout.addStretch()
        sport_layout.addLayout(activite_layout)
        
        # Checkbox auto-détection
        self.auto_detect_checkbox = QCheckBox("Auto-détection d'activité depuis le nom du fichier")
        self.auto_detect_checkbox.setChecked(True)
        self.auto_detect_checkbox.setToolTip(
            "Si activé, l'activité sera détectée automatiquement si le nom du fichier contient:\n"
            "MARCHE, COURSE, VELO, VTT, SKI, RANDONNEE, NATATION"
        )
        sport_layout.addWidget(self.auto_detect_checkbox)
        
        # Info sur l'auto-détection
        info_label = QLabel(
            "💡 <i>L'auto-détection cherche des mots-clés dans le nom du fichier GPX<br>"
            "(ex: \"sortie_COURSE_2024.gpx\" sera détecté comme Course à pied)</i>"
        )
        info_label.setStyleSheet("color: #666; padding: 5px; font-size: 11px;")
        info_label.setWordWrap(True)
        sport_layout.addWidget(info_label)
        
        # Niveau sportif
        niveau_layout = QHBoxLayout()
        niveau_layout.addWidget(QLabel("Niveau :"))
        self.niveau_combo = QComboBox()
        self.niveau_combo.addItems(["Débutant", "Intermédiaire", "Avancé", "Expert"])
        niveau_layout.addWidget(self.niveau_combo)
        niveau_layout.addStretch()
        sport_layout.addLayout(niveau_layout)
        
        # Fréquence cardiaque au repos
        fc_layout = QHBoxLayout()
        fc_layout.addWidget(QLabel("FC repos :"))
        self.fc_repos_spinbox = QSpinBox()
        self.fc_repos_spinbox.setRange(40, 100)
        self.fc_repos_spinbox.setValue(60)
        self.fc_repos_spinbox.setSuffix(" bpm")
        fc_layout.addWidget(self.fc_repos_spinbox)
        fc_layout.addStretch()
        sport_layout.addLayout(fc_layout)
        
        sport_group.setLayout(sport_layout)
        main_layout.addWidget(sport_group)
        
        # === Boutons ===
        buttons_layout = QHBoxLayout()
        
        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("💾 Enregistrer")
        btn_save.clicked.connect(self.save_config)
        btn_save.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        buttons_layout.addWidget(btn_save)
        
        main_layout.addLayout(buttons_layout)
        
        # Charger la configuration existante si elle existe
        self.load_config()
    
    def get_config_data(self):
        """Retourne les données de configuration sous forme de dictionnaire"""
        activite_map = {
            "Marche": "marche",
            "Course à pied": "course",
            "Vélo": "velo",
            "VTT": "vtt",
            "Ski": "ski",
            "Randonnée": "randonnee",
            "Natation": "natation"
        }
        
        return {
            "age": self.age_spinbox.value(),
            "poids": self.poids_spinbox.value(),
            "taille": self.taille_spinbox.value(),
            "sexe": self.sexe_combo.currentText(),
            "activite_defaut": activite_map[self.activite_combo.currentText()],
            "activite_defaut_display": self.activite_combo.currentText(),
            "auto_detect_activity": self.auto_detect_checkbox.isChecked(),
            "niveau": self.niveau_combo.currentText(),
            "fc_repos": self.fc_repos_spinbox.value()
        }
    
    def save_config(self):
        """Enregistre la configuration dans un fichier JSON"""
        try:
            config = self.get_config_data()
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                dump(config, f, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Succès", "Profil enregistré avec succès !")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")
    
    def load_config(self):
        """Charge la configuration depuis le fichier JSON"""
        if not os.path.exists(CONFIG_FILE):
            return
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = load(f)
            
            self.age_spinbox.setValue(config.get("age", 30))
            self.poids_spinbox.setValue(config.get("poids", 70.0))
            self.taille_spinbox.setValue(config.get("taille", 170))
            
            # Sexe
            sexe = config.get("sexe", "Homme")
            index = self.sexe_combo.findText(sexe)
            if index >= 0:
                self.sexe_combo.setCurrentIndex(index)
            
            # Activité
            activite = config.get("activite_defaut_display", "Marche")
            index = self.activite_combo.findText(activite)
            if index >= 0:
                self.activite_combo.setCurrentIndex(index)
            
            # Auto-détection
            self.auto_detect_checkbox.setChecked(config.get("auto_detect_activity", True))
            
            # Niveau
            niveau = config.get("niveau", "Intermédiaire")
            index = self.niveau_combo.findText(niveau)
            if index >= 0:
                self.niveau_combo.setCurrentIndex(index)
            
            self.fc_repos_spinbox.setValue(config.get("fc_repos", 60))
            
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")


def detect_activity_from_filename(filename):
    """
    Détecte l'activité sportive à partir du nom de fichier.
    Retourne le code d'activité (ex: 'course', 'velo') ou None si non détecté.
    """
    filename_upper = filename.upper()
    
    # Dictionnaire de mots-clés pour chaque activité
    keywords = {
        "marche": ["MARCHE", "WALK"],
        "course": ["COURSE", "RUN", "RUNNING", "FOOTING", "JOGGING"],
        "velo": ["VELO", "VÉLO", "BIKE", "CYCLING", "CYCLISME"],
        "vtt": ["VTT", "MTB", "MOUNTAIN"],
        "ski": ["SKI", "SKIING"],
        "randonnee": ["RANDONNEE", "RANDONNÉE", "RANDO", "HIKING", "HIKE", "TREK"],
        "natation": ["NATATION", "NAT", "SWIM", "SWIMMING", "PISCINE"]
    }
    
    # Chercher les mots-clés dans le nom de fichier
    for activity, words in keywords.items():
        for word in words:
            if word in filename_upper:
                return activity
    
    return None


def get_activity_display_name(activity_code):
    """
    Convertit le code d'activité en nom d'affichage.
    """
    display_map = {
        "marche": "Marche",
        "course": "Course à pied",
        "velo": "Vélo",
        "vtt": "VTT",
        "ski": "Ski",
        "randonnee": "Randonnée",
        "natation": "Natation"
    }
    return display_map.get(activity_code, activity_code)


def get_user_config(config_name="user_profile"):
    """Fonction utilitaire pour récupérer la configuration utilisateur"""
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return load(f)
    except:
        return None


def get_activity_for_trace(filename, user_config=None):
    """
    Détermine l'activité à utiliser pour une trace donnée.
    
    Args:
        filename: Nom du fichier GPX
        user_config: Configuration utilisateur (obtenue via get_user_config())
    
    Returns:
        tuple: (activity_code, activity_display_name, is_detected)
        - activity_code: code de l'activité (ex: 'course')
        - activity_display_name: nom d'affichage (ex: 'Course à pied')
        - is_detected: True si l'activité a été auto-détectée
    """
    if user_config is None:
        user_config = get_user_config()
    
    # Activité par défaut
    default_activity = user_config.get("activite_defaut", "marche") if user_config else "marche"
    default_display = user_config.get("activite_defaut_display", "Marche") if user_config else "Marche"
    
    # Vérifier si l'auto-détection est activée
    auto_detect = user_config.get("auto_detect_activity", True) if user_config else True
    
    if auto_detect:
        detected_activity = detect_activity_from_filename(filename)
        if detected_activity:
            return (detected_activity, get_activity_display_name(detected_activity), True)
    
    # Retourner l'activité par défaut
    return (default_activity, default_display, False)