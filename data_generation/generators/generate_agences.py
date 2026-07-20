# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_agences.py
Description     : Générateur de données pour les agences bancaires BOA.
"""

import pandas as pd
import random
from data_generation.utils.logger import logger
from data_generation.utils.faker_utils import fake

def generate_agences() -> pd.DataFrame:
    """
    Génère le référentiel des 10 agences réparties sur les 7 régions de BOA.
    
    Returns:
        pd.DataFrame: DataFrame contenant les données des agences.
    """
    logger.info("Début de la génération des agences...")
    
    # Définition statique des 10 agences pour correspondre aux spécifications de distribution
    agences_data = [
        # Casablanca-Settat (ID Region: 1, 2 agences)
        {"id_agence": 1, "code_agence": "AGE_001", "nom_agence": "BOA Casablanca Zerktouni", "ville": "Casablanca", "id_region": 1},
        {"id_agence": 2, "code_agence": "AGE_002", "nom_agence": "BOA Mohammedia Centre", "ville": "Mohammedia", "id_region": 1},
        
        # Rabat-Salé-Kénitra (ID Region: 2, 2 agences)
        {"id_agence": 3, "code_agence": "AGE_003", "nom_agence": "BOA Rabat Riad", "ville": "Rabat", "id_region": 2},
        {"id_agence": 4, "code_agence": "AGE_004", "nom_agence": "BOA Kénitra Maâmora", "ville": "Kénitra", "id_region": 2},
        
        # Fès-Meknès (ID Region: 3, 1 agence)
        {"id_agence": 5, "code_agence": "AGE_005", "nom_agence": "BOA Fès Hassan II", "ville": "Fès", "id_region": 3},
        
        # Marrakech-Safi (ID Region: 4, 1 agence)
        {"id_agence": 6, "code_agence": "AGE_006", "nom_agence": "BOA Marrakech Guéliz", "ville": "Marrakech", "id_region": 4},
        
        # Tanger-Tétouan-Al Hoceïma (ID Region: 5, 1 agence)
        {"id_agence": 7, "code_agence": "AGE_007", "nom_agence": "BOA Tanger Zone Franche", "ville": "Tanger", "id_region": 5},
        
        # Oriental (ID Region: 6, 1 agence)
        {"id_agence": 8, "code_agence": "AGE_008", "nom_agence": "BOA Oujda Al Qods", "ville": "Oujda", "id_region": 6},
        
        # Sud (ID Region: 7, 2 agences)
        {"id_agence": 9, "code_agence": "AGE_009", "nom_agence": "BOA Agadir Port", "ville": "Agadir", "id_region": 7},
        {"id_agence": 10, "code_agence": "AGE_010", "nom_agence": "BOA Laâyoune Place Dcheira", "ville": "Laâyoune", "id_region": 7}
    ]
    
    # Ajout des informations complémentaires (adresse, date_ouverture, statut)
    # Graine fixe pour garantir la reproductibilité
    random.seed(42)
    
    for agence in agences_data:
        # Génération d'une adresse marocaine réaliste fictive
        agence["adresse"] = f"N° {random.randint(10, 250)}, Avenue des FAR, {agence['ville']}, Maroc"
        # Date d'ouverture fictive entre 2005 et 2018
        year = random.randint(2005, 2018)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        agence["date_ouverture"] = f"{year:04d}-{month:02d}-{day:02d}"
        agence["statut"] = "Active"
        # Ajout de l'alias region_id pour la compatibilité demandée
        agence["region_id"] = agence["id_region"]
        
    df_agences = pd.DataFrame(agences_data)
    
    logger.info(f"Génération terminée : {len(df_agences)} agences générées.")
    return df_agences

if __name__ == "__main__":
    df = generate_agences()
    print("\n--- TEST GENERATE AGENCES ---")
    print(df)
    
    print("\n--- DISTRIBUTION DES AGENCES PAR REGION ---")
    print(df.groupby("id_region").size())
