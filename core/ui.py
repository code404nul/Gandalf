import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QSpinBox, QLabel, QFileDialog)
from PyQt5.QtCore import Qt
from pyqtlet2 import L, MapWidget

from core.gpx import get_info
from core.user_config import UserConfigDialog, get_user_config
from utils.calculator import calculate_calories, calculate_fitness_metrics
from utils.info_display import *

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trace GPS avec PyQtlet - Interactive")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Layout pour les contrôles
        controls_layout = QHBoxLayout()
        
        # Bouton Setup (en premier, à gauche)
        btn_setup = QPushButton("Setup")
        btn_setup.clicked.connect(self.open_setup)
        btn_setup.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        controls_layout.addWidget(btn_setup)
        
        # Contrôle de zoom
        zoom_label = QLabel("Zoom:")
        controls_layout.addWidget(zoom_label)
        
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setMinimum(1)
        self.zoom_spinbox.setMaximum(18)
        self.zoom_spinbox.setValue(6)
        self.zoom_spinbox.valueChanged.connect(self.change_zoom)
        controls_layout.addWidget(self.zoom_spinbox)
        
        # Bouton importer GPX
        btn_import_gpx = QPushButton("Importer un GPX")
        btn_import_gpx.clicked.connect(self.import_gpx)
        controls_layout.addWidget(btn_import_gpx)
        
        # Bouton centrer sur trace
        btn_fit = QPushButton("Centrer sur trace")
        btn_fit.clicked.connect(self.fit_bounds)
        controls_layout.addWidget(btn_fit)
        
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Création du MapWidget
        self.map_widget = MapWidget()
        main_layout.addWidget(self.map_widget, stretch=3)
        
        # Zone d'informations modifiable - Layout horizontal pour plusieurs cartes
        self.info_widget = QWidget()
        self.info_layout = QHBoxLayout(self.info_widget)
        self.info_layout.setSpacing(10)
        
        # Carte principale - Trace GPS
        self.trace_card = QLabel("Importez un fichier GPX pour commencer")
        self.trace_card.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.trace_card.setStyleSheet(TRACE_CARD_STYLE)
        self.info_layout.addWidget(self.trace_card, stretch=1)
        
        # Carte Fitness
        self.fitness_card = QLabel("Configurez votre profil\npour voir les stats")
        self.fitness_card.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)
        self.info_layout.addWidget(self.fitness_card, stretch=1)
        
        main_layout.addWidget(self.info_widget)
        
        # Points vides au départ
        self.points = []
        self.coords = []
        self.current_gpx_data = None
        
        # Initialiser self.map à None
        self.map = None
        self.markers = []

    def showEvent(self, event):
        """Appelé quand la fenêtre est affichée"""
        super().showEvent(event)
        # Initialiser la carte seulement après que la fenêtre soit visible
        if self.map is None:
            self.setup_map()

    def setup_map(self):
        # Si une carte existe déjà, la supprimer
        if hasattr(self, 'map') and self.map is not None:
            # Supprimer les anciens marqueurs
            if hasattr(self, 'markers'):
                for marker in self.markers:
                    self.map.removeLayer(marker)
            # Supprimer l'ancienne polyline
            if hasattr(self, 'polyline') and self.polyline is not None:
                self.map.removeLayer(self.polyline)
        
        # Créer ou recréer la carte
        self.map = L.map(self.map_widget)
        self.map.setView([46.5, 2.5], 6)
        
        L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            {
                'attribution': 'Tiles © Esri',
                'maxZoom': 18
            }
        ).addTo(self.map)
        
        # Ajouter la polyline seulement si on a des coordonnées
        if self.coords:
            self.polyline = L.polyline(
                self.coords,
                {
                    'color': 'red',
                    'weight': 4,
                    'opacity': 0.8
                }
            )
            self.polyline.addTo(self.map)
        else:
            self.polyline = None
        
        # Ajout de marqueurs avec infos
        self.markers = []
        for city in self.points:
            marker = L.marker([city['lat'], city['lon']])
            
            # Popup avec infos détaillées
            popup_content = f"<b>{city['name']}</b><br>{city['info'].replace(chr(10), '<br>')}"
            marker.bindPopup(popup_content)
            
            self.markers.append(marker)
            marker.addTo(self.map)
        
        print("Carte PyQtlet interactive générée !")

    def open_setup(self):
        """Ouvre la fenêtre de configuration utilisateur"""
        dialog = UserConfigDialog(self)
        if dialog.exec_():
            # Si la configuration a été sauvegardée, mettre à jour l'affichage
            if self.current_gpx_data:
                self.update_info_display()
            print(" Configuration mise à jour")

    def import_gpx(self):
        """Ouvre une boîte de dialogue pour importer un fichier GPX"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier GPX",
            "",
            "Fichiers GPX (*.gpx);;Tous les fichiers (*)"
        )
        
        if not file_path:  # Si l'utilisateur annule
            return

        current_file = get_info(file_path)
        self.current_gpx_data = current_file
        
        self.points = []
        for i, point in enumerate(current_file["points"]):
            self.points.append({'name': f'Point {i}',
                                'lat' : point.latitude,
                                'lon': point.longitude,
                                'info': f'Altitude : {point.elevation} m\nHeure : {point.time}'})
        self.coords = [[city['lat'], city['lon']] for city in self.points]

        # Mettre à jour le label d'information
        self.update_info_display()

        self.setup_map()
        self.fit_bounds()  # Centrer automatiquement sur la trace
        print(f" GPX importé : {len(self.points)} points")

    def update_info_display(self):
        """Met à jour l'affichage des informations avec les calculs de fitness"""
        if not self.current_gpx_data:
            return
        
        deniv = self.current_gpx_data["denivele"]
        duree = self.current_gpx_data["durée"]
        distance = self.current_gpx_data["distance_km"]
        
        # Durée totale en minutes
        duree_minutes = duree['heures'] * 60 + duree['minutes'] + duree['secondes'] / 60
        
        # Obtenir la configuration utilisateur
        config = get_user_config()
        
        # === Carte Trace GPS ===
        trace_html = generate_trace_html(
            distance_km=distance,
            nb_points=len(self.points),
            deniv_pos=deniv['positif'],
            deniv_neg=deniv['negatif'],
            duree_dict=duree
        )
        self.trace_card.setText(trace_html)
        self.trace_card.setTextFormat(Qt.RichText)
        
        # === Carte Fitness ===
        if config:
            calories = calculate_calories(distance, deniv['positif'], duree_minutes, config)
            metrics = calculate_fitness_metrics(distance, deniv['positif'], duree_minutes, config)
            
            if calories and metrics:
                fitness_html = generate_fitness_html(config, calories, metrics)
                self.fitness_card.setText(fitness_html)
                self.fitness_card.setTextFormat(Qt.RichText)
                self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_ACTIVE)
        else:
            self.fitness_card.setText(generate_no_profile_html())
            self.fitness_card.setTextFormat(Qt.RichText)
            self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)

    def change_zoom(self, value):
        """Change le niveau de zoom"""
        if self.map is not None:
            self.map.setZoom(value)

    def fit_bounds(self):
        """Centre la carte sur la trace GPS"""
        if not self.points:
            return
        
        # Calcul des limites
        lats = [city['lat'] for city in self.points]
        lons = [city['lon'] for city in self.points]
        
        bounds = [
            [min(lats), min(lons)],
            [max(lats), max(lons)]
        ]
        
        self.map.fitBounds(bounds)
        # Ne pas changer le zoom manuellement, fitBounds le fait automatiquement
