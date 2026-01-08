import json
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QPushButton,
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import Qt

CONFIG_FILE = "user_profile.json"


class UserConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Utilisateur")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("⚙️ Profil Sportif")
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
        self.activite_combo.addItems(["🚶 Marche", "🏃 Course à pied", "🚴 Vélo", "🚵 VTT", "⛷️ Ski", "🥾 Randonnée"])
        activite_layout.addWidget(self.activite_combo)
        activite_layout.addStretch()
        sport_layout.addLayout(activite_layout)
        
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
            "🚶 Marche": "marche",
            "🏃 Course à pied": "course",
            "🚴 Vélo": "velo",
            "🚵 VTT": "vtt",
            "⛷️ Ski": "ski",
            "🥾 Randonnée": "randonnee"
        }
        
        return {
            "age": self.age_spinbox.value(),
            "poids": self.poids_spinbox.value(),
            "taille": self.taille_spinbox.value(),
            "sexe": self.sexe_combo.currentText(),
            "activite_defaut": activite_map[self.activite_combo.currentText()],
            "activite_defaut_display": self.activite_combo.currentText(),
            "niveau": self.niveau_combo.currentText(),
            "fc_repos": self.fc_repos_spinbox.value()
        }
    
    def save_config(self):
        """Enregistre la configuration dans un fichier JSON"""
        try:
            config = self.get_config_data()
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
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
                config = json.load(f)
            
            self.age_spinbox.setValue(config.get("age", 30))
            self.poids_spinbox.setValue(config.get("poids", 70.0))
            self.taille_spinbox.setValue(config.get("taille", 170))
            
            # Sexe
            sexe = config.get("sexe", "Homme")
            index = self.sexe_combo.findText(sexe)
            if index >= 0:
                self.sexe_combo.setCurrentIndex(index)
            
            # Activité
            activite = config.get("activite_defaut_display", "🚶 Marche")
            index = self.activite_combo.findText(activite)
            if index >= 0:
                self.activite_combo.setCurrentIndex(index)
            
            # Niveau
            niveau = config.get("niveau", "Intermédiaire")
            index = self.niveau_combo.findText(niveau)
            if index >= 0:
                self.niveau_combo.setCurrentIndex(index)
            
            self.fc_repos_spinbox.setValue(config.get("fc_repos", 60))
            
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration : {e}")


def get_user_config():
    """Fonction utilitaire pour récupérer la configuration utilisateur"""
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

