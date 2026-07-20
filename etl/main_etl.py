# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/main_etl.py
Description     : Orchestrateur général du pipeline ETL (Extraction -> Staging -> DWH -> Data Marts).
"""

import time
import sys
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from data_generation.utils.database import engine
from data_generation.config.config import BASE_DIR

# Configuration d'un logger spécifique pour l'ETL
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
etl_log_file = LOG_DIR / "etl.log"

etl_logger = logging.getLogger("etl_logger")
etl_logger.setLevel(logging.INFO)
if not etl_logger.handlers:
    # Handler fichier
    fh = logging.FileHandler(etl_log_file, mode="a", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    etl_logger.addHandler(fh)
    
    # Handler console
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    etl_logger.addHandler(ch)

# Importations des modules ETL
from etl.staging.load_staging import load_staging
from etl.dimensions.dim_temps import load_dim_temps
from etl.dimensions.dim_region import load_dim_region
from etl.dimensions.dim_agence import load_dim_agence
from etl.dimensions.dim_employe import load_dim_employe
from etl.dimensions.dim_entreprise import load_dim_entreprise
from etl.dimensions.dim_compte import load_dim_compte
from etl.dimensions.dim_produit_credit import load_dim_produit_credit
from etl.dimensions.dim_solution_digitale import load_dim_solution_digitale

from etl.facts.fait_depots import load_fait_depots
from etl.facts.fait_credits import load_fait_credits
from etl.facts.fait_transactions import load_fait_transactions
from etl.facts.fait_digital import load_fait_digital

from etl.datamarts.dm_depots import load_dm_depots
from etl.datamarts.dm_credits import load_dm_credits
from etl.datamarts.dm_performance import load_dm_performance
from etl.datamarts.dm_digital import load_dm_digital

def get_row_count(schema: str, table: str) -> int:
    """Retourne le nombre de lignes d'une table PostgreSQL."""
    try:
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
            return res.scalar()
    except Exception:
        return 0

def generate_etl_report(
    times: dict, 
    status: dict, 
    global_success: bool, 
    start_time_str: str, 
    duration: float
) -> None:
    """Génère le rapport HTML final de l'ETL décisionnel."""
    report_dir = BASE_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "etl_report.html"
    
    # Récupération dynamique des volumétries
    tables = [
        ("regions", "dim_region", "dm_depots"),  # simple exemple de mapping
        ("agences", "dim_agence", "dm_credits"),
        ("employes", "dim_employe", "dm_performance"),
        ("entreprises", "dim_entreprise", "dm_digital"),
        ("comptes", "dim_compte", None),
        ("produits_credits", "dim_produit_credit", None),
        ("solutions_digitales", "dim_solution_digitale", None),
        ("contrats_credits", None, None),
        ("garanties", None, None),
        ("transactions", None, None),
        ("souscriptions_digitales", None, None),
        ("connexions_digitales", None, None)
    ]
    
    table_rows_html = ""
    for oltp_t, dwh_t, dm_t in tables:
        oltp_c = get_row_count("oltp", oltp_t)
        stg_c = get_row_count("staging", oltp_t)
        dwh_c = get_row_count("dwh", dwh_t) if dwh_t else "-"
        dm_c = get_row_count("datamarts", dm_t) if dm_t else "-"
        
        table_rows_html += f"""
        <tr>
            <td>{oltp_t}</td>
            <td>{oltp_c:,}</td>
            <td>{stg_c:,}</td>
            <td>{dwh_c}</td>
            <td>{dm_c}</td>
        </tr>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport d'Exécution ETL Decisionnel BOA</title>
    <style>
        :root {{
            --bg-color: #0b1329;
            --card-bg: #1c2541;
            --primary: #5bc0be;
            --text: #ffffff;
            --text-muted: #9a9b9c;
            --success: #3a86c8; /* bleu de marque */
            --danger: #e63946;
            --border: #3a506b;
        }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background-color: var(--bg-color);
            color: var(--text);
            margin: 0;
            padding: 30px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        header {{
            background: linear-gradient(135deg, #1c2541, #3a506b);
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid var(--border);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background-color: var(--card-bg);
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }}
        .card h4 {{ margin: 0 0 10px 0; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; }}
        .card .value {{ font-size: 1.8rem; font-weight: bold; color: var(--primary); }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border);
            margin-bottom: 25px;
        }}
        th, td {{ padding: 12px 15px; text-align: left; }}
        th {{ background-color: #3a506b; color: var(--text); font-weight: bold; }}
        tr {{ border-bottom: 1px solid var(--border); }}
        .badge {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }}
        .badge-success {{ background-color: rgba(91, 192, 190, 0.1); color: var(--primary); }}
        .badge-danger {{ background-color: rgba(230, 57, 70, 0.1); color: var(--danger); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1 style="margin:0;">Rapport d'Exécution du Pipeline ETL Décisionnel</h1>
            <p style="margin: 5px 0 0 0; color: var(--text-muted);">BOA Business Banking Platform - Entrepôt de Données</p>
            <div style="margin-top: 15px;">
                <span class="badge {"badge-success" if global_success else "badge-danger"}" style="font-size: 1rem; padding: 6px 12px;">
                    { "✓ SUCCÈS COMPLET DU PIPELINE" if global_success else "✗ ÉCHEC DETECTÉ DURANT LE TRAITEMENT" }
                </span>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <h4>Date d'Exécution</h4>
                <div class="value" style="font-size:1.4rem;">{start_time_str}</div>
            </div>
            <div class="card">
                <h4>Durée Totale</h4>
                <div class="value">{duration:.2f} s</div>
            </div>
            <div class="card">
                <h4>Staging (Phase 1)</h4>
                <div class="value">{times.get('staging', 0.0):.2f} s</div>
            </div>
            <div class="card">
                <h4>Dimensions (Phase 2)</h4>
                <div class="value">{times.get('dimensions', 0.0):.2f} s</div>
            </div>
        </div>

        <h2>Volumétries et Cohérence par Couches</h2>
        <table>
            <thead>
                <tr>
                    <th>Entité</th>
                    <th>Lignes OLTP</th>
                    <th>Lignes Staging</th>
                    <th>Lignes DWH (Dimension)</th>
                    <th>Lignes Data Marts</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>

        <h2>Performance par Sous-Modules</h2>
        <table>
            <thead>
                <tr>
                    <th>Module / Script</th>
                    <th>Description</th>
                    <th>Temps (secondes)</th>
                    <th>Statut</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>load_staging</td>
                    <td>Ingestion brute dans staging</td>
                    <td>{times.get('staging', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_temps</td>
                    <td>Calendrier analytique</td>
                    <td>{times.get('dim_temps', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_region</td>
                    <td>Territoires d'agences</td>
                    <td>{times.get('dim_region', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_agence</td>
                    <td>Agences dénormalisées</td>
                    <td>{times.get('dim_agence', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_employe</td>
                    <td>Structure RH et Managers</td>
                    <td>{times.get('dim_employe', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_entreprise</td>
                    <td>Notation, Digitalisation, CA</td>
                    <td>{times.get('dim_entreprise', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_compte</td>
                    <td>Comptes dépôts</td>
                    <td>{times.get('dim_compte', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_produit_credit</td>
                    <td>Catalogue de financement</td>
                    <td>{times.get('dim_produit_credit', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dim_solution_digitale</td>
                    <td>Canaux internet/mobile</td>
                    <td>{times.get('dim_solution_digitale', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>fait_depots</td>
                    <td>Suivi trimestriel des dépôts</td>
                    <td>{times.get('fait_depots', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>fait_credits</td>
                    <td>Suivi d'amortissement de prêts</td>
                    <td>{times.get('fait_credits', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>fait_transactions</td>
                    <td>Flux de comptes unitaires</td>
                    <td>{times.get('fait_transactions', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>fait_digital</td>
                    <td>Sessions et connexions</td>
                    <td>{times.get('fait_digital', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dm_depots</td>
                    <td>Data Mart Dépôts</td>
                    <td>{times.get('dm_depots', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dm_credits</td>
                    <td>Data Mart Financements</td>
                    <td>{times.get('dm_credits', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dm_performance</td>
                    <td>Data Mart Productivité Commerciale</td>
                    <td>{times.get('dm_performance', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
                <tr>
                    <td>dm_digital</td>
                    <td>Data Mart Adoption Web/Mobile</td>
                    <td>{times.get('dm_digital', 0.0):.2f} s</td>
                    <td><span class="badge-success badge">✓ OK</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html)
        etl_logger.info(f"Rapport HTML final de l'ETL généré avec succès : {report_file}")
    except Exception as e:
        etl_logger.warning(f"Erreur durant l'écriture du rapport HTML final : {str(e)}")

def main() -> None:
    """Orchestrateur principal du pipeline ETL décisionnel."""
    etl_logger.info("=============================================================")
    etl_logger.info("DÉMARRAGE DU PIPELINE ETL BUSINESS BANKING DÉCISIONNEL BOA")
    etl_logger.info("=============================================================")
    
    start_global = time.time()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    times = {}
    status = {}
    
    # ---------------------------------------------------------
    # ÉTAPE 1 : STAGING
    # ---------------------------------------------------------
    start = time.time()
    try:
        success = load_staging()
        times["staging"] = time.time() - start
        if not success:
            etl_logger.error("Arrêt critique : Échec lors du chargement de l'étape Staging.")
            sys.exit(1)
    except Exception as e:
        etl_logger.error(f"Échec critique non géré durant Staging : {str(e)}")
        sys.exit(1)
        
    # ---------------------------------------------------------
    # ÉTAPE 2 : DIMENSIONS
    # ---------------------------------------------------------
    etl_logger.info("Lancement de la Phase 2 : Alimentation des Dimensions...")
    dimensions = [
        ("dim_temps", load_dim_temps),
        ("dim_region", load_dim_region),
        ("dim_agence", load_dim_agence),
        ("dim_employe", load_dim_employe),
        ("dim_entreprise", load_dim_entreprise),
        ("dim_compte", load_dim_compte),
        ("dim_produit_credit", load_dim_produit_credit),
        ("dim_solution_digitale", load_dim_solution_digitale)
    ]
    
    dim_start = time.time()
    for name, func in dimensions:
        start_sub = time.time()
        try:
            success = func()
            times[name] = time.time() - start_sub
            if not success:
                etl_logger.error(f"Arrêt critique : Échec du chargement de la dimension {name}.")
                sys.exit(1)
        except Exception as e:
            etl_logger.error(f"Échec critique sur dimension {name} : {str(e)}")
            sys.exit(1)
            
    times["dimensions"] = time.time() - dim_start
    
    # ---------------------------------------------------------
    # ÉTAPE 3 : TABLES DE FAITS
    # ---------------------------------------------------------
    etl_logger.info("Lancement de la Phase 3 : Alimentation des Tables de Faits...")
    facts = [
        ("fait_depots", load_fait_depots),
        ("fait_credits", load_fait_credits),
        ("fait_transactions", load_fait_transactions),
        ("fait_digital", load_fait_digital)
    ]
    
    fact_start = time.time()
    for name, func in facts:
        start_sub = time.time()
        try:
            success = func()
            times[name] = time.time() - start_sub
            if not success:
                etl_logger.error(f"Arrêt critique : Échec du chargement de la table de faits {name}.")
                sys.exit(1)
        except Exception as e:
            etl_logger.error(f"Échec critique sur fait {name} : {str(e)}")
            sys.exit(1)
            
    times["facts"] = time.time() - fact_start
    
    # ---------------------------------------------------------
    # ÉTAPE 4 : DATA MARTS
    # ---------------------------------------------------------
    etl_logger.info("Lancement de la Phase 4 : Alimentation des Data Marts...")
    datamarts = [
        ("dm_depots", load_dm_depots),
        ("dm_credits", load_dm_credits),
        ("dm_performance", load_dm_performance),
        ("dm_digital", load_dm_digital)
    ]
    
    dm_start = time.time()
    for name, func in datamarts:
        start_sub = time.time()
        try:
            success = func()
            times[name] = time.time() - start_sub
            if not success:
                etl_logger.error(f"Arrêt critique : Échec du chargement du Data Mart {name}.")
                sys.exit(1)
        except Exception as e:
            etl_logger.error(f"Échec critique sur Data Mart {name} : {str(e)}")
            sys.exit(1)
            
    times["datamarts"] = time.time() - dm_start
    
    # ---------------------------------------------------------
    # ÉTAPE 5 : RAPPORT FINAL
    # ---------------------------------------------------------
    duration = time.time() - start_global
    etl_logger.info("Lancement de la Phase 5 : Génération du Rapport final...")
    generate_etl_report(times, status, global_success=True, start_time_str=start_time_str, duration=duration)
    
    etl_logger.info("=============================================================")
    etl_logger.info(f"✓ PIPELINE ETL TERMINÉ ET CHARGÉ AVEC SUCCÈS EN {duration:.2f} SECONDES")
    etl_logger.info("=============================================================")

if __name__ == "__main__":
    main()
