# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_regions.py
Description     : Validateur de cohérence et de qualité pour les données régions.
"""

import pandas as pd
from data_generation.utils.logger import logger
from data_generation.config.config import NB_REGIONS

def validate_regions(df_regions: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des régions selon les contraintes métiers et de qualité.
    
    Args:
        df_regions (pd.DataFrame): DataFrame généré des régions.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table regions...")
    errors = 0
    
    # 1. Vérification du nombre exact de régions
    nb_lignes = len(df_regions)
    if nb_lignes != NB_REGIONS:
        logger.error(f"[ERR_REG_01] Nombre de lignes incorrect : {nb_lignes} trouvé, attendu {NB_REGIONS}.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie ok : {nb_lignes} régions.")

    # 2. Vérification des valeurs nulles
    null_counts = df_regions.isnull().sum().sum()
    if null_counts > 0:
        logger.error(f"[ERR_REG_02] Des valeurs nulles ont été détectées dans la table regions ({null_counts} cellule(s)).")
        errors += 1
    else:
        logger.info("Vérification des valeurs nulles ok.")

    # 3. Vérification des doublons sur l'identifiant
    dup_ids = df_regions["id_region"].duplicated().sum()
    if dup_ids > 0:
        logger.error(f"[ERR_REG_03] Doublons d'identifiants détectés dans la colonne id_region ({dup_ids} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité id_region ok.")

    # 4. Vérification des doublons sur le nom de région
    dup_names = df_regions["nom_region"].duplicated().sum()
    if dup_names > 0:
        logger.error(f"[ERR_REG_04] Doublons de noms détectés dans la colonne nom_region ({dup_names} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité nom_region ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table regions.")
        return True
    
    logger.error(f"Validation échouée pour la table regions avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    # Test indépendant du module de validation
    from data_generation.generators.generate_regions import generate_regions
    df = generate_regions()
    res = validate_regions(df)
    print(f"\n--- TEST VALIDATE REGIONS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
