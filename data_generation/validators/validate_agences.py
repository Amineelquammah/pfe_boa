# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_agences.py
Description     : Validateur de cohérence et de qualité pour les données agences.
"""

import pandas as pd
from data_generation.utils.logger import logger
from data_generation.config.config import NB_AGENCES

# Répartition attendue des agences par région (ID)
EXPECTED_DISTRIBUTION = {
    1: 2,  # Casablanca-Settat
    2: 2,  # Rabat-Salé-Kénitra
    3: 1,  # Fès-Meknès
    4: 1,  # Marrakech-Safi
    5: 1,  # Tanger-Tétouan-Al Hoceïma
    6: 1,  # Oriental
    7: 2   # Sud
}

def validate_agences(df_agences: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des agences selon les contraintes métiers et de qualité.
    
    Args:
        df_agences (pd.DataFrame): DataFrame généré des agences.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table agences...")
    errors = 0
    
    # 1. Vérification de la volumétrie globale
    nb_lignes = len(df_agences)
    if nb_lignes != NB_AGENCES:
        logger.error(f"[ERR_AGE_01] Nombre de lignes incorrect : {nb_lignes} trouvé, attendu {NB_AGENCES}.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie globale ok : {nb_lignes} agences.")

    # 2. Vérification des valeurs nulles
    null_counts = df_agences.isnull().sum().sum()
    if null_counts > 0:
        logger.error(f"[ERR_AGE_02] Des valeurs nulles ont été détectées dans la table agences ({null_counts} cellule(s)).")
        errors += 1
    else:
        logger.info("Vérification des valeurs nulles ok.")

    # 3. Vérification des doublons sur code_agence
    dup_codes = df_agences["code_agence"].duplicated().sum()
    if dup_codes > 0:
        logger.error(f"[ERR_AGE_03] Doublons détectés dans la colonne code_agence ({dup_codes} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité code_agence ok.")

    # 4. Vérification de l'existence des region_id dans l'intervalle [1, 7]
    invalid_regions = df_agences[~df_agences["region_id"].between(1, 7)]
    if not invalid_regions.empty:
        logger.error(f"[ERR_AGE_04] region_id invalides détectés (non compris entre 1 et 7) : {invalid_regions['region_id'].tolist()}.")
        errors += 1
    else:
        logger.info("Vérification de l'intégrité des region_id ok.")

    # 5. Vérification de la répartition par région
    actual_distribution = df_agences.groupby("region_id").size().to_dict()
    for reg_id, expected_count in EXPECTED_DISTRIBUTION.items():
        actual_count = actual_distribution.get(reg_id, 0)
        if actual_count != expected_count:
            logger.error(f"[ERR_AGE_05] Répartition incorrecte pour la région {reg_id} : {actual_count} agence(s) trouvée(s), attendu {expected_count}.")
            errors += 1
            
    if errors == 0:
        logger.info("Validation réussie pour la table agences.")
        return True
        
    logger.error(f"Validation échouée pour la table agences avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_agences import generate_agences
    df = generate_agences()
    res = validate_agences(df)
    print(f"\n--- TEST VALIDATE AGENCES : {'SUCCÈS' if res else 'ÉCHEC'} ---")
