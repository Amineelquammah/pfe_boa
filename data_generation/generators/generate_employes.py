# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_employes.py
Description     : Générateur de données pour les employés de la banque (siège, régions, agences).
"""

import pandas as pd
import random
import unicodedata
from typing import List, Dict, Any
from data_generation.utils.logger import logger

# Listes de noms et prénoms marocains typiques pour le réalisme
MALE_FIRST_NAMES = [
    "Mohamed", "Ahmed", "Youssef", "Tarik", "Reda", "Mehdi", "Omar", "Hamza", "Karim", "Amine", 
    "Saad", "Adil", "Jalal", "Mourad", "Rachid", "Anass", "Khalid", "Hassan", "Kamal", "Fouad"
]
FEMALE_FIRST_NAMES = [
    "Fatima", "Yasmina", "Meriem", "Laila", "Salma", "Kenza", "Ghita", "Sara", "Latifa", "Sanaa", 
    "Hind", "Khadija", "Bouchra", "Zineb", "Asmaa", "Nouzha", "Leila", "Meryem", "Nadia", "Ilham"
]
LAST_NAMES = [
    "Alaoui", "Benjelloun", "Bennani", "Tazi", "Chraibi", "Berrada", "El Fassi", "Filali", "Amrani", 
    "Mezouar", "Slaoui", "Mansouri", "Naciri", "Kadiri", "El Ouali", "Jahidi", "Tahiri", "Alami",
    "Daoudi", "Kabbaj", "Guessous", "Bouaziz", "Hakimi", "El Amri", "Belkhayat", "Zouiten", "Sebbar"
]

def clean_string(s: str) -> str:
    """Nettoie une chaîne de caractères (retire les accents, espaces et tirets)."""
    s = s.replace(" ", "").replace("-", "").replace("'", "")
    nfkd_form = unicodedata.normalize('NFKD', s)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

def generate_employes() -> pd.DataFrame:
    """
    Génère les 48 employés de la banque en respectant la hiérarchie et les affectations.
    
    Returns:
        pd.DataFrame: DataFrame des employés.
    """
    logger.info("Début de la génération des employés...")
    random.seed(42)  # Reproductibilité
    
    employes: List[Dict[str, Any]] = []
    current_id = 1
    
    # ---------------------------------------------------------
    # NIVEAU 1 : Siège - Directeur Général
    # ---------------------------------------------------------
    dg_first_name = random.choice(MALE_FIRST_NAMES)
    dg_last_name = random.choice(LAST_NAMES)
    dg_email = f"{clean_string(dg_first_name)}.{clean_string(dg_last_name)}@bankofafrica.ma"
    
    dg = {
        "id_employe": current_id,
        "matricule": f"EMP{current_id:06d}",
        "nom": dg_last_name,
        "prenom": dg_first_name,
        "sexe": "M",
        "date_naissance": "1968-04-12",
        "date_embauche": "2005-09-01",
        "fonction": "Directeur Général",
        "service": "Direction Générale",
        "email_professionnel": dg_email,
        "telephone": f"06{random.randint(10000000, 99999999):08d}",
        "statut": "Actif",
        "id_agence": None,
        "agence_id": None,
        "id_region": None,
        "region_id": None,
        "manager_id": None
    }
    employes.append(dg)
    dg_id = current_id
    current_id += 1

    # ---------------------------------------------------------
    # NIVEAU 2 : Directions Régionales - 7 Directeurs Régionaux
    # ---------------------------------------------------------
    dr_ids_by_region: Dict[int, int] = {}
    
    for region_idx in range(1, 8):
        sexe = random.choice(["M", "F"])
        first_name = random.choice(MALE_FIRST_NAMES if sexe == "M" else FEMALE_FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{clean_string(first_name)}.{clean_string(last_name)}@bankofafrica.ma"
        
        dr = {
            "id_employe": current_id,
            "matricule": f"EMP{current_id:06d}",
            "nom": last_name,
            "prenom": first_name,
            "sexe": sexe,
            "date_naissance": f"{random.randint(1972, 1980):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "date_embauche": f"{random.randint(2010, 2015):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "fonction": "Directeur Régional",
            "service": "Direction Régionale",
            "email_professionnel": email,
            "telephone": f"06{random.randint(10000000, 99999999):08d}",
            "statut": "Actif",
            "id_agence": None,
            "agence_id": None,
            "id_region": region_idx,
            "region_id": region_idx,
            "manager_id": dg_id
        }
        employes.append(dr)
        dr_ids_by_region[region_idx] = current_id
        current_id += 1

    # ---------------------------------------------------------
    # NIVEAU 3 : Agences - 40 employés (10 DA, 20 CE, 10 CC)
    # ---------------------------------------------------------
    # Mapping Agence -> Région
    agence_regions = {
        1: 1, 2: 1,  # Casablanca-Settat
        3: 2, 4: 2,  # Rabat-Salé-Kénitra
        5: 3,        # Fès-Meknès
        6: 4,        # Marrakech-Safi
        7: 5,        # Tanger-Tétouan-Al Hoceïma
        8: 6,        # Oriental
        9: 7, 10: 7  # Sud
    }
    
    for agence_idx in range(1, 11):
        region_idx = agence_regions[agence_idx]
        dr_manager_id = dr_ids_by_region[region_idx]
        
        # A. 1 Directeur d'Agence (DA)
        sexe_da = random.choice(["M", "F"])
        first_da = random.choice(MALE_FIRST_NAMES if sexe_da == "M" else FEMALE_FIRST_NAMES)
        last_da = random.choice(LAST_NAMES)
        email_da = f"{clean_string(first_da)}.{clean_string(last_da)}@bankofafrica.ma"
        da_id = current_id
        
        da = {
            "id_employe": da_id,
            "matricule": f"EMP{current_id:06d}",
            "nom": last_da,
            "prenom": first_da,
            "sexe": sexe_da,
            "date_naissance": f"{random.randint(1980, 1988):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "date_embauche": f"{random.randint(2015, 2018):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "fonction": "Directeur d'Agence",
            "service": "Agence Commerciale",
            "email_professionnel": email_da,
            "telephone": f"06{random.randint(10000000, 99999999):08d}",
            "statut": "Actif",
            "id_agence": agence_idx,
            "agence_id": agence_idx,
            "id_region": region_idx,
            "region_id": region_idx,
            "manager_id": dr_manager_id
        }
        employes.append(da)
        current_id += 1
        
        # B. 2 Conseillers Entreprises (CE)
        for ce_count in range(1, 3):
            sexe_ce = random.choice(["M", "F"])
            first_ce = random.choice(MALE_FIRST_NAMES if sexe_ce == "M" else FEMALE_FIRST_NAMES)
            last_ce = random.choice(LAST_NAMES)
            email_ce = f"{clean_string(first_ce)}.{clean_string(last_ce)}@bankofafrica.ma"
            
            ce = {
                "id_employe": current_id,
                "matricule": f"EMP{current_id:06d}",
                "nom": last_ce,
                "prenom": first_ce,
                "sexe": sexe_ce,
                "date_naissance": f"{random.randint(1985, 1996):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "date_embauche": f"{random.randint(2018, 2021):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "fonction": "Conseiller Entreprises",
                "service": "Agence Commerciale",
                "email_professionnel": email_ce,
                "telephone": f"06{random.randint(10000000, 99999999):08d}",
                "statut": "Actif",
                "id_agence": agence_idx,
                "agence_id": agence_idx,
                "id_region": region_idx,
                "region_id": region_idx,
                "manager_id": da_id
            }
            employes.append(ce)
            current_id += 1
            
        # C. 1 Chargé de Caisse (CC)
        sexe_cc = random.choice(["M", "F"])
        first_cc = random.choice(MALE_FIRST_NAMES if sexe_cc == "M" else FEMALE_FIRST_NAMES)
        last_cc = random.choice(LAST_NAMES)
        email_cc = f"{clean_string(first_cc)}.{clean_string(last_cc)}@bankofafrica.ma"
        
        cc = {
            "id_employe": current_id,
            "matricule": f"EMP{current_id:06d}",
            "nom": last_cc,
            "prenom": first_cc,
            "sexe": sexe_cc,
            "date_naissance": f"{random.randint(1988, 1998):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "date_embauche": f"{random.randint(2019, 2021):04d}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            "fonction": "Chargé de Caisse",
            "service": "Caisse",
            "email_professionnel": email_cc,
            "telephone": f"06{random.randint(10000000, 99999999):08d}",
            "statut": "Actif",
            "id_agence": agence_idx,
            "agence_id": agence_idx,
            "id_region": region_idx,
            "region_id": region_idx,
            "manager_id": da_id
        }
        employes.append(cc)
        current_id += 1
        
    df_employes = pd.DataFrame(employes)
    
    logger.info(f"Génération terminée : {len(df_employes)} employés générés.")
    return df_employes

if __name__ == "__main__":
    df = generate_employes()
    print("\n--- TEST GENERATE EMPLOYES ---")
    print(df.head(10))
    print("\n--- EFFECTIFS PAR FONCTION ---")
    print(df["fonction"].value_counts())
    print("\n--- EFFECTIFS PAR REGION ---")
    print(df["region_id"].value_counts(dropna=False))
    print("\n--- EFFECTIFS PAR AGENCE ---")
    print(df["agence_id"].value_counts(dropna=False))
