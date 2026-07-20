# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/datamarts/dm_performance.py
Description     : Alimentation du Data Mart DM_Performance (Commercial, Agence et Région).
Source          : fait_depots + fait_credits + dimensions DWH
"""

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dm_performance() -> bool:
    """
    Extrait et fusionne les indicateurs de dépôts, crédits et digitalisation
    au grain Conseiller × Trimestre, et charge datamarts.dm_performance.
    
    Returns:
        bool: True si réussite.
    """
    logger.info("Début de l'alimentation du Data Mart DM_Performance...")
    try:
        # Extraction des faits et dimensions nécessaires
        df_dep = pd.read_sql_table("fait_depots", con=engine, schema="dwh")
        df_cred = pd.read_sql_table("fait_credits", con=engine, schema="dwh")
        
        dim_temps = pd.read_sql_table("dim_temps", con=engine, schema="dwh")
        dim_ent = pd.read_sql_table("dim_entreprise", con=engine, schema="dwh")
        dim_emp = pd.read_sql_table("dim_employe", con=engine, schema="dwh")
        
        # Joindre les faits avec dim_entreprise pour récupérer les axes client
        df_dep_joined = pd.merge(df_dep, dim_ent[["entreprise_sk", "segment", "secteur_activite", "notation_interne", "potentiel_commercial"]], on="entreprise_sk", how="inner")
        df_cred_joined = pd.merge(df_cred, dim_ent[["entreprise_sk", "segment", "secteur_activite", "notation_interne", "potentiel_commercial"]], on="entreprise_sk", how="inner")
        
        # 1. Agrégation dépôts par conseiller, trimestre et axes client
        df_dep_agg = df_dep_joined.groupby(["employe_sk", "temps_sk", "segment", "secteur_activite", "notation_interne", "potentiel_commercial"]).agg(
            encours_depots=("encours", "sum"),
            collecte_nette=("collecte_nette", "sum"),
            nombre_comptes_actifs=("nombre_comptes_actifs", "sum")
        ).reset_index()
        
        # 2. Agrégation crédits par conseiller, trimestre et axes client
        df_cred_agg = df_cred_joined.groupby(["employe_sk", "temps_sk", "segment", "secteur_activite", "notation_interne", "potentiel_commercial"]).agg(
            encours_credits=("encours_restant", "sum"),
            production_credits=("montant_octroye", "sum"),
            nombre_credits=("montant_octroye", "size")
        ).reset_index()
        
        # 3. Fusion des deux faits (Outer join sur employe_sk, temps_sk, et les axes client)
        df_perf = pd.merge(df_dep_agg, df_cred_agg, on=["employe_sk", "temps_sk", "segment", "secteur_activite", "notation_interne", "potentiel_commercial"], how="outer")
        df_perf.fillna(0.0, inplace=True)
        
        # 4. Jointures dimensions pour les axes temporels et géographiques/commerciaux
        df_perf = pd.merge(df_perf, dim_temps[["temps_sk", "annee", "nom_trimestre"]], on="temps_sk", how="inner")
        
        dim_emp["nom_conseiller"] = dim_emp["prenom"] + " " + dim_emp["nom"]
        df_perf = pd.merge(df_perf, dim_emp[["employe_sk", "nom_conseiller", "nom_agence", "nom_region", "nom_manager"]], on="employe_sk", how="inner")
        
        # 5. Calcul des métriques portefeuilles par conseiller
        ent_counts = dim_ent.groupby("id_conseiller").size().to_dict()
        dig_map = {"Élevé": 1.0, "Moyen": 0.5, "Faible": 0.1}
        dim_ent["dig_num"] = dim_ent["niveau_digitalisation"].map(dig_map)
        dig_scores = dim_ent.groupby("id_conseiller")["dig_num"].mean().to_dict()
        sk_to_id = dim_emp.set_index("employe_sk")["id_employe"].to_dict()
        
        def get_nb_ent(sk):
            emp_id = sk_to_id.get(sk, -1)
            return ent_counts.get(emp_id, 0)
            
        def get_dig_rate(sk):
            emp_id = sk_to_id.get(sk, -1)
            return round(dig_scores.get(emp_id, 0.0) * 100, 2)
            
        df_perf["nombre_entreprises_gerees"] = df_perf["employe_sk"].apply(get_nb_ent)
        df_perf["taux_digitalisation_portefeuille"] = df_perf["employe_sk"].apply(get_dig_rate)
        
        # Arrondir les montants et les comptes
        float_cols = ["encours_depots", "collecte_nette", "encours_credits", "production_credits", "nombre_comptes_actifs", "nombre_credits"]
        df_perf[float_cols] = df_perf[float_cols].round(2)
        
        # Convertir les comptes et crédits en entiers après fillna / round
        df_perf["nombre_comptes_actifs"] = df_perf["nombre_comptes_actifs"].astype(int)
        df_perf["nombre_credits"] = df_perf["nombre_credits"].astype(int)
        
        # Chargement
        df_perf.to_sql(
            name="dm_performance",
            con=engine,
            schema="datamarts",
            if_exists="replace",
            index=False
        )
        logger.info(f"Data Mart dm_performance alimenté ({len(df_perf)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dm_performance : {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue sur dm_performance : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dm_performance()
    print(f"Alimentation dm_performance : {'RÉUSSI' if success else 'ÉCHEC'}")
