# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_employes.py
Description     : Validateur de cohérence et de qualité pour les données employés.
"""

import pandas as pd
from data_generation.utils.logger import logger

def validate_employes(df_employes: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des employés selon les contraintes métiers et de qualité.
    
    Args:
        df_employes (pd.DataFrame): DataFrame généré des employés.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table employes...")
    errors = 0
    
    # 1. Vérification de la volumétrie globale (48 employés)
    nb_lignes = len(df_employes)
    if nb_lignes != 48:
        logger.error(f"[ERR_EMP_01] Nombre d'employés incorrect : {nb_lignes} trouvé, attendu 48.")
        errors += 1
    else:
        logger.info("Vérification volumétrie globale ok (48 employés).")

    # 2. Vérification des doublons sur le matricule
    dup_matricules = df_employes["matricule"].duplicated().sum()
    if dup_matricules > 0:
        logger.error(f"[ERR_EMP_02] Matricules en double détectés ({dup_matricules} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité matricule ok.")

    # 3. Vérification des doublons sur l'email professionnel
    dup_emails = df_employes["email_professionnel"].duplicated().sum()
    if dup_emails > 0:
        logger.error(f"[ERR_EMP_03] Emails professionnels en double détectés ({dup_emails} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité email ok.")

    # 4. Vérification de la validité hiérarchique des managers (manager_id doit exister dans id_employe)
    valid_ids = set(df_employes["id_employe"])
    # Récupérer les manager_id non nuls
    managers_to_check = df_employes["manager_id"].dropna().astype(int).tolist()
    invalid_managers = [m for m in managers_to_check if m not in valid_ids]
    
    if len(invalid_managers) > 0:
        logger.error(f"[ERR_EMP_04] manager_id invalides détectés (employés inexistants) : {invalid_managers}.")
        errors += 1
    else:
        logger.info("Vérification cohérence hiérarchique manager_id ok.")

    # 5. Vérification des structures par agence
    # Agences valides (1 à 10)
    for ag_id in range(1, 11):
        df_ag = df_employes[df_employes["agence_id"] == ag_id]
        
        # Directeur d'Agence : exactement 1
        da_count = len(df_ag[df_ag["fonction"] == "Directeur d'Agence"])
        if da_count != 1:
            logger.error(f"[ERR_EMP_05] Agence {ag_id} possède {da_count} Directeur(s), attendu 1.")
            errors += 1
            
        # Conseiller Entreprises : exactement 2
        ce_count = len(df_ag[df_ag["fonction"] == "Conseiller Entreprises"])
        if ce_count != 2:
            logger.error(f"[ERR_EMP_06] Agence {ag_id} possède {ce_count} Conseiller(s) Entreprises, attendu 2.")
            errors += 1
            
        # Chargé de Caisse : exactement 1
        cc_count = len(df_ag[df_ag["fonction"] == "Chargé de Caisse"])
        if cc_count != 1:
            logger.error(f"[ERR_EMP_07] Agence {ag_id} possède {cc_count} Chargé(s) de Caisse, attendu 1.")
            errors += 1

    # 6. Vérification au niveau régional (1 Directeur Régional par région de 1 à 7)
    for reg_id in range(1, 8):
        df_reg = df_employes[(df_employes["region_id"] == reg_id) & (df_employes["fonction"] == "Directeur Régional")]
        dr_count = len(df_reg)
        if dr_count != 1:
            logger.error(f"[ERR_EMP_08] Région {reg_id} possède {dr_count} Directeur(s) Régionaux, attendu 1.")
            errors += 1
            
    # 7. Vérification du Directeur Général (exactement 1 global)
    dg_count = len(df_employes[df_employes["fonction"] == "Directeur Général"])
    if dg_count != 1:
        logger.error(f"[ERR_EMP_09] Nombre de Directeur Général incorrect : {dg_count} trouvé, attendu 1.")
        errors += 1

    if errors == 0:
        logger.info("Validation réussie pour la table employes.")
        return True
        
    logger.error(f"Validation échouée pour la table employes avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_employes import generate_employes
    df = generate_employes()
    res = validate_employes(df)
    print(f"\n--- TEST VALIDATE EMPLOYES : {'SUCCÈS' if res else 'ÉCHEC'} ---")
