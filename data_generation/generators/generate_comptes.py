# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_comptes.py
Description     : Générateur de données pour les comptes de dépôts et placements (DAT).
"""

import pandas as pd
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.utils.faker_utils import generate_rib
from data_generation.generators.generate_entreprises import generate_entreprises

def generate_comptes() -> pd.DataFrame:
    """
    Génère les comptes courants et les dépôts à terme (DAT) pour les 2000 entreprises.
    
    Returns:
        pd.DataFrame: DataFrame contenant les données des comptes.
    """
    logger.info("Début de la génération des comptes...")
    random.seed(42)  # Reproductibilité
    
    # Clear state in faker_utils to ensure reproducibility across repeated function calls
    if hasattr(generate_rib, "_used_ribs"):
        generate_rib._used_ribs.clear()
        
    # Chargement des entreprises sources
    df_entreprises = generate_entreprises()
    
    comptes: List[Dict[str, Any]] = []
    current_id = 1
    
    # Date limite de simulation pour le calcul des mouvements
    sim_end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    
    for _, ent in df_entreprises.iterrows():
        ent_id = int(ent["id_entreprise"])
        ag_id = int(ent["id_agence"])
        cons_id = int(ent["id_conseiller"])
        segment = ent["segment"]
        date_creation_ent = datetime.strptime(str(ent["date_creation"]), "%Y-%m-%d")
        
        # 1. Détermination de la liquidité totale de l'entreprise
        if segment == "TPE":
            total_cash = random.uniform(5000.0, 500000.0)
        elif segment == "PME":
            total_cash = random.uniform(100000.0, 10000000.0)
        else:  # Grande Entreprise
            total_cash = random.uniform(1000000.0, 100000000.0)
            
        # 2. Détermination de la présence d'un DAT (25% de probabilité)
        has_dat = random.random() < 0.25
        
        if has_dat:
            # Répartition de la liquidité : 60% à 80% dans le courant, le reste en DAT
            ratio_courant = random.uniform(0.60, 0.80)
            solde_courant = round(total_cash * ratio_courant, 2)
            solde_dat = round(total_cash * (1.0 - ratio_courant), 2)
        else:
            solde_courant = round(total_cash, 2)
            solde_dat = 0.0
            
        # --- A. COMPTE COURANT ---
        # Date d'ouverture : date création entreprise + 0 à 30 jours
        date_ouv_courant = date_creation_ent + timedelta(days=random.randint(0, 30))
        
        rib_courant = generate_rib()
        iban_courant = f"MA64{rib_courant}"
        num_compte_courant = rib_courant[6:22]
        
        # Date de dernier mouvement (entre l'ouverture et fin 2024)
        days_since_open = (sim_end_date - date_ouv_courant).days
        if days_since_open > 0:
            date_mvt_courant = date_ouv_courant + timedelta(days=random.randint(0, days_since_open))
        else:
            date_mvt_courant = date_ouv_courant
            
        # Classification d'activité basée sur l'ancienneté du dernier mouvement
        days_inactive = (sim_end_date - date_mvt_courant).days
        if days_inactive < 90:
            classification = "Actif"
        elif days_inactive < 180:
            classification = "Faiblement actif"
        else:
            classification = "Inactif"
            
        solde_moyen = round(solde_courant * random.uniform(0.90, 1.10), 2)
        
        # Statut du compte
        statut = "ACTIF" if classification != "Inactif" or random.random() < 0.80 else "INACTIF"
        
        compte_courant_id = current_id
        cc = {
            "id_compte": compte_courant_id,
            "numero_compte": num_compte_courant,
            "rib": rib_courant,
            "RIB": rib_courant, # Alias
            "iban": iban_courant,
            "IBAN": iban_courant, # Alias
            "type_compte": "COURANT",
            "devise": "MAD",
            "date_ouverture": date_ouv_courant.strftime("%Y-%m-%d"),
            "statut": statut,
            "solde_actuel": solde_courant,
            "id_entreprise": ent_id,
            "entreprise_id": ent_id, # Alias
            "id_agence": ag_id,
            "agence_id": ag_id, # Alias
            "id_conseiller": cons_id,
            "conseiller_id": cons_id, # Alias
            "id_compte_courant_parent": None,
            "compte_parent_id": None, # Alias
            "date_dernier_mouvement": date_mvt_courant.strftime("%Y-%m-%d"),
            "solde_moyen_trimestriel": solde_moyen,
            "classification": classification
        }
        comptes.append(cc)
        current_id += 1
        
        # --- B. COMPTE DAT (si éligible) ---
        if has_dat:
            # Date d'ouverture : courant + 30 à 365 jours (cohérent)
            # Ne doit pas dépasser la fin de simulation
            days_to_add = random.randint(30, 365)
            date_ouv_dat = date_ouv_courant + timedelta(days=days_to_add)
            if date_ouv_dat > sim_end_date:
                date_ouv_dat = sim_end_date - timedelta(days=random.randint(10, 90))
                
            rib_dat = generate_rib()
            iban_dat = f"MA64{rib_dat}"
            num_compte_dat = rib_dat[6:22]
            
            # Pour un DAT, le dernier mouvement est souvent la date d'ouverture
            solde_moyen_dat = solde_dat
            
            dat = {
                "id_compte": current_id,
                "numero_compte": num_compte_dat,
                "rib": rib_dat,
                "RIB": rib_dat, # Alias
                "iban": iban_dat,
                "IBAN": iban_dat, # Alias
                "type_compte": "DAT",
                "devise": "MAD",
                "date_ouverture": date_ouv_dat.strftime("%Y-%m-%d"),
                "statut": "ACTIF",
                "solde_actuel": solde_dat,
                "id_entreprise": ent_id,
                "entreprise_id": ent_id, # Alias
                "id_agence": ag_id,
                "agence_id": ag_id, # Alias
                "id_conseiller": cons_id,
                "conseiller_id": cons_id, # Alias
                "id_compte_courant_parent": compte_courant_id,
                "compte_parent_id": compte_courant_id, # Alias
                "date_dernier_mouvement": date_ouv_dat.strftime("%Y-%m-%d"),
                "solde_moyen_trimestriel": solde_moyen_dat,
                "classification": "Actif"
            }
            comptes.append(dat)
            current_id += 1
            
    df_comptes = pd.DataFrame(comptes)
    logger.info(f"Génération terminée : {len(df_comptes)} comptes générés.")
    return df_comptes

if __name__ == "__main__":
    df = generate_comptes()
    print("\n--- TEST GENERATE COMPTES ---")
    print(df.head(10))
    
    print("\n--- REPARTITION DES TYPES DE COMPTE ---")
    print(df["type_compte"].value_counts())
    
    print("\n--- STATISTIQUES DES SOLDES PAR TYPE ---")
    print(df.groupby("type_compte")["solde_actuel"].describe())
    
    print("\n--- NOMBRE DE COMPTES PAR AGENCE ---")
    print(df["id_agence"].value_counts().sort_index())
