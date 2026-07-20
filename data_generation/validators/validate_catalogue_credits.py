# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_catalogue_credits.py
Description     : Validateur pour la hiérarchie du catalogue de crédit (familles, programmes, produits).
"""

import pandas as pd
from typing import Tuple
from data_generation.utils.logger import logger

def validate_catalogue_credits(
    df_familles: pd.DataFrame, 
    df_programmes: pd.DataFrame, 
    df_produits: pd.DataFrame
) -> bool:
    """
    Valide les DataFrames du catalogue de crédit selon les contraintes métiers.
    
    Args:
        df_familles (pd.DataFrame): DataFrame des familles.
        df_programmes (pd.DataFrame): DataFrame des programmes.
        df_produits (pd.DataFrame): DataFrame des produits.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation du catalogue de crédit...")
    errors = 0
    
    # 1. Vérification des Familles
    if df_familles["code_famille"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_01] Doublons trouvés dans les codes familles de crédits.")
        errors += 1
    if df_familles["nom_famille"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_02] Doublons trouvés dans les noms familles de crédits.")
        errors += 1
        
    # 2. Vérification des Programmes
    if df_programmes["code_programme"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_03] Doublons trouvés dans les codes programmes de crédits.")
        errors += 1
    if df_programmes["nom_programme"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_04] Doublons trouvés dans les noms programmes de crédits.")
        errors += 1
        
    # Vérification FK id_famille dans programmes
    invalid_fam_ids = df_programmes[~df_programmes["id_famille"].isin(df_familles["id_famille"])]
    if not invalid_fam_ids.empty:
        logger.error(f"[ERR_CAT_05] programmes avec id_famille orphelin : {invalid_fam_ids['id_programme'].tolist()}.")
        errors += 1

    # 3. Vérification des Produits
    if df_produits["code_produit"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_06] Doublons trouvés dans les codes produits de crédits.")
        errors += 1
    if df_produits["nom_produit"].duplicated().sum() > 0:
        logger.error("[ERR_CAT_07] Doublons trouvés dans les noms produits de crédits.")
        errors += 1
        
    # Vérification FK id_programme dans produits
    invalid_prog_ids = df_produits[~df_produits["id_programme"].isin(df_programmes["id_programme"])]
    if not invalid_prog_ids.empty:
        logger.error(f"[ERR_CAT_08] produits avec id_programme orphelin : {invalid_prog_ids['id_produit'].tolist()}.")
        errors += 1

    # 4. Cohérence des Montants, Taux, et Durées pour chaque produit
    for _, row in df_produits.iterrows():
        # Montants
        if row["montant_min"] <= 0 or row["montant_max"] <= 0:
            logger.error(f"[ERR_CAT_09] Montants non positifs pour le produit {row['code_produit']}.")
            errors += 1
        if row["montant_min"] > row["montant_max"]:
            logger.error(f"[ERR_CAT_10] montant_min supérieur à montant_max pour {row['code_produit']}.")
            errors += 1
            
        # Taux
        if row["taux_min"] < 0 or row["taux_max"] < 0:
            logger.error(f"[ERR_CAT_11] Taux négatif détecté pour {row['code_produit']}.")
            errors += 1
        if row["taux_min"] > row["taux_max"]:
            logger.error(f"[ERR_CAT_12] taux_min supérieur à taux_max pour {row['code_produit']}.")
            errors += 1
            
        # Durées
        if row["duree_min"] < 1 or row["duree_max"] < 1:
            logger.error(f"[ERR_CAT_13] Durées non positives pour {row['code_produit']}.")
            errors += 1
        if row["duree_min"] > row["duree_max"]:
            logger.error(f"[ERR_CAT_14] duree_min supérieure à duree_max pour {row['code_produit']}.")
            errors += 1

    if errors == 0:
        logger.info("Validation réussie pour l'ensemble du catalogue de crédit (familles, programmes, produits).")
        return True
        
    logger.error(f"Validation échouée pour le catalogue de crédit avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_catalogue_credits import generate_catalogue_credits
    df_fam, df_prog, df_prod = generate_catalogue_credits()
    res = validate_catalogue_credits(df_fam, df_prog, df_prod)
    print(f"\n--- TEST VALIDATE CATALOGUE CREDITS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
