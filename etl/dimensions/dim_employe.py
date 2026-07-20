# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_employe.py
Description     : Alimentation de la dimension Employé (dim_employe) avec hiérarchie organisationnelle.
Source          : staging.employes + staging.agences + staging.regions
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_employe() -> bool:
    """
    Extrait et dénormalise les employés avec leur agence, région et manager direct,
    génère la clé substitut employe_sk et charge dwh.dim_employe.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Employé (dim_employe)...")
    try:
        # Extraction
        df_emp = pd.read_sql_table(table_name="employes", con=engine, schema="staging")
        df_ag = pd.read_sql_table(table_name="agences", con=engine, schema="staging")
        df_reg = pd.read_sql_table(table_name="regions", con=engine, schema="staging")
        
        # 1. Jointure avec les agences
        df_merged = pd.merge(df_emp, df_ag[["id_agence", "nom_agence"]], on="id_agence", how="left")
        
        # 2. Jointure avec les régions
        df_merged = pd.merge(df_merged, df_reg[["id_region", "nom_region"]], on="id_region", how="left")
        
        # 3. Auto-jointure pour obtenir le nom du manager
        df_managers = df_emp[["id_employe", "nom", "prenom"]].copy()
        df_managers["nom_manager"] = df_managers["prenom"] + " " + df_managers["nom"]
        df_merged = pd.merge(df_merged, df_managers[["id_employe", "nom_manager"]], left_on="manager_id", right_on="id_employe", how="left", suffixes=("", "_mgr"))
        
        # Nettoyage des colonnes issues de la jointure
        if "id_employe_mgr" in df_merged.columns:
            df_merged.drop(columns=["id_employe_mgr"], inplace=True)
            
        # Clé substitut
        df_merged.insert(0, "employe_sk", range(1, len(df_merged) + 1))
        
        # Chargement
        df_merged.to_sql(
            name="dim_employe",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_employe alimentée ({len(df_merged)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_employe : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_employe()
    print(f"Alimentation dim_employe : {'RÉUSSI' if success else 'ÉCHEC'}")
