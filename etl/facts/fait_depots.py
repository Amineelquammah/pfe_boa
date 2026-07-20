# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/facts/fait_depots.py
Description     : Alimentation de la table de faits fait_depots (Trimestrielle).
Granularité     : Un compte × un trimestre (identifié par la fin de trimestre).
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_fait_depots() -> bool:
    """
    Extrait les transactions et comptes de staging, associe les surrogate keys (SK) 
    depuis les dimensions du DWH, agrège les mesures par compte et trimestre,
    et charge dwh.fait_depots.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation de la table de faits fait_depots...")
    try:
        # 1. Extraction des données de Staging
        df_tx = pd.read_sql_table(table_name="transactions", con=engine, schema="staging")
        df_cpt = pd.read_sql_table(table_name="comptes", con=engine, schema="staging")
        
        # Charger les dimensions pour récupérer les surrogate keys
        dim_compte = pd.read_sql_table(table_name="dim_compte", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table(table_name="dim_entreprise", con=engine, schema="dwh")
        dim_ag = pd.read_sql_table(table_name="dim_agence", con=engine, schema="dwh")
        dim_reg = pd.read_sql_table(table_name="dim_region", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table(table_name="dim_employe", con=engine, schema="dwh")
        
        # 2. Transformations temporelles des transactions
        df_tx["date_dt"] = pd.to_datetime(df_tx["date_transaction"])
        df_tx["annee"] = df_tx["date_dt"].dt.year
        df_tx["trimestre"] = (df_tx["date_dt"].dt.month - 1) // 3 + 1
        
        # Mapper le trimestre à la date de fin de trimestre (temps_sk)
        q_end_dates = {
            (2022, 1): 20220331, (2022, 2): 20220630, (2022, 3): 20220930, (2022, 4): 20221231,
            (2023, 1): 20230331, (2023, 2): 20230630, (2023, 3): 20230930, (2023, 4): 20231231,
            (2024, 1): 20240331, (2024, 2): 20240630, (2024, 3): 20240930, (2024, 4): 20241231
        }
        df_tx["temps_sk"] = df_tx.apply(lambda r: q_end_dates.get((r["annee"], r["trimestre"])), axis=1)
        
        # 3. Agrégation des mesures par compte et trimestre
        aggs = []
        for (cpt_id, temps_sk), grp in df_tx.groupby(["id_compte", "temps_sk"]):
            versements = grp[grp["sens"] == "CREDIT"]["montant"].sum()
            retraits = grp[grp["sens"] == "DEBIT"]["montant"].sum()
            nb_tx = len(grp)
            solde_moyen = grp["solde_apres"].mean()
            # Encours = solde après de la toute dernière transaction du groupe chronologique
            last_row = grp.sort_values(by=["date_transaction", "heure_transaction"]).iloc[-1]
            encours = last_row["solde_apres"]
            
            aggs.append({
                "id_compte": cpt_id,
                "temps_sk": temps_sk,
                "montant_versements": round(versements, 2),
                "montant_retraits": round(retraits, 2),
                "collecte_nette": round(versements - retraits, 2),
                "nombre_transactions": nb_tx,
                "solde_moyen_trimestriel": round(solde_moyen, 2),
                "encours": round(encours, 2),
                "nombre_comptes_actifs": 1 if nb_tx > 0 else 0
            })
            
        df_agg = pd.DataFrame(aggs)
        
        # 4. Jointures séquentielles pour récupérer les Surrogate Keys (SK)
        # A. Récupération de compte_sk
        df_fact = pd.merge(df_agg, dim_compte[["id_compte", "compte_sk"]], on="id_compte", how="inner")
        
        # B. Récupération des clés métiers associées au compte (id_entreprise, id_agence, id_conseiller)
        df_cpt_meta = df_cpt[["id_compte", "id_entreprise", "id_agence", "id_conseiller"]]
        df_fact = pd.merge(df_fact, df_cpt_meta, on="id_compte", how="inner")
        
        # C. Jointure entreprise -> entreprise_sk (id_region exclu de la sélection)
        df_fact = pd.merge(df_fact, dim_ent[["id_entreprise", "entreprise_sk"]], on="id_entreprise", how="inner")
        
        # D. Jointure agence -> agence_sk et récupération d'id_region
        df_fact = pd.merge(df_fact, dim_ag[["id_agence", "agence_sk", "id_region"]], on="id_agence", how="inner")
        
        # E. Jointure region -> region_sk (via id_region récupéré d'agence)
        df_fact = pd.merge(df_fact, dim_reg[["id_region", "region_sk"]], on="id_region", how="inner")
        
        # F. Jointure employe (conseiller) -> employe_sk
        df_fact = pd.merge(df_fact, dim_emp[["id_employe", "employe_sk"]], left_on="id_conseiller", right_on="id_employe", how="inner")
        
        # 5. Sélection des colonnes finales de la table de faits
        final_cols = [
            "temps_sk", "compte_sk", "entreprise_sk", "agence_sk", "region_sk", "employe_sk",
            "solde_moyen_trimestriel", "encours", "montant_versements", "montant_retraits",
            "collecte_nette", "nombre_transactions", "nombre_comptes_actifs"
        ]
        df_final = df_fact[final_cols].copy()
        
        # 6. Chargement dans le schéma DWH (chunksize=2000 pour pg8000)
        df_final.to_sql(
            name="fait_depots",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False,
            chunksize=2000,
            method="multi"
        )
        logger.info(f"Table de faits fait_depots alimentée ({len(df_final)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur fait_depots : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur fait_depots : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_fait_depots()
    print(f"Alimentation fait_depots : {'RÉUSSI' if success else 'ÉCHEC'}")