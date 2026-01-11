import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QSpinBox, QLabel, QFileDialog,
                             QListWidget, QListWidgetItem, QCheckBox, QMessageBox, QMenu)
from PyQt5.QtCore import Qt
from pyqtlet2 import L, MapWidget

from core.gpx import get_info
from core.user_config import UserConfigDialog, get_user_config, get_activity_for_trace
from utils.calculator import calculate_calories, calculate_fitness_metrics
from utils.info_display import *
from utils.export_data import export_to_json, export_to_csv

# Couleurs pour les différentes traces
TRACE_COLORS = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFA500', 
                '#00FFFF', '#FFFF00', '#8B00FF', '#FF1493', '#32CD32']


class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trace GPS Multi-fichiers - Interactive")
        self.setGeometry(100, 100, 1400, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # === PANNEAU GAUCHE - Liste des traces ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(300)
        
        # Titre du panneau
        traces_title = QLabel("Traces GPS")
        traces_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        left_layout.addWidget(traces_title)
        
        # Liste des traces chargées
        self.traces_list = QListWidget()
        self.traces_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        self.traces_list.itemClicked.connect(self.on_trace_selected)
        left_layout.addWidget(self.traces_list)
        
        # Boutons de gestion
        btn_import = QPushButton("Importer GPX")
        btn_import.clicked.connect(self.import_gpx)
        btn_import.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 10px;")
        left_layout.addWidget(btn_import)
        
        btn_remove = QPushButton("Supprimer sélection")
        btn_remove.clicked.connect(self.remove_selected_trace)
        btn_remove.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px; border-radius: 10px;")
        left_layout.addWidget(btn_remove)
        
        btn_clear = QPushButton("Tout effacer")
        btn_clear.clicked.connect(self.clear_all_traces)
        btn_clear.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold; padding: 10px; border-radius: 10px;")
        left_layout.addWidget(btn_clear)
        
        btn_show_all = QPushButton("Vue globale")
        btn_show_all.clicked.connect(self.show_global_view)
        btn_show_all.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 10px;  border-radius: 10px;")
        left_layout.addWidget(btn_show_all)
        
        # Bouton d'export
        btn_export = QPushButton("Exporter")
        btn_export.clicked.connect(self.export_data)
        btn_export.setStyleSheet("background-color: #009688; color: white; font-weight: bold; padding: 10px; border-radius: 10px;")
        left_layout.addWidget(btn_export)
        
        main_layout.addWidget(left_panel)
        
        # === PANNEAU DROIT - Carte et infos ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Layout pour les contrôles
        controls_layout = QHBoxLayout()
        
        # Bouton Setup
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
        
        # Bouton centrer sur traces
        btn_fit = QPushButton("Centrer sur traces")
        btn_fit.clicked.connect(self.fit_bounds)
        controls_layout.addWidget(btn_fit)
        
        controls_layout.addStretch()
        right_layout.addLayout(controls_layout)
        
        # Création du MapWidget
        self.map_widget = MapWidget()
        right_layout.addWidget(self.map_widget, stretch=3)
        
        # Zone d'informations
        self.info_widget = QWidget()
        self.info_layout = QHBoxLayout(self.info_widget)
        self.info_layout.setSpacing(10)
        
        # Carte Trace GPS
        self.trace_card = QLabel("Importez un ou plusieurs fichiers GPX pour commencer")
        self.trace_card.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.trace_card.setStyleSheet(TRACE_CARD_STYLE)
        self.info_layout.addWidget(self.trace_card, stretch=1)
        
        # Carte Fitness
        self.fitness_card = QLabel("Configurez votre profil\npour voir les stats")
        self.fitness_card.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)
        self.info_layout.addWidget(self.fitness_card, stretch=1)
        
        right_layout.addWidget(self.info_widget)
        
        main_layout.addWidget(right_panel)
        
        # Stockage des traces
        self.loaded_traces = []  # Liste de dicts: {data, polyline, color, visible, checkbox}
        self.map = None
        self.selected_trace_index = None  # Index de la trace sélectionnée

    def showEvent(self, event):
        """Appelé quand la fenêtre est affichée"""
        super().showEvent(event)
        if self.map is None:
            self.setup_map()

    def setup_map(self):
        """Initialise ou réinitialise la carte"""
        if hasattr(self, 'map') and self.map is not None:
            # Nettoyer les anciennes polylines
            for trace in self.loaded_traces:
                if trace.get('polyline'):
                    self.map.removeLayer(trace['polyline'])
        
        # Créer la carte
        self.map = L.map(self.map_widget)
        self.map.setView([46.5, 2.5], 6)
        
        L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            {
                'attribution': 'Tiles © Esri',
                'maxZoom': 18
            }
        ).addTo(self.map)
        
        # Redessiner toutes les traces visibles
        for trace in self.loaded_traces:
            if trace['visible']:
                self.draw_trace(trace)
        
        print("Carte PyQtlet interactive générée !")

    def draw_trace(self, trace):
        """Dessine une trace sur la carte"""
        if not trace['data']['points']:
            return
        
        coords = [[p.latitude, p.longitude] for p in trace['data']['points']]
        
        polyline = L.polyline(
            coords,
            {
                'color': trace['color'],
                'weight': 4,
                'opacity': 0.8
            }
        )
        polyline.addTo(self.map)
        trace['polyline'] = polyline

    def import_gpx(self):
        """Importe un ou plusieurs fichiers GPX"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Sélectionner un ou plusieurs fichiers GPX",
            "",
            "Fichiers GPX (*.gpx);;Tous les fichiers (*)"
        )
        
        if not file_paths:
            return

        user_config = get_user_config()

        for file_path in file_paths:
            gpx_data = get_info(file_path)
            
            # Détecter l'activité pour cette trace
            activity_code, activity_display, is_detected = get_activity_for_trace(
                gpx_data['filename'], 
                user_config
            )
            
            # Ajouter les infos d'activité aux données
            gpx_data['activity'] = activity_code
            gpx_data['activity_display'] = activity_display
            gpx_data['activity_auto_detected'] = is_detected
            
            # Attribuer une couleur
            color_index = len(self.loaded_traces) % len(TRACE_COLORS)
            color = TRACE_COLORS[color_index]
            
            # Créer l'entrée de trace
            trace = {
                'data': gpx_data,
                'color': color,
                'visible': True,
                'polyline': None
            }
            
            self.loaded_traces.append(trace)
            
            # Ajouter à la liste
            self.add_trace_to_list(trace, gpx_data['filename'])
            
            # Dessiner la trace
            if self.map:
                self.draw_trace(trace)
            
            # Log de l'activité détectée
            if is_detected:
                print(f"✓ {gpx_data['filename']}: Activité auto-détectée -> {activity_display}")
            else:
                print(f"  {gpx_data['filename']}: Activité par défaut -> {activity_display}")
        
        # Mise à jour de l'affichage en vue globale
        self.show_global_view()
        
        print(f"{len(file_paths)} fichier(s) GPX importé(s)")

    def add_trace_to_list(self, trace, filename):
        """Ajoute une trace à la liste avec checkbox"""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Checkbox pour visibilité
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda state, t=trace: self.toggle_trace_visibility(t, state))
        item_layout.addWidget(checkbox)
        trace['checkbox'] = checkbox
        
        # Indicateur de couleur
        color_label = QLabel("●")
        color_label.setStyleSheet(f"color: {trace['color']}; font-size: 20px;")
        item_layout.addWidget(color_label)
        
        # Nom du fichier
        name_label = QLabel(filename)
        name_label.setStyleSheet("font-weight: bold;")
        item_layout.addWidget(name_label)
        
        item_layout.addStretch()
        
        # Stats rapides
        stats_label = QLabel(f"{trace['data']['distance_km']:.1f} km")
        stats_label.setStyleSheet("color: #666; font-size: 11px;")
        item_layout.addWidget(stats_label)
        
        # Créer l'item
        item = QListWidgetItem(self.traces_list)
        item.setSizeHint(item_widget.sizeHint())
        self.traces_list.addItem(item)
        self.traces_list.setItemWidget(item, item_widget)

    def on_trace_selected(self, item):
        """Appelé quand une trace est sélectionnée dans la liste"""
        index = self.traces_list.row(item)
        self.selected_trace_index = index
        
        # Afficher uniquement les infos de cette trace
        self.update_info_display_single(index)
        
        # Zoomer sur cette trace
        self.fit_bounds_single(index)
        
        print(f"Trace sélectionnée : {self.loaded_traces[index]['data']['filename']}")

    def toggle_trace_visibility(self, trace, state):
        """Active/désactive la visibilité d'une trace"""
        trace['visible'] = (state == Qt.Checked)
        
        if trace['polyline']:
            if trace['visible']:
                trace['polyline'].addTo(self.map)
            else:
                self.map.removeLayer(trace['polyline'])

    def remove_selected_trace(self):
        """Supprime la trace sélectionnée"""
        current_row = self.traces_list.currentRow()
        if current_row >= 0:
            trace = self.loaded_traces[current_row]
            
            # Retirer de la carte
            if trace.get('polyline'):
                self.map.removeLayer(trace['polyline'])
            
            # Retirer de la liste
            self.traces_list.takeItem(current_row)
            self.loaded_traces.pop(current_row)
            
            # Réinitialiser la sélection
            self.selected_trace_index = None
            
            # Afficher la vue globale si des traces restent
            if self.loaded_traces:
                self.show_global_view()
            else:
                self.update_info_display_global()
            
            print("Trace supprimée")

    def clear_all_traces(self):
        """Efface toutes les traces"""
        for trace in self.loaded_traces:
            if trace.get('polyline'):
                self.map.removeLayer(trace['polyline'])
        
        self.loaded_traces.clear()
        self.traces_list.clear()
        self.selected_trace_index = None
        self.update_info_display_global()
        print("Toutes les traces effacées")

    def show_global_view(self):
        """Affiche la vue globale avec toutes les traces"""
        self.selected_trace_index = None
        self.traces_list.clearSelection()
        self.update_info_display_global()
        self.fit_bounds()
        print("Vue globale activée")

    def open_setup(self):
        """Ouvre la fenêtre de configuration utilisateur"""
        dialog = UserConfigDialog(self)
        if dialog.exec_():
            if self.loaded_traces:
                if self.selected_trace_index is not None:
                    self.update_info_display_single(self.selected_trace_index)
                else:
                    self.update_info_display_global()
            print("Configuration mise à jour")

    def export_data(self):
        """Ouvre un menu pour choisir le format d'export"""
        if not self.loaded_traces:
            QMessageBox.warning(self, "Aucune donnée", "Aucune trace à exporter.")
            return
        
        # Créer le menu contextuel
        menu = QMenu(self)
        
        # Initialiser les variables à None
        action_json_single = None
        action_csv_single = None
        
        # Déterminer quelles traces exporter
        if self.selected_trace_index is not None:
            # Une trace est sélectionnée
            menu.addSection("Exporter trace sélectionnée")
            action_json_single = menu.addAction("JSON - Trace sélectionnée")
            action_csv_single = menu.addAction("CSV - Trace sélectionnée")
            menu.addSeparator()
        
        # Toujours proposer l'export global
        menu.addSection("Exporter toutes les traces")
        action_json_all = menu.addAction("JSON - Toutes les traces")
        action_csv_all = menu.addAction("CSV - Toutes les traces")
        
        # Afficher le menu à la position du bouton
        export_btn = self.sender()
        if export_btn:
            action = menu.exec_(export_btn.mapToGlobal(export_btn.rect().bottomLeft()))
            
            if action:
                # Déterminer les traces à exporter
                if self.selected_trace_index is not None and action in [action_json_single, action_csv_single]:
                    # Exporter uniquement la trace sélectionnée
                    traces_to_export = [self.loaded_traces[self.selected_trace_index]]
                else:
                    # Exporter toutes les traces
                    traces_to_export = self.loaded_traces
                
                # Exporter selon le format choisi
                if action in [action_json_single, action_json_all]:
                    export_to_json(self, traces_to_export)
                elif action in [action_csv_single, action_csv_all]:
                    export_to_csv(self, traces_to_export)

    def update_info_display_single(self, trace_index):
        """Affiche les informations d'une seule trace"""
        if trace_index >= len(self.loaded_traces):
            return
        
        trace_data = self.loaded_traces[trace_index]['data']
        trace_color = self.loaded_traces[trace_index]['color']
        
        deniv = trace_data["denivele"]
        duree = trace_data["durée"]
        distance = trace_data["distance_km"]
        
        # Récupérer l'activité
        activity_display = trace_data.get('activity_display', 'Non défini')
        is_auto_detected = trace_data.get('activity_auto_detected', False)
        activity_icon = "🔍" if is_auto_detected else "⚙️"
        activity_label = f"{activity_icon} {activity_display}"
        
        # Durée totale en minutes
        duree_minutes = duree['heures'] * 60 + duree['minutes'] + duree['secondes'] / 60
        
        # Obtenir la configuration utilisateur
        config = get_user_config()
        
        # Vérifier si la durée est à 0 et estimer si nécessaire
        duree_dict_display = duree.copy()
        if duree_minutes == 0 and config:
            from utils.calculator import _estimate_duration
            activity_code = trace_data.get('activity', config.get("activite_defaut", "marche"))
            duree_estimee_minutes = _estimate_duration(
                distance, 
                deniv['positif'], 
                activity_code, 
                config.get("niveau", "Intermédiaire")
            )
            
            duree_dict_display = {
                'heures': int(duree_estimee_minutes // 60),
                'minutes': int(duree_estimee_minutes % 60),
                'secondes': int((duree_estimee_minutes % 1) * 60)
            }
            duree_minutes = duree_estimee_minutes
        
        # === Carte Trace GPS ===
        trace_html = f"""
        <div style='font-family: Arial, sans-serif;'>
            <h3 style='color: {trace_color}; margin-top: 0;'>{trace_data['filename']}</h3>
            <p style='background-color: #e3f2fd; padding: 5px; border-radius: 4px; margin: 5px 0;'>
                <b>Type:</b> {activity_label}
            </p>
            <table style='width: 100%; border-spacing: 0;'>
                <tr><td style='padding: 5px 0;'><b>Distance:</b></td><td style='text-align: right;'>{distance:.2f} km</td></tr>
                <tr><td style='padding: 5px 0;'><b>Points:</b></td><td style='text-align: right;'>{len(trace_data['points'])}</td></tr>
                <tr style='background-color: #e8f5e9;'><td style='padding: 5px 0;'><b>D+ ⬆️:</b></td><td style='text-align: right;'>{deniv['positif']:.0f} m</td></tr>
                <tr style='background-color: #ffebee;'><td style='padding: 5px 0;'><b>D- ⬇️:</b></td><td style='text-align: right;'>{deniv['negatif']:.0f} m</td></tr>
                <tr><td style='padding: 5px 0;'><b>Durée:</b></td><td style='text-align: right;'>{duree_dict_display['heures']}h {duree_dict_display['minutes']}m {duree_dict_display['secondes']}s</td></tr>
            </table>
        </div>
        """
        
        self.trace_card.setText(trace_html)
        self.trace_card.setTextFormat(Qt.RichText)
        
        # === Carte Fitness ===
        if config:
            # Utiliser l'activité de la trace pour les calculs
            activity_code = trace_data.get('activity', config.get("activite_defaut", "marche"))
            activity_display_name = trace_data.get('activity_display', config.get("activite_defaut_display", "Marche"))
            
            # Créer une config temporaire avec l'activité de cette trace
            trace_config = config.copy()
            trace_config['activite_defaut'] = activity_code
            trace_config['activite_defaut_display'] = activity_display_name
            
            calories = calculate_calories(distance, deniv['positif'], duree_minutes, trace_config)
            metrics = calculate_fitness_metrics(distance, deniv['positif'], duree_minutes, trace_config)
            
            if calories and metrics:
                fitness_html = generate_fitness_html(trace_config, calories, metrics)
                self.fitness_card.setText(fitness_html)
                self.fitness_card.setTextFormat(Qt.RichText)
                self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_ACTIVE)
        else:
            self.fitness_card.setText(generate_no_profile_html())
            self.fitness_card.setTextFormat(Qt.RichText)
            self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)


    # Pour la vue globale, vous pouvez aussi afficher un récapitulatif des activités :

    def update_info_display_global(self):
        """Met à jour l'affichage avec les statistiques globales"""
        if not self.loaded_traces:
            self.trace_card.setText("Importez un ou plusieurs fichiers GPX pour commencer")
            self.fitness_card.setText("Configurez votre profil\npour voir les stats")
            self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)
            return
        
        # Calculer les totaux
        total_distance = sum(t['data']['distance_km'] for t in self.loaded_traces)
        total_deniv_pos = sum(t['data']['denivele']['positif'] for t in self.loaded_traces)
        total_deniv_neg = sum(t['data']['denivele']['negatif'] for t in self.loaded_traces)
        total_points = sum(len(t['data']['points']) for t in self.loaded_traces)
        
        # Compter les activités
        activity_counts = {}
        for trace in self.loaded_traces:
            activity = trace['data'].get('activity_display', 'Non défini')
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        activities_summary = ", ".join([f"{count}x {act}" for act, count in activity_counts.items()])
        
        # Calculer la durée totale
        total_seconds = sum(
            t['data']['durée']['heures'] * 3600 + 
            t['data']['durée']['minutes'] * 60 + 
            t['data']['durée']['secondes']
            for t in self.loaded_traces
        )
        
        duree_dict = {
            'heures': int(total_seconds // 3600),
            'minutes': int((total_seconds % 3600) // 60),
            'secondes': int(total_seconds % 60)
        }
        
        # Vérifier si la durée totale est 0 et estimer si nécessaire
        duree_minutes = total_seconds / 60
        config = get_user_config()
        
        if duree_minutes == 0 and config:
            from utils.calculator import _estimate_duration
            activity = config.get("activite_defaut", "marche")
            duree_estimee_minutes = _estimate_duration(total_distance, total_deniv_pos, activity, config.get("niveau", "Intermédiaire"))
            
            duree_dict = {
                'heures': int(duree_estimee_minutes // 60),
                'minutes': int(duree_estimee_minutes % 60),
                'secondes': int((duree_estimee_minutes % 1) * 60)
            }
            duree_minutes = duree_estimee_minutes
        
        # Afficher les infos de trace
        trace_html = f"""
        <div style='font-family: Arial, sans-serif;'>
            <h3 style='color: #1976D2; margin-top: 0;'>Statistiques Globales</h3>
            <p style='background-color: #e3f2fd; padding: 5px; border-radius: 4px;'>
                <b>{len(self.loaded_traces)} trace(s) chargée(s)</b>
            </p>
            <p style='background-color: #f3e5f5; padding: 5px; border-radius: 4px; font-size: 11px;'>
                {activities_summary}
            </p>
            <table style='width: 100%; border-spacing: 0;'>
                <tr><td style='padding: 5px 0;'><b>Distance totale:</b></td><td style='text-align: right;'>{total_distance:.2f} km</td></tr>
                <tr><td style='padding: 5px 0;'><b>Points totaux:</b></td><td style='text-align: right;'>{total_points}</td></tr>
                <tr style='background-color: #e8f5e9;'><td style='padding: 5px 0;'><b>D+ total ⬆️:</b></td><td style='text-align: right;'>{total_deniv_pos:.0f} m</td></tr>
                <tr style='background-color: #ffebee;'><td style='padding: 5px 0;'><b>D- total ⬇️:</b></td><td style='text-align: right;'>{total_deniv_neg:.0f} m</td></tr>
                <tr><td style='padding: 5px 0;'><b>Durée totale:</b></td><td style='text-align: right;'>{duree_dict['heures']}h {duree_dict['minutes']}m {duree_dict['secondes']}s</td></tr>
            </table>
        </div>
        """
        
        self.trace_card.setText(trace_html)
        self.trace_card.setTextFormat(Qt.RichText)
        
        # Calculer les stats fitness (basées sur les totaux)
        if config:
            calories = calculate_calories(total_distance, total_deniv_pos, duree_minutes, config)
            metrics = calculate_fitness_metrics(total_distance, total_deniv_pos, duree_minutes, config)
            
            if calories and metrics:
                fitness_html = generate_fitness_html(config, calories, metrics)
                self.fitness_card.setText(fitness_html)
                self.fitness_card.setTextFormat(Qt.RichText)
                self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_ACTIVE)
        else:
            self.fitness_card.setText(generate_no_profile_html())
            self.fitness_card.setTextFormat(Qt.RichText)
            self.fitness_card.setStyleSheet(FITNESS_CARD_STYLE_INACTIVE)
        
        # Calculer les stats fitness (basées sur les totaux)
        if config:
            calories = calculate_calories(total_distance, total_deniv_pos, duree_minutes, config)
            metrics = calculate_fitness_metrics(total_distance, total_deniv_pos, duree_minutes, config)
            
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

    def fit_bounds_single(self, trace_index):
        """Centre la carte sur une seule trace"""
        if trace_index >= len(self.loaded_traces):
            return
        
        points = self.loaded_traces[trace_index]['data']['points']
        if not points:
            return
        
        lats = [p.latitude for p in points]
        lons = [p.longitude for p in points]
        
        bounds = [
            [min(lats), min(lons)],
            [max(lats), max(lons)]
        ]
        
        self.map.fitBounds(bounds)

    def fit_bounds(self):
        """Centre la carte sur toutes les traces visibles"""
        visible_points = []
        for trace in self.loaded_traces:
            if trace['visible']:
                visible_points.extend(trace['data']['points'])
        
        if not visible_points:
            return
        
        lats = [p.latitude for p in visible_points]
        lons = [p.longitude for p in visible_points]
        
        bounds = [
            [min(lats), min(lons)],
            [max(lats), max(lons)]
        ]
        
        self.map.fitBounds(bounds)