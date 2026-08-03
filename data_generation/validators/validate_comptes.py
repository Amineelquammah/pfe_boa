# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_comptes.py
Description     : Validateur de cohérence et de qualité pour les données comptes.
"""

import pandas as pd
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises

def validate_comptes(df_comptes: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des comptes selon les contraintes métiers.
    
    Args:
        df_comptes (pd.DataFrame): DataFrame généré des comptes.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table comptes...")
    errors = 0
    
    # Chargement des entreprises pour validation croisée
    df_entreprises = generate_entreprises()
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    
    # 1. Vérification de la volumétrie globale (~2500 comptes)
    nb_lignes = len(df_comptes)
    if not (2400 <= nb_lignes <= 2600):
        logger.error(f"[ERR_CPT_01] Volumétrie globale incorrecte : {nb_lignes} comptes trouvés, attendu environ 2500.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie ok : {nb_lignes} comptes.")

    # 2. Vérification d'un compte courant par entreprise minimum
    courants = df_comptes[df_comptes["type_compte"] == "COURANT"]
    nb_courants = len(courants)
    if nb_courants != 2000:
        logger.error(f"[ERR_CPT_02] Nombre de comptes courants incorrect : {nb_courants} trouvé, attendu exactement 2000 (1 par entreprise).")
        errors += 1
        
    # Unicité id_entreprise pour les comptes courants (exactement un par entreprise)
    dup_ent_courant = courants["id_entreprise"].duplicated().sum()
    if dup_ent_courant > 0:
        logger.error(f"[ERR_CPT_03] Doublons d'entreprises sur les comptes courants détectés ({dup_ent_courant} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification : exactement un compte courant par entreprise ok.")

    # 3. Vérification des DAT sans compte parent valide
    dats = df_comptes[df_comptes["type_compte"] == "DAT"]
    courant_ids = set(courants["id_compte"])
    
    invalid_dats = dats[~dats["id_compte_courant_parent"].isin(courant_ids)]
    if not invalid_dats.empty:
        logger.error(f"[ERR_CPT_04] DATs orphelins détectés (sans compte parent courant valide) : {invalid_dats['id_compte'].tolist()}.")
        errors += 1
    else:
        logger.info("Vérification : pas de DAT orphelin ok.")

    # 4. Vérification de la cohérence de la filiation DAT -> Courant pour la même entreprise
    for _, dat_row in dats.iterrows():
        parent_id = dat_row["id_compte_courant_parent"]
        parent_compte = courants[courants["id_compte"] == parent_id]
        if not parent_compte.empty:
            parent_ent = parent_compte.iloc[0]["id_entreprise"]
            if parent_ent != dat_row["id_entreprise"]:
                logger.error(f"[ERR_CPT_05] Le DAT {dat_row['id_compte']} est lié à un compte parent appartenant à une autre entreprise ({parent_ent} vs {dat_row['id_entreprise']}).")
                errors += 1
                
    if errors == 0:
        logger.info("Vérification : cohérence entreprise parent/enfant DAT ok.")

    # 5. Vérification des doublons sur les colonnes d'identifiants uniques
    for col in ["numero_compte", "rib", "iban"]:
        dup = df_comptes[col].duplicated().sum()
        if dup > 0:
            logger.error(f"[ERR_CPT_06] Doublons détectés dans la colonne {col} ({dup} doublon(s)).")
            errors += 1
        else:
            logger.info(f"Vérification : unicité de {col} ok.")

    # 6. Vérification de la cohérence de l'agence et du conseiller (héritage entreprise)
    for _, row in df_comptes.iterrows():
        ent_id = row["id_entreprise"]
        if ent_id in ent_dict:
            ent_meta = ent_dict[ent_id]
            if row["id_agence"] != ent_meta["id_agence"] or row["id_conseiller"] != ent_meta["id_conseiller"]:
                logger.error(f"[ERR_CPT_07] Compte {row['id_compte']} possède un rattachement agence/conseiller incohérent avec l'entreprise {ent_id}.")
                errors += 1
                
    if errors == 0:
        logger.info("Vérification : cohérence héritage agence/conseiller ok.")

    # 7. Vérification des soldes positifs
    negative_balances = df_comptes[df_comptes["solde_actuel"] < 0]
    if not negative_balances.empty:
        logger.error(f"[ERR_CPT_08] Des soldes négatifs ont été détectés ({len(negative_balances)} compte(s)).")
        errors += 1
    else:
        logger.info("Vérification : soldes positifs ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table comptes.")
        return True
        
    logger.error(f"Validation échouée pour la table comptes avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_comptes import generate_comptes
    df = generate_comptes()
    res = validate_comptes(df)
    print(f"\n--- TEST VALIDATE COMPTES : {'SUCCÈS' if res else 'ÉCHEC'} ---")
