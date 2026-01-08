"""
Module pour générer l'affichage HTML des informations GPS et fitness
"""

def generate_trace_html(distance_km, nb_points, deniv_pos, deniv_neg, duree_dict):
    """
    Génère le HTML pour la carte Trace GPS
    
    Args:
        distance_km: Distance en kilomètres
        nb_points: Nombre de points
        deniv_pos: Dénivelé positif en mètres
        deniv_neg: Dénivelé négatif en mètres
        duree_dict: Dictionnaire {'heures': x, 'minutes': y, 'secondes': z}
    
    Returns:
        str: Code HTML formaté
    """
    return f"""
    <div style='font-family: Arial, sans-serif;'>
        <h3 style='color: #1976D2; margin-top: 0;'>Trace GPS</h3>
        <table style='width: 100%; border-spacing: 0;'>
            <tr><td style='padding: 5px 0;'><b>Distance:</b></td><td style='text-align: right;'>{distance_km:.2f} km</td></tr>
            <tr><td style='padding: 5px 0;'><b>Points:</b></td><td style='text-align: right;'>{nb_points}</td></tr>
            <tr style='background-color: #e8f5e9;'><td style='padding: 5px 0;'><b>D+ ⬆️:</b></td><td style='text-align: right;'>{deniv_pos:.0f} m</td></tr>
            <tr style='background-color: #ffebee;'><td style='padding: 5px 0;'><b>D- ⬇️:</b></td><td style='text-align: right;'>{deniv_neg:.0f} m</td></tr>
            <tr><td style='padding: 5px 0;'><b>Durée:</b></td><td style='text-align: right;'>{duree_dict['heures']}h {duree_dict['minutes']}m {duree_dict['secondes']}s</td></tr>
        </table>
    </div>
    """


def generate_fitness_html(config, calories, metrics):
    """
    Génère le HTML pour la carte Indicateurs Fitness
    
    Args:
        config: Dictionnaire de configuration utilisateur
        calories: Nombre de calories brûlées
        metrics: Dictionnaire des métriques fitness
    
    Returns:
        str: Code HTML formaté
    """
    return f"""
    <div style='font-family: Arial, sans-serif;'>
        <h3 style='color: #FF6F00; margin-top: 0;'>Indicateurs Fitness</h3>
        <p style='margin: 5px 0; background-color: #fff9c4; padding: 5px; border-radius: 4px;'>
            <b>Activité:</b> {config['activite_defaut_display']}
        </p>
        <table style='width: 100%; border-spacing: 0; margin-top: 10px;'>
            <tr><td style='padding: 5px 0;'><b>Calories:</b></td><td style='text-align: right; color: #d32f2f;'><b>{calories:.0f} kcal</b></td></tr>
            <tr><td style='padding: 5px 0;'><b>Vitesse moy:</b></td><td style='text-align: right;'>{metrics['vitesse_moy']:.1f} km/h</td></tr>
            <tr><td style='padding: 5px 0;'><b>FC moyenne:</b></td><td style='text-align: right;'>{metrics['fc_moyenne']:.0f} bpm</td></tr>
            <tr><td style='padding: 5px 0;'><b>Intensité:</b></td><td style='text-align: right;'>{metrics['intensite']:.0f}%</td></tr>
        </table>
    </div>
    """


def generate_no_profile_html():
    """
    Génère le HTML pour le message "pas de profil configuré"
    
    Returns:
        str: Code HTML formaté
    """
    return "<b>Configurez votre profil</b><br>pour voir les statistiques fitness"


# Styles CSS pour les cartes
TRACE_CARD_STYLE = """
    font-size: 14px; 
    padding: 15px; 
    background-color: #ffffff;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    color: #333;
"""

FITNESS_CARD_STYLE_ACTIVE = """
    font-size: 14px; 
    padding: 15px; 
    background-color: #fff3e0;
    border: 2px solid #ffb74d;
    border-radius: 8px;
    color: #333;
"""

FITNESS_CARD_STYLE_INACTIVE = """
    font-size: 14px; 
    padding: 15px; 
    background-color: #ffebee;
    border: 2px solid #ef5350;
    border-radius: 8px;
    color: #333;
"""