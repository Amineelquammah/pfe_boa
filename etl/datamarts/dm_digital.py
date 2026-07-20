# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/datamarts/dm_digital.py
Description     : Alimentation du Data Mart DM_Digital pour les analyses d'adoption digitale.
Source          : dwh.fait_digital + dimensions DWH
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dm_digital() -> bool:
    """
    Extrait du DWH, agrège par trimestre, région, agence, solution, segment
    et charge dans datamarts.dm_digital.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation du Data Mart DM_Digital...")
    try:
        # Extraction des faits et dimensions nécessaires
        df_fact = pd.read_sql_table("fait_digital", con=engine, schema="dwh")
        dim_temps = pd.read_sql_table("dim_temps", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table("dim_entreprise", con=engine, schema="dwh")
        dim_sol = pd.read_sql_table("dim_solution_digitale", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table("dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table("dim_region", con=engine, schema="dwh")
        
        # Jointures
        df_merged = pd.merge(df_fact, dim_temps[["temps_sk", "annee", "nom_trimestre"]], on="temps_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ent[["entreprise_sk", "segment", "raison_sociale", "ice", "ville", "secteur_activite", "niveau_digitalisation", "potentiel_commercial"]], on="entreprise_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_sol[["solution_digitale_sk", "nom_solution"]], on="solution_digitale_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ag[["agence_sk", "nom_agence"]], on="agence_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_reg[["region_sk", "nom_region"]], on="region_sk", how="inner")
        
        # Agrégation
        group_cols = ["annee", "nom_trimestre", "nom_region", "nom_agence", "nom_solution", "segment", "raison_sociale", "ice", "ville", "secteur_activite", "niveau_digitalisation", "potentiel_commercial"]
        
        df_dm = df_merged.groupby(group_cols).agg(
            nombre_connexions=("nombre_connexions", "sum"),
            duree_session_moyenne=("duree_session", "mean"),
            nombre_operations_total=("nombre_operations", "sum"),
            utilisateurs_actifs_total=("indicateur_utilisateur_actif", "sum")
        ).reset_index()
        
        # Arrondir la durée moyenne
        df_dm["duree_session_moyenne"] = df_dm["duree_session_moyenne"].round(1)
        
        # Chargement
        df_dm.to_sql(
            name="dm_digital",
            con=engine,
            schema="datamarts",
            if_exists="replace",
            index=False
        )
        logger.info(f"Data Mart dm_digital alimenté ({len(df_dm)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dm_digital : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur dm_digital : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dm_digital()
    print(f"Alimentation dm_digital : {'RÉUSSI' if success else 'ÉCHEC'}")
