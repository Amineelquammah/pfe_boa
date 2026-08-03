# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_garanties.py
Description     : Validateur de cohérence et de qualité pour les données de garanties.
"""

import pandas as pd
from datetime import datetime
from data_generation.utils.logger import logger
from data_generation.generators.generate_contrats_credits import generate_contrats_credits

# Liste des types de garanties valides
VALID_TYPES = [
    "Hypothèque", "Nantissement", "Caution personnelle", "Caution bancaire", 
    "Garantie de l'État", "Garantie Tamwilcom", "Aval", 
    "Garantie sur fonds de commerce", "Garantie sur matériel", "Garantie sur créances"
]

# Liste des statuts de garanties valides
VALID_STATUS = ["Active", "Expirée", "Libérée", "En cours de réalisation"]

def validate_garanties(df_garanties: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des garanties selon les contraintes métiers.
    
    Args:
        df_garanties (pd.DataFrame): DataFrame des garanties générées.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table garanties...")
    errors = 0
    
    # Chargement des contrats de crédits pour validation croisée
    df_contrats = generate_contrats_credits()
    contracts_dict = df_contrats.set_index("id_contrat").to_dict(orient="index")
    
    # 1. Vérification de la volumétrie globale (~800 garanties)
    nb_lignes = len(df_garanties)
    if not (750 <= nb_lignes <= 850):
        logger.error(f"[ERR_GAR_01] Nombre de garanties incorrect : {nb_lignes} trouvé, attendu environ 800.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie globale ok : {nb_lignes} garanties.")

    # 2. Vérification de l'unicité de numero_garantie
    dup_nums = df_garanties["numero_garantie"].duplicated().sum()
    if dup_nums > 0:
        logger.error(f"[ERR_GAR_02] Numéros de garantie en double détectés ({dup_nums} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité numero_garantie ok.")

    # 3. Vérification de la validité de id_contrat
    invalid_contracts = df_garanties[~df_garanties["id_contrat"].isin(contracts_dict.keys())]
    if not invalid_contracts.empty:
        logger.error(f"[ERR_GAR_03] garanties liées à des contrats de crédit inexistants : {invalid_contracts['id_garantie'].tolist()}.")
        errors += 1
    else:
        logger.info("Vérification intégrité référentielle id_contrat ok.")

    # 4. Vérification des montants (valeur positive)
    invalid_values = df_garanties[(df_garanties["valeur_initiale"] <= 0) | (df_garanties["valeur_actuelle"] <= 0)]
    if not invalid_values.empty:
        logger.error(f"[ERR_GAR_04] Valeurs initiales ou actuelles non positives détectées : {invalid_values['id_garantie'].tolist()}.")
        errors += 1
    else:
        logger.info("Vérification positivité des valeurs de garanties ok.")

    # 5. Cohérence temporelle (affectation >= octroi crédit et expiration > affectation)
    for _, row in df_garanties.iterrows():
        contrat_id = row["id_contrat"]
        if contrat_id in contracts_dict:
            contrat_meta = contracts_dict[contrat_id]
            date_octroi = datetime.strptime(contrat_meta["date_octroi"], "%Y-%m-%d")
            date_affectation = datetime.strptime(row["date_affectation"], "%Y-%m-%d")
            date_expiration = datetime.strptime(row["date_expiration"], "%Y-%m-%d")
            
            if date_affectation < date_octroi:
                logger.error(f"[ERR_GAR_05] Garantie {row['id_garantie']} mise en place avant l'octroi du crédit ({row['date_affectation']} vs {contrat_meta['date_octroi']}).")
                errors += 1
            if date_expiration <= date_affectation:
                logger.error(f"[ERR_GAR_06] Garantie {row['id_garantie']} expire avant ou le jour de sa mise en place ({row['date_expiration']} vs {row['date_affectation']}).")
                errors += 1

    if errors == 0:
        logger.info("Vérification cohérence temporelle ok.")

    # 6. Type de garantie valide
    invalid_types = df_garanties[~df_garanties["type_garantie"].isin(VALID_TYPES)]
    if not invalid_types.empty:
        logger.error(f"[ERR_GAR_07] Types de garanties invalides détectés : {invalid_types['type_garantie'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des types ok.")

    # 7. Statuts valides
    invalid_status = df_garanties[~df_garanties["statut"].isin(VALID_STATUS)]
    if not invalid_status.empty:
        logger.error(f"[ERR_GAR_08] Statuts de garanties invalides détectés : {invalid_status['statut'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des statuts ok.")

    # 8. Cohérence du taux de couverture par rapport à l'encours
    for _, row in df_garanties.iterrows():
        contrat_id = row["id_contrat"]
        if contrat_id in contracts_dict:
            contrat_meta = contracts_dict[contrat_id]
            encours = float(contrat_meta["encours_restant"])
            actual_rate = row["taux_couverture"]
            
            if encours > 0:
                expected_rate = round(row["valeur_actuelle"] / encours, 4)
                # Une marge de tolérance de 0.001 pour les arrondis
                if abs(actual_rate - expected_rate) > 0.001:
                    logger.error(f"[ERR_GAR_09] Taux de couverture incohérent sur garantie {row['id_garantie']} (trouvé {actual_rate}, calculé {expected_rate}).")
                    errors += 1
            else:
                if actual_rate != 0.0:
                    logger.error(f"[ERR_GAR_10] Taux de couverture non nul sur contrat remboursé pour garantie {row['id_garantie']} (taux: {actual_rate}).")
                    errors += 1

    if errors == 0:
        logger.info("Vérification cohérence des taux de couverture ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table garanties.")
        return True
        
    logger.error(f"Validation échouée pour la table garanties avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_garanties import generate_garanties
    df = generate_garanties()
    res = validate_garanties(df)
    print(f"\n--- TEST VALIDATE GARANTIES : {'SUCCÈS' if res else 'ÉCHEC'} ---")
