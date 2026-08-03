# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_contrats_credits.py
Description     : Validateur pour la cohérence et la qualité des contrats de crédits.
"""

import pandas as pd
import numpy as np
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_employes import generate_employes
from data_generation.generators.generate_catalogue_credits import generate_catalogue_credits

def validate_contrats_credits(df_contrats: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des contrats de crédit selon les contraintes métiers et réglementaires.
    
    Args:
        df_contrats (pd.DataFrame): DataFrame des contrats générés.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table contrats_credits...")
    errors = 0
    
    # Chargement des tables pour vérifications croisées
    df_entreprises = generate_entreprises()
    df_employes = generate_employes()
    _, _, df_produits = generate_catalogue_credits()
    
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    prod_dict = df_produits.set_index("id_produit").to_dict(orient="index")
    valid_ce_ids = set(df_employes[df_employes["fonction"] == "Conseiller Entreprises"]["id_employe"])
    
    # 1. Vérification de la volumétrie (~1000 contrats)
    nb_lignes = len(df_contrats)
    if not (950 <= nb_lignes <= 1050):
        logger.error(f"[ERR_CON_01] Nombre de contrats incorrect : {nb_lignes} trouvé, attendu environ 1000.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie globale ok : {nb_lignes} contrats de crédit.")

    # 2. Vérification des doublons sur numero_contrat
    dup_nums = df_contrats["numero_contrat"].duplicated().sum()
    if dup_nums > 0:
        logger.error(f"[ERR_CON_02] Numéros de contrat en double détectés ({dup_nums} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité numero_contrat ok.")

    # 3. Vérification de la cohérence de l'affectation commerciale (héritage agence/conseiller de l'entreprise)
    for _, row in df_contrats.iterrows():
        ent_id = row["id_entreprise"]
        if ent_id in ent_dict:
            ent_meta = ent_dict[ent_id]
            if row["id_agence"] != ent_meta["id_agence"] or row["id_conseiller"] != ent_meta["id_conseiller"]:
                logger.error(f"[ERR_CON_03] Le contrat {row['id_contrat']} possède un rattachement agence/conseiller incohérent avec l'entreprise {ent_id}.")
                errors += 1
                
    if errors == 0:
        logger.info("Vérification cohérence héritage agence/conseiller ok.")

    # 4. Vérification de la validité du conseiller_id
    invalid_ce = df_contrats[~df_contrats["id_conseiller"].isin(valid_ce_ids)]
    if not invalid_ce.empty:
        logger.error(f"[ERR_CON_04] id_conseiller invalides (non conseillers d'entreprise) : {invalid_ce['id_conseiller'].unique().tolist()}.")
        errors += 1
    else:
        logger.info("Vérification validité des conseillers ok.")

    # 5. Bornes du produit (Montant, Taux, Durée)
    for _, row in df_contrats.iterrows():
        prod_id = row["id_produit"]
        if prod_id in prod_dict:
            prod_meta = prod_dict[prod_id]
            
            # Montant
            if not (float(prod_meta["montant_min"]) <= row["montant_principal"] <= float(prod_meta["montant_max"])):
                logger.error(f"[ERR_CON_05] Contrat {row['id_contrat']} hors bornes montant du produit {prod_id} ({row['montant_principal']} MAD vs [{prod_meta['montant_min']}, {prod_meta['montant_max']}]).")
                errors += 1
                
            # Taux
            if not (float(prod_meta["taux_min"]) <= row["taux_interet"] <= float(prod_meta["taux_max"])):
                logger.error(f"[ERR_CON_06] Contrat {row['id_contrat']} hors bornes taux du produit {prod_id} ({row['taux_interet']}% vs [{prod_meta['taux_min']}, {prod_meta['taux_max']}]).")
                errors += 1
                
            # Durée
            if not (int(prod_meta["duree_min"]) <= row["duree"] <= int(prod_meta["duree_max"])):
                logger.error(f"[ERR_CON_07] Contrat {row['id_contrat']} hors bornes durée du produit {prod_id} ({row['duree']} mois vs [{prod_meta['duree_min']}, {prod_meta['duree_max']}]).")
                errors += 1

    if errors == 0:
        logger.info("Vérification conformité aux caractéristiques produits ok.")

    # 6. Cohérence de l'encours restant et du capital remboursé
    # capital_rembourse + encours_restant = montant_principal (avec tolérance aux arrondis de 1 MAD)
    for _, row in df_contrats.iterrows():
        diff = abs((row["capital_rembourse"] + row["encours_restant"]) - row["montant_principal"])
        if diff > 1.0:
            logger.error(f"[ERR_CON_08] Incohérence amortissement capital pour contrat {row['id_contrat']} (remboursé: {row['capital_rembourse']}, encours: {row['encours_restant']}, accordé: {row['montant_principal']}).")
            errors += 1

    if errors == 0:
        logger.info("Vérification équilibre de l'encours et du capital remboursé ok.")

    # 7. Cohérence indicateur NPL et statut
    for _, row in df_contrats.iterrows():
        # NPL si et seulement si jours_retard >= 90 et statut == 'NPL'
        is_npl = row["indicateur_npl"]
        jours = row["jours_retard"]
        statut = row["statut"]
        
        if is_npl:
            if jours < 90 or statut != "NPL":
                logger.error(f"[ERR_CON_09] Contrat {row['id_contrat']} marqué NPL mais jours={jours} et statut={statut}.")
                errors += 1
        else:
            if jours >= 90 or statut == "NPL":
                logger.error(f"[ERR_CON_10] Contrat {row['id_contrat']} non marqué NPL mais jours={jours} et statut={statut}.")
                errors += 1

    if errors == 0:
        logger.info("Vérification indicateur NPL et statut de risque ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table contrats_credits.")
        return True
        
    logger.error(f"Validation échouée pour la table contrats_credits avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_contrats_credits import generate_contrats_credits
    df = generate_contrats_credits()
    res = validate_contrats_credits(df)
    print(f"\n--- TEST VALIDATE CONTRATS CREDITS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
