def _estimate_duration(distance_km, denivele_positif, activity, niveau="Intermédiaire"):
    """
    Estime la durée en minutes pour une activité sans timestamps
    Tient compte du niveau de l'utilisateur
    """
    # Vitesses de base pour niveau Intermédiaire (km/h)
    vitesse_base_intermediaire = {
        "marche": 5.0,
        "course": 10.0,
        "velo": 23.0,
        "vtt": 15.0,
        "ski": 8.0,
        "randonnee": 4.0
    }
    
    # Coefficients multiplicateurs selon le niveau
    coef_niveau = {
        "Débutant": 0.75,      # 25% plus lent
        "Intermédiaire": 1.0,  # vitesse de référence
        "Avancé": 1.15,        # 15% plus rapide
        "Expert": 1.30         # 30% plus rapide
    }
    
    vitesse_base = vitesse_base_intermediaire.get(activity, 5.0)
    vitesse_ajustee = vitesse_base * coef_niveau.get(niveau, 1.0)
    
    temps_base_heures = distance_km / vitesse_ajustee
    
    # Impact dénivelé : vélo moins affecté que marche/course
    # Les experts gèrent mieux le dénivelé aussi
    coef_base_denivele = 0.25 if activity in ["velo", "vtt"] else 0.17
    coef_denivele_niveau = {
        "Débutant": 1.3,      # 30% plus lent sur D+
        "Intermédiaire": 1.0,
        "Avancé": 0.85,       # 15% plus rapide sur D+
        "Expert": 0.70        # 30% plus rapide sur D+
    }
    
    coef_denivele = coef_base_denivele * coef_denivele_niveau.get(niveau, 1.0)
    temps_denivele_heures = (denivele_positif / 100) * coef_denivele
    
    duree_minutes = (temps_base_heures + temps_denivele_heures) * 60
    print(f"⚠️ Durée estimée ({niveau}) : {duree_minutes:.1f} min ({duree_minutes/60:.2f}h)")
    
    return duree_minutes


def calculate_calories(distance_km, denivele_positif, duree_minutes, config, activity_type=None):
    """
    Calcule les calories brûlées selon la formule MET standard
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
    
    # Valeurs MET selon activité et vitesse
    met_base = {
        "marche": 3.5, "course": 9.0, "velo": 7.5,
        "vtt": 8.5, "ski": 7.0, "randonnee": 6.0
    }
    
    # Ajustement MET selon vitesse réelle
    if activity == "marche":
        met = 2.5 if vitesse_kmh < 4 else 3.5 if vitesse_kmh < 5 else 4.3 if vitesse_kmh < 6 else 5.0
    elif activity == "course":
        met = 8.0 if vitesse_kmh < 8 else 9.0 if vitesse_kmh < 10 else 11.0 if vitesse_kmh < 12 else 12.5
    elif activity == "randonnee":
        met = 7.3 if denivele_positif > 500 else 6.0
    else:
        met = met_base.get(activity, 5.0)
    
    # Calcul calories : base MET + bonus dénivelé
    calories_base = met * poids * duree_heures
    calories_denivele = (denivele_positif / 100) * poids * 0.5
    
    return round(calories_base + calories_denivele, 1)


def calculate_fitness_metrics(distance_km, denivele_positif, duree_minutes, config):
    """
    Calcule divers indicateurs de fitness
    """
    if not config:
        return None
    
    activity = config.get("activite_defaut", "marche")
    niveau = config.get("niveau", "Intermédiaire")
    
    # Estimation durée si manquante
    if duree_minutes == 0:
        duree_minutes = _estimate_duration(distance_km, denivele_positif, activity, niveau)
    
    # Calculs métriques
    vitesse_moy = (distance_km / (duree_minutes / 60)) if duree_minutes > 0 else 0
    
    fc_max = 220 - config["age"]
    fc_repos = config["fc_repos"]
    
    # Estimation intensité : vitesse + dénivelé
    vitesse_factor = min(vitesse_moy / 10, 0.8)
    denivele_factor = min(denivele_positif / 1000 * 0.1, 0.2)
    intensite = min(0.5 + vitesse_factor + denivele_factor, 1.0)
    
    fc_moyenne = fc_repos + (fc_max - fc_repos) * intensite
    
    return {
        "vitesse_moy": round(vitesse_moy, 2),
        "fc_moyenne": round(fc_moyenne),
        "fc_max": fc_max,
        "intensite": round(intensite * 100, 1)
    }