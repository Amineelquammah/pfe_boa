# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step05_quality_report.py
Description     : Étape 5 du pipeline : compilation et génération du rapport de qualité HTML.
"""

import os
from typing import Dict, Any
import pandas as pd
from data_generation.utils.logger import logger
from data_generation.config.config import BASE_DIR

def run_quality_report(
    data_dict: Dict[str, pd.DataFrame],
    validation_status: Dict[str, bool],
    execution_times: Dict[str, float],
    global_success: bool
) -> bool:
    """
    Génère un rapport de qualité HTML dynamique résumant le chargement,
    les volumétries, la qualité des données et les performances.
    
    Args:
        data_dict (Dict[str, pd.DataFrame]): Les DataFrames générés.
        validation_status (Dict[str, bool]): Statuts détaillés par table.
        execution_times (Dict[str, float]): Temps d'exécution par étape.
        global_success (bool): Statut général de succès ou échec.
        
    Returns:
        bool: True si la génération s'est effectuée sans erreur.
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 5 : GÉNÉRATION DU RAPPORT HTML")
    logger.info("=========================================")
    
    # Création du dossier reports/ s'il n'existe pas
    report_dir = BASE_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "quality_report.html"
    
    # Calcul dynamique de métriques de qualité
    total_rows = sum(len(df) for df in data_dict.values())
    
    # Comptage des doublons sur l'ensemble
    total_duplicates = 0
    # Liste de clés à vérifier
    unique_keys = {
        "regions": "id_region", "agences": "code_agence", "employes": "matricule",
        "entreprises": "ice", "comptes": "numero_compte", "contrats_credits": "numero_contrat",
        "garanties": "numero_garantie", "transactions": "reference_transaction",
        "solutions_digitales": "nom_solution", "souscriptions_digitales": "id_souscription",
        "connexions_digitales": "id_connexion"
    }
    for key, col in unique_keys.items():
        if key in data_dict:
            total_duplicates += data_dict[key][col].duplicated().sum()
            
    # Comptage des valeurs nulles
    total_nulls = sum(data_dict[k].isnull().sum().sum() for k in data_dict)
    
    # Taux de réussite des validations
    nb_validations = len(validation_status)
    successful_validations = sum(1 for v in validation_status.values() if v)
    validation_rate = (successful_validations / nb_validations) * 100 if nb_validations > 0 else 0
    
    # Construction du corps HTML avec du style CSS moderne et premium (sans device frame)
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Qualité - Pipeline BOA</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --primary-color: #0284c7;
            --text-color: #f1f5f9;
            --text-muted: #94a3b8;
            --success-color: #10b981;
            --danger-color: #ef4444;
            --border-color: #334155;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #0369a1, #0f172a);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }}
        h1 {{
            margin: 0 0 10px 0;
            font-size: 2.2rem;
            letter-spacing: -0.5px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 30px;
            font-weight: bold;
            font-size: 0.95rem;
            margin-top: 10px;
        }}
        .status-success {{
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--success-color);
            border: 1px solid var(--success-color);
        }}
        .status-failed {{
            background-color: rgba(239, 68, 68, 0.2);
            color: var(--danger-color);
            border: 1px solid var(--danger-color);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        .card {{
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }}
        .card h3 {{
            margin-top: 0;
            color: var(--text-muted);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .card .value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--text-color);
            margin: 10px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background-color: var(--card-bg);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
        }}
        th {{
            background-color: rgba(2, 132, 199, 0.2);
            font-weight: 600;
            color: var(--primary-color);
            border-bottom: 2px solid var(--border-color);
        }}
        tr {{
            border-bottom: 1px solid var(--border-color);
        }}
        tr:hover {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        .badge-table {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }}
        .badge-success {{
            background-color: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
        }}
        .badge-danger {{
            background-color: rgba(239, 68, 68, 0.1);
            color: var(--danger-color);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Rapport de Qualité des Données</h1>
            <p style="margin: 0; color: var(--text-muted);">Généré automatiquement par le pipeline décisionnel BOA</p>
            <div class="status-badge {'status-success' if global_success else 'status-failed'}">
                { "✓ PIPELINE EXÉCUTÉ AVEC SUCCÈS" if global_success else "✗ ERREURS DE DÉTECTÉES DANS LE TRAITEMENT" }
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <h3>Lignes Chargées</h3>
                <div class="value">{total_rows:,}</div>
                <p style="margin: 0; color: var(--text-muted);">Dans 14 tables opérationnelles</p>
            </div>
            <div class="card">
                <h3>Taux de Validation</h3>
                <div class="value">{validation_rate:.1f} %</div>
                <p style="margin: 0; color: var(--text-muted);">{successful_validations} / {nb_validations} contrôles validés</p>
            </div>
            <div class="card">
                <h3>Qualité Données</h3>
                <p style="margin: 5px 0;"><strong>Doublons :</strong> {total_duplicates}</p>
                <p style="margin: 5px 0;"><strong>Valeurs nulles :</strong> {total_nulls}</p>
            </div>
            <div class="card">
                <h3>Performance Totale</h3>
                <div class="value">{execution_times.get('total', 0.0):.2f} s</div>
                <p style="margin: 0; color: var(--text-muted);">Temps d'exécution total du pipeline</p>
            </div>
        </div>

        <h2>Détail des Performances d'Étapes</h2>
        <table>
            <thead>
                <tr>
                    <th>Étape</th>
                    <th>Description</th>
                    <th>Temps d'exécution (secondes)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Étape 1</td>
                    <td>Génération des DataFrames Pandas</td>
                    <td>{execution_times.get('generate', 0.0):.2f} s</td>
                </tr>
                <tr>
                    <td>Étape 2</td>
                    <td>Validation des règles métiers</td>
                    <td>{execution_times.get('validate', 0.0):.2f} s</td>
                </tr>
                <tr>
                    <td>Étape 3</td>
                    <td>Sauvegarde intermédiaire CSV</td>
                    <td>{execution_times.get('export', 0.0):.2f} s</td>
                </tr>
                <tr>
                    <td>Étape 4</td>
                    <td>Chargement PostgreSQL (Bulk Insert)</td>
                    <td>{execution_times.get('load', 0.0):.2f} s</td>
                </tr>
            </tbody>
        </table>

        <h2>Statut de Cohérence des Tables</h2>
        <table>
            <thead>
                <tr>
                    <th>Composant Métier / Table</th>
                    <th>Volume (Lignes)</th>
                    <th>Contrôles Métier</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Directions Régionales (regions)</td>
                    <td>{len(data_dict.get('regions', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('regions') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('regions') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Agences Bancaires (agences)</td>
                    <td>{len(data_dict.get('agences', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('agences') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('agences') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Collaborateurs RH (employes)</td>
                    <td>{len(data_dict.get('employes', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('employes') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('employes') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Entreprises Clients (entreprises)</td>
                    <td>{len(data_dict.get('entreprises', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('entreprises') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('entreprises') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Comptes Dépôts / DAT (comptes)</td>
                    <td>{len(data_dict.get('comptes', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('comptes') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('comptes') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Catalogue Crédits (produits/programmes/familles)</td>
                    <td>{len(data_dict.get('produits_credits', []))} produits</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('catalogue_credits') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('catalogue_credits') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Contrats Prêts (contrats_credits)</td>
                    <td>{len(data_dict.get('contrats_credits', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('contrats_credits') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('contrats_credits') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Garanties Risques (garanties)</td>
                    <td>{len(data_dict.get('garanties', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('garanties') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('garanties') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Transactions Courantes (transactions)</td>
                    <td>{len(data_dict.get('transactions', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('transactions') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('transactions') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Solutions Digitales Reference (solutions_digitales)</td>
                    <td>{len(data_dict.get('solutions_digitales', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('solutions_digitales') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('solutions_digitales') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Souscriptions Digitales (souscriptions_digitales)</td>
                    <td>{len(data_dict.get('souscriptions_digitales', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('souscriptions_digitales') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('souscriptions_digitales') else "✗ ERREUR"}</span></td>
                </tr>
                <tr>
                    <td>Sessions et Logs Connexions (connexions_digitales)</td>
                    <td>{len(data_dict.get('connexions_digitales', []))}</td>
                    <td><span class="badge-table {'badge-success' if validation_status.get('connexions_digitales') else 'badge-danger'}">{"✓ CONFORME" if validation_status.get('connexions_digitales') else "✗ ERREUR"}</span></td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    try:
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Rapport de qualité généré avec succès : {report_file}")
        return True
    except Exception as e:
        logger.error(f"Échec de l'écriture du rapport HTML : {str(e)}")
        return False
