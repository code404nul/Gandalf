import gpxpy
from datetime import datetime
from typing import List, Dict, Optional
from shutil import copy
from os import getcwd
import os.path
from math import radians, sin, cos, sqrt, atan2

class TrackPoint:
    def __init__(self, latitude: float, longitude: float, 
                 elevation: Optional[float] = None, 
                 time: Optional[datetime] = None):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.time = time
    
    def __repr__(self):
        return f"Point(lat={self.latitude:.6f}, lon={self.longitude:.6f}, elev={self.elevation}m, time={self.time})"


class GPXParser:
    def __init__(self, filepath: str):
        current_main_directory = getcwd()
        
        # Créer le chemin du dossier temp_files
        temp_dir = os.path.join(current_main_directory, "ressources", "temp_files")
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extraire le nom du fichier et créer le chemin complet de destination
        filename = os.path.basename(filepath)
        self.filepath = os.path.join(temp_dir, filename)
        
        # Copier le fichier
        copy(filepath, self.filepath)
        
        self.gpx_data = None
        self.points: List[TrackPoint] = []
        self.metadata: Dict = {}
        self.source_type = None
    
    def parse(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as gpx_file:
                self.gpx_data = gpxpy.parse(gpx_file)
            
            self._extract_metadata()
            self._extract_all_points()
            
            return True
            
        except FileNotFoundError:
            print(f"Erreur : Fichier '{self.filepath}' introuvable")
            return False
        except Exception as e:
            print(f"Erreur lors du parsing : {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_metadata(self):
        if self.gpx_data:
            self.metadata = {
                'nom': self.gpx_data.name or "Sans nom",
                'description': self.gpx_data.description or "Aucune description",
                'auteur': self.gpx_data.author_name or "Inconnu",
                'date_creation': self.gpx_data.time,
                'nb_tracks': len(self.gpx_data.tracks),
                'nb_routes': len(self.gpx_data.routes),
                'nb_waypoints': len(self.gpx_data.waypoints),
            }
    
    def _extract_all_points(self):
        self.points = []
        
        if self.gpx_data.tracks:
            self.source_type = 'tracks'
            for track in self.gpx_data.tracks:
                for segment in track.segments:
                    for point in segment.points:
                        self.points.append(TrackPoint(
                            latitude=point.latitude,
                            longitude=point.longitude,
                            elevation=point.elevation,
                            time=point.time
                        ))
            return
        if self.gpx_data.routes:
            self.source_type = 'routes'
            for route in self.gpx_data.routes:
                for point in route.points:
                    self.points.append(TrackPoint(
                        latitude=point.latitude,
                        longitude=point.longitude,
                        elevation=point.elevation,
                        time=getattr(point, 'time', None)
                    ))
            return
        
        if self.gpx_data.waypoints:
            self.source_type = 'waypoints'
            for waypoint in self.gpx_data.waypoints:
                self.points.append(TrackPoint(
                    latitude=waypoint.latitude,
                    longitude=waypoint.longitude,
                    elevation=waypoint.elevation,
                    time=waypoint.time
                ))
            return
    
    def get_denivele(self):
        deniveles = [self.points[i+1].elevation - self.points[i].elevation for i in range(len(self.points) - 1) if self.points[i].elevation is not None and self.points[i+1].elevation is not None]
        denivele_pos, denivele_neg = 0, 0
        for denivele in deniveles:
            if denivele >= 0: 
                denivele_pos += denivele
            else: 
                denivele_neg += abs(denivele)
        print((denivele_pos, denivele_neg))
        return (denivele_pos, denivele_neg)

    def get_duration(self):
        """Calcule la durée totale en secondes entre le premier et le dernier point"""
        times = [p.time for p in self.points if p.time is not None]
        if len(times) < 2:
            return 0
        
        times_sorted = sorted(times)
        duree_secondes = (times_sorted[-1] - times_sorted[0]).total_seconds()
        return duree_secondes
    
    def get_distance(self):
        """Calcule la distance totale en mètres en utilisant la formule de Haversine"""
        if len(self.points) < 2:
            return 0
        
        def haversine(lat1, lon1, lat2, lon2):
            """Calcule la distance entre deux points GPS en mètres"""
            R = 6371000  # Rayon de la Terre en mètres
            
            lat1_rad = radians(lat1)
            lat2_rad = radians(lat2)
            delta_lat = radians(lat2 - lat1)
            delta_lon = radians(lon2 - lon1)
            
            a = sin(delta_lat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            
            return R * c
        
        distance_totale = 0
        for i in range(len(self.points) - 1):
            distance_totale += haversine(
                self.points[i].latitude,
                self.points[i].longitude,
                self.points[i+1].latitude,
                self.points[i+1].longitude
            )
        
        return distance_totale

def get_info(fichier_gpx="ressources/test_files/fells_loop.gpx"):
    
    parser = GPXParser(fichier_gpx)
    
    # Valeurs par défaut
    deniv_pos, deniv_neg = 0, 0
    heures, minutes, secondes = 0, 0, 0
    distance_km = 0

    if parser.parse():
        deniv_pos, deniv_neg = parser.get_denivele()
        print(f"D+ : {deniv_pos:.1f} m")
        print(f"D- : {deniv_neg:.1f} m")
        
        duree = parser.get_duration()
        heures = int(duree // 3600)
        minutes = int((duree % 3600) // 60)
        secondes = int(duree % 60)
        
        print(f"Durée : {heures}h {minutes}m {secondes}s")
        
        distance_m = parser.get_distance()
        distance_km = distance_m / 1000
        print(f"Distance : {distance_km:.2f} km")
    else:
        print("Échec du parsing du fichier GPX")
        
    return {"denivele": {"positif": deniv_pos, "negatif": deniv_neg},
            "durée": {"heures": heures, "minutes": minutes, "secondes": secondes},
            "distance_km": distance_km,
            "points": parser.points}