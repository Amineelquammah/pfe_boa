# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/main.py
Description     : Point d'entrée principal de l'orchestration du pipeline de génération.
"""

import time
import sys
from data_generation.utils.logger import logger

from data_generation.pipeline.step01_generate import run_generate
from data_generation.pipeline.step02_validate import run_validate
from data_generation.pipeline.step03_export_csv import run_export_csv
from data_generation.pipeline.step04_load_database import run_load_database
from data_generation.pipeline.step05_quality_report import run_quality_report

def main() -> None:
    """
    Orchestrateur principal : lance successivement les 5 étapes du pipeline.
    Si une étape critique échoue (génération, validation, chargement), le pipeline s'arrête immédiatement.
    """
    logger.info("=============================================================")
    logger.info("LANCEMENT DU PIPELINE DÉCISIONNEL BUSINESS BANKING BOA MAROC")
    logger.info("=============================================================")
    
    times = {}
    start_global = time.time()
    
    # ---------------------------------------------------------
    # ÉTAPE 1 : GÉNÉRATION
    # ---------------------------------------------------------
    start_step = time.time()
    try:
        data = run_generate()
        times["generate"] = time.time() - start_step
    except Exception as e:
        logger.error(f"ÉCHEC CRITIQUE À L'ÉTAPE 1 : {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # ÉTAPE 2 : VALIDATION
    # ---------------------------------------------------------
    start_step = time.time()
    try:
        val_success, val_status = run_validate(data)
        times["validate"] = time.time() - start_step
        if not val_success:
            logger.error("Arrêt du pipeline : anomalies détectées lors de la validation métier.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"ÉCHEC CRITIQUE À L'ÉTAPE 2 : {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # ÉTAPE 3 : EXPORT CSV
    # ---------------------------------------------------------
    start_step = time.time()
    try:
        export_success = run_export_csv(data)
        times["export"] = time.time() - start_step
        if not export_success:
            logger.error("Arrêt du pipeline : échec lors de l'écriture des fichiers CSV.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"ÉCHEC CRITIQUE À L'ÉTAPE 3 : {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # ÉTAPE 4 : CHARGEMENT POSTGRESQL
    # ---------------------------------------------------------
    start_step = time.time()
    try:
        load_success = run_load_database(data)
        times["load"] = time.time() - start_step
        if not load_success:
            logger.error("Arrêt du pipeline : échec critique lors de l'insertion PostgreSQL (Rollback effectué).")
            sys.exit(1)
    except Exception as e:
        logger.error(f"ÉCHEC CRITIQUE À L'ÉTAPE 4 : {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # ÉTAPE 5 : RAPPORT DE QUALITÉ
    # ---------------------------------------------------------
    times["total"] = time.time() - start_global
    try:
        report_success = run_quality_report(data, val_status, times, global_success=True)
        if not report_success:
            logger.warning("Attention : Échec de la génération du rapport HTML final.")
    except Exception as e:
        logger.error(f"Erreur durant l'étape 5 : {str(e)}")
        
    logger.info("=============================================================")
    logger.info(f"✓ PIPELINE EXÉCUTÉ ET CHARGÉ AVEC SUCCÈS EN {times['total']:.2f} SECONDES")
    logger.info("=============================================================")

if __name__ == "__main__":
    main()
