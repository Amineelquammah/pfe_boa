# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_region.py
Description     : Alimentation de la dimension Région (dim_region) dans le DWH.
Source          : staging.regions
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_region() -> bool:
    """
    Extrait de staging.regions, crée la clé substitut region_sk et charge dans dwh.dim_region.
    
    Returns:
        bool: True si alimentation réussie.
    """
    logger.info("Début de l'alimentation de la dimension Région (dim_region)...")
    try:
        # Extraction
        df = pd.read_sql_table(table_name="regions", con=engine, schema="staging")
        
        # Transformation : Clé substitut
        df.insert(0, "region_sk", range(1, len(df) + 1))
        
        # Chargement
        df.to_sql(
            name="dim_region",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_region alimentée ({len(df)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_region : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_region()
    print(f"Alimentation dim_region : {'RÉUSSI' if success else 'ÉCHEC'}")
