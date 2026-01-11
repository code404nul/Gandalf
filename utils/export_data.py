import json
import csv
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from core.user_config import get_user_config
from utils.calculator import calculate_calories, calculate_fitness_metrics
from utils.co2_calculator import calculate_co2_saved, format_co2_for_export, get_co2_summary_text


def export_to_json(parent, traces_data):
    """Exporte les données en JSON avec stats de santé et CO2"""
    if not traces_data:
        QMessageBox.warning(parent, "Aucune donnée", "Aucune trace à exporter.")
        return
    
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Exporter en JSON",
        f"export_traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "Fichiers JSON (*.json)"
    )
    
    if not file_path:
        return
    
    config = get_user_config()
    export_data = {
        "export_date": datetime.now().isoformat(),
        "user_profile": config if config else None,
        "traces": []
    }
    
    total_co2_saved = None
    
    for trace in traces_data:
        data = trace['data']
        deniv = data['denivele']
        duree = data['durée']
        distance = data['distance_km']
        
        duree_minutes = duree['heures'] * 60 + duree['minutes'] + duree['secondes'] / 60
        
        # Estimation de durée si nécessaire
        if duree_minutes == 0 and config:
            from utils.calculator import _estimate_duration
            activity = config.get("activite_defaut", "marche")
            duree_minutes = _estimate_duration(distance, deniv['positif'], activity, config.get("niveau", "Intermédiaire"))
        
        trace_export = {
            "filename": data['filename'],
            "color": trace['color'],
            "distance_km": distance,
            "elevation_gain_m": deniv['positif'],
            "elevation_loss_m": deniv['negatif'],
            "duration_hours": duree['heures'],
            "duration_minutes": duree['minutes'],
            "duration_seconds": duree['secondes'],
            "total_points": len(data['points'])
        }
        
        # Ajouter les stats de santé si profil configuré
        if config:
            calories = calculate_calories(distance, deniv['positif'], duree_minutes, config)
            metrics = calculate_fitness_metrics(distance, deniv['positif'], duree_minutes, config)
            
            if calories and metrics:
                # Calcul de l'allure (pace en min/km)
                allure = (duree_minutes / distance) if distance > 0 else 0
                
                trace_export["health_metrics"] = {
                    "calories_burned": calories,
                    "average_speed_kmh": metrics['vitesse_moy'],
                    "average_pace_min_per_km": round(allure, 2),
                    "average_heart_rate": metrics['fc_moyenne'],
                    "max_heart_rate": metrics['fc_max'],
                    "intensity_percent": metrics['intensite']
                }
        
        # Calcul CO2 économisé pour cette trace
        co2_data = calculate_co2_saved(distance)
        if co2_data:
            trace_export["environmental_impact"] = format_co2_for_export(co2_data, "json")
        
        export_data["traces"].append(trace_export)
    
    # Ajouter les totaux
    total_distance = sum(t['data']['distance_km'] for t in traces_data)
    total_deniv_pos = sum(t['data']['denivele']['positif'] for t in traces_data)
    total_deniv_neg = sum(t['data']['denivele']['negatif'] for t in traces_data)
    
    total_seconds = sum(
        t['data']['durée']['heures'] * 3600 + 
        t['data']['durée']['minutes'] * 60 + 
        t['data']['durée']['secondes']
        for t in traces_data
    )
    
    total_duree_minutes = total_seconds / 60
    
    if total_duree_minutes == 0 and config:
        from utils.calculator import _estimate_duration
        activity = config.get("activite_defaut", "marche")
        total_duree_minutes = _estimate_duration(total_distance, total_deniv_pos, activity, config.get("niveau", "Intermédiaire"))
    
    export_data["summary"] = {
        "total_traces": len(traces_data),
        "total_distance_km": total_distance,
        "total_elevation_gain_m": total_deniv_pos,
        "total_elevation_loss_m": total_deniv_neg,
        "total_duration_minutes": total_duree_minutes
    }
    
    if config:
        total_calories = calculate_calories(total_distance, total_deniv_pos, total_duree_minutes, config)
        if total_calories:
            export_data["summary"]["total_calories_burned"] = total_calories
    
    # Calcul CO2 total économisé
    total_co2_data = calculate_co2_saved(total_distance)
    if total_co2_data:
        export_data["summary"]["total_environmental_impact"] = format_co2_for_export(total_co2_data, "json")
        # Ajouter un message lisible
        export_data["summary"]["environmental_message"] = get_co2_summary_text(total_co2_data, "detaille")
    
    # Sauvegarder
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # Message de succès avec info CO2
        msg = f"Données exportées dans:\n{file_path}"
        if total_co2_data:
            msg += f"\n\n{get_co2_summary_text(total_co2_data, 'court')}"
        
        QMessageBox.information(parent, "Export réussi", msg)
    except Exception as e:
        QMessageBox.critical(parent, "Erreur d'export", f"Impossible d'exporter les données:\n{str(e)}")


def export_to_csv(parent, traces_data):
    """Exporte les données en CSV avec stats de santé et CO2"""
    if not traces_data:
        QMessageBox.warning(parent, "Aucune donnée", "Aucune trace à exporter.")
        return
    
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Exporter en CSV",
        f"export_traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "Fichiers CSV (*.csv)"
    )
    
    if not file_path:
        return
    
    config = get_user_config()
    total_distance = 0
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'Fichier', 'Couleur', 'Distance (km)', 'D+ (m)', 'D- (m)',
                'Durée (h)', 'Durée (min)', 'Durée (s)', 'Points',
                'Calories', 'Vitesse moy. (km/h)', 'Allure (min/km)', 
                'FC moy. (bpm)', 'Intensité (%)',
                'CO2 économisé voiture (kg)', 'CO2 économisé bus (kg)', 
                'CO2 économisé train (kg)', 'Équiv. arbres (jours)'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for trace in traces_data:
                data = trace['data']
                deniv = data['denivele']
                duree = data['durée']
                distance = data['distance_km']
                total_distance += distance
                
                duree_minutes = duree['heures'] * 60 + duree['minutes'] + duree['secondes'] / 60
                
                if duree_minutes == 0 and config:
                    from utils.calculator import _estimate_duration
                    activity = config.get("activite_defaut", "marche")
                    duree_minutes = _estimate_duration(distance, deniv['positif'], activity, config.get("niveau", "Intermédiaire"))
                
                row = {
                    'Fichier': data['filename'],
                    'Couleur': trace['color'],
                    'Distance (km)': f"{distance:.2f}",
                    'D+ (m)': f"{deniv['positif']:.0f}",
                    'D- (m)': f"{deniv['negatif']:.0f}",
                    'Durée (h)': duree['heures'],
                    'Durée (min)': duree['minutes'],
                    'Durée (s)': duree['secondes'],
                    'Points': len(data['points']),
                    'Calories': '',
                    'Vitesse moy. (km/h)': '',
                    'Allure (min/km)': '',
                    'FC moy. (bpm)': '',
                    'Intensité (%)': '',
                    'CO2 économisé voiture (kg)': '',
                    'CO2 économisé bus (kg)': '',
                    'CO2 économisé train (kg)': '',
                    'Équiv. arbres (jours)': ''
                }
                
                if config:
                    calories = calculate_calories(distance, deniv['positif'], duree_minutes, config)
                    metrics = calculate_fitness_metrics(distance, deniv['positif'], duree_minutes, config)
                    
                    if calories and metrics:
                        # Calcul de l'allure
                        allure = (duree_minutes / distance) if distance > 0 else 0
                        
                        row['Calories'] = f"{calories:.0f}"
                        row['Vitesse moy. (km/h)'] = f"{metrics['vitesse_moy']:.2f}"
                        row['Allure (min/km)'] = f"{allure:.2f}"
                        row['FC moy. (bpm)'] = f"{metrics['fc_moyenne']:.0f}"
                        row['Intensité (%)'] = f"{metrics['intensite']:.1f}"
                
                # Calcul CO2
                co2_data = calculate_co2_saved(distance)
                if co2_data:
                    co2_csv = format_co2_for_export(co2_data, "csv")
                    row.update(co2_csv)
                
                writer.writerow(row)
        
        # Message de succès avec info CO2
        msg = f"Données exportées dans:\n{file_path}"
        total_co2_data = calculate_co2_saved(total_distance)
        if total_co2_data:
            msg += f"\n\n{get_co2_summary_text(total_co2_data, 'court')}"
        
        QMessageBox.information(parent, "Export réussi", msg)
    except Exception as e:
        QMessageBox.critical(parent, "Erreur d'export", f"Impossible d'exporter les données:\n{str(e)}")