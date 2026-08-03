# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/generators/generate_contrats_credits.py
Description     : Générateur des contrats de crédits accordés aux entreprises.
"""

import pandas as pd
import random
import math
from typing import List, Dict, Any
from datetime import datetime, timedelta
from data_generation.utils.logger import logger
from data_generation.generators.generate_entreprises import generate_entreprises
from data_generation.generators.generate_catalogue_credits import generate_catalogue_credits

def generate_contrats_credits() -> pd.DataFrame:
    """
    Génère environ 1000 contrats de crédit pour les entreprises BOA,
    en respectant le ratio d'endettement <= 45% et les bornes produits.
    
    Returns:
        pd.DataFrame: DataFrame des contrats de crédit.
    """
    logger.info("Début de la génération des contrats de crédit...")
    random.seed(42)  # Reproductibilité
    
    # Chargement des entreprises et du catalogue de crédit
    df_entreprises = generate_entreprises()
    _, _, df_produits = generate_catalogue_credits()
    
    # Organiser les produits par segment d'éligibilité pour éviter les incohérences
    # TPE : Découvert, Facilité caisse, Campagne, Cautions (IDs: 1, 2, 3, 11, 13)
    # PME : Tout sauf les très grosses enveloppes
    # GE : Tout avec de grands montants
    prod_dict = df_produits.set_index("id_produit").to_dict(orient="index")
    
    contrats: List[Dict[str, Any]] = []
    current_id = 1
    sim_end_date = datetime.strptime("2024-12-31", "%Y-%m-%d")
    
    # Nous voulons environ 1000 contrats de crédit.
    # Pour y parvenir de manière stable, nous pouvons sélectionner les entreprises éligibles.
    # Environ 50% des 2000 entreprises auront au moins un crédit.
    # Loop à travers les entreprises :
    for _, ent in df_entreprises.iterrows():
        ent_id = int(ent["id_entreprise"])
        ag_id = int(ent["id_agence"])
        cons_id = int(ent["id_conseiller"])
        segment = ent["segment"]
        ca_annuel = float(ent["chiffre_affaires"])
        date_creation_ent = datetime.strptime(str(ent["date_creation"]), "%Y-%m-%d")
        
        # 1. Probabilité d'avoir un crédit selon le segment
        if segment == "TPE":
            prob = 0.40
            eligible_prod_ids = [1, 2, 3, 11, 13]
        elif segment == "PME":
            prob = 0.65
            eligible_prod_ids = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14]
        else: # Grande Entreprise
            prob = 0.85
            eligible_prod_ids = [1, 4, 6, 7, 10, 12, 14]
            
        # Décision d'octroi de crédit
        if random.random() > prob:
            continue
            
        # Nombre de crédits pour cette entreprise (la plupart en ont 1, certaines 2)
        nb_credits = 1 if random.random() < 0.85 else 2
        
        for cred_idx in range(nb_credits):
            # Choisir un produit éligible
            prod_id = random.choice(eligible_prod_ids)
            prod = prod_dict[prod_id]
            
            # 2. Capacité d'endettement mensuelle (max 45% du CA annuel divisé par 12)
            capacité_mensuelle = (ca_annuel * 0.45) / 12.0
            
            # Choisir une durée aléatoire dans les limites du produit
            duree = random.randint(int(prod["duree_min"]), int(prod["duree_max"]))
            
            # Déterminer le montant accordé
            # Montant max théorique basé sur la capacité et la durée du prêt
            max_montant_capacite = capacité_mensuelle * duree
            
            montant_min = float(prod["montant_min"])
            montant_max = float(prod["montant_max"])
            
            # Ajustement réaliste de l'enveloppe selon le segment de l'entreprise
            if segment == "TPE":
                montant_max = min(montant_max, 1000000.0)
            elif segment == "PME":
                montant_max = min(montant_max, 15000000.0)
                
            # Choisir le montant
            montant_accorde = random.uniform(montant_min, min(montant_max, max(montant_min + 1000, max_montant_capacite)))
            montant_accorde = round(montant_accorde, 2)
            montant_demande = round(montant_accorde * random.uniform(1.0, 1.15), 2)  # Demande légèrement supérieure
            
            # Taux d'intérêt dans les bornes du produit
            taux = round(random.uniform(float(prod["taux_min"]), float(prod["taux_max"])), 2)
            
            # 3. Dates
            # Taux d'intérêt périodique r
            r = taux / (100.0 * 12.0)
            
            # Déterminer la cible de remboursement P et calculer months_passed
            u = random.random()
            if u < 0.10:
                # 10% totalement remboursés (encours < 10 MAD)
                months_passed_extra = random.randint(0, 12)
                total_months_ago = duree + months_passed_extra
            elif u < 0.30:
                # 20% : entre 70% et 80% du capital remboursé
                p_target = random.uniform(0.70, 0.80)
                if r > 0:
                    val_inside = 1.0 + p_target * ((1.0 + r) ** duree - 1.0)
                    m_float = math.log(val_inside) / math.log(1.0 + r)
                    months_passed = int(round(m_float))
                else:
                    months_passed = int(round(p_target * duree))
                months_passed = max(0, min(months_passed, duree - 1))
                total_months_ago = months_passed
            elif u < 0.70:
                # 40% : entre 30% et 70% du capital remboursé
                p_target = random.uniform(0.30, 0.70)
                if r > 0:
                    val_inside = 1.0 + p_target * ((1.0 + r) ** duree - 1.0)
                    m_float = math.log(val_inside) / math.log(1.0 + r)
                    months_passed = int(round(m_float))
                else:
                    months_passed = int(round(p_target * duree))
                months_passed = max(0, min(months_passed, duree - 1))
                total_months_ago = months_passed
            else:
                # 30% : moins de 30% du capital remboursé
                p_target = random.uniform(0.01, 0.30)
                if r > 0:
                    val_inside = 1.0 + p_target * ((1.0 + r) ** duree - 1.0)
                    m_float = math.log(val_inside) / math.log(1.0 + r)
                    months_passed = int(round(m_float))
                else:
                    months_passed = int(round(p_target * duree))
                months_passed = max(0, min(months_passed, duree - 1))
                total_months_ago = months_passed
            
            # Reculer de total_months_ago mois par rapport à sim_end_date
            year_offset = total_months_ago // 12
            month_offset = total_months_ago % 12
            
            octroi_year = sim_end_date.year - year_offset
            octroi_month = sim_end_date.month - month_offset
            
            if octroi_month <= 0:
                octroi_month += 12
                octroi_year -= 1
                
            day_octroi = random.randint(1, 28)
            date_octroi = datetime(octroi_year, octroi_month, day_octroi)
            
            # S'assurer que le crédit n'a pas été octroyé avant la création de l'entreprise
            if date_octroi < date_creation_ent + timedelta(days=30):
                date_octroi = date_creation_ent + timedelta(days=random.randint(30, 90))
                # Ajuster si cela dépasse la date de fin de simulation
                if date_octroi >= sim_end_date:
                    date_octroi = sim_end_date - timedelta(days=random.randint(1, 10))
            
            date_demande = date_octroi - timedelta(days=random.randint(10, 45))
            date_1ere_ech = date_octroi + timedelta(days=30)
            date_fin = date_octroi + timedelta(days=int(duree * 30.4))
            
            # 4. Calcul de la Mensualité (formule d'amortissement constante)
            # Pour les garanties / cautions (taux faible d'engagement), c'est une commission linéaire
            if r > 0:
                mensualite = (montant_accorde * r) / (1.0 - (1.0 + r) ** -duree)
            else:
                mensualite = montant_accorde / duree
            mensualite = round(mensualite, 2)
            
            # 5. Calcul de l'Amortissement au 31/12/2024
            # Nombre de mensualités payées
            months_passed = (sim_end_date.year - date_octroi.year) * 12 + (sim_end_date.month - date_octroi.month)
            if sim_end_date.day < date_octroi.day:
                months_passed -= 1
                
            months_passed = max(0, min(months_passed, duree))
            
            # Simulation de l'historique d'amortissement
            capital_rembourse = 0.0
            interets_payes = 0.0
            encours_restant = montant_accorde
            
            temp_balance = montant_accorde
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
            montant_rembourse = round(capital_rembourse + interets_payes, 2)
            
            # 6. Gestion du Risque et Retard (au 31/12/2024)
            # 0 = Sain, 1-89 = Surveillance, 90+ = NPL
            jours_retard = 0
            statut_val = "SAIN"
            statut_risque = "SAIN"
            indicateur_npl = False
            
            # Ne simuler des retards que si le prêt est en cours (encours > 0) et qu'au moins 1 mois est passé
            if encours_restant > 0 and months_passed > 0:
                risk_rand = random.random()
                # TPE plus risquées que PME et GE
                npl_threshold = 0.06 if segment == "TPE" else (0.04 if segment == "PME" else 0.02)
                surv_threshold = npl_threshold + 0.08
                
                if risk_rand < npl_threshold:
                    # NPL (90 jours et plus de retard)
                    jours_retard = random.randint(90, 270)
                    statut_val = "NPL"
                    statut_risque = "NPL"
                    indicateur_npl = True
                    # Ajuster l'encours pour simuler des mensualités impayées (encours restant plus élevé)
                    missed_months = min(months_passed, int(jours_retard / 30))
                    # On rajoute la part en retard dans l'encours (approximation)
                    encours_restant = min(montant_accorde, round(encours_restant + (missed_months * mensualite * 0.8), 2))
                    capital_rembourse = max(0.0, round(montant_accorde - encours_restant, 2))
                    montant_rembourse = round(capital_rembourse + interets_payes, 2)
                elif risk_rand < surv_threshold:
                    # Surveillance (1 à 89 jours de retard)
                    jours_retard = random.randint(5, 80)
                    statut_val = "SURVEILLANCE"
                    statut_risque = "SURVEILLANCE"
                    
            # Si le prêt est complètement remboursé
            if encours_restant == 0.0:
                statut_val = "SAIN"
                statut_risque = "SAIN"
                
            cont = {
                "id_contrat": current_id,
                "numero_contrat": f"CON_{current_id:06d}",
                "id_entreprise": ent_id,
                "id_agence": ag_id,
                "id_conseiller": cons_id,
                "id_produit": prod_id,
                "date_demande": date_demande.strftime("%Y-%m-%d"),
                "date_octroi": date_octroi.strftime("%Y-%m-%d"),
                "date_premiere_echeance": date_1ere_ech.strftime("%Y-%m-%d"),
                "date_echeance": date_fin.strftime("%Y-%m-%d"),
                "montant_demande": montant_demande,
                "montant_principal": montant_accorde,
                "duree": duree,
                "taux_interet": taux,
                "mensualite": mensualite,
                "encours_restant": encours_restant,
                "montant_rembourse": montant_rembourse,
                "capital_rembourse": capital_rembourse,
                "interets_payes": interets_payes,
                "jours_retard": jours_retard,
                "statut": statut_val,
                "statut_risque": statut_risque,
                "indicateur_npl": indicateur_npl
            }
            contrats.append(cont)
            current_id += 1
            
            # Limiter pour cibler exactement environ 1000 contrats (par exemple max 1050)
            if len(contrats) >= 1010:
                break
        if len(contrats) >= 1010:
            break
            
    df_contrats = pd.DataFrame(contrats)
    logger.info(f"Génération terminée : {len(df_contrats)} contrats de crédit générés.")
    return df_contrats

if __name__ == "__main__":
    df = generate_contrats_credits()
    print("\n--- TEST GENERATE CONTRATS CREDITS ---")
    print(df.head(5))
    
    print("\n--- NOMBRE TOTAL DE CONTRATS ---")
    print(len(df))
    
    print("\n--- REPARTITION DES STATUTS DE RISQUE ---")
    print(df["statut"].value_counts())
    
    print("\n--- TAUX DE NPL GLOBAL ---")
    npl_rate = df["indicateur_npl"].mean() * 100
    print(f"{npl_rate:.2f} %")
    
    print("\n--- MONTANT TOTAL OCTROYE ---")
    print(f"{df['montant_principal'].sum():,.2f} MAD")
