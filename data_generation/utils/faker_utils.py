# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/utils/faker_utils.py
Description     : Fonctions utilitaires basées sur Faker pour la simulation marocaine.
"""

import random
from typing import Dict, List
from faker import Faker
from data_generation.config.config import SEED

# Initialisation de Faker avec la localisation française pour le Maroc (fr_FR)
fake = Faker("fr_FR")
Faker.seed(SEED)
random.seed(SEED)

# Mapping des villes marocaines par région administrative BOA
REGION_CITIES: Dict[str, List[str]] = {
    "Casablanca-Settat": ["Casablanca", "Mohammedia", "El Jadida", "Settat"],
    "Rabat-Salé-Kénitra": ["Rabat", "Salé", "Kénitra", "Témara"],
    "Fès-Meknès": ["Fès", "Meknès", "Taza"],
    "Marrakech-Safi": ["Marrakech", "Safi", "Essaouira"],
    "Tanger-Tétouan-Al Hoceïma": ["Tanger", "Tétouan", "Al Hoceïma"],
    "Oriental": ["Oujda", "Nador", "Berkane"],
    "Sud": ["Agadir", "Laâyoune", "Dakhla"]
}

# Liste des régions ordonnées pour correspondre à NB_REGIONS = 7
REGIONS_LIST: List[str] = list(REGION_CITIES.keys())

def get_regions() -> List[str]:
    """Retourne la liste des 7 régions administratives."""
    return REGIONS_LIST

def get_cities_for_region(region: str) -> List[str]:
    """Retourne la liste des villes pour une région donnée."""
    return REGION_CITIES.get(region, ["Casablanca"])

def generate_ice() -> str:
    """
    Génère un ICE (Identifiant Commun de l'Entreprise) marocain réaliste de 15 caractères.
    Format type : 9 chiffres (Identifiant Fiscal) + 4 zéros + 2 chiffres de contrôle.
    """
    if not hasattr(generate_ice, "_used_ices"):
        generate_ice._used_ices = set()
    
    while True:
        if len(generate_ice._used_ices) > 1000000:
            generate_ice._used_ices.clear() # Reset de précaution
            
        fiscal_part = f"{random.randint(100000000, 999999999):09d}"
        control_part = f"{random.randint(10, 99):02d}"
        ice = f"{fiscal_part}0000{control_part}"
        
        if ice not in generate_ice._used_ices:
            generate_ice._used_ices.add(ice)
            return ice

def generate_rib() -> str:
    """
    Génère un RIB (Relevé d'Identité Bancaire) marocain de 24 chiffres.
    Structure : 3 code banque (ex: 011 BOA) + 3 code ville + 16 num de compte et contrôle.
    """
    if not hasattr(generate_rib, "_used_ribs"):
        generate_rib._used_ribs = set()
        
    while True:
        bank_code = "011" # BOA Maroc
        city_code = f"{random.randint(100, 999):03d}"
        account_num = f"{random.randint(10000000, 99999999):08d}"
        control_key = f"{random.randint(10000000, 99999999):08d}"
        rib = f"{bank_code}{city_code}{account_num}{control_key}"
        
        if rib not in generate_rib._used_ribs:
            generate_rib._used_ribs.add(rib)
            return rib

def generate_raison_sociale(sector: str) -> str:
    """
    Génère un nom d'entreprise (raison sociale) marocain réaliste en fonction du secteur.
    """
    roots = ["Atlas", "Maroc", "Maghreb", "Chaouia", "Sous", "Saiss", "Taza", "Med", "Riad", "Bahia", "Koutoubia", "Zilis", "Bouregreg"]
    prefixes = ["Somaco", "Somibat", "Soma", "Afric", "Euro", "Inter", "Global", "Société Marocaine de", "Compagnie du", "Union"]
    
    sector_terms = {
        "Commerce": ["Distribution", "Trading", "Import-Export", "Négoce", "Market", "Wholesale"],
        "BTP": ["Bâtiment", "Travaux", "Construction", "Génie Civil", "Béton", "Aménagement"],
        "Services": ["Services", "Logistique", "Conseil", "Security", "Nettoyage", "Holding"],
        "Industrie": ["Industrie", "Manufacture", "Plastique", "Métal", "Textile", "Câblage"],
        "Agriculture": ["Agro", "Ferme", "Laiterie", "Oléicole", "Agrumes", "Export Agri"],
        "Technologies": ["Tech", "Systems", "Soft", "Digital", "Data", "Telecom", "Web"]
    }
    
    terms = sector_terms.get(sector, ["Entreprise"])
    suffix = random.choice(["SARL", "SA", "SARL AU", "SNC"])
    
    pattern = random.randint(1, 3)
    if pattern == 1:
        name = f"{random.choice(prefixes)} {random.choice(terms)}"
    elif pattern == 2:
        name = f"{random.choice(roots)} {random.choice(terms)}"
    else:
        name = f"Société {random.choice(roots)} de {random.choice(terms)}"
        
    # Unicité de précaution
    if not hasattr(generate_raison_sociale, "_used_names"):
        generate_raison_sociale._used_names = set()
    
    unique_name = f"{name} {suffix}"
    count = 1
    while unique_name in generate_raison_sociale._used_names:
        unique_name = f"{name} {count} {suffix}"
        count += 1
        
    generate_raison_sociale._used_names.add(unique_name)
    return unique_name
