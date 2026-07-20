# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_agence.py
Description     : Alimentation de la dimension Agence (dim_agence) dénormalisée.
Source          : staging.agences + staging.regions
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_agence() -> bool:
    """
    Extrait et dénormalise les agences avec leur région, génère la clé substitut agence_sk
    et charge dwh.dim_agence.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Agence (dim_agence)...")
    try:
        # Extraction
        df_ag = pd.read_sql_table(table_name="agences", con=engine, schema="staging")
        df_reg = pd.read_sql_table(table_name="regions", con=engine, schema="staging")
        
        # Transformation : Jointure
        df_merged = pd.merge(df_ag, df_reg, on="id_region", how="inner")
        
        # Sélection des colonnes utiles
        cols = [
            "id_agence", "code_agence", "nom_agence", "ville", 
            "adresse", "date_ouverture", "statut", "id_region", "nom_region"
        ]
        df_dim = df_merged[cols].copy()
        
        # Clé substitut
        df_dim.insert(0, "agence_sk", range(1, len(df_dim) + 1))
        
        # Chargement
        df_dim.to_sql(
            name="dim_agence",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_agence alimentée ({len(df_dim)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_agence : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_agence()
    print(f"Alimentation dim_agence : {'RÉUSSI' if success else 'ÉCHEC'}")
