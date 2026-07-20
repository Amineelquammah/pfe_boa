# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_connexions.py
Description     : Générateur de données pour l'historique des sessions et connexions digitales.
"""

import pandas as pd
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_souscriptions import generate_souscriptions

# Actions métiers par solution digitale
ACTIONS_BY_SOLUTION = {
    1: ["recevoir", "transférer", "retrait GAB", "paiement"],  # DabaPay Pro
    2: ["consultation", "virement", "téléchargement relevé", "validation paiement", "Trade Finance"],  # Business Online
    3: ["simulation", "demande", "suivi dossier"],  # CreditBusinessOnline
    4: ["question", "assistance", "réclamation"],  # KODI
    5: ["conversation", "suivi dossier", "demande information"]  # WhatsApp Business
}

def generate_connexions() -> pd.DataFrame:
    """
    Génère environ 100 000 connexions digitales réparties chronologiquement
    et corrélées avec la digitalisation des entreprises.
    
    Returns:
        pd.DataFrame: DataFrame des connexions.
    """
    logger.info("Début de la génération des connexions...")
    random.seed(42)  # Reproductibilité
    
    # Chargement des tables parentes
    df_entreprises = generate_entreprises()
    df_souscriptions = generate_souscriptions()
    
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    
    connexions: List[Dict[str, Any]] = []
    current_id = 1
    sim_end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    
    # Équipements de navigation (systèmes, navigateurs, appareils) par canal
    WEB_ENV = {
        "appareils": ["Desktop", "Tablet"],
        "systemes": ["Windows", "macOS", "Linux"],
        "navigateurs": ["Chrome", "Firefox", "Safari", "Edge"]
    }
    MOBILE_ENV = {
        "appareils": ["Mobile"],
        "systemes": ["Android", "iOS"],
        "navigateurs": ["Mobile App", "WhatsApp Client"]
    }
    
    # Multiplicateurs d'activité par segment et niveau d'utilisation
    SEGMENT_MULTIPLIERS = {"TPE": 1.0, "PME": 2.0, "Grande Entreprise": 3.5}
    USE_MULTIPLIERS = {"FAIBLE": 0.5, "MOYEN": 1.5, "ELEVE": 3.0}
    
    for _, sub in df_souscriptions.iterrows():
        ent_id = int(sub["id_entreprise"])
        sol_id = int(sub["id_solution"])
        date_sous = datetime.strptime(str(sub["date_souscription"]), "%Y-%m-%d")
        niveau_util = sub["niveau_utilisation"]
        statut_sub = sub["statut"]
        
        # Ignorer si la souscription est résiliée trop tôt (on simplifie)
        if statut_sub == "RESILIE" and random.random() < 0.80:
            continue
            
        ent_meta = ent_dict[ent_id]
        segment = ent_meta["segment"]
        
        # Calcul des jours d'activité
        active_days = (sim_end_date - date_sous).days
        if active_days <= 0:
            active_days = 30
            date_sous = sim_end_date - timedelta(days=30)
            
        # Calcul du volume de connexion pour cette souscription
        base_freq = 7.5  # Fréquence de base calibrée pour ~100 000 connexions au total
        seg_mult = SEGMENT_MULTIPLIERS[segment]
        use_mult = USE_MULTIPLIERS[niveau_util]
        
        nb_conn = int(base_freq * seg_mult * use_mult * (active_days / 365.25))
        nb_conn = max(1, nb_conn)
        
        # Générer des dates croissantes pour cette souscription avec la répartition annuelle demandée
        conn_dates = []
        for _ in range(nb_conn):
            eligible_years = []
            weights = []
            
            if date_sous.year <= 2022:
                eligible_years.append(2022)
                weights.append(0.20)
            if date_sous.year <= 2023:
                eligible_years.append(2023)
                weights.append(0.35)
            if date_sous.year <= 2024:
                eligible_years.append(2024)
                weights.append(0.45)
                
            if not eligible_years:
                eligible_years.append(2024)
                weights.append(1.0)
                
            total_w = sum(weights)
            weights = [w / total_w for w in weights]
            
            chosen_year = random.choices(eligible_years, weights=weights, k=1)[0]
            
            year_start = datetime(chosen_year, 1, 1)
            year_end = datetime(chosen_year, 12, 31)
            
            start_dt = max(date_sous, year_start)
            if start_dt > year_end:
                start_dt = year_end - timedelta(days=30)
                
            days_range = (year_end - start_dt).days
            offset = random.randint(0, max(0, days_range))
            conn_dates.append(start_dt + timedelta(days=offset))
        conn_dates.sort()
        
        # Déterminer le canal pour le routage de l'appareil
        # Solutions 1 (DabaPay) et 5 (WhatsApp) sont sur Mobile. 2 et 3 sur Web. 4 (Kodi) est mixte.
        if sol_id in [1, 5]:
            canal = "MOBILE"
        elif sol_id in [2, 3]:
            canal = "WEB"
        else: # Kodi
            canal = "WEB" if random.random() < 0.50 else "MOBILE"
            
        for dt in conn_dates:
            # 1. Sélection de l'appareil, OS et navigateur cohérents avec le canal
            if canal == "WEB":
                app = random.choice(WEB_ENV["appareils"])
                sys = random.choice(WEB_ENV["systemes"])
                nav = random.choice(WEB_ENV["navigateurs"])
            else:
                app = random.choice(MOBILE_ENV["appareils"])
                sys = random.choice(MOBILE_ENV["systemes"])
                nav = "WhatsApp Client" if sol_id == 5 else "Mobile App"
                
            # 2. IP marocaine réaliste (souvent 196.200.x.x ou 105.155.x.x)
            ip = f"196.200.{random.randint(10, 254)}.{random.randint(10, 254)}"
            
            # 3. Durée de session en secondes
            duree_sec = random.randint(15, 600) if sol_id in [1, 4, 5] else random.randint(120, 1800)
            
            # 4. Action réalisée
            action = random.choice(ACTIONS_BY_SOLUTION[sol_id])
            
            # 5. Statut de connexion (96% succès, 4% échec)
            statut = "SUCCES" if random.random() < 0.96 else "ECHEC"
            
            # Heure aléatoire
            hour = random.randint(7, 21)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            conn = {
                "id_connexion": current_id,
                "id_entreprise": ent_id,
                "entreprise_id": ent_id,  # Alias
                "id_solution": sol_id,
                "solution_id": sol_id,  # Alias
                "date_connexion": dt.strftime("%Y-%m-%d"),
                "heure_connexion": f"{hour:02d}:{minute:02d}:{second:02d}",
                "duree_session": duree_sec,
                "adresse_ip": ip,
                "navigateur": nav,
                "systeme": sys,
                "appareil": app,
                "action_realisee": action,
                "statut": statut
            }
            connexions.append(conn)
            current_id += 1
            
            # Limiter pour cibler exactement ~100 000 connexions (max 102 000)
            if len(connexions) >= 102000:
                break
        if len(connexions) >= 102000:
            break
            
    df_connexions = pd.DataFrame(connexions)
    
    # Ordonner chronologiquement l'ensemble
    df_connexions.sort_values(by=["date_connexion", "heure_connexion"], inplace=True)
    df_connexions.reset_index(drop=True, inplace=True)
    df_connexions["id_connexion"] = range(1, len(df_connexions) + 1)
    
    logger.info(f"Génération terminée : {len(df_connexions)} connexions digitales générées.")
    return df_connexions

if __name__ == "__main__":
    df = generate_connexions()
    print("\n--- TEST GENERATE CONNEXIONS ---")
    print(df.head(5))
    print(f"\nNombre total de connexions : {len(df)}")
    print("\nRépartition par appareil :")
    print(df["appareil"].value_counts())
    print("\nRépartition par action :")
    print(df["action_realisee"].value_counts().head(10))
