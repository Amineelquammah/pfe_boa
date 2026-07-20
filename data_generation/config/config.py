# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/config/config.py
Description     : Configuration globale et constantes pour la génération de données.
"""

import os
from pathlib import Path
from typing import Dict, List

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Chargement manuel du fichier .env pour éviter les dépendances externes obligatoires
def load_env() -> None:
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# --- CONFIGURATION BASE DE DONNÉES ---
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_DATABASE: str = os.getenv("DB_DATABASE", "pfe_boa_db")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL: str = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

# --- REPRODUCTIBILITÉ ---
SEED: int = 42

# --- VOLUMÉTRIE CIBLE ---
NB_REGIONS: int = 7
NB_AGENCES: int = 10
NB_EMPLOYES: int = 50  # Strictement repartis (1 Dir, 2 Conseillers, 1 Caisse)
NB_ENTREPRISES: int = 2000
NB_COMPTES: int = 2500
NB_CREDITS: int = 1000
NB_GARANTIES: int = 800
NB_TRANSACTIONS: int = 150000
NB_SOUSCRIPTIONS: int = 1500
NB_CONNEXIONS: int = 100000

# --- HORIZON TEMPOREL ---
START_DATE: str = "2022-01-01"
END_DATE: str = "2024-12-31"

# --- DISTRIBUTIONS ET PROBABILITÉS DES ENTREPRISES ---
SECTEURS: List[str] = ['Commerce', 'BTP', 'Services', 'Industrie', 'Agriculture', 'Technologies']
SECTEUR_PROBAS: List[float] = [0.30, 0.15, 0.25, 0.15, 0.10, 0.05]

SEGMENTS: List[str] = ['TPE', 'PME', 'Grande Entreprise']
SEGMENT_PROBAS: List[float] = [0.70, 0.25, 0.05]

FORMES_JURIDIQUES: List[str] = ['SARL', 'SA', 'SNC', 'EURL']
FORME_PROBAS: List[float] = [0.65, 0.20, 0.10, 0.05]

# Seuil Chiffre d'Affaires annuel en MAD par segment
CA_RANGES: Dict[str, Dict[str, float]] = {
    'TPE': {'min': 100000.0, 'max': 3000000.0},
    'PME': {'min': 3000000.0, 'max': 50000000.0},
    'Grande Entreprise': {'min': 50000000.0, 'max': 500000000.0}
}

# Seuil Nombre de salariés par segment
EFFECTIF_RANGES: Dict[str, Dict[str, int]] = {
    'TPE': {'min': 1, 'max': 10},
    'PME': {'min': 10, 'max': 200},
    'Grande Entreprise': {'min': 200, 'max': 5000}
}

# --- TAUX D'ADOPTION DU DIGITAL PAR SEGMENT ---
TAUX_DIGITALISATION: Dict[str, float] = {
    'TPE': 0.60,
    'PME': 0.85,
    'Grande Entreprise': 0.98
}

# --- PARAMÈTRES FINANCIERS CRÉDITS ---
MAX_ENDETTEMENT_RATIO: float = 0.45  # 45% maximum du CA
TAUX_INTERET_RANGES: Dict[str, Dict[str, float]] = {
    'TRESORERIE': {'min': 4.5, 'max': 7.0},
    'INVESTISSEMENT': {'min': 3.5, 'max': 5.5},
    'INTERNATIONAL': {'min': 4.0, 'max': 6.5}
}

# --- SOLUTIONS DIGITALES CIBLES ---
SOLUTIONS_DIGITALES_LIST: List[Dict[str, str]] = [
    {"nom": "DabaPay Pro", "canal": "MOBILE"},
    {"nom": "Business Online", "canal": "WEB"},
    {"nom": "Credit Business Online", "canal": "WEB"},
    {"nom": "WhatsApp Business", "canal": "MOBILE"},
    {"nom": "KODI", "canal": "ASSISTANT"}
]
