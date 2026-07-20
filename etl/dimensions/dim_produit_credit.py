# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_produit_credit.py
Description     : Alimentation de la dimension Produit Crédit (dim_produit_credit) dénormalisée.
Source          : staging.produits_credits + staging.programmes_credits + staging.familles_credits
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_produit_credit() -> bool:
    """
    Extrait et dénormalise le catalogue des crédits, crée la clé substitut produit_credit_sk
    et charge dwh.dim_produit_credit.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Produit Crédit (dim_produit_credit)...")
    try:
        # Extraction
        df_prod = pd.read_sql_table(table_name="produits_credits", con=engine, schema="staging")
        df_prog = pd.read_sql_table(table_name="programmes_credits", con=engine, schema="staging")
        df_fam = pd.read_sql_table(table_name="familles_credits", con=engine, schema="staging")
        
        # Jointures
        df_merged = pd.merge(df_prod, df_prog[["id_programme", "nom_programme", "id_famille"]], on="id_programme", how="inner")
        df_merged = pd.merge(df_merged, df_fam[["id_famille", "nom_famille"]], on="id_famille", how="inner")
        
        # Sélection des colonnes analytiques
        cols = [
            "id_produit", "code_produit", "nom_produit", "description", 
            "duree_min", "duree_max", "taux_min", "taux_max", 
            "montant_min", "montant_max", "devise", "statut", 
            "nom_programme", "nom_famille"
        ]
        df_dim = df_merged[cols].copy()
        
        # Clé substitut
        df_dim.insert(0, "produit_credit_sk", range(1, len(df_dim) + 1))
        
        # Chargement
        df_dim.to_sql(
            name="dim_produit_credit",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_produit_credit alimentée ({len(df_dim)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_produit_credit : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_produit_credit()
    print(f"Alimentation dim_produit_credit : {'RÉUSSI' if success else 'ÉCHEC'}")
