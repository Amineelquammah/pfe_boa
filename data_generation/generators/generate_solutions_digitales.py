# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_solutions_digitales.py
Description     : Générateur du catalogue des solutions de Digital Banking BOA.
"""

import pandas as pd
from data_generation.utils.logger import logger

def generate_solutions_digitales() -> pd.DataFrame:
    """
    Génère le catalogue des 5 solutions de Digital Banking de BOA.
    
    Returns:
        pd.DataFrame: DataFrame des solutions digitales.
    """
    logger.info("Début de la génération des solutions digitales...")
    
    solutions = [
        {
            "id_solution": 1,
            "nom_solution": "DabaPay Pro",
            "description": "Portefeuille mobile pour recevoir, transférer, payer les marchands et retirer sur GAB sans carte",
            "canal": "MOBILE",
            "statut": "ACTIF"
        },
        {
            "id_solution": 2,
            "nom_solution": "Business Online",
            "description": "Portail web pour consultation de comptes, virements en masse, Cash Management et Trade Finance",
            "canal": "WEB",
            "statut": "ACTIF"
        },
        {
            "id_solution": 3,
            "nom_solution": "CreditBusinessOnline",
            "description": "Plateforme web de consultation, demande et suivi en temps réel des dossiers de crédits d'entreprises",
            "canal": "WEB",
            "statut": "ACTIF"
        },
        {
            "id_solution": 4,
            "nom_solution": "KODI",
            "description": "Assistant conversationnel et FAQ intelligent d'accompagnement client et de suivi des requêtes",
            "canal": "ASSISTANT",
            "statut": "ACTIF"
        },
        {
            "id_solution": 5,
            "nom_solution": "WhatsApp Business",
            "description": "Service client automatisé et notifications par messagerie instantanée WhatsApp",
            "canal": "MOBILE",
            "statut": "ACTIF"
        }
    ]
    
    df_solutions = pd.DataFrame(solutions)
    logger.info(f"Génération terminée : {len(df_solutions)} solutions digitales créées.")
    return df_solutions

if __name__ == "__main__":
    df = generate_solutions_digitales()
    print("\n--- TEST GENERATE SOLUTIONS DIGITALES ---")
    print(df)
