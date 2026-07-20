# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step01_generate.py
Description     : Étape 1 du pipeline : exécution séquentielle de la génération de données.
"""

from typing import Dict
import pandas as pd
from data_generation.utils.logger import logger

from data_generation.generators.generate_regions import generate_regions
from data_generation.generators.generate_agences import generate_agences
from data_generation.generators.generate_employes import generate_employes
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_comptes import generate_comptes
from data_generation.generators.generate_catalogue_credits import generate_catalogue_credits
from data_generation.generators.generate_contrats_credits import generate_contrats_credits
from data_generation.generators.generate_garanties import generate_garanties
from data_generation.generators.generate_transactions import generate_transactions
from data_generation.generators.generate_solutions_digitales import generate_solutions_digitales
from data_generation.generators.generate_souscriptions import generate_souscriptions
from data_generation.generators.generate_connexions import generate_connexions

def run_generate() -> Dict[str, pd.DataFrame]:
    """
    Exécute tous les générateurs dans le bon ordre et retourne les DataFrames.
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionnaire indexé par le nom technique de la table.
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 1 : GÉNÉRATION DES DATAFRAMES")
    logger.info("=========================================")
    
    data = {}
    
    # 1. Organisation
    data["regions"] = generate_regions()
    data["agences"] = generate_agences()
    data["employes"] = generate_employes()
    
    # 2. Entreprises
    data["entreprises"] = generate_entreprises()
    
    # 3. Comptes (temporaires)
    df_comptes_temp = generate_comptes()
    
    # 4. Catalogue crédits
    df_fam, df_prog, df_prod = generate_catalogue_credits()
    data["familles_credits"] = df_fam
    data["programmes_credits"] = df_prog
    data["produits_credits"] = df_prod
    
    # 5. Contrats crédits
    data["contrats_credits"] = generate_contrats_credits()
    
    # 6. Garanties
    data["garanties"] = generate_garanties()
    
    # 7. Transactions et ajustement des comptes finaux
    df_txns, df_comptes_final = generate_transactions(df_comptes_temp)
    data["transactions"] = df_txns
    data["comptes"] = df_comptes_final
    
    # 8. Digital Banking
    data["solutions_digitales"] = generate_solutions_digitales()
    data["souscriptions_digitales"] = generate_souscriptions()
    data["connexions_digitales"] = generate_connexions()
    
    logger.info("Étape 1 terminée avec succès.")
    return data

if __name__ == "__main__":
    res = run_generate()
    print({k: len(v) for k, v in res.items()})
