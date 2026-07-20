# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/datamarts/dm_credits.py
Description     : Alimentation du Data Mart DM_Credits pour les analyses Power BI de crédits.
Source          : dwh.fait_credits + dimensions DWH
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dm_credits() -> bool:
    """
    Extrait du DWH, agrège par trimestre, région, agence, conseiller, produit, segment,
    et charge dans datamarts.dm_credits.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation du Data Mart DM_Credits...")
    try:
        # Extraction des faits et dimensions nécessaires
        df_fact = pd.read_sql_table("fait_credits", con=engine, schema="dwh")
        dim_temps = pd.read_sql_table("dim_temps", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table("dim_entreprise", con=engine, schema="dwh")
        dim_prod = pd.read_sql_table("dim_produit_credit", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table("dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table("dim_region", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table("dim_employe", con=engine, schema="dwh")
        
        # Jointures
        df_merged = pd.merge(df_fact, dim_temps[["temps_sk", "annee", "nom_trimestre"]], on="temps_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ent[["entreprise_sk", "segment", "secteur_activite", "raison_sociale", "ice", "ville", "notation_interne", "potentiel_commercial", "niveau_digitalisation"]], on="entreprise_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_prod[["produit_credit_sk", "nom_produit", "nom_programme", "nom_famille"]], on="produit_credit_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_ag[["agence_sk", "nom_agence"]], on="agence_sk", how="inner")
        df_merged = pd.merge(df_merged, dim_reg[["region_sk", "nom_region"]], on="region_sk", how="inner")
        
        dim_emp["nom_conseiller"] = dim_emp["prenom"] + " " + dim_emp["nom"]
        df_merged = pd.merge(df_merged, dim_emp[["employe_sk", "nom_conseiller"]], on="employe_sk", how="inner")
        
        # Agrégation
        group_cols = [
            "annee", "nom_trimestre", "nom_region", "nom_agence", "nom_conseiller", 
            "nom_produit", "nom_programme", "nom_famille", "segment", "secteur_activite",
            "raison_sociale", "ice", "ville", "notation_interne", "potentiel_commercial", "niveau_digitalisation"
        ]
        
        df_dm = df_merged.groupby(group_cols).agg(
            montant_octroye_total=("montant_octroye", "sum"),
            encours_total=("encours_restant", "sum"),
            capital_rembourse_total=("capital_rembourse", "sum"),
            interets_payes_total=("interets_payes", "sum"),
            mensualite_totale=("mensualite", "sum"),
            nombre_credits=("montant_octroye", "size"),
            jours_retard_max=("jours_retard", "max"),
            nombre_credits_npl=("indicateur_NPL", "sum"),
            taux_interet_moyen=("taux_interet", "mean")
        ).reset_index()
        
        # Arrondir les valeurs
        float_cols = [
            "montant_octroye_total", "encours_total", "capital_rembourse_total", 
            "interets_payes_total", "mensualite_totale", "taux_interet_moyen"
        ]
        df_dm[float_cols] = df_dm[float_cols].round(2)
        
        # Chargement
        df_dm.to_sql(
            name="dm_credits",
            con=engine,
            schema="datamarts",
            if_exists="replace",
            index=False
        )
        logger.info(f"Data Mart dm_credits alimenté ({len(df_dm)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dm_credits : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur dm_credits : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dm_credits()
    print(f"Alimentation dm_credits : {'RÉUSSI' if success else 'ÉCHEC'}")
