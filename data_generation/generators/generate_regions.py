# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_regions.py
Description     : Générateur de données pour les régions administratives BOA.
"""

import pandas as pd
from data_generation.utils.logger import logger
from data_generation.utils.faker_utils import get_regions

def generate_regions() -> pd.DataFrame:
    """
    Génère le référentiel des 7 régions administratives sous forme de DataFrame Pandas.
    
    Returns:
        pd.DataFrame: DataFrame contenant les colonnes 'id_region' et 'nom_region'.
    """
    logger.info("Début de la génération des régions...")
    
    # Récupération de la liste des 7 régions depuis les utilitaires
    regions_list = get_regions()
    
    # Création du DataFrame avec un identifiant séquentiel de 1 à 7
    data = {
        "id_region": range(1, len(regions_list) + 1),
        "nom_region": regions_list
    }
    
    df_regions = pd.DataFrame(data)
    
    logger.info(f"Génération terminée : {len(df_regions)} régions générées.")
    return df_regions

if __name__ == "__main__":
    # Test indépendant du module de génération
    df = generate_regions()
    print("\n--- TEST GENERATE REGIONS ---")
    print(df)
