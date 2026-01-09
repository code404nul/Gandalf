# Constantes de configuration
VITESSE_BASE_INTERMEDIAIRE = {
    "marche": 5.0,
    "course": 10.0,
    "velo": 23.0,
    "vtt": 15.0,
    "ski": 8.0,
    "randonnee": 4.0,
    "natation": 2.5,
    "voile": 12.0
}

COEF_NIVEAU = {
    "Débutant": 0.70,
    "Intermédiaire": 1.0,
    "Avancé": 1.25,
    "Expert": 1.50
}

COEF_DENIVELE_NIVEAU = {
    "Débutant": 1.3,
    "Intermédiaire": 1.0,
    "Avancé": 0.85,
    "Expert": 0.70
}

MET_BASE = {
    "marche": 3.5,
    "course": 9.0,
    "velo": 7.5,
    "vtt": 8.5,
    "ski": 7.0,
    "randonnee": 6.0,
    "natation": 8.3,
    "voile": 3.3
}

# Activités sans impact de dénivelé
ACTIVITES_2D = {"natation", "voile"}


def _estimate_duration(distance_km, denivele_positif, activity, niveau="Intermédiaire"):
    """
    Estime la durée en minutes pour une activité sans timestamps.
    
    Args:
        distance_km: Distance parcourue en km
        denivele_positif: Dénivelé positif en mètres
        activity: Type d'activité
        niveau: Niveau du pratiquant
    
    Returns:
        float: Durée estimée en minutes
    """
    # Calcul temps de base
    vitesse_base = VITESSE_BASE_INTERMEDIAIRE.get(activity, 5.0)
    vitesse_ajustee = vitesse_base * COEF_NIVEAU.get(niveau, 1.0)
    temps_base_heures = distance_km / vitesse_ajustee
    
    # Calcul temps lié au dénivelé
    temps_denivele_heures = 0
    if activity not in ACTIVITES_2D:
        coef_base = 0.25 if activity in ["velo", "vtt"] else 0.17
        coef_ajuste = coef_base * COEF_DENIVELE_NIVEAU.get(niveau, 1.0)
        temps_denivele_heures = (denivele_positif / 100) * coef_ajuste
    
    duree_minutes = (temps_base_heures + temps_denivele_heures) * 60
    print(f"⚠️ Durée estimée ({niveau}) : {duree_minutes:.1f} min ({duree_minutes/60:.2f}h)")
    
    return duree_minutes


def _get_met_voile(vitesse_kmh):
    """Calcule le MET pour la voile selon la vitesse."""
    thresholds = [(8, 2.0), (12, 3.0), (15, 3.3), (18, 4.5), (22, 6.5)]
    
    for seuil, met in thresholds:
        if vitesse_kmh < seuil:
            return met
    return 9.3  # Compétition intensive


def _get_met_natation(vitesse_kmh):
    """Calcule le MET pour la natation selon la vitesse."""
    thresholds = [(2.0, 6.0), (2.5, 7.0), (3.0, 8.3), (3.5, 10.0)]
    
    for seuil, met in thresholds:
        if vitesse_kmh < seuil:
            return met
    return 11.0


def _get_met_marche(vitesse_kmh):
    """Calcule le MET pour la marche selon la vitesse."""
    thresholds = [(4, 2.5), (5, 3.5), (6, 4.3)]
    
    for seuil, met in thresholds:
        if vitesse_kmh < seuil:
            return met
    return 5.0


def _get_met_course(vitesse_kmh):
    """Calcule le MET pour la course selon la vitesse."""
    thresholds = [(8, 8.0), (10, 9.0), (12, 11.0)]
    
    for seuil, met in thresholds:
        if vitesse_kmh < seuil:
            return met
    return 12.5


def _calculate_met(activity, vitesse_kmh, denivele_positif):
    """
    Calcule la valeur MET selon l'activité et les conditions.
    
    Args:
        activity: Type d'activité
        vitesse_kmh: Vitesse moyenne en km/h
        denivele_positif: Dénivelé positif en mètres
    
    Returns:
        float: Valeur MET
    """
    met_calculators = {
        "voile": _get_met_voile,
        "natation": _get_met_natation,
        "marche": _get_met_marche,
        "course": _get_met_course
    }
    
    if activity in met_calculators:
        return met_calculators[activity](vitesse_kmh)
    
    if activity == "randonnee":
        return 7.3 if denivele_positif > 500 else 6.0
    
    return MET_BASE.get(activity, 5.0)


def calculate_calories(distance_km, denivele_positif, duree_minutes, config, activity_type=None):
    """
    Calcule les calories brûlées selon la formule MET standard.
    
    Args:
        distance_km: Distance parcourue en km
        denivele_positif: Dénivelé positif en mètres
        duree_minutes: Durée de l'activité en minutes
        config: Configuration utilisateur (poids, activité, niveau)
        activity_type: Type d'activité (optionnel, sinon utilise config)
    
    Returns:
        float: Calories brûlées (arrondi à 1 décimale)
    """
    if not config:
        return None
    
    activity = activity_type or config["activite_defaut"]
    niveau = config.get("niveau", "Intermédiaire")
    
    # Estimation durée si manquante
    if duree_minutes == 0:
        duree_minutes = _estimate_duration(distance_km, denivele_positif, activity, niveau)
    
    duree_heures = duree_minutes / 60
    poids = config["poids"]
    vitesse_kmh = distance_km / duree_heures if duree_heures > 0 else 0
    
    # Calcul MET et calories de base
    met = _calculate_met(activity, vitesse_kmh, denivele_positif)
    calories_base = met * poids * duree_heures
    
    # Bonus dénivelé (non applicable pour activités 2D)
    calories_denivele = 0
    if activity not in ACTIVITES_2D:
        calories_denivele = (denivele_positif / 100) * poids * 0.5
    
    return round(calories_base + calories_denivele, 1)


def _get_intensite_voile(vitesse_moy):
    """Calcule l'intensité pour la voile selon la vitesse."""
    thresholds = [(8, 0.30), (12, 0.40), (15, 0.50), (18, 0.60), (22, 0.70)]
    
    for seuil, intensite in thresholds:
        if vitesse_moy < seuil:
            return intensite
    return 0.85


def _get_intensite_natation(vitesse_moy):
    """Calcule l'intensité pour la natation selon la vitesse."""
    thresholds = [(2.0, 0.50), (2.5, 0.60), (3.0, 0.70), (3.5, 0.80)]
    
    for seuil, intensite in thresholds:
        if vitesse_moy < seuil:
            return intensite
    return 0.90


def _calculate_fc_moyenne(activity, vitesse_moy, denivele_positif, fc_repos, fc_max):
    """
    Calcule la fréquence cardiaque moyenne selon l'activité.
    
    Args:
        activity: Type d'activité
        vitesse_moy: Vitesse moyenne en km/h
        denivele_positif: Dénivelé positif en mètres
        fc_repos: Fréquence cardiaque au repos
        fc_max: Fréquence cardiaque maximale
    
    Returns:
        tuple: (fc_moyenne, intensite)
    """
    if activity == "voile":
        intensite = _get_intensite_voile(vitesse_moy)
        fc_moyenne = fc_repos + (fc_max - fc_repos) * intensite
        
    elif activity == "natation":
        intensite = _get_intensite_natation(vitesse_moy)
        fc_moyenne_base = fc_repos + (fc_max - fc_repos) * intensite
        fc_moyenne = fc_moyenne_base - 13  # Correction spécifique natation
        
    else:
        # Calcul général pour autres activités
        vitesse_factor = min(vitesse_moy / 10, 0.8)
        denivele_factor = min(denivele_positif / 1000 * 0.1, 0.2)
        intensite = min(0.5 + vitesse_factor + denivele_factor, 1.0)
        fc_moyenne = fc_repos + (fc_max - fc_repos) * intensite
    
    return fc_moyenne, intensite


def calculate_fitness_metrics(distance_km, denivele_positif, duree_minutes, config):
    """
    Calcule divers indicateurs de fitness.
    
    Args:
        distance_km: Distance parcourue en km
        denivele_positif: Dénivelé positif en mètres
        duree_minutes: Durée de l'activité en minutes
        config: Configuration utilisateur
    
    Returns:
        dict: Métriques de fitness (vitesse, FC, intensité)
    """
    if not config:
        return None
    
    activity = config.get("activite_defaut", "marche")
    niveau = config.get("niveau", "Intermédiaire")
    
    # Estimation durée si manquante
    if duree_minutes == 0:
        duree_minutes = _estimate_duration(distance_km, denivele_positif, activity, niveau)
    
    # Calcul vitesse moyenne
    vitesse_moy = (distance_km / (duree_minutes / 60)) if duree_minutes > 0 else 0
    
    # Calcul fréquence cardiaque
    fc_max = 220 - config["age"]
    fc_repos = config["fc_repos"]
    fc_moyenne, intensite = _calculate_fc_moyenne(
        activity, vitesse_moy, denivele_positif, fc_repos, fc_max
    )
    
    return {
        "vitesse_moy": round(vitesse_moy, 2),
        "fc_moyenne": round(fc_moyenne),
        "fc_max": fc_max,
        "intensite": round(intensite * 100, 1)
    }