# Émissions de CO2 en grammes par kilomètre par personne
# Sources : ADEME Base Carbone, notre-environnement.gouv.fr, SNCF (2024)
EMISSIONS_CO2_G_KM = {
    "voiture": 218,      # Voiture thermique moyenne (notre-environnement.gouv.fr)
    "voiture_elec": 103, # Voiture électrique incluant fabrication (ADEME)
    "bus": 113,          # Bus urbain thermique (notre-environnement.gouv.fr)
    "car": 29,           # Autocar longue distance (ADEME)
    "train": 24,         # Train régional (TER moyenne SNCF)
    "tgv": 2.4,          # TGV (SNCF 2024)
    "metro": 4,          # Métro
    "tramway": 5,        # Tramway
    "moto": 113,         # Moto moyenne
    "scooter": 72,       # Scooter 50-125cc
    "avion_court": 230,  # Avion court-courrier (<1000km) avec traînées
    "avion_moyen": 178,  # Avion moyen-courrier (1000-3500km) avec traînées
    "avion_long": 152,   # Avion long-courrier (>3500km) avec traînées
}

# Équivalences en arbres et en voitures
KG_CO2_PAR_ARBRE_AN = 25  # kg de CO2 absorbés par un arbre mature par an
KM_VOITURE_MOYEN_AN = 13000  # km moyens parcourus par an en voiture


def calculate_co2_saved(distance_km):
    """
    Calcule le CO2 économisé par rapport à différents modes de transport.
    
    Args:
        distance_km: Distance parcourue en km
    
    Returns:
        dict: CO2 économisé pour chaque mode de transport avec équivalences
    """
    if distance_km <= 0:
        return None
    
    results = {}
    total_max_co2 = 0
    
    # Calcul pour chaque mode de transport
    for mode, emission_g_km in EMISSIONS_CO2_G_KM.items():
        co2_g = distance_km * emission_g_km
        co2_kg = co2_g / 1000
        
        results[mode] = {
            "co2_grammes": round(co2_g, 1),
            "co2_kg": round(co2_kg, 3),
            "nom_francais": _get_transport_name(mode)
        }
        
        total_max_co2 = max(total_max_co2, co2_kg)
    
    # Ajout des équivalences pour la comparaison la plus impactante (voiture)
    co2_voiture_kg = results["voiture"]["co2_kg"]
    
    equivalences = {
        "arbres_jours": round(co2_voiture_kg / (KG_CO2_PAR_ARBRE_AN / 365), 1),
        "arbres_mois": round(co2_voiture_kg / (KG_CO2_PAR_ARBRE_AN / 12), 2),
        "pct_voiture_annuel": round((co2_voiture_kg / (EMISSIONS_CO2_G_KM["voiture"] * KM_VOITURE_MOYEN_AN / 1000)) * 100, 2)
    }
    
    return {
        "transports": results,
        "equivalences": equivalences,
        "distance_km": distance_km
    }


def _get_transport_name(mode):
    """Retourne le nom français du mode de transport."""
    names = {
        "voiture": "Voiture thermique",
        "voiture_elec": "Voiture électrique",
        "bus": "Bus",
        "car": "Autocar",
        "train": "Train régional",
        "tgv": "TGV",
        "metro": "Métro",
        "tramway": "Tramway",
        "moto": "Moto",
        "scooter": "Scooter",
        "avion_court": "Avion court-courrier",
        "avion_moyen": "Avion moyen-courrier",
        "avion_long": "Avion long-courrier"
    }
    return names.get(mode, mode)


def get_co2_summary_text(co2_data, format="court"):
    """
    Génère un texte résumant les économies de CO2.
    
    Args:
        co2_data: Données retournées par calculate_co2_saved
        format: "court" ou "detaille"
    
    Returns:
        str: Texte formaté
    """
    if not co2_data:
        return ""
    
    transports = co2_data["transports"]
    equiv = co2_data["equivalences"]
    distance = co2_data["distance_km"]
    
    if format == "court":
        co2_voiture = transports["voiture"]["co2_kg"]
        return (
            f"En parcourant {distance:.1f} km à pied/vélo, vous avez économisé "
            f"{co2_voiture:.2f} kg de CO2 par rapport à la voiture "
            f"(équivalent à {equiv['arbres_jours']:.1f} jour(s) d'absorption d'un arbre)."
        )
    
    # Format détaillé
    lines = [
        f"Impact environnemental pour {distance:.1f} km :",
        "",
        "CO2 économisé par rapport à :"
    ]
    
    # Top 5 des transports les plus polluants
    sorted_transports = sorted(
        transports.items(),
        key=lambda x: x[1]["co2_kg"],
        reverse=True
    )[:5]
    
    for mode, data in sorted_transports:
        lines.append(f"  • {data['nom_francais']}: {data['co2_kg']:.2f} kg CO2")
    
    lines.extend([
        "",
        "Équivalences :",
        f"  • {equiv['arbres_jours']:.1f} jour(s) d'absorption d'un arbre mature",
        f"  • {equiv['pct_voiture_annuel']:.2f}% du trajet annuel moyen en voiture"
    ])
    
    return "\n".join(lines)


def format_co2_for_export(co2_data, export_format="json"):
    """
    Formate les données CO2 pour l'export JSON ou CSV.
    
    Args:
        co2_data: Données retournées par calculate_co2_saved
        export_format: "json" ou "csv"
    
    Returns:
        dict ou str: Données formatées selon le format demandé
    """
    if not co2_data:
        return None
    
    if export_format == "json":
        return {
            "distance_km": co2_data["distance_km"],
            "co2_saved": {
                mode: {
                    "transport": data["nom_francais"],
                    "co2_kg": data["co2_kg"],
                    "co2_grammes": data["co2_grammes"]
                }
                for mode, data in co2_data["transports"].items()
            },
            "equivalences": {
                "trees_absorption_days": co2_data["equivalences"]["arbres_jours"],
                "trees_absorption_months": co2_data["equivalences"]["arbres_mois"],
                "percent_annual_car_usage": co2_data["equivalences"]["pct_voiture_annuel"]
            }
        }
    
    # Format CSV - retourne les valeurs principales
    return {
        "CO2 économisé voiture (kg)": f"{co2_data['transports']['voiture']['co2_kg']:.2f}",
        "CO2 économisé bus (kg)": f"{co2_data['transports']['bus']['co2_kg']:.2f}",
        "CO2 économisé train (kg)": f"{co2_data['transports']['train']['co2_kg']:.2f}",
        "Équiv. arbres (jours)": f"{co2_data['equivalences']['arbres_jours']:.1f}"
    }