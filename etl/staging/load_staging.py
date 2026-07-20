# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/staging/load_staging.py
Description     : Phase 1 de l'ETL : extraction de l'OLTP, nettoyage simple et chargement dans STAGING.
"""

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique les nettoyages autorisés en staging :
    - Nettoyage des espaces blancs dans les chaînes.
    - Suppression des doublons de lignes complets.
    """
    # Nettoyage des espaces blancs pour les colonnes de type texte
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()
        
    # Suppression des doublons
    initial_len = len(df)
    df = df.drop_duplicates()
    final_len = len(df)
    
    if initial_len != final_len:
        logger.info(f"Nettoyage : {initial_len - final_len} doublon(s) supprimé(s).")
        
    return df

def load_staging() -> bool:
    """
    Copie toutes les tables du schéma 'oltp' vers le schéma 'staging'
    après application de nettoyages simples et normalisations.
    
    Returns:
        bool: True si la phase s'est déroulée avec succès.
    """
    logger.info("=========================================")
    logger.info("DÉBUT PHASE ETL 1 : CHARGEMENT DU STAGING")
    logger.info("=========================================")
    
    tables = [
        "regions",
        "agences",
        "employes",
        "entreprises",
        "comptes",
        "familles_credits",
        "programmes_credits",
        "produits_credits",
        "contrats_credits",
        "garanties",
        "transactions",
        "solutions_digitales",
        "souscriptions_digitales",
        "connexions_digitales"
    ]
    
    try:
        for table in tables:
            logger.info(f"Extraction de la table oltp.{table}...")
            
            # 1. Extraction depuis l'OLTP
            df = pd.read_sql_table(table_name=table, con=engine, schema="oltp")
            
            # 2. Nettoyage simple (espaces, doublons)
            df_cleaned = clean_dataframe(df)
            
            # 3. Chargement dans le schéma staging (remplacement systématique)
            logger.info(f"Chargement dans la table staging.{table}...")
            df_cleaned.to_sql(
                name=table,
                con=engine,
                schema="staging",
                if_exists="replace",
                index=False,
                chunksize=2000,
                method="multi"
            )
            logger.info(f"Table staging.{table} alimentée ({len(df_cleaned)} lignes).")
            
        logger.info("Phase 1 (Staging) terminée avec succès.")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL lors du chargement de la phase Staging : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue durant la phase Staging : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_staging()
    print(f"Chargement staging : {'RÉUSSI' if success else 'ÉCHEC'}")
