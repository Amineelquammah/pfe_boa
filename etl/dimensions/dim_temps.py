# -*- coding: utf-8 -*-
"""
Nom du fichier : etl/dimensions/dim_temps.py
Description     : Alimentation de la dimension Temps (dim_temps) dans le DWH.
Source          : Génération autonome d'un calendrier de 2022 à 2024.
"""

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_dim_temps() -> bool:
    """
    Génère et charge la dimension Temps dans dwh.dim_temps.
    
    Returns:
        bool: True si l'alimentation s'est terminée sans erreur.
    """
    logger.info("Début de l'alimentation de la dimension Temps (dim_temps)...")
    
    start_date = datetime.strptime("2022-01-01", "%Y-%m-%d")
    end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    
    dates = []
    curr = start_date
    while curr <= end_date:
        dates.append(curr)
        curr += timedelta(days=1)
        
    calendar = []
    month_names = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    day_names = {
        0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi", 4: "Vendredi", 5: "Samedi", 6: "Dimanche"
    }
    
    for dt in dates:
        sk = int(dt.strftime("%Y%m%d"))
        semestre = 1 if dt.month <= 6 else 2
        est_we = "Oui" if dt.weekday() >= 5 else "Non"
        
        calendar.append({
            "temps_sk": sk,
            "date_temps": dt.date(),
            "jour": dt.day,
            "mois": dt.month,
            "nom_mois": month_names[dt.month],
            "trimestre": (dt.month - 1) // 3 + 1,
            "nom_trimestre": f"T{(dt.month - 1) // 3 + 1}",
            "semestre": semestre,
            "annee": dt.year,
            "jour_semaine": day_names[dt.weekday()],
            "est_weekend": est_we
        })
        
    df_temps = pd.DataFrame(calendar)
    
    try:
        df_temps.to_sql(
            name="dim_temps",
            con=engine,
            schema="dwh",
            if_exists="replace",
            index=False,
            chunksize=5000,
            method="multi"
        )
        logger.info(f"Dimension dim_temps alimentée ({len(df_temps)} lignes).")
        return True
    except SQLAlchemyError as e:
        logger.error(f"Erreur SQL sur dim_temps : {str(e)}")
        return False

if __name__ == "__main__":
    success = load_dim_temps()
    print(f"Alimentation dim_temps : {'RÉUSSI' if success else 'ÉCHEC'}")
