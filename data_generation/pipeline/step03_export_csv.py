# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step03_export_csv.py
Description     : Étape 3 du pipeline : sauvegarde des DataFrames en fichiers CSV.
"""

import os
from typing import Dict
import pandas as pd
from data_generation.utils.logger import logger
from data_generation.config.config import BASE_DIR

def run_export_csv(data_dict: Dict[str, pd.DataFrame]) -> bool:
    """
    Exporte l'ensemble des DataFrames du dictionnaire sous forme de fichiers CSV dans data/generated/.
    
    Args:
        data_dict (Dict[str, pd.DataFrame]): Dictionnaire des DataFrames.
        
    Returns:
        bool: True si l'export s'est terminé sans erreur.
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 3 : EXPORT DES FICHIERS CSV")
    logger.info("=========================================")
    
    # Création du dossier cible s'il n'existe pas
    export_dir = BASE_DIR / "data" / "generated"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        for key, df in data_dict.items():
            file_path = export_dir / f"{key}.csv"
            
            # Sauvegarde au format CSV avec encodage UTF-8 et séparateur virgule
            df.to_csv(file_path, index=False, encoding="utf-8")
            logger.info(f"Fichier exporté avec succès : {file_path} ({len(df)} lignes).")
            
        logger.info("Étape 3 terminée avec succès.")
        return True
    except Exception as e:
        logger.error(f"Échec de l'export des fichiers CSV : {str(e)}")
        return False
