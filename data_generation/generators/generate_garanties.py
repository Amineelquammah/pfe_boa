# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_garanties.py
Description     : Générateur de données pour les garanties liées aux contrats de crédits.
"""

import pandas as pd
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_contrats_credits import generate_contrats_credits

def generate_garanties() -> pd.DataFrame:
    """
    Génère environ 800 garanties associées aux contrats de crédit.
    
    Returns:
        pd.DataFrame: DataFrame des garanties.
    """
    logger.info("Début de la génération des garanties...")
    random.seed(42)  # Reproductibilité
    
    # Chargement des contrats et des entreprises
    df_contrats = df_contrats_raw = generate_contrats_credits()
    df_entreprises = generate_entreprises()
    
    ent_dict = df_entreprises.set_index("id_entreprise").to_dict(orient="index")
    
    garanties: List[Dict[str, Any]] = []
    current_id = 1
    
    # Parcourir les contrats pour leur attribuer des garanties
    for _, contrat in df_contrats.iterrows():
        contrat_id = int(contrat["id_contrat"])
        ent_id = int(contrat["id_entreprise"])
        montant_accorde = float(contrat["montant_principal"])
        encours_restant = float(contrat["encours_restant"])
        date_octroi = datetime.strptime(str(contrat["date_octroi"]), "%Y-%m-%d")
        date_fin = datetime.strptime(str(contrat["date_echeance"]), "%Y-%m-%d")
        statut_val = contrat["statut"]
        
        ent_meta = ent_dict[ent_id]
        segment = ent_meta["segment"]
        
        # 1. Détermination de la probabilité d'avoir une garantie selon le produit et le segment
        prod_id = int(contrat["id_produit"])
        
        # Crédits d'investissement (IDs 4, 5, 6, 7) ont toujours une garantie
        if prod_id in [4, 5, 6, 7]:
            prob_gar = 1.0
        # Trade Finance (IDs 8, 9, 10) : 95%
        elif prod_id in [8, 9, 10]:
            prob_gar = 0.95
        # Exploitation (IDs 1, 2, 3) : 78%
        elif prod_id in [1, 2, 3]:
            prob_gar = 0.78
        # Autres : 50%
        else:
            prob_gar = 0.50
            
        if random.random() > prob_gar:
            continue
            
        # Déterminer le nombre de garanties à générer (les Grandes Entreprises et PME ont parfois des garanties multiples)
        nb_gar = 1
        if segment == "Grande Entreprise" and random.random() < 0.50:
            nb_gar = random.randint(2, 3)
        elif segment == "PME" and random.random() < 0.20:
            nb_gar = 2
            
        for gar_idx in range(nb_gar):
            # 2. Choix du type de garantie selon le segment de l'entreprise
            if segment == "TPE":
                type_gar = random.choice(["Caution personnelle", "Garantie Tamwilcom"])
            elif segment == "PME":
                type_gar = random.choice(["Caution bancaire", "Hypothèque", "Garantie Tamwilcom", "Nantissement", "Garantie sur matériel"])
            else: # Grande Entreprise
                type_gar = random.choice(["Hypothèque", "Nantissement", "Garantie de l'État", "Aval", "Garantie sur créances", "Garantie sur fonds de commerce"])
                
            # Organisme garant
            organisme_garant = "None"
            if type_gar == "Garantie Tamwilcom":
                organisme_garant = "Tamwilcom (SNGFE)"
            elif type_gar == "Garantie de l'État":
                organisme_garant = "État Marocain"
            elif type_gar == "Caution bancaire":
                organisme_garant = random.choice(["BOA Assurances", "RMA Watanya"])
                
            # 3. Calcul des valeurs de la garantie
            # Hypothèque/Nantissement couvrent souvent plus que le prêt (ex: 120%)
            # Cautions couvrent environ 80% à 100%
            if type_gar in ["Hypothèque", "Nantissement", "Garantie sur fonds de commerce"]:
                ratio_valeur = random.uniform(1.0, 1.4)
            else:
                ratio_valeur = random.uniform(0.7, 1.0)
                
            valeur_initiale = round(montant_accorde * ratio_valeur / nb_gar, 2)
            
            # Dépréciation au 31/12/2024 (légère décote pour le matériel ou créances)
            decay_factor = random.uniform(0.80, 1.0) if type_gar in ["Garantie sur matériel", "Garantie sur créances"] else random.uniform(0.95, 1.05)
            valeur_actuelle = round(valeur_initiale * decay_factor, 2)
            
            # Taux de couverture par rapport à l'encours
            if encours_restant > 0:
                taux_couverture = round((valeur_actuelle / encours_restant), 4)
            else:
                taux_couverture = 0.0
                
            # 4. Dates
            date_affectation = date_octroi + timedelta(days=random.randint(0, 7))
            date_expiration = date_fin + timedelta(days=random.randint(30, 180))
            
            # 5. Détermination du statut de la garantie
            if encours_restant == 0:
                statut = random.choice(["Libérée", "Expirée"])
            elif statut_val == "NPL":
                statut = "En cours de réalisation" if random.random() < 0.30 else "Active"
            else:
                statut = "Active"
                
            obs = f"Couverture standard {type_gar} pour dossier {segment}"
            
            gar = {
                "id_garantie": current_id,
                "numero_garantie": f"GAR_{current_id:06d}",
                "id_contrat": contrat_id,
                "type_garantie": type_gar,
                "valeur": valeur_actuelle,
                "valeur_initiale": valeur_initiale,
                "valeur_actuelle": valeur_actuelle,
                "taux_couverture": taux_couverture,
                "date_affectation": date_affectation.strftime("%Y-%m-%d"),
                "date_expiration": date_expiration.strftime("%Y-%m-%d"),
                "statut": statut,
                "organisme_garant": organisme_garant,
                "observations": obs
            }
            garanties.append(gar)
            current_id += 1
            
            # On veut cibler environ 800 garanties
            if len(garanties) >= 810:
                break
        if len(garanties) >= 810:
            break
            
    df_garanties = pd.DataFrame(garanties)
    logger.info(f"Génération terminée : {len(df_garanties)} garanties générées.")
    return df_garanties

if __name__ == "__main__":
    df = generate_garanties()
    print("\n--- TEST GENERATE GARANTIES ---")
    print(df.head(5))
    
    print("\n--- NOMBRE TOTAL DE GARANTIES ---")
    print(len(df))
    
    print("\n--- REPARTITION PAR TYPE DE GARANTIE ---")
    print(df["type_garantie"].value_counts())
    
    print("\n--- REPARTITION PAR STATUT ---")
    print(df["statut"].value_counts())
    
    print("\n--- VALEUR TOTALE DES GARANTIES ---")
    print(f"{df['valeur_actuelle'].sum():,.2f} MAD")
