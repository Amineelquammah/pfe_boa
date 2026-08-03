# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/facts/fait_credits.py
Description     : Alimentation de la table de faits fait_credits (Trimestrielle).
Granularité     : Un contrat × un trimestre.
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_fait_credits() -> bool:
    """
    Extrait les contrats de crédit de staging, calcule l'état d'amortissement trimestriel,
    associe les surrogate keys (SK) et charge dwh.fait_credits.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la table de faits fait_credits...")
    try:
        # 1. Extraction des données
        df_con = pd.read_sql_table(table_name="contrats_credits", con=engine, schema="staging")
        
        # Charger les dimensions
        dim_ent = pd.read_sql_table(table_name="dim_entreprise", con=engine, schema="dwh")
        dim_prod = pd.read_sql_table(table_name="dim_produit_credit", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table(table_name="dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table(table_name="dim_region", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table(table_name="dim_employe", con=engine, schema="dwh")
        
        # Trimestres de simulation (fin de trimestres)
        quarter_ends = [
            datetime(2022, 3, 31), datetime(2022, 6, 30), datetime(2022, 9, 30), datetime(2022, 12, 31),
            datetime(2023, 3, 31), datetime(2023, 6, 30), datetime(2023, 9, 30), datetime(2023, 12, 31),
            datetime(2024, 3, 31), datetime(2024, 6, 30), datetime(2024, 9, 30), datetime(2024, 12, 31)
        ]
        
        facts = []
        
        # 2. Projection historique par trimestre pour chaque contrat
        for _, row in df_con.iterrows():
            contrat_id = int(row["id_contrat"])
            ent_id = int(row["id_entreprise"])
            ag_id = int(row["id_agence"])
            cons_id = int(row["id_conseiller"])
            prod_id = int(row["id_produit"])
            
            date_octroi = pd.to_datetime(row["date_octroi"])
            date_echeance = pd.to_datetime(row["date_echeance"])
            
            montant_principal = float(row["montant_principal"])
            taux_interet = float(row["taux_interet"])
            statut_final = row["statut"]
            
            # Paramètres de base
            duree = (date_echeance - date_octroi).days // 30.4
            duree = max(1, int(duree))
            
            r = taux_interet / (100.0 * 12.0)
            if r > 0:
                mensualite = (montant_principal * r) / (1.0 - (1.0 + r) ** -duree)
            else:
                mensualite = montant_principal / duree
            mensualite = round(mensualite, 2)
            
            # Projeter l'état du contrat à chaque fin de trimestre
            for q_end in quarter_ends:
                # Le contrat n'a de faits que s'il est déjà octroyé dans ce trimestre
                if date_octroi > q_end:
                    continue
                    
                # Nombre de mois passés depuis l'octroi
                months_passed = (q_end.year - date_octroi.year) * 12 + (q_end.month - date_octroi.month)
                if q_end.day < date_octroi.day:
                    months_passed -= 1
                months_passed = max(0, min(months_passed, duree))
                
                # Calcul de l'amortissement
                capital_rembourse = 0.0
                interets_payes = 0.0
                encours_restant = montant_principal
                
                temp_balance = montant_principal
                for m in range(months_passed):
                    interest_part = temp_balance * r
                    principal_part = mensualite - interest_part
                    if principal_part > temp_balance:
                        principal_part = temp_balance
                        interest_part = max(0.0, mensualite - principal_part)
                    
                    capital_rembourse += principal_part
                    interets_payes += interest_part
                    temp_balance -= principal_part
                    
                capital_rembourse = round(capital_rembourse, 2)
                interets_payes = round(interets_payes, 2)
                encours_restant = round(max(0.0, temp_balance), 2)
                
                # Retards de paiement (uniquement pertinents pour les trimestres récents si le crédit est NPL/Surveillance)
                # On projette le retard final uniquement sur les trimestres de 2024 pour simplifier
                jours_retard = 0
                statut_trim = "SAIN"
                
                if encours_restant > 0:
                    if statut_final == "NPL" and q_end.year == 2024:
                        jours_retard = 95
                        statut_trim = "NPL"
                    elif statut_final == "SURVEILLANCE" and q_end.year == 2024:
                        jours_retard = 45
                        statut_trim = "SURVEILLANCE"
                        
                facts.append({
                    "id_contrat": contrat_id,
                    "id_entreprise": ent_id,
                    "id_agence": ag_id,
                    "id_conseiller": cons_id,
                    "id_produit": prod_id,
                    "temps_sk": int(q_end.strftime("%Y%m%d")),
                    "montant_octroye": montant_principal,
                    "encours_restant": encours_restant,
                    "capital_rembourse": capital_rembourse,
                    "interets_payes": interets_payes,
                    "mensualite": mensualite,
                    "jours_retard": jours_retard,
                    "indicateur_npl": 1 if statut_trim == "NPL" else 0,
                    "taux_interet": taux_interet
                })
                
        df_proj = pd.DataFrame(facts)
        
        # 3. Récupération des Surrogate Keys
        df_fact = pd.merge(df_proj, dim_ent[["id_entreprise", "entreprise_sk"]], on="id_entreprise", how="inner")
        df_fact = pd.merge(df_fact, dim_prod[["id_produit", "produit_credit_sk"]], on="id_produit", how="inner")
        df_fact = pd.merge(df_fact, dim_ag[["id_agence", "agence_sk"]], on="id_agence", how="inner")
        
        # Jointure region (via agence)
        df_ag_staging = pd.read_sql_table(table_name="agences", con=engine, schema="staging")
        df_fact = pd.merge(df_fact, df_ag_staging[["id_agence", "id_region"]], on="id_agence", how="inner")
        df_fact = pd.merge(df_fact, dim_reg[["id_region", "region_sk"]], on="id_region", how="inner")
        
        # Jointure employe (conseiller)
        df_fact = pd.merge(df_fact, dim_emp[["id_employe", "employe_sk"]], left_on="id_conseiller", right_on="id_employe", how="inner")
        
        # Sélection des colonnes finales
        final_cols = [
            "temps_sk", "entreprise_sk", "produit_credit_sk", "agence_sk", "region_sk", "employe_sk",
            "montant_octroye", "encours_restant", "capital_rembourse", "interets_payes",
            "mensualite", "jours_retard", "indicateur_npl", "taux_interet"
        ]
        df_final = df_fact[final_cols].copy()
        
        # Chargement
        df_final.to_sql(
            name="fait_credits",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False,
            chunksize=2000,
            method="multi"
        )
        logger.info(f"Table de faits fait_credits alimentée ({len(df_final)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur fait_credits : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur fait_credits : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_fait_credits()
    print(f"Alimentation fait_credits : {'RÉUSSI' if success else 'ÉCHEC'}")
