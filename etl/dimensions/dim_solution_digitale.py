# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_solution_digitale.py
Description     : Alimentation de la dimension Solution Digitale (dim_solution_digitale) dans le DWH.
Source          : staging.solutions_digitales
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_solution_digitale() -> bool:
    """
    Extrait de staging.solutions_digitales, crée la clé substitut solution_digitale_sk
    et charge dwh.dim_solution_digitale.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Solution Digitale (dim_solution_digitale)...")
    try:
        # Extraction
        df = pd.read_sql_table(table_name="solutions_digitales", con=engine, schema="staging")
        
        # Transformation : Clé substitut
        df.insert(0, "solution_digitale_sk", range(1, len(df) + 1))
        
        # Chargement
        df.to_sql(
            name="dim_solution_digitale",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_solution_digitale alimentée ({len(df)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_solution_digitale : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_solution_digitale()
    print(f"Alimentation dim_solution_digitale : {'RÉUSSI' if success else 'ÉCHEC'}")
