# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step04_load_database.py
Description     : Étape 4 du pipeline : insertion des données dans la base PostgreSQL.
"""

from typing import Dict
import pandas as pd
from data_generation.utils.logger import logger
from data_generation.loaders.loader import load_data_to_postgres

def run_load_database(data_dict: Dict[str, pd.DataFrame]) -> bool:
    """
    Exécute le chargeur SQL pour insérer toutes les données dans PostgreSQL.
    
    Args:
        data_dict (Dict[str, pd.DataFrame]): Dictionnaire des DataFrames.
        
    Returns:
        bool: True si le chargement s'est déroulé sans erreur.
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 4 : CHARGEMENT POSTGRESQL")
    logger.info("=========================================")
    
    try:
        success = load_data_to_postgres(data_dict)
        if success:
            logger.info("Étape 4 terminée avec succès.")
            return True
        return False
    except Exception as e:
        logger.error(f"Échec critique à l'étape 4 (Chargement base) : {str(e)}")
        return False
