# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_transactions.py
Description     : Générateur des transactions bancaires courantes et financières (2022-2024).
"""

import pandas as pd
import random
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.generators.generate_comptes import generate_comptes
from data_generation.generators.generate_contrats_credits import generate_contrats_credits

def generate_transactions(df_comptes_in: pd.DataFrame = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Génère environ 150 000 transactions sur la période 2022-2024,
    recalculant chronologiquement les soldes et mettant à jour le solde final des comptes.
    
    Args:
        df_comptes_in (pd.DataFrame): DataFrame des comptes facultatif.
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (df_transactions, df_comptes_mis_a_jour)
    """
    logger.info("Début de la génération des transactions...")
    random.seed(42)  # Reproductibilité
    
    # Chargement des données d'entrée
    df_comptes = df_comptes_in if df_comptes_in is not None else generate_comptes()
    df_contrats = generate_contrats_credits()
    
    # Dictionnaires d'indexation pour accès rapides
    comptes_list = df_comptes.to_dict(orient="records")
    comptes_by_id = {c["id_compte"]: c for c in comptes_list}
    comptes_by_ent = {}
    for c in comptes_list:
        comptes_by_ent.setdefault(c["id_entreprise"], []).append(c)
        
    # Organiser les contrats par entreprise
    contrats_by_ent = {}
    for _, row in df_contrats.iterrows():
        contrats_by_ent.setdefault(int(row["id_entreprise"]), []).append(row.to_dict())
        
    all_txns: List[Dict[str, Any]] = []
    current_txn_id = 1
    sim_end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    sim_start_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
    
    # Typologie de transactions par sens
    CREDIT_TYPES = ["Virement entrant", "Encaissement client", "Versement"]
    DEBIT_TYPES = ["Virement sortant", "Paiement fournisseur", "Retrait", "Prélèvement"]
    
    # Canaux et probabilités par segment d'entreprise
    CANALS_BY_SEGMENT = {
        "TPE": (["ATM/GAB", "Agence", "DabaPay Pro"], [0.45, 0.25, 0.30]),
        "PME": (["Business Online", "DabaPay Pro", "ATM/GAB", "Agence"], [0.55, 0.25, 0.10, 0.10]),
        "Grande Entreprise": (["Business Online", "API Entreprise", "Agence"], [0.50, 0.45, 0.05])
    }
    
    # Autorisations de découvert par segment
    OVERDRAFT_LIMITS = {
        "TPE": 20000.0,
        "PME": 150000.0,
        "Grande Entreprise": 1500000.0
    }
    
    # 1. GENERATION DE LA TRAME CHRONOLOGIQUE DES TRANSACTIONS COURANTES
    logger.info("Simulation des transactions courantes...")
    for c in comptes_list:
        if c["type_compte"] == "DAT":
            # Les DAT n'ont pas d'opérations courantes
            continue
            
        ent_id = c["id_entreprise"]
        compte_id = c["id_compte"]
        ag_id = c["id_agence"]
        cons_id = c["id_conseiller"]
        
        # Récupération de la classification de l'entreprise
        # On va chercher son segment
        # Pour éviter de joindre avec df_entreprises à chaque fois, on déduit le segment du solde cible
        solde_cible = float(c["solde_actuel"])
        if solde_cible < 600000.0:
            segment = "TPE"
            nb_txns_target = random.randint(27, 45)
        elif solde_cible < 12000000.0:
            segment = "PME"
            nb_txns_target = random.randint(78, 114)
        else:
            segment = "Grande Entreprise"
            nb_txns_target = random.randint(192, 264)
            
        date_ouv = datetime.strptime(c["date_ouverture"], "%Y-%m-%d")
        effective_start = max(sim_start_date, date_ouv)
        active_days = (sim_end_date - effective_start).days
        
        if active_days <= 0:
            active_days = 30
            effective_start = sim_end_date - timedelta(days=30)
            
        # Calculer le volume de transaction réel prorata temporis
        nb_txns = int(nb_txns_target * (active_days / 1095.0))
        nb_txns = max(5, nb_txns)
        
        # Générer des dates croissantes pour ce compte avec la répartition annuelle demandée (20% pour 2022, 35% pour 2023, 45% pour 2024)
        txn_dates: List[datetime] = []
        for _ in range(nb_txns):
            eligible_years = []
            weights = []
            
            if effective_start.year <= 2022:
                eligible_years.append(2022)
                weights.append(0.171)
            if effective_start.year <= 2023:
                eligible_years.append(2023)
                weights.append(0.349)
            if effective_start.year <= 2024:
                eligible_years.append(2024)
                weights.append(0.480)
                
            if not eligible_years:
                eligible_years.append(2024)
                weights.append(1.0)
                
            total_w = sum(weights)
            weights = [w / total_w for w in weights]
            
            chosen_year = random.choices(eligible_years, weights=weights, k=1)[0]
            
            year_start = datetime(chosen_year, 1, 1)
            year_end = datetime(chosen_year, 12, 31)
            
            start_dt = max(effective_start, year_start)
            if start_dt > year_end:
                start_dt = year_end - timedelta(days=30)
                
            days_range = (year_end - start_dt).days
            offset = random.randint(0, max(0, days_range))
            txn_dates.append(start_dt + timedelta(days=offset))
            
        txn_dates.sort()
        
        # Variables de solde temporaire
        # On commence à 60% du solde cible pour permettre des fluctuations
        running_bal = round(solde_cible * 0.60, 2)
        overdraft = OVERDRAFT_LIMITS[segment]
        
        # Générer chaque transaction courante
        for dt in txn_dates:
            # Choix du sens
            sens = "CREDIT" if random.random() < 0.48 else "DEBIT"
            
            # Choix du type et canal
            if sens == "CREDIT":
                t_type = random.choice(CREDIT_TYPES)
            else:
                t_type = random.choice(DEBIT_TYPES)
                
            canals, probas = CANALS_BY_SEGMENT[segment]
            canal = random.choices(canals, weights=probas, k=1)[0]
            
            # Détermination du montant
            if segment == "TPE":
                amount = random.uniform(200.0, 15000.0)
            elif segment == "PME":
                amount = random.uniform(2000.0, 150000.0)
            else:
                amount = random.uniform(20000.0, 1500000.0)
            amount = round(amount, 2)
            
            # Vérification de la limite de découvert pour les DEBITS
            if sens == "DEBIT" and (running_bal - amount) < -overdraft:
                # Réduction du montant pour rester dans la limite ou transformation en crédit
                amount = round(running_bal + overdraft - 100.0, 2)
                if amount < 10.0:
                    # Trop bas, on force un versement de trésorerie (CREDIT)
                    sens = "CREDIT"
                    t_type = "Versement"
                    amount = round(random.uniform(5000.0, 20000.0), 2)
                    
            solde_avant = running_bal
            if sens == "CREDIT":
                running_bal = round(running_bal + amount, 2)
            else:
                running_bal = round(running_bal - amount, 2)
            solde_apres = running_bal
            
            # Heure aléatoire
            hour = random.randint(8, 18)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            
            txn = {
                "id_transaction": current_txn_id,
                "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": compte_id,
                "id_entreprise": ent_id,
                "id_agence": ag_id,
                "id_conseiller": cons_id,
                "date_transaction": dt.strftime("%Y-%m-%d"),
                "heure_transaction": time_str,
                "type_transaction": t_type,
                "canal": canal,
                "sens": sens,
                "montant": amount,
                "solde_avant": solde_avant,
                "solde_apres": solde_apres,
                "statut": "VALIDE",
                "commentaire": f"Opération {t_type} de trésorerie"
            }
            all_txns.append(txn)
            current_txn_id += 1
            
        # Sauvegarde du solde courant temporaire pour y greffer les échéances et DAT
        c["_temp_running_bal"] = running_bal

    # ---------------------------------------------------------
    # 2. INTÉGRATION DES OPÉRATIONS FINANCIÈRES (CRÉDITS & DAT)
    # ---------------------------------------------------------
    logger.info("Simulation des opérations financières (crédits et DAT)...")
    
    # A. Placements & Clôtures DAT
    for c in comptes_list:
        if c["type_compte"] != "DAT":
            continue
            
        # C'est un DAT
        parent_id = c["id_compte_courant_parent"]
        parent_c = comptes_by_id[parent_id]
        solde_dat = float(c["solde_actuel"])
        date_ouv_dat = datetime.strptime(c["date_ouverture"], "%Y-%m-%d")
        
        # Placement DAT : DEBIT sur courant, CREDIT sur DAT
        if sim_start_date <= date_ouv_dat <= sim_end_date:
            # 1. Transaction sur le Courant
            parent_bal_avant = parent_c["_temp_running_bal"]
            parent_c["_temp_running_bal"] = round(parent_bal_avant - solde_dat, 2)
            
            txn_placement_cc = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": parent_id,
                "id_entreprise": c["id_entreprise"],
                "id_agence": c["id_agence"],
                "id_conseiller": c["id_conseiller"],
                "date_transaction": date_ouv_dat.strftime("%Y-%m-%d"), "heure_transaction": "11:00:00",
                "type_transaction": "Placement DAT", "canal": "Agence", "sens": "DEBIT", "montant": solde_dat,
                "solde_avant": parent_bal_avant, "solde_apres": parent_c["_temp_running_bal"],
                "statut": "VALIDE", "commentaire": f"Placement Dépôt à Terme réf DAT_{c['id_compte']}"
            }
            all_txns.append(txn_placement_cc)
            current_txn_id += 1
            
            # 2. Transaction sur le DAT
            txn_placement_dat = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": c["id_compte"],
                "id_entreprise": c["id_entreprise"],
                "id_agence": c["id_agence"],
                "id_conseiller": c["id_conseiller"],
                "date_transaction": date_ouv_dat.strftime("%Y-%m-%d"), "heure_transaction": "11:05:00",
                "type_transaction": "Placement DAT", "canal": "Agence", "sens": "CREDIT", "montant": solde_dat,
                "solde_avant": 0.0, "solde_apres": solde_dat,
                "statut": "VALIDE", "commentaire": f"Dépôt de capital DAT"
            }
            all_txns.append(txn_placement_dat)
            current_txn_id += 1
            
        # Clôture du DAT si expiré avant le 31/12/2024 (on simule qu'il dure 12 mois)
        date_mat_dat = date_ouv_dat + timedelta(days=365)
        if sim_start_date <= date_mat_dat <= sim_end_date:
            interest_gain = round(solde_dat * 0.035, 2)  # 3.5% d'intérêt
            solde_total_retour = round(solde_dat + interest_gain, 2)
            
            # Débit du DAT
            txn_cloture_dat = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": c["id_compte"],
                "id_entreprise": c["id_entreprise"],
                "id_agence": c["id_agence"],
                "id_conseiller": c["id_conseiller"],
                "date_transaction": date_mat_dat.strftime("%Y-%m-%d"), "heure_transaction": "15:00:00",
                "type_transaction": "Clôture DAT", "canal": "Agence", "sens": "DEBIT", "montant": solde_dat,
                "solde_avant": solde_dat, "solde_apres": 0.0,
                "statut": "VALIDE", "commentaire": f"Clôture de contrat DAT et libération des fonds"
            }
            all_txns.append(txn_cloture_dat)
            current_txn_id += 1
            
            # Crédit du courant parent
            parent_bal_avant = parent_c["_temp_running_bal"]
            parent_c["_temp_running_bal"] = round(parent_bal_avant + solde_total_retour, 2)
            
            txn_cloture_cc = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": parent_id,
                "id_entreprise": c["id_entreprise"],
                "id_agence": c["id_agence"],
                "id_conseiller": c["id_conseiller"],
                "date_transaction": date_mat_dat.strftime("%Y-%m-%d"), "heure_transaction": "15:10:00",
                "type_transaction": "Clôture DAT", "canal": "Agence", "sens": "CREDIT", "montant": solde_total_retour,
                "solde_avant": parent_bal_avant, "solde_apres": parent_c["_temp_running_bal"],
                "statut": "VALIDE", "commentaire": f"Retour de fonds DAT avec intérêts cumulés"
            }
            all_txns.append(txn_cloture_cc)
            current_txn_id += 1

    # B. Décaissements & Remboursements de Crédits
    for _, contrat in df_contrats.iterrows():
        ent_id = int(contrat["id_entreprise"])
        if ent_id not in comptes_by_ent:
            continue
            
        # Récupérer le compte courant de l'entreprise
        cc_accounts = [acc for acc in comptes_by_ent[ent_id] if acc["type_compte"] == "COURANT"]
        if not cc_accounts:
            continue
        cc = cc_accounts[0]
        cc_id = cc["id_compte"]
        
        montant_accorde = float(contrat["montant_principal"])
        mensualite = float(contrat["mensualite"])
        date_octroi = datetime.strptime(str(contrat["date_octroi"]), "%Y-%m-%d")
        date_1ere_ech = datetime.strptime(str(contrat["date_premiere_echeance"]), "%Y-%m-%d")
        duree = int(contrat["duree"])
        
        # 1. Transaction de Décaissement du Crédit (CREDIT sur courant)
        if sim_start_date <= date_octroi <= sim_end_date:
            parent_bal_avant = cc["_temp_running_bal"]
            cc["_temp_running_bal"] = round(parent_bal_avant + montant_accorde, 2)
            
            txn_decaissement = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": cc_id,
                "id_entreprise": ent_id,
                "id_agence": cc["id_agence"],
                "id_conseiller": cc["id_conseiller"],
                "date_transaction": date_octroi.strftime("%Y-%m-%d"), "heure_transaction": "09:30:00",
                "type_transaction": "Virement entrant", "canal": "API Entreprise", "sens": "CREDIT", "montant": montant_accorde,
                "solde_avant": parent_bal_avant, "solde_apres": cc["_temp_running_bal"],
                "statut": "VALIDE", "commentaire": f"Décaissement de prêt BOA Ref CON_{contrat['id_contrat']:06d}"
            }
            all_txns.append(txn_decaissement)
            current_txn_id += 1
            
        # 2. Échéances mensuelles de remboursement (DEBIT sur courant)
        for m in range(duree):
            date_ech = date_1ere_ech + timedelta(days=int(m * 30.4))
            if date_ech > sim_end_date:
                break
            if date_ech < sim_start_date:
                continue
                
            # Si le crédit est NPL, certains mois ne sont pas remboursés
            # (simulé par rapport aux jours de retard)
            if contrat["statut"] == "NPL" and m >= (duree - int(contrat["jours_retard"] / 30)):
                # Client en défaut, ne paie plus les mensualités
                continue
                
            parent_bal_avant = cc["_temp_running_bal"]
            cc["_temp_running_bal"] = round(parent_bal_avant - mensualite, 2)
            
            txn_echeance = {
                "id_transaction": current_txn_id, "reference_transaction": f"TXN_{current_txn_id:08d}",
                "id_compte": cc_id,
                "id_entreprise": ent_id,
                "id_agence": cc["id_agence"],
                "id_conseiller": cc["id_conseiller"],
                "date_transaction": date_ech.strftime("%Y-%m-%d"), "heure_transaction": "00:05:00",
                "type_transaction": "Paiement échéance crédit", "canal": "API Entreprise", "sens": "DEBIT", "montant": mensualite,
                "solde_avant": parent_bal_avant, "solde_apres": cc["_temp_running_bal"],
                "statut": "VALIDE", "commentaire": f"Prélèvement échéance crédit CON_{contrat['id_contrat']:06d}"
            }
            all_txns.append(txn_echeance)
            current_txn_id += 1

    # ---------------------------------------------------------
    # 3. RECONSTRUCTION CHRONOLOGIQUE ET CALCUL DES SOLDES FINAUX
    # ---------------------------------------------------------
    logger.info("Tri chronologique et recalcul final des balances...")
    df_txns = pd.DataFrame(all_txns)
    
    # Tri par compte et par date/heure
    df_txns.sort_values(by=["id_compte", "date_transaction", "heure_transaction"], inplace=True)
    df_txns.reset_index(drop=True, inplace=True)
    
    # Recalculer les identifiants et les références pour qu'ils soient ordonnés chronologiquement au global
    df_txns.sort_values(by=["date_transaction", "heure_transaction", "id_transaction"], inplace=True)
    df_txns.reset_index(drop=True, inplace=True)
    
    df_txns["id_transaction"] = range(1, len(df_txns) + 1)
    df_txns["reference_transaction"] = df_txns["id_transaction"].apply(lambda x: f"TXN_{x:08d}")
    
    # Recalcul chronologique des soldes pour chaque compte individuel
    logger.info("Recalcul final des soldes courants...")
    comptes_final_soldes = {}
    
    # Groupement des transactions par compte pour recalculer la chaîne de soldes
    for cpt_id, group in df_txns.groupby("id_compte"):
        group_indices = group.index.tolist()
        
        # On va chercher le solde cible de départ ou on initialise
        c_meta = comptes_by_id[cpt_id]
        
        # Solde initial calculé pour correspondre au solde final
        # Solde de départ du compte
        # On prend le solde actuel ciblé dans comptes.py
        target_final_solde = float(c_meta["solde_actuel"])
        
        # On parcourt le groupe une première fois pour faire le bilan Débit/Crédit
        bilan = 0.0
        for idx in group_indices:
            row = df_txns.loc[idx]
            m = float(row["montant"])
            if row["sens"] == "CREDIT":
                bilan += m
            else:
                bilan -= m
                
        # Le solde initial doit être : target_final_solde - bilan
        solde_initial = round(target_final_solde - bilan, 2)
        if solde_initial < 0:
            # Éviter de démarrer en négatif si possible (on décale les soldes)
            solde_initial = 1000.0 if c_meta["type_compte"] == "COURANT" else 0.0
            
        current_bal = solde_initial
        
        for idx in group_indices:
            row = df_txns.loc[idx]
            m = float(row["montant"])
            
            solde_avant = current_bal
            if row["sens"] == "CREDIT":
                current_bal = round(current_bal + m, 2)
            else:
                current_bal = round(current_bal - m, 2)
            solde_apres = current_bal
            
            df_txns.at[idx, "solde_avant"] = solde_avant
            df_txns.at[idx, "solde_apres"] = solde_apres
            
        # Sauvegarde du solde final réel
        comptes_final_soldes[cpt_id] = current_bal

    # Mise à jour des soldes dans le DataFrame des comptes
    for c in comptes_list:
        cpt_id = c["id_compte"]
        if cpt_id in comptes_final_soldes:
            c["solde_actuel"] = comptes_final_soldes[cpt_id]
            # Mettre à jour également le solde moyen trimestriel pour la cohérence
            c["solde_moyen_trimestriel"] = round(c["solde_actuel"] * random.uniform(0.95, 1.05), 2)
            
    df_comptes_updated = pd.DataFrame(comptes_list)
    
    # Retirer les colonnes temporaires
    if "_temp_running_bal" in df_comptes_updated.columns:
        df_comptes_updated.drop(columns=["_temp_running_bal"], inplace=True)
        
    logger.info(f"Génération terminée : {len(df_txns)} transactions simulées.")
    return df_txns, df_comptes_updated

if __name__ == "__main__":
    df_txns, df_comptes_up = generate_transactions()
    print("\n--- TEST GENERATE TRANSACTIONS ---")
    print(df_txns.head(5))
    
    print("\n--- VOLUMÉTRIE TOTALE ---")
    print(f"Transactions : {len(df_txns)}")
    
    print("\n--- RÉPARTITION PAR CANAL ---")
    print(df_txns["canal"].value_counts())
    
    print("\n--- RÉPARTITION PAR TYPE DE TRANSACTION ---")
    print(df_txns["type_transaction"].value_counts())
    
    print("\n--- MONTANT MOYEN PAR SENS ---")
    print(df_txns.groupby("sens")["montant"].mean())
