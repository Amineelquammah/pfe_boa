# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_entreprise.py
Description     : Alimentation de la dimension Entreprise (dim_entreprise) enrichie.
Source          : staging.entreprises + staging.souscriptions_digitales
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def get_notation(ca: float) -> str:
    """Attribue une notation interne logique en fonction du CA."""
    if ca >= 100000000.0:
        return "A"
    elif ca >= 20000000.0:
        return "B"
    elif ca >= 2000000.0:
        return "C"
    else:
        return "D"

def get_potentiel(ca: float) -> str:
    """Attribue un potentiel commercial basé sur le CA."""
    if ca >= 50000000.0:
        return "Très Fort"
    elif ca >= 10000000.0:
        return "Fort"
    elif ca >= 2000000.0:
        return "Moyen"
    else:
        return "Faible"

def load_dim_entreprise() -> bool:
    """
    Extrait les entreprises, calcule les variables analytiques (ancienneté,
    notation, potentiel, digitalisation), génère la clé substitut entreprise_sk
    et charge dwh.dim_entreprise.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la dimension Entreprise (dim_entreprise)...")
    try:
        # Extraction
        df_ent = pd.read_sql_table(table_name="entreprises", con=engine, schema="staging")
        
        # Récupération des souscriptions pour calculer le niveau de digitalisation réel
        try:
            df_sub = pd.read_sql_table(table_name="souscriptions_digitales", con=engine, schema="staging")
            # Compter les souscriptions actives par entreprise
            df_sub_active = df_sub[df_sub["statut"] == "ACTIF"]
            sub_counts = df_sub_active.groupby("id_entreprise").size().to_dict()
        except Exception:
            sub_counts = {}
            
        # Transformations
        # 1. Ancienneté (par rapport à 2024)
        df_ent["date_creation_dt"] = pd.to_datetime(df_ent["date_creation"])
        df_ent["anciennete"] = 2024 - df_ent["date_creation_dt"].dt.year
        df_ent.drop(columns=["date_creation_dt"], inplace=True)
        
        # 2. Notation interne et Potentiel commercial
        df_ent["notation_interne"] = df_ent["chiffre_affaires"].apply(get_notation)
        df_ent["potentiel_commercial"] = df_ent["chiffre_affaires"].apply(get_potentiel)
        
        # 3. Niveau de digitalisation
        def get_digital_level(ent_id: int) -> str:
            count = sub_counts.get(ent_id, 0)
            if count >= 4:
                return "Élevé"
            elif count >= 2:
                return "Moyen"
            else:
                return "Faible"
                
        df_ent["niveau_digitalisation"] = df_ent["id_entreprise"].apply(get_digital_level)
        
        # Clé substitut
        df_ent.insert(0, "entreprise_sk", range(1, len(df_ent) + 1))
        
        # Chargement
        df_ent.to_sql(
            name="dim_entreprise",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False
        )
        logger.info(f"Dimension dim_entreprise alimentée ({len(df_ent)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_entreprise : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_entreprise()
    print(f"Alimentation dim_entreprise : {'RÉUSSI' if success else 'ÉCHEC'}")
