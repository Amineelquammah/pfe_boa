# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_solutions_digitales.py
Description     : Validateur de cohérence pour la table solutions_digitales.
"""

import pandas as pd
from data_generation.utils.logger import logger

def validate_solutions_digitales(df_solutions: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des solutions digitales.
    
    Args:
        df_solutions (pd.DataFrame): DataFrame des solutions.
        
    Returns:
        bool: True si la table est valide, False sinon.
    """
    logger.info("Début de la validation de la table solutions_digitales...")
    errors = 0
    
    # 1. Volumétrie exacte (5)
    nb_lignes = len(df_solutions)
    if nb_lignes != 5:
        logger.error(f"[ERR_SD_01] Nombre de solutions incorrect : {nb_lignes} trouvé, attendu 5.")
        errors += 1
    else:
        logger.info("Vérification volumétrie ok (5 solutions).")

    # 2. Unicité du nom
    dup_names = df_solutions["nom_solution"].duplicated().sum()
    if dup_names > 0:
        logger.error(f"[ERR_SD_02] Noms de solutions dupliqués détectés ({dup_names} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité nom_solution ok.")

    # 3. Validité du canal
    invalid_canals = df_solutions[~df_solutions["canal"].isin(["MOBILE", "WEB", "ASSISTANT"])]
    if not invalid_canals.empty:
        logger.error(f"[ERR_SD_03] Canaux invalides détectés : {invalid_canals['canal'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des canaux ok.")

    # 4. Validité du statut
    invalid_statuts = df_solutions[~df_solutions["statut"].isin(["ACTIF", "INACTIF"])]
    if not invalid_statuts.empty:
        logger.error(f"[ERR_SD_04] Statuts invalides détectés : {invalid_statuts['statut'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des statuts ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table solutions_digitales.")
        return True
        
    logger.error(f"Validation échouée pour la table solutions_digitales avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_solutions_digitales import generate_solutions_digitales
    df = generate_solutions_digitales()
    res = validate_solutions_digitales(df)
    print(f"\n--- TEST VALIDATE SOLUTIONS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
