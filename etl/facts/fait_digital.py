# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/facts/fait_digital.py
Description     : Alimentation de la table de faits fait_digital (Unitaire).
Granularité     : Une connexion digitale unitaire.
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_fait_digital() -> bool:
    """
    Extrait les connexions de staging, associe les surrogate keys (SK)
    et charge dwh.fait_digital.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la table de faits fait_digital...")
    try:
        # 1. Extraction
        df_conn = pd.read_sql_table(table_name="connexions_digitales", con=engine, schema="staging")
        df_cpt = pd.read_sql_table(table_name="comptes", con=engine, schema="staging")
        
        # Charger les dimensions
        dim_ent = pd.read_sql_table(table_name="dim_entreprise", con=engine, schema="dwh")
        dim_sol = pd.read_sql_table(table_name="dim_solution_digitale", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table(table_name="dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table(table_name="dim_region", con=engine, schema="dwh")
        
        # 2. Transformations
        # temps_sk = YYYYMMDD
        df_conn["temps_sk"] = pd.to_datetime(df_conn["date_connexion"]).dt.strftime("%Y%m%d").astype(int)
        
        # Mesures
        df_conn["nombre_connexions"] = 1
        df_conn["nombre_operations"] = df_conn["statut"].apply(lambda s: 1 if s == "SUCCES" else 0)
        df_conn["indicateur_utilisateur_actif"] = 1
        
        # 3. Récupération des Surrogate Keys
        # Obtenir la relation entreprise -> agence depuis staging.comptes
        df_ent_ag = df_cpt[["id_entreprise", "id_agence"]].drop_duplicates()
        
        # Fusionner pour obtenir id_agence
        df_fact = pd.merge(df_conn, df_ent_ag, on="id_entreprise", how="inner")
        
        # Associer les Surrogate Keys des dimensions
        df_fact = pd.merge(df_fact, dim_ent[["id_entreprise", "entreprise_sk"]], on="id_entreprise", how="inner")
        df_fact = pd.merge(df_fact, dim_sol[["id_solution", "solution_digitale_sk"]], on="id_solution", how="inner")
        df_fact = pd.merge(df_fact, dim_ag[["id_agence", "agence_sk", "id_region"]], on="id_agence", how="inner")
        df_fact = pd.merge(df_fact, dim_reg[["id_region", "region_sk"]], on="id_region", how="inner")
        
        # Sélection des colonnes de fait
        final_cols = [
            "temps_sk", "entreprise_sk", "solution_digitale_sk", "agence_sk", "region_sk",
            "nombre_connexions", "duree_session", "nombre_operations", "indicateur_utilisateur_actif"
        ]
        df_final = df_fact[final_cols].copy()
        
        # Chargement (chunksize=2000 pour pg8000)
        df_final.to_sql(
            name="fait_digital",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False,
            chunksize=2000,
            method="multi"
        )
        logger.info(f"Table de faits fait_digital alimentée ({len(df_final)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur fait_digital : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur fait_digital : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_fait_digital()
    print(f"Alimentation fait_digital : {'RÉUSSI' if success else 'ÉCHEC'}")