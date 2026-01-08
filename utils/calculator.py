def calculate_calories(distance_km, denivele_positif, duree_minutes, config, activity_type=None):
    """
    Calcule les calories brûlées selon la formule MET standard
    """
    if not config or duree_minutes == 0:
        return None
    
    poids = config["poids"]
    activity = activity_type or config["activite_defaut"]
    duree_heures = duree_minutes / 60
    
    # Valeurs MET selon l'intensité
    # Source : Compendium of Physical Activities
    met_base = {
        "marche": 3.5,        # marche modérée 4-5 km/h
        "course": 9.0,        # course ~10 km/h
        "velo": 7.5,          # vélo ~20 km/h
        "vtt": 8.5,           # VTT terrain varié
        "ski": 7.0,           # ski de fond modéré
        "randonnee": 6.0      # randonnée sans sac
    }
    
    # Ajustement MET selon vitesse réelle
    vitesse_kmh = distance_km / duree_heures if duree_heures > 0 else 0
    
    if activity == "marche":
        if vitesse_kmh < 4:
            met = 2.5
        elif vitesse_kmh < 5:
            met = 3.5
        elif vitesse_kmh < 6:
            met = 4.3
        else:
            met = 5.0
    elif activity == "course":
        if vitesse_kmh < 8:
            met = 8.0
        elif vitesse_kmh < 10:
            met = 9.0
        elif vitesse_kmh < 12:
            met = 11.0
        else:
            met = 12.5
    elif activity == "randonnee":
        # MET varie selon terrain
        met = 6.0  # MET de base sans sac
        if denivele_positif > 500:
            met = 7.3  # terrain difficile
    else:
        met = met_base.get(activity, 5.0)
    
    # Calories de base (formule MET standard)
    calories_base = met * poids * duree_heures
    
    # Ajout pour le dénivelé
    # Approximation : 100m D+ ≈ 2.4 km sur plat ≈ 35-50 kcal pour 70kg
    # Soit environ 0.5 kcal par kg par mètre de D+
    calories_denivele = (denivele_positif / 100) * poids * 0.5
    
    return round(calories_base + calories_denivele, 1)

def calculate_fitness_metrics(distance_km, denivele_positif, duree_minutes, config):
    """
    Calcule divers indicateurs de fitness
    """
    if not config or duree_minutes == 0:
        return None
    
    vitesse_moy = (distance_km / (duree_minutes / 60))
    
    # FC estimation plus réaliste basée sur vitesse ET dénivelé
    fc_max = 220 - config["age"]
    fc_repos = config["fc_repos"]
    
    # Estimation intensité selon vitesse et dénivelé
    # Plus réaliste que des valeurs fixes
    vitesse_factor = min(vitesse_moy / 10, 0.8)  # normalise vitesse
    denivele_factor = min(denivele_positif / 1000 * 0.1, 0.2)  # impact D+
    
    intensite = 0.5 + vitesse_factor + denivele_factor  # 0.5 à 1.0
    intensite = min(intensite, 1.0)  # cap à 100%
    
    fc_moyenne = fc_repos + (fc_max - fc_repos) * intensite
    
    return {
        "vitesse_moy": round(vitesse_moy, 2),
        "fc_moyenne": round(fc_moyenne),
        "fc_max": fc_max,
        "intensite": round(intensite * 100, 1)
    }