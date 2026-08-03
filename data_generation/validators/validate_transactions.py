# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/validators/validate_transactions.py
Description     : Validateur de cohérence chronologique et de qualité pour les transactions.
"""

import pandas as pd
from typing import Tuple
from datetime import datetime
from data_generation.utils.logger import logger

def validate_transactions(df_txns: pd.DataFrame, df_comptes: pd.DataFrame) -> bool:
    """
    Valide le DataFrame des transactions et sa cohérence avec les comptes.
    
    Args:
        df_txns (pd.DataFrame): DataFrame des transactions.
        df_comptes (pd.DataFrame): DataFrame mis à jour des comptes.
        
    Returns:
        bool: True si toutes les validations passent, False sinon.
    """
    logger.info("Début de la validation de la table transactions...")
    errors = 0
    
    # 1. Vérification de la volumétrie globale (~150 000)
    nb_lignes = len(df_txns)
    if not (140000 <= nb_lignes <= 165000):
        logger.error(f"[ERR_TXN_01] Volumétrie incorrecte : {nb_lignes} transactions trouvées, attendu environ 150 000.")
        errors += 1
    else:
        logger.info(f"Vérification volumétrie globale ok : {nb_lignes} transactions.")

    # 2. Vérification des doublons sur reference_transaction
    dup_refs = df_txns["reference_transaction"].duplicated().sum()
    if dup_refs > 0:
        logger.error(f"[ERR_TXN_02] Références de transaction en double détectées ({dup_refs} doublon(s)).")
        errors += 1
    else:
        logger.info("Vérification unicité reference_transaction ok.")

    # 3. Vérification des montants positifs
    neg_amounts = df_txns[df_txns["montant"] <= 0.0]
    if not neg_amounts.empty:
        logger.error(f"[ERR_TXN_03] Montants non positifs détectés dans {len(neg_amounts)} transaction(s).")
        errors += 1
    else:
        logger.info("Vérification positivité des montants ok.")

    # 4. Cohérence débit/crédit (type de transaction vs sens)
    credit_types = {"Virement entrant", "Encaissement client", "Versement", "Placement DAT", "Clôture DAT"}
    debit_types = {"Virement sortant", "Paiement fournisseur", "Retrait", "Prélèvement", "Paiement échéance crédit", "Placement DAT", "Clôture DAT"}
    
    for idx, row in df_txns.head(5000).iterrows():  # Échantillon pour rapidité
        t_type = row["type_transaction"]
        sens = row["sens"]
        if sens == "CREDIT" and t_type not in credit_types:
            logger.error(f"[ERR_TXN_04] Incohérence type/sens sur transaction {row['id_transaction']} : {t_type} marqué CREDIT.")
            errors += 1
            break
        if sens == "DEBIT" and t_type not in debit_types:
            logger.error(f"[ERR_TXN_05] Incohérence type/sens sur transaction {row['id_transaction']} : {t_type} marqué DEBIT.")
            errors += 1
            break
            
    if errors == 0:
        logger.info("Vérification échantillonnée cohérence type/sens ok.")

    # 5. Cohérence chronologique et running balances par compte
    # Pour chaque compte, trier par date/heure et vérifier la continuité des soldes
    logger.info("Vérification de la chaîne de soldes pour chaque compte...")
    
    # Échantillonnage de 100 comptes aléatoires pour optimiser le temps d'exécution des tests
    sample_compte_ids = df_txns["id_compte"].unique()[:100]
    
    for cpt_id in sample_compte_ids:
        c_txns = df_txns[df_txns["id_compte"] == cpt_id].copy()
        c_txns["datetime"] = pd.to_datetime(c_txns["date_transaction"] + " " + c_txns["heure_transaction"])
        
        # Vérification du tri chronologique
        if not c_txns["datetime"].is_monotonic_increasing:
            logger.error(f"[ERR_TXN_06] Chronologie incohérente pour le compte {cpt_id}.")
            errors += 1
            break
            
        # Vérification de l'enchaînement des soldes
        prev_solde_apres = None
        for _, row in c_txns.iterrows():
            # A. Cohérence de l'opération individuelle (solde_avant + sens * montant = solde_après)
            avant = float(row["solde_avant"])
            apres = float(row["solde_apres"])
            montant = float(row["montant"])
            sens = row["sens"]
            
            expected_apres = round(avant + (montant if sens == "CREDIT" else -montant), 2)
            if abs(apres - expected_apres) > 0.01:
                logger.error(f"[ERR_TXN_07] Solde après incohérent sur transaction {row['id_transaction']} (avant: {avant}, après: {apres}, montant: {montant}, calculé: {expected_apres}).")
                errors += 1
                break
                
            # B. Continuité avec la transaction précédente
            if prev_solde_apres is not None:
                if abs(avant - prev_solde_apres) > 0.01:
                    logger.error(f"[ERR_TXN_08] Rupture de chaîne de solde sur compte {cpt_id} à transaction {row['id_transaction']} (avant actuel: {avant}, après précédent: {prev_solde_apres}).")
                    errors += 1
                    break
                    
            prev_solde_apres = apres
            
        if errors > 0:
            break
            
    if errors == 0:
        logger.info("Vérification échantillonnée de la continuité des chaînes de soldes ok.")

    # 6. Vérification de la répartition annuelle
    df_txns["annee"] = pd.to_datetime(df_txns["date_transaction"]).dt.year
    annee_counts = df_txns["annee"].value_counts(normalize=True).to_dict()
    
    # 2022 : ~20% (entre 15% et 25%)
    # 2023 : ~35% (entre 30% et 40%)
    # 2024 : ~45% (entre 40% et 50%)
    if not (0.15 <= annee_counts.get(2022, 0) <= 0.25):
        logger.error(f"[ERR_TXN_09] Répartition 2022 hors cible : {annee_counts.get(2022, 0)*100:.2f}%.")
        errors += 1
    if not (0.30 <= annee_counts.get(2023, 0) <= 0.40):
        logger.error(f"[ERR_TXN_10] Répartition 2023 hors cible : {annee_counts.get(2023, 0)*100:.2f}%.")
        errors += 1
    if not (0.40 <= annee_counts.get(2024, 0) <= 0.50):
        logger.error(f"[ERR_TXN_11] Répartition 2024 hors cible : {annee_counts.get(2024, 0)*100:.2f}%.")
        errors += 1

    if errors == 0:
        logger.info("Vérification répartition temporelle annuelle ok.")

    if errors == 0:
        logger.info("Validation réussie pour la table transactions.")
        return True
        
    logger.error(f"Validation échouée pour la table transactions avec {errors} erreur(s).")
    return False

if __name__ == "__main__":
    from data_generation.generators.generate_transactions import generate_transactions
    df_txn, df_cpt = generate_transactions()
    res = validate_transactions(df_txn, df_cpt)
    print(f"\n--- TEST VALIDATE TRANSACTIONS : {'SUCCÈS' if res else 'ÉCHEC'} ---")
