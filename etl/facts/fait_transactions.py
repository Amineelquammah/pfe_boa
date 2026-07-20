# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/facts/fait_transactions.py
Description     : Alimentation de la table de faits fait_transactions (Unitaire).
Granularité     : Une transaction unitaire.
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_fait_transactions() -> bool:
    """
    Extrait les transactions unitaires, associe les surrogate keys (SK)
    et charge dwh.fait_transactions.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la table de faits fait_transactions...")
    try:
        # 1. Extraction
        df_tx = pd.read_sql_table(table_name="transactions", con=engine, schema="staging")
        df_cpt = pd.read_sql_table(table_name="comptes", con=engine, schema="staging")
        
        # Charger les dimensions
        dim_compte = pd.read_sql_table(table_name="dim_compte", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table(table_name="dim_entreprise", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table(table_name="dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table(table_name="dim_region", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table(table_name="dim_employe", con=engine, schema="dwh")
        
        # 2. Transformations
        # temps_sk = YYYYMMDD
        df_tx["temps_sk"] = pd.to_datetime(df_tx["date_transaction"]).dt.strftime("%Y%m%d").astype(int)
        
        # Débit / Crédit
        df_tx["debit"] = df_tx.apply(lambda r: float(r["montant"]) if r["sens"] == "DEBIT" else 0.0, axis=1)
        df_tx["credit"] = df_tx.apply(lambda r: float(r["montant"]) if r["sens"] == "CREDIT" else 0.0, axis=1)
        df_tx["nombre_transactions"] = 1
        
        # 3. Récupération des Surrogate Keys
        df_cpt_meta = df_cpt[["id_compte", "id_entreprise", "id_agence", "id_conseiller"]]
        
        # Supprimer les colonnes en double dans df_tx pour éviter les conflits _x / _y
        df_tx_clean = df_tx.drop(columns=["id_entreprise", "id_agence", "id_conseiller"], errors="ignore")
        
        df_fact = pd.merge(df_tx_clean, dim_compte[["id_compte", "compte_sk"]], on="id_compte", how="inner")
        df_fact = pd.merge(df_fact, df_cpt_meta, on="id_compte", how="inner")
        df_fact = pd.merge(df_fact, dim_ent[["id_entreprise", "entreprise_sk"]], on="id_entreprise", how="inner")
        df_fact = pd.merge(df_fact, dim_ag[["id_agence", "agence_sk", "id_region"]], on="id_agence", how="inner")
        df_fact = pd.merge(df_fact, dim_reg[["id_region", "region_sk"]], on="id_region", how="inner")
        df_fact = pd.merge(df_fact, dim_emp[["id_employe", "employe_sk"]], left_on="id_conseiller", right_on="id_employe", how="inner")
        
        # Sélection des colonnes finales
        final_cols = [
            "temps_sk", "compte_sk", "entreprise_sk", "agence_sk", "region_sk", "employe_sk",
            "montant", "nombre_transactions", "debit", "credit"
        ]
        df_final = df_fact[final_cols].copy()
        
        # Chargement bulk
        df_final.to_sql(
            name="fait_transactions",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False,
            chunksize=2000,
            method="multi"
        )
        logger.info(f"Table de faits fait_transactions alimentée ({len(df_final)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur fait_transactions : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur fait_transactions : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_fait_transactions()
    print(f"Alimentation fait_transactions : {'RÉUSSI' if success else 'ÉCHEC'}")
