# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_compte.py
Description     : Alimentation de la dimension Compte (dim_compte) dans le DWH.
Source          : staging.comptes
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_compte() -> bool:
    """
    Extrait de staging.comptes, génère la clé substitut compte_sk et charge dwh.dim_compte.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Compte (dim_compte)...")
    try:
        # Extraction
        df = pd.read_sql_table(table_name="comptes", con=engine, schema="staging")
        
        # Transformation : Sélectionner les colonnes analytiques
        cols = [
            "id_compte", "numero_compte", "rib", "iban", "type_compte", 
            "devise", "date_ouverture", "statut", "classification", 
            "date_dernier_mouvement", "id_compte_courant_parent"
        ]
        df_dim = df[cols].copy()
        
        # Clé substitut
        df_dim.insert(0, "compte_sk", range(1, len(df_dim) + 1))
        
        # Chargement
        df_dim.to_sql(
            name="dim_compte",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_compte alimentée ({len(df_dim)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_compte : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_compte()
    print(f"Alimentation dim_compte : {'RÉUSSI' if success else 'ÉCHEC'}")
