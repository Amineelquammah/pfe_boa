# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_catalogue_credits.py
Description     : Générateur des tables de référence du catalogue de crédit BOA.
"""

from typing import Tuple
import pandas as pd
from data_generation.utils.logger import logger

def generate_catalogue_credits() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Génère la hiérarchie complète du catalogue de crédit de Bank of Africa :
    les familles de crédits, les programmes, et les produits correspondants.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: DataFrames (familles, programmes, produits).
    """
    logger.info("Début de la génération du catalogue de crédit...")
    
    # ---------------------------------------------------------
    # 1. FAMILLES DE CRÉDITS
    # ---------------------------------------------------------
    familles = [
        {"id_famille": 1, "code_famille": "EXPLOITATION", "nom_famille": "Crédit d'exploitation"},
        {"id_famille": 2, "code_famille": "INVESTISSEMENT", "nom_famille": "Crédit d'investissement"},
        {"id_famille": 3, "code_famille": "TRADE_FINANCE", "nom_famille": "Trade Finance"},
        {"id_famille": 4, "code_famille": "GARANTIES", "nom_famille": "Garanties et Engagements"}
    ]
    df_familles = pd.DataFrame(familles)
    
    # ---------------------------------------------------------
    # 2. PROGRAMMES DE CRÉDITS
    # ---------------------------------------------------------
    programmes = [
        # Famille 1 : Exploitation
        {"id_programme": 1, "code_programme": "DECOUVERT", "nom_programme": "Découvert", "id_famille": 1},
        {"id_programme": 2, "code_programme": "FACILITE_CAISSE", "nom_programme": "Facilité de caisse", "id_famille": 1},
        {"id_programme": 3, "code_programme": "CAMPAGNE", "nom_programme": "Crédit de campagne", "id_famille": 1},
        
        # Famille 2 : Investissement
        {"id_programme": 4, "code_programme": "INVEST_CLASSIQUE", "nom_programme": "Investissement classique", "id_famille": 2},
        {"id_programme": 5, "code_programme": "MAROC_PME", "nom_programme": "Maroc PME", "id_famille": 2},
        {"id_programme": 6, "code_programme": "TAMWILCOM", "nom_programme": "Tamwilcom", "id_famille": 2},
        {"id_programme": 7, "code_programme": "GREEN_FINANCE", "nom_programme": "Green Finance", "id_famille": 2},
        
        # Famille 3 : Trade Finance
        {"id_programme": 8, "code_programme": "IMPORT", "nom_programme": "Import", "id_famille": 3},
        {"id_programme": 9, "code_programme": "EXPORT", "nom_programme": "Export", "id_famille": 3},
        {"id_programme": 10, "code_programme": "CREDOC", "nom_programme": "Crédits documentaires", "id_famille": 3},
        
        # Famille 4 : Garanties
        {"id_programme": 11, "code_programme": "CAUTION", "nom_programme": "Caution bancaire", "id_famille": 4},
        {"id_programme": 12, "code_programme": "AVAL", "nom_programme": "Aval", "id_famille": 4},
        {"id_programme": 13, "code_programme": "SOUMISSION", "nom_programme": "Garantie de soumission", "id_famille": 4},
        {"id_programme": 14, "code_programme": "BONNE_FIN", "nom_programme": "Garantie de bonne fin", "id_famille": 4}
    ]
    df_programmes = pd.DataFrame(programmes)
    
    # ---------------------------------------------------------
    # 3. PRODUITS DE CRÉDITS
    # ---------------------------------------------------------
    produits = [
        # Découvert
        {
            "id_produit": 1, "code_produit": "PROD_DECOUVERT_COURT", "nom_produit": "Découvert Garanti BOA", 
            "description": "Ligne de découvert court terme pour la trésorerie courante", 
            "duree_min": 1, "duree_max": 12, "taux_min": 5.5, "taux_max": 8.0, 
            "montant_min": 50000.0, "montant_max": 5000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 1
        },
        # Facilité de Caisse
        {
            "id_produit": 2, "code_produit": "PROD_FACILITE_COURT", "nom_produit": "Facilité de Caisse Entreprise", 
            "description": "Financement des décalages ponctuels de trésorerie", 
            "duree_min": 1, "duree_max": 12, "taux_min": 6.0, "taux_max": 8.5, 
            "montant_min": 20000.0, "montant_max": 2000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 2
        },
        # Crédit de campagne
        {
            "id_produit": 3, "code_produit": "PROD_CAMPAGNE_AGRI", "nom_produit": "Crédit de Campagne Agricole", 
            "description": "Financement saisonnier lié au cycle agricole marocain", 
            "duree_min": 3, "duree_max": 12, "taux_min": 5.0, "taux_max": 7.5, 
            "montant_min": 50000.0, "montant_max": 10000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 3
        },
        # Investissement Classique
        {
            "id_produit": 4, "code_produit": "PROD_INVEST_EQUIPEMENT", "nom_produit": "Crédit Moyen Long Terme Classique", 
            "description": "Financement classique des équipements et des infrastructures", 
            "duree_min": 12, "duree_max": 120, "taux_min": 4.5, "taux_max": 6.5, 
            "montant_min": 100000.0, "montant_max": 50000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 4
        },
        # Maroc PME
        {
            "id_produit": 5, "code_produit": "PROD_MAROC_PME_DEV", "nom_produit": "Ligne Maroc PME Invest", 
            "description": "Crédit d'investissement conventionné avec l'agence Maroc PME", 
            "duree_min": 24, "duree_max": 84, "taux_min": 4.0, "taux_max": 5.5, 
            "montant_min": 100000.0, "montant_max": 20000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 5
        },
        # Tamwilcom
        {
            "id_produit": 6, "code_produit": "PROD_TAMWILCOM_GAR", "nom_produit": "Co-financement Tamwilcom", 
            "description": "Crédit d'investissement garanti par la SNGFE (Tamwilcom)", 
            "duree_min": 36, "duree_max": 120, "taux_min": 3.5, "taux_max": 5.0, 
            "montant_min": 500000.0, "montant_max": 30000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 6
        },
        # Green Finance
        {
            "id_produit": 7, "code_produit": "PROD_GREEN_INVEST", "nom_produit": "Financement Green Invest", 
            "description": "Ligne verte de transition écologique et efficacité énergétique", 
            "duree_min": 36, "duree_max": 120, "taux_min": 3.0, "taux_max": 4.8, 
            "montant_min": 500000.0, "montant_max": 40000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 7
        },
        # Import
        {
            "id_produit": 8, "code_produit": "PROD_FIN_IMPORT", "nom_produit": "Avance sur Marché Import", 
            "description": "Financement de l'approvisionnement à l'international", 
            "duree_min": 1, "duree_max": 6, "taux_min": 4.5, "taux_max": 6.8, 
            "montant_min": 100000.0, "montant_max": 20000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 8
        },
        # Export
        {
            "id_produit": 9, "code_produit": "PROD_FIN_EXPORT", "nom_produit": "Préfinancement à l'Exportation", 
            "description": "Financement de la trésorerie pour couvrir la production exportable", 
            "duree_min": 1, "duree_max": 9, "taux_min": 4.2, "taux_max": 6.5, 
            "montant_min": 100000.0, "montant_max": 20000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 9
        },
        # Crédits documentaires
        {
            "id_produit": 10, "code_produit": "PROD_CREDOC_CONF", "nom_produit": "Crédit Documentaire Confirmé", 
            "description": "Garantie de paiement de transactions commerciales internationales", 
            "duree_min": 1, "duree_max": 12, "taux_min": 4.0, "taux_max": 6.0, 
            "montant_min": 200000.0, "montant_max": 100000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 10
        },
        # Caution Bancaire
        {
            "id_produit": 11, "code_produit": "PROD_CAUTION_ADMIN", "nom_produit": "Caution Administrative en MAD", 
            "description": "Engagement de signature pour répondre aux marchés publics", 
            "duree_min": 1, "duree_max": 36, "taux_min": 1.0, "taux_max": 2.5, 
            "montant_min": 10000.0, "montant_max": 10000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 11
        },
        # Aval
        {
            "id_produit": 12, "code_produit": "PROD_AVAL_EFFET", "nom_produit": "Aval d'Effets de Commerce", 
            "description": "Garantie de paiement d'effets de commerce tirés", 
            "duree_min": 1, "duree_max": 12, "taux_min": 1.5, "taux_max": 3.0, 
            "montant_min": 50000.0, "montant_max": 50000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 12
        },
        # Garantie de Soumission
        {
            "id_produit": 13, "code_produit": "PROD_CAUTION_SOUM", "nom_produit": "Garantie de Soumission de Marché", 
            "description": "Caution requise lors de l'appel d'offres", 
            "duree_min": 1, "duree_max": 12, "taux_min": 0.8, "taux_max": 2.0, 
            "montant_min": 10000.0, "montant_max": 5000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 13
        },
        # Garantie de Bonne Fin
        {
            "id_produit": 14, "code_produit": "PROD_CAUTION_BONNE_FIN", "nom_produit": "Garantie de Bonne Fin de Marché", 
            "description": "Caution de bon déroulement d'exécution de marché", 
            "duree_min": 6, "duree_max": 60, "taux_min": 1.0, "taux_max": 2.2, 
            "montant_min": 50000.0, "montant_max": 20000000.0, "devise": "MAD", "statut": "ACTIF", "id_programme": 14
        }
    ]
    df_produits = pd.DataFrame(produits)
    
    logger.info(f"Génération terminée : {len(df_familles)} familles, {len(df_programmes)} programmes et {len(df_produits)} produits.")
    return df_familles, df_programmes, df_produits

if __name__ == "__main__":
    df_fam, df_prog, df_prod = generate_catalogue_credits()
    print("\n--- TEST CATALOGUE CREDITS ---")
    print("\n--- FAMILLES ---")
    print(df_fam)
    print("\n--- PROGRAMMES ---")
    print(df_prog.head(5))
    print("\n--- PRODUITS ---")
    print(df_prod.head(5))
    
    print("\n--- STATISTIQUES DES MONTANTS ---")
    print(df_prod[["montant_min", "montant_max"]].describe())
    print("\n--- STATISTIQUES DES TAUX ---")
    print(df_prod[["taux_min", "taux_max"]].describe())
