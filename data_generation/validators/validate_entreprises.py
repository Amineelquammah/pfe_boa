# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_entreprises.py
Description     : Validateur de cohérence et de qualité pour les données entreprises.
"""

import pandas as pd
from data_generation.utils.logger import logger
from data_generation.generators.generate_employes import generate_employes

def validate_entreprises(df_entreprises: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des entreprises selon les contraintes métiers et réglementaires.
    
    Args:
        df_entreprises (pd.DataFrame): DataFrame généré des entreprises.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table entreprises...")
    errors = 0
    
    # 1. Vérification de la volumétrie globale (2000 entreprises)
    nb_lignes = len(df_entreprises)
    if nb_lignes != 2000:
        logger.error(f"[ERR_ENT_01] Nombre d'entreprises incorrect : {nb_lignes} trouvé, attendu 2000.")
        errors += 1
    else:
        logger.info("Vérification volumétrie globale ok (2000 entreprises).")

    # 2. Vérification des doublons sur l'ICE
    dup_ices = df_entreprises["ice"].duplicated().sum()
    if dup_ices > 0:
        logger.error(f"[ERR_ENT_02] ICEs en double détectés ({dup_ices} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité ICE ok.")

    # 3. Vérification des doublons sur l'email
    dup_emails = df_entreprises["email"].duplicated().sum()
    if dup_emails > 0:
        logger.error(f"[ERR_ENT_03] Emails en double détectés ({dup_emails} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité email ok.")

    # 4. Vérification des doublons sur le téléphone
    dup_phones = df_entreprises["telephone"].duplicated().sum()
    if dup_phones > 0:
        logger.error(f"[ERR_ENT_04] Téléphones en double détectés ({dup_phones} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité téléphone ok.")

    # 5. Vérification de la validité de l'id_agence (1 à 10)
    invalid_agences = df_entreprises[~df_entreprises["id_agence"].between(1, 10)]
    if not invalid_agences.empty:
        logger.error(f"[ERR_ENT_05] id_agence invalides détectés : {invalid_agences['id_agence'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité id_agence ok.")

    # 6. Vérification de la validité du id_conseiller (doit être un conseiller de l'agence commerciale)
    df_employes = generate_employes()
    valid_conseillers_ids = set(df_employes[df_employes["fonction"] == "Conseiller Entreprises"]["id_employe"])
    invalid_conseillers = df_entreprises[~df_entreprises["id_conseiller"].isin(valid_conseillers_ids)]
    
    if not invalid_conseillers.empty:
        logger.error(f"[ERR_ENT_06] id_conseiller invalides détectés (employés inexistants ou non conseillers) : {invalid_conseillers['id_conseiller'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité id_conseiller ok.")

    # 7. Vérification de la cohérence CA vs Segment
    # TPE: CA [100 000, 5 000 000]
    tpe_ca_err = df_entreprises[(df_entreprises["segment"] == "TPE") & (~df_entreprises["chiffre_affaires"].between(100000.0, 5000000.0))]
    if not tpe_ca_err.empty:
        logger.error(f"[ERR_ENT_07] Incohérence CA pour TPE ({len(tpe_ca_err)} ligne(s)).")
        errors += 1
        
    # PME: CA [5 000 000, 100 000 000]
    pme_ca_err = df_entreprises[(df_entreprises["segment"] == "PME") & (~df_entreprises["chiffre_affaires"].between(5000000.0, 100000000.0))]
    if not pme_ca_err.empty:
        logger.error(f"[ERR_ENT_08] Incohérence CA pour PME ({len(pme_ca_err)} ligne(s)).")
        errors += 1
        
    # GE: CA >= 100 000 000
    ge_ca_err = df_entreprises[(df_entreprises["segment"] == "Grande Entreprise") & (df_entreprises["chiffre_affaires"] < 100000000.0)]
    if not ge_ca_err.empty:
        logger.error(f"[ERR_ENT_09] Incohérence CA pour Grande Entreprise ({len(ge_ca_err)} ligne(s)).")
        errors += 1

    # 8. Vérification de la cohérence Salariés vs Segment
    # TPE: [1, 9]
    tpe_emp_err = df_entreprises[(df_entreprises["segment"] == "TPE") & (~df_entreprises["nombre_employes"].between(1, 9))]
    if not tpe_emp_err.empty:
        logger.error(f"[ERR_ENT_10] Incohérence effectif salariés pour TPE ({len(tpe_emp_err)} ligne(s)).")
        errors += 1
        
    # PME: [10, 199]
    pme_emp_err = df_entreprises[(df_entreprises["segment"] == "PME") & (~df_entreprises["nombre_employes"].between(10, 199))]
    if not pme_emp_err.empty:
        logger.error(f"[ERR_ENT_11] Incohérence effectif salariés pour PME ({len(pme_emp_err)} ligne(s)).")
        errors += 1
        
    # GE: >= 200
    ge_emp_err = df_entreprises[(df_entreprises["segment"] == "Grande Entreprise") & (df_entreprises["nombre_employes"] < 200)]
    if not ge_emp_err.empty:
        logger.error(f"[ERR_ENT_12] Incohérence effectif salariés pour Grande Entreprise ({len(ge_emp_err)} ligne(s)).")
        errors += 1

    # 9. Vérification des proportions de segment (tolérance de +/- 5%)
    seg_counts = df_entreprises["segment"].value_counts(normalize=True).to_dict()
    tpe_prop = seg_counts.get("TPE", 0)
    pme_prop = seg_counts.get("PME", 0)
    ge_prop = seg_counts.get("Grande Entreprise", 0)
    
    if not (0.50 <= tpe_prop <= 0.60):
        logger.error(f"[ERR_ENT_13] Proportion TPE hors cible ({tpe_prop*100:.2f}%, attendu 55%).")
        errors += 1
    if not (0.30 <= pme_prop <= 0.40):
        logger.error(f"[ERR_ENT_14] Proportion PME hors cible ({pme_prop*100:.2f}%, attendu 35%).")
        errors += 1
    if not (0.07 <= ge_prop <= 0.13):
        logger.error(f"[ERR_ENT_15] Proportion Grande Entreprise hors cible ({ge_prop*100:.2f}%, attendu 10%).")
        errors += 1

    if errors == 0:
        logger.info("Validation réussie pour la table entreprises.")
        return True
        
    logger.error(f"Validation échouée pour la table entreprises avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_entreprises import generate_entreprises
    df = generate_entreprises()
    res = validate_entreprises(df)
    print(f"\n--- TEST VALIDATE ENTREPRISES : {'SUCCÈS' if res else 'ÉCHEC'} ---")
