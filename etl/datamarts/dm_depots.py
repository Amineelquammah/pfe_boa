# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/datamarts/dm_depots.py
Description     : Alimentation du Data Mart DM_Depots pour les analyses Power BI de dépôts.
Source          : dwh.fait_depots + dimensions DWH
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dm_depots() -> bool:
    """
    Extrait du DWH, agrège par trimestre, région, agence, conseiller, segment,
    secteur et charge dans datamarts.dm_depots.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation du Data Mart DM_Depots...")
    try:
        # Extraction des faits et dimensions nécessaires
        df_fact = pd.read_sql_table("fait_depots", con=engine, schema="dwh")
        dim_temps = pd.read_sql_table("dim_temps", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table("dim_entreprise", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table("dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table("dim_region", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table("dim_employe", con=engine, schema="dwh")
        
        # Jointures
        df_merged = pd.merge(df_fact, dim_temps[["temps_sk", "annee", "nom_trimestre"]], on="temps_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ent[["entreprise_sk", "segment", "secteur_activite", "raison_sociale", "ice", "ville", "notation_interne", "potentiel_commercial", "niveau_digitalisation"]], on="entreprise_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ag[["agence_sk", "nom_agence"]], on="agence_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_reg[["region_sk", "nom_region"]], on="region_sk", how="inner")
        
        # Le nom du conseiller de l'employé
        dim_emp["nom_conseiller"] = dim_emp["prenom"] + " " + dim_emp["nom"]
        df_merged = pd.merge(df_merged, dim_emp[["employe_sk", "nom_conseiller"]], on="employe_sk", how="inner")
        
        # Agrégation
        group_cols = ["annee", "nom_trimestre", "nom_region", "nom_agence", "nom_conseiller", "segment", "secteur_activite", "raison_sociale", "ice", "ville", "notation_interne", "potentiel_commercial", "niveau_digitalisation"]
        
        df_dm = df_merged.groupby(group_cols).agg(
            encours_total=("encours", "sum"),
            solde_moyen_total=("solde_moyen_trimestriel", "sum"),
            collecte_nette_totale=("collecte_nette", "sum"),
            versements_total=("montant_versements", "sum"),
            retraits_total=("montant_retraits", "sum"),
            nombre_comptes_actifs=("nombre_comptes_actifs", "sum"),
            nombre_transactions=("nombre_transactions", "sum")
        ).reset_index()
        
        # Arrondir les montants
        float_cols = ["encours_total", "solde_moyen_total", "collecte_nette_totale", "versements_total", "retraits_total"]
        df_dm[float_cols] = df_dm[float_cols].round(2)
        
        # Chargement
        df_dm.to_sql(
            name="dm_depots",
            con=engine,
            schema="datamarts",
            if_exists="replace",
            index=False
        )
        logger.info(f"Data Mart dm_depots alimenté ({len(df_dm)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dm_depots : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur dm_depots : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dm_depots()
    print(f"Alimentation dm_depots : {'RÉUSSI' if success else 'ÉCHEC'}")
