# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/utils/logger.py
Description     : Configuration du logger standard du pipeline (console + fichier).
"""

import logging
from pathlib import Path
from data_generation.config.config import BASE_DIR

# Définition et création automatique du dossier des logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / "pipeline.log"

# Création du logger principal
logger = logging.getLogger("pipeline_logger")
logger.setLevel(logging.INFO)

# Empêcher la duplication des handlers
if not logger.handlers:
    # Handler pour l'écriture dans le fichier log
    file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Handler pour la sortie console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Rattachement des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
