# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step02_validate.py
Description     : Étape 2 du pipeline : exécution des règles métiers et validations.
"""

from typing import Dict, Tuple
import pandas as pd
from data_generation.utils.logger import logger

from data_generation.validators.validate_regions import validate_regions
from data_generation.validators.validate_agences import validate_agences
from data_generation.validators.validate_employes import validate_employes
from data_generation.validators.validate_entreprises import validate_entreprises
from data_generation.validators.validate_comptes import validate_comptes
from data_generation.validators.validate_catalogue_credits import validate_catalogue_credits
from data_generation.validators.validate_contrats_credits import validate_contrats_credits
from data_generation.validators.validate_garanties import validate_garanties
from data_generation.validators.validate_transactions import validate_transactions
from data_generation.validators.validate_solutions_digitales import validate_solutions_digitales
from data_generation.validators.validate_souscriptions import validate_souscriptions
from data_generation.validators.validate_connexions import validate_connexions

def run_validate(data_dict: Dict[str, pd.DataFrame]) -> Tuple[bool, Dict[str, bool]]:
    """
    Exécute l'ensemble des modules de validation métiers et structurelles sur les DataFrames.
    
    Args:
        data_dict (Dict[str, pd.DataFrame]): Dictionnaire des DataFrames générés.
        
    Returns:
        Tuple[bool, Dict[str, bool]]: (Statut global de validation, détail par table).
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 2 : VALIDATIONS DES REGLES METIERS")
    logger.info("=========================================")
    
    validation_status = {}
    
    validation_status["regions"] = validate_regions(data_dict["regions"])
    validation_status["agences"] = validate_agences(data_dict["agences"])
    validation_status["employes"] = validate_employes(data_dict["employes"])
    validation_status["entreprises"] = validate_entreprises(data_dict["entreprises"])
    validation_status["comptes"] = validate_comptes(data_dict["comptes"])
    
    # Catalogue crédits (3 tables liées)
    validation_status["catalogue_credits"] = validate_catalogue_credits(
        data_dict["familles_credits"],
        data_dict["programmes_credits"],
        data_dict["produits_credits"]
    )
    
    validation_status["contrats_credits"] = validate_contrats_credits(data_dict["contrats_credits"])
    validation_status["garanties"] = validate_garanties(data_dict["garanties"])
    
    # Validation transactions en fournissant les comptes associés
    validation_status["transactions"] = validate_transactions(data_dict["transactions"], data_dict["comptes"])
    
    validation_status["solutions_digitales"] = validate_solutions_digitales(data_dict["solutions_digitales"])
    validation_status["souscriptions_digitales"] = validate_souscriptions(data_dict["souscriptions_digitales"])
    validation_status["connexions_digitales"] = validate_connexions(data_dict["connexions_digitales"])
    
    # Évaluation du succès global
    success = all(validation_status.values())
    
    if success:
        logger.info("Étape 2 : Toutes les validations métiers ont été franchies avec succès.")
    else:
        failed_tables = [k for k, v in validation_status.items() if not v]
        logger.error(f"Étape 2 : Validation échouée sur les composants suivants : {failed_tables}.")
        
    return success, validation_status
