from os import getcwd
from json import load
import os.path

RESSOURCES_FOLDER = os.path.join(getcwd, "ressources")


def get_user_config(config_name="user_profile"):
    """Fonction utilitaire pour récupérer la configuration utilisateur"""
    CONFIG_FILE = RESSOURCES_FOLDER + f'/{config_name}.json'
    if not os.path.exists(CONFIG_FILE):
        return None
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return load(f)
    except:
        return None