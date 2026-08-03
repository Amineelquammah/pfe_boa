# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_souscriptions.py
Description     : Générateur de données pour les souscriptions des entreprises aux solutions digitales.
"""

import pandas as pd
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_solutions_digitales import generate_solutions_digitales

def generate_souscriptions() -> pd.DataFrame:
    """
    Génère environ 3500 souscriptions uniques (id_entreprise, id_solution).
    
    Returns:
        pd.DataFrame: DataFrame des souscriptions digitales.
    """
    logger.info("Début de la génération des souscriptions...")
    random.seed(42)  # Reproductibilité
    
    # Chargement des entreprises et du catalogue des solutions
    df_entreprises = generate_entreprises()
    df_solutions = generate_solutions_digitales()
    
    # Probabilités ajustées (divisées par 2) pour atteindre la cible globale de ~3500 souscriptions
    # tout en conservant les proportions cibles relatives des solutions
    PROBAS_SOLUTION = {
        1: 0.35,  # DabaPay Pro (70% / 2)
        2: 0.475, # Business Online (95% / 2)
        3: 0.20,  # CreditBusinessOnline (40% / 2)
        4: 0.325, # KODI (65% / 2)
        5: 0.45   # WhatsApp Business (90% / 2)
    }
    
    souscriptions: List[Dict[str, Any]] = []
    current_id = 1
    sim_end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    
    for _, ent in df_entreprises.iterrows():
        ent_id = int(ent["id_entreprise"])
        date_creation_ent = datetime.strptime(str(ent["date_creation"]), "%Y-%m-%d")
        
        # Pour chaque solution du catalogue, décider si l'entreprise y souscrit
        for sol_id, prob in PROBAS_SOLUTION.items():
            if random.random() <= prob:
                # Date de souscription : après la création de l'entreprise et après le début de la simulation (2022-01-01)
                start_sim = datetime(2022, 1, 1)
                effective_start = max(date_creation_ent, start_sim)
                days_since_creation = (sim_end_date - effective_start).days
                if days_since_creation > 30:
                    date_sous = effective_start + timedelta(days=random.randint(15, min(days_since_creation, 365)))
                else:
                    date_sous = effective_start + timedelta(days=random.randint(1, 15))
                    
                if date_sous > sim_end_date:
                    date_sous = sim_end_date - timedelta(days=random.randint(1, 30))
                    
                # Niveau d'utilisation
                niveau = random.choice(["FAIBLE", "MOYEN", "ELEVE"])
                # Statut (95% Actif, 5% Résilié)
                statut = "ACTIF" if random.random() < 0.95 else "RESILIE"
                
                sub = {
                    "id_souscription": current_id,
                    "id_entreprise": ent_id,
                    "id_solution": sol_id,
                    "date_souscription": date_sous.strftime("%Y-%m-%d"),
                    "statut": statut,
                    "niveau_utilisation": niveau
                }
                souscriptions.append(sub)
                current_id += 1
                
    df_souscriptions = pd.DataFrame(souscriptions)
    logger.info(f"Génération terminée : {len(df_souscriptions)} souscriptions digitales générées.")
    return df_souscriptions

if __name__ == "__main__":
    df = generate_souscriptions()
    print("\n--- TEST GENERATE SOUSCRIPTIONS ---")
    print(df.head(5))
    
    print("\n--- NOMBRE TOTAL DE SOUSCRIPTIONS ---")
    print(len(df))
    
    print("\n--- EQUIPEMENT PAR SOLUTION (RAPPORTS) ---")
    print(df["id_solution"].value_counts())
