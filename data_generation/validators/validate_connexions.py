# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_connexions.py
Description     : Validateur de cohérence pour la table connexions_digitales.
"""

import pandas as pd
from datetime import datetime
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_connexions import ACTIONS_BY_SOLUTION

def validate_connexions(df_connexions: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des connexions digitales.
    
    Args:
        df_connexions (pd.DataFrame): DataFrame des connexions.
        
    Returns:
        bool: True si la table est valide, False sinon.
    """
    logger.info("Début de la validation de la table connexions...")
    errors = 0
    
    # Chargement des entreprises pour validation croisée
    df_entreprises = generate_entreprises()
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    
    # 1. Vérification de la volumétrie (~100 000)
    nb_lignes = len(df_connexions)
    if not (90000 <= nb_lignes <= 110000):
        logger.error(f"[ERR_CON_01] Nombre de connexions incorrect : {nb_lignes} trouvé, attendu environ 100 000.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie ok : {nb_lignes} connexions.")

    # 2. Vérification des doublons sur l'identifiant
    dup_ids = df_connexions["id_connexion"].duplicated().sum()
    if dup_ids > 0:
        logger.error(f"[ERR_CON_02] Identifiants id_connexion dupliqués détectés ({dup_ids} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité id_connexion ok.")

    # 3. Vérification des relations entreprises et solutions
    invalid_ents = df_connexions[~df_connexions["id_entreprise"].isin(ent_dict.keys())]
    if not invalid_ents.empty:
        logger.error(f"[ERR_CON_03] connexions liées à des entreprises inexistantes : {invalid_ents['id_connexion'].head(5).tolist()}.")
        errors += 1
        
    invalid_sols = df_connexions[~df_connexions["id_solution"].between(1, 5)]
    if not invalid_sols.empty:
        logger.error(f"[ERR_CON_04] connexions liées à des solutions inexistantes : {invalid_sols['id_connexion'].head(5).tolist()}.")
        errors += 1
        
    if errors == 0:
        logger.info("Vérification intégrité référentielle ok.")

    # 4. Cohérence des actions selon la solution
    # Echantillonnage de 5000 lignes pour rapidité
    for idx, row in df_connexions.head(5000).iterrows():
        sol_id = int(row["id_solution"])
        action = row["action_realisee"]
        
        valid_actions = ACTIONS_BY_SOLUTION.get(sol_id, [])
        if action not in valid_actions:
            logger.error(f"[ERR_CON_05] Action '{action}' invalide pour la solution {sol_id} (attendu parmi {valid_actions}).")
            errors += 1
            break
            
    if errors == 0:
        logger.info("Vérification échantillonnée de la cohérence des actions ok.")

    # 5. Cohérence appareil vs solution
    # Solutions 1 (DabaPay Pro) et 5 (WhatsApp Business) doivent être sur Mobile.
    # Solutions 2 (Business Online) et 3 (CreditBusinessOnline) doivent être sur Desktop ou Tablet.
    for idx, row in df_connexions.head(5000).iterrows():
        sol_id = int(row["id_solution"])
        app = row["appareil"]
        
        if sol_id in [1, 5] and app != "Mobile":
            logger.error(f"[ERR_CON_06] Appareil '{app}' incohérent pour solution mobile {sol_id}.")
            errors += 1
            break
        if sol_id in [2, 3] and app not in ["Desktop", "Tablet"]:
            logger.error(f"[ERR_CON_07] Appareil '{app}' incohérent pour solution web {sol_id}.")
            errors += 1
            break
            
    if errors == 0:
        logger.info("Vérification échantillonnée de la cohérence des appareils ok.")

    # 6. Validité du statut (SUCCES, ECHEC)
    invalid_status = df_connexions[~df_connexions["statut"].isin(["SUCCES", "ECHEC"])]
    if not invalid_status.empty:
        logger.error(f"[ERR_CON_08] Statuts de connexions invalides détectés : {invalid_status['statut'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des statuts ok.")

    # 7. Cohérence des dates (date_connexion >= date_creation entreprise)
    for _, row in df_connexions.head(1000).iterrows():
        ent_id = row["id_entreprise"]
        if ent_id in ent_dict:
            ent_meta = ent_dict[ent_id]
            date_creation = datetime.strptime(ent_meta["date_creation"], "%Y-%m-%d")
            date_conn = datetime.strptime(row["date_connexion"], "%Y-%m-%d")
            
            if date_conn < date_creation:
                logger.error(f"[ERR_CON_09] Connexion {row['id_connexion']} enregistrée avant la création de l'entreprise ({row['date_connexion']} vs {ent_meta['date_creation']}).")
                errors += 1
                break

    if errors == 0:
        logger.info("Vérification échantillonnée de la cohérence temporelle ok.")

    # 8. Répartition annuelle
    df_connexions["annee"] = pd.to_datetime(df_connexions["date_connexion"]).dt.year
    annee_counts = df_connexions["annee"].value_counts(normalize=True).to_dict()
    
    # 2022 : ~20%
    # 2023 : ~35%
    # 2024 : ~45%
    # Marge de +/- 8%
    if not (0.12 <= annee_counts.get(2022, 0) <= 0.28):
        logger.error(f"[ERR_CON_10] Répartition annuelle 2022 hors cible : {annee_counts.get(2022, 0)*100:.2f}%.")
        errors += 1
    if not (0.28 <= annee_counts.get(2023, 0) <= 0.42):
        logger.error(f"[ERR_CON_11] Répartition annuelle 2023 hors cible : {annee_counts.get(2023, 0)*100:.2f}%.")
        errors += 1
    if not (0.38 <= annee_counts.get(2024, 0) <= 0.52):
        logger.error(f"[ERR_CON_12] Répartition annuelle 2024 hors cible : {annee_counts.get(2024, 0)*100:.2f}%.")
        errors += 1

    if errors == 0:
        logger.info("Vérification répartition temporelle ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table connexions_digitales.")
        return True
        
    logger.error(f"Validation échouée pour la table connexions_digitales avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_connexions import generate_connexions
    df = generate_connexions()
    res = validate_connexions(df)
    print(f"\n--- TEST VALIDATE CONNEXIONS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
