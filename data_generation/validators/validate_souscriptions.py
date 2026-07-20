# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_souscriptions.py
Description     : Validateur de cohérence pour la table souscriptions_digitales.
"""

import pandas as pd
from datetime import datetime
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises

def validate_souscriptions(df_souscriptions: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des souscriptions digitales.
    
    Args:
        df_souscriptions (pd.DataFrame): DataFrame des souscriptions.
        
    Returns:
        bool: True si la table est valide, False sinon.
    """
    logger.info("Début de la validation de la table souscriptions...")
    errors = 0
    
    # Chargement des entreprises pour validation croisée
    df_entreprises = generate_entreprises()
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    
    # 1. Vérification de la volumétrie (~3500)
    nb_lignes = len(df_souscriptions)
    if not (3200 <= nb_lignes <= 3800):
        logger.error(f"[ERR_SUB_01] Nombre de souscriptions incorrect : {nb_lignes} trouvé, attendu environ 3500.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie ok : {nb_lignes} souscriptions.")

    # 2. Vérification de l'unicité du couple (id_entreprise, id_solution)
    dup_keys = df_souscriptions.duplicated(subset=["id_entreprise", "id_solution"]).sum()
    if dup_keys > 0:
        logger.error(f"[ERR_SUB_02] Doublons sur le couple (id_entreprise, id_solution) détectés ({dup_keys} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité de la clé composite ok.")

    # 3. Vérification de l'existence des entreprises et des solutions (1 à 5)
    invalid_ents = df_souscriptions[~df_souscriptions["id_entreprise"].isin(ent_dict.keys())]
    if not invalid_ents.empty:
        logger.error(f"[ERR_SUB_03] souscriptions liées à des entreprises inexistantes : {invalid_ents['id_souscription'].tolist()}.")
        errors += 1
        
    invalid_sols = df_souscriptions[~df_souscriptions["id_solution"].between(1, 5)]
    if not invalid_sols.empty:
        logger.error(f"[ERR_SUB_04] souscriptions liées à des solutions inexistantes (hors 1-5) : {invalid_sols['id_souscription'].tolist()}.")
        errors += 1
        
    if errors == 0:
        logger.info("Vérification intégrité référentielle ok.")

    # 4. Cohérence des dates (date_souscription >= date_creation entreprise)
    for _, row in df_souscriptions.iterrows():
        ent_id = row["id_entreprise"]
        if ent_id in ent_dict:
            ent_meta = ent_dict[ent_id]
            date_creation = datetime.strptime(ent_meta["date_creation"], "%Y-%m-%d")
            date_sous = datetime.strptime(row["date_souscription"], "%Y-%m-%d")
            
            if date_sous < date_creation:
                logger.error(f"[ERR_SUB_05] Souscription {row['id_souscription']} mise en place avant la création de l'entreprise ({row['date_souscription']} vs {ent_meta['date_creation']}).")
                errors += 1
                break

    if errors == 0:
        logger.info("Vérification cohérence temporelle ok.")

    # 5. Validité des statuts et niveau d'utilisation
    invalid_status = df_souscriptions[~df_souscriptions["statut"].isin(["ACTIF", "RESILIE"])]
    if not invalid_status.empty:
        logger.error(f"[ERR_SUB_06] Statuts de souscriptions invalides : {invalid_status['statut'].unique().tolist()}.")
        errors += 1
        
    invalid_use = df_souscriptions[~df_souscriptions["niveau_utilisation"].isin(["FAIBLE", "MOYEN", "ELEVE"])]
    if not invalid_use.empty:
        logger.error(f"[ERR_SUB_07] Niveau d'utilisation invalide : {invalid_use['niveau_utilisation'].unique().tolist()}.")
        errors += 1

    if errors == 0:
        logger.info("Validation réussie pour la table souscriptions.")
        return True
        
    logger.error(f"Validation échouée pour la table souscriptions avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_souscriptions import generate_souscriptions
    df = generate_souscriptions()
    res = validate_souscriptions(df)
    print(f"\n--- TEST VALIDATE SOUSCRIPTIONS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
