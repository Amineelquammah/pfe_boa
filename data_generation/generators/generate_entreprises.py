# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_entreprises.py
Description     : Générateur de données pour les entreprises (clients professionnels).
"""

import pandas as pd
import random
import re
import unicodedata
from typing import List, Dict, Any
from data_generation.utils.logger import logger
from data_generation.utils.faker_utils import generate_ice, generate_raison_sociale, fake
from data_generation.generators.generate_agences import generate_agences
from data_generation.generators.generate_employes import generate_employes

# Constantes pour les secteurs marocains demandés et leur répartition
SECTEURS = [
    "Commerce", "Services", "Industrie", "BTP", "Agriculture", 
    "Transport", "Tourisme", "Technologies", "Santé", "Éducation"
]
SECTEUR_PROBAS = [0.25, 0.20, 0.15, 0.12, 0.10, 0.05, 0.05, 0.04, 0.02, 0.02]

# Segments et leur répartition
SEGMENTS = ["TPE", "PME", "Grande Entreprise"]
SEGMENT_PROBAS = [0.55, 0.35, 0.10]

FORMES_JURIDIQUES = ["SARL", "SA", "SNC", "EURL"]
FORME_PROBAS = [0.65, 0.20, 0.10, 0.05]

# Définition des volumes d'entreprises cibles par agence
AGENCE_COMPANY_VOLUMES = {
    1: 350, 2: 350,  # Casablanca-Settat (Total 700)
    3: 200, 4: 200,  # Rabat-Salé-Kénitra (Total 400)
    5: 180,          # Fès-Meknès (Total 180)
    6: 220,          # Marrakech-Safi (Total 220)
    7: 220,          # Tanger-Tétouan-Al Hoceïma (Total 220)
    8: 140,          # Oriental (Total 140)
    9: 70, 10: 70    # Sud (Total 140)
}

def clean_company_name(name: str) -> str:
    """Nettoie le nom de l'entreprise pour générer un email propre."""
    # Retirer le suffixe légal (SARL, SA, etc.)
    name_clean = re.sub(r'\s+(SARL|SA|SNC|EURL|SARL AU)$', '', name, flags=re.IGNORECASE)
    name_clean = name_clean.replace(" ", "").replace("-", "").replace("'", "")
    nfkd_form = unicodedata.normalize('NFKD', name_clean)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

def generate_entreprises() -> pd.DataFrame:
    """
    Génère les 2 000 entreprises clientes réparties entre les 10 agences et 20 conseillers.
    
    Returns:
        pd.DataFrame: DataFrame contenant les données des entreprises.
    """
    logger.info("Début de la génération des entreprises...")
    random.seed(42)  # Reproductibilité
    
    # Clear state in faker_utils to ensure reproducibility across repeated function calls
    if hasattr(generate_raison_sociale, "_used_names"):
        generate_raison_sociale._used_names.clear()
    if hasattr(generate_ice, "_used_ices"):
        generate_ice._used_ices.clear()
        
    # Chargement des agences et employés pour les affectations
    df_agences = generate_agences()
    df_employes = generate_employes()
    
    # Dictionnaires d'informations utiles
    agences_info = df_agences.set_index("id_agence").to_dict(orient="index")
    
    # Trouver les conseillers par agence
    df_conseillers = df_employes[df_employes["fonction"] == "Conseiller Entreprises"]
    conseillers_by_agence: Dict[int, List[int]] = {}
    for ag_id in range(1, 11):
        conseillers_by_agence[ag_id] = df_conseillers[df_conseillers["agence_id"] == ag_id]["id_employe"].tolist()
        
    entreprises: List[Dict[str, Any]] = []
    current_id = 1
    used_emails = set()
    
    # Génération séquentielle pour chaque agence afin de respecter la répartition exacte
    for ag_id, target_volume in AGENCE_COMPANY_VOLUMES.items():
        agence_meta = agences_info[ag_id]
        region_id = agence_meta["id_region"]
        ville_agence = agence_meta["ville"]
        advisers = conseillers_by_agence[ag_id]
        
        for i in range(target_volume):
            # 1. Détermination du segment
            segment = random.choices(SEGMENTS, weights=SEGMENT_PROBAS, k=1)[0]
            
            # 2. Détermination du CA et effectifs cohérents
            if segment == "TPE":
                ca = round(random.uniform(100000.0, 5000000.0), 2)
                employes_count = random.randint(1, 9)
            elif segment == "PME":
                ca = round(random.uniform(5000000.0, 100000000.0), 2)
                employes_count = random.randint(10, 199)
            else: # Grande Entreprise
                ca = round(random.uniform(100000000.0, 500000000.0), 2)
                employes_count = random.randint(200, 3000)
                
            # 3. Secteur et Raison Sociale
            secteur = random.choices(SECTEURS, weights=SECTEUR_PROBAS, k=1)[0]
            raison_sociale = generate_raison_sociale(secteur)
            forme_juridique = random.choices(FORMES_JURIDIQUES, weights=FORME_PROBAS, k=1)[0]
            
            # 4. Affectation commerciale (Equitable entre les conseillers de l'agence)
            # Utilise l'index i modulo le nombre de conseillers
            conseiller_id = advisers[i % len(advisers)]
            
            # 5. Dates et coordonnées fictives
            # Création de l'entreprise entre 2005 et 2021
            year = random.randint(2005, 2021)
            month = random.randint(1, 12)
            day = random.randint(1, 28)
            date_creation = f"{year:04d}-{month:02d}-{day:02d}"
            
            clean_name = clean_company_name(raison_sociale)
            email = f"contact@{clean_name}.ma"
            count = 1
            while email in used_emails:
                email = f"contact@{clean_name}{count}.ma"
                count += 1
            used_emails.add(email)
            
            # Téléphone fixe marocain (ex: 0522... ou 0537...)
            phone_prefix = "0522" if region_id == 1 else ("0537" if region_id == 2 else "0524")
            phone = f"{phone_prefix}{random.randint(100000, 999999):06d}"
            
            # Adresse factice dans la ville de l'agence
            adresse = f"Zone Industrielle, N° {random.randint(10, 500)}, Route de {fake.city()}, {ville_agence}, Maroc"
            
            ent = {
                "id_entreprise": current_id,
                "ice": generate_ice(),
                "raison_sociale": raison_sociale,
                "forme_juridique": forme_juridique,
                "secteur_activite": secteur,
                "secteur": secteur,  # Alias
                "segment": segment,
                "chiffre_affaires": ca,
                "chiffre_affaires_annuel": ca,  # Alias
                "nombre_employes": employes_count,
                "date_creation": date_creation,
                "ville": ville_agence,
                "adresse": adresse,
                "telephone": phone,
                "email": email,
                "statut": "Actif",
                "id_agence": ag_id,
                "agence_id": ag_id,  # Alias
                "id_region": region_id,
                "region_id": region_id,  # Alias
                "id_conseiller": conseiller_id,
                "conseiller_id": conseiller_id  # Alias
            }
            
            entreprises.append(ent)
            current_id += 1
            
    df_entreprises = pd.DataFrame(entreprises)
    logger.info(f"Génération terminée : {len(df_entreprises)} entreprises générées.")
    return df_entreprises

if __name__ == "__main__":
    df = generate_entreprises()
    print("\n--- TEST GENERATE ENTREPRISES ---")
    print(df.head(5))
    
    print("\n--- VOLUMES PAR AGENCE ---")
    print(df["id_agence"].value_counts().sort_index())
    
    print("\n--- VOLUMES PAR CONSEILLER ---")
    print(df["id_conseiller"].value_counts().sort_index())
    
    print("\n--- VOLUMES PAR SEGMENT ---")
    print(df["segment"].value_counts(normalize=True))
    
    print("\n--- STATISTIQUES SUR LE CHIFFRE D'AFFAIRES PAR SEGMENT ---")
    print(df.groupby("segment")["chiffre_affaires"].describe())
