# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/pipeline/step03_export_csv.py
Description     : Étape 3 du pipeline : sauvegarde des DataFrames en fichiers CSV.
"""

import os
from typing import Dict
import pandas as pd
from data_generation.utils.logger import logger
from data_generation.config.config import BASE_DIR

def run_export_csv(data_dict: Dict[str, pd.DataFrame]) -> bool:
    """
    Exporte l'ensemble des DataFrames du dictionnaire sous forme de fichiers CSV dans data/generated/.
    
    Args:
        data_dict (Dict[str, pd.DataFrame]): Dictionnaire des DataFrames.
        
    Returns:
        bool: True si l'export s'est terminé sans erreur.
    """
    logger.info("=========================================")
    logger.info("DÉBUT ÉTAPE 3 : EXPORT DES FICHIERS CSV")
    logger.info("=========================================")
    
    # Création du dossier cible s'il n'existe pas
    export_dir = BASE_DIR / "data" / "generated"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Ordre des colonnes physiques de la DDL
    ddl_cols = {
        "regions": ['id_region', 'nom_region'],
        "agences": ['id_agence', 'code_agence', 'nom_agence', 'ville', 'adresse', 'date_ouverture', 'statut', 'id_region'],
        "employes": ['id_employe', 'matricule', 'nom', 'prenom', 'sexe', 'date_naissance', 'date_embauche', 'fonction', 'service', 'email_professionnel', 'telephone', 'statut', 'id_agence', 'id_region', 'manager_id'],
        "entreprises": ['id_entreprise', 'ice', 'raison_sociale', 'forme_juridique', 'secteur_activite', 'segment', 'chiffre_affaires', 'nombre_employes', 'date_creation', 'ville', 'adresse', 'telephone', 'email', 'statut', 'id_agence', 'id_conseiller'],
        "comptes": ['id_compte', 'numero_compte', 'rib', 'iban', 'type_compte', 'devise', 'date_ouverture', 'statut', 'solde_actuel', 'id_entreprise', 'id_agence', 'id_conseiller', 'id_compte_courant_parent', 'date_dernier_mouvement', 'classification'],
        "familles_credits": ['id_famille', 'code_famille', 'nom_famille'],
        "programmes_credits": ['id_programme', 'code_programme', 'nom_programme', 'id_famille'],
        "produits_credits": ['id_produit', 'code_produit', 'nom_produit', 'description', 'duree_min', 'duree_max', 'taux_min', 'taux_max', 'montant_min', 'montant_max', 'devise', 'statut', 'id_programme'],
        "contrats_credits": ['id_contrat', 'numero_contrat', 'id_entreprise', 'id_agence', 'id_conseiller', 'id_produit', 'date_octroi', 'date_echeance', 'montant_principal', 'taux_interet', 'encours_restant', 'statut'],
        "garanties": ['id_garantie', 'numero_garantie', 'id_contrat', 'type_garantie', 'valeur', 'date_affectation'],
        "transactions": ['id_transaction', 'reference_transaction', 'id_compte', 'id_entreprise', 'id_agence', 'id_conseiller', 'date_transaction', 'heure_transaction', 'type_transaction', 'canal', 'sens', 'montant', 'solde_avant', 'solde_apres', 'statut'],
        "solutions_digitales": ['id_solution', 'nom_solution', 'description', 'canal', 'statut'],
        "souscriptions_digitales": ['id_souscription', 'id_entreprise', 'id_solution', 'date_souscription', 'statut', 'niveau_utilisation'],
        "connexions_digitales": ['id_connexion', 'id_entreprise', 'id_solution', 'date_connexion', 'heure_connexion', 'duree_session', 'adresse_ip', 'navigateur', 'systeme', 'appareil', 'action_realisee', 'statut']
    }
    
    try:
        for key, df in data_dict.items():
            file_path = export_dir / f"{key}.csv"
            df_to_save = df.copy()
            if key in ddl_cols:
                # Filtrer les colonnes physiques de la DDL
                df_to_save = df_to_save[ddl_cols[key]]
            
            # Sauvegarde au format CSV avec encodage UTF-8 et séparateur virgule
            df_to_save.to_csv(file_path, index=False, encoding="utf-8")
            logger.info(f"Fichier exporté avec succès : {file_path} ({len(df)} lignes).")
            
        logger.info("Étape 3 terminée avec succès.")
        return True
    except Exception as e:
        logger.error(f"Échec de l'export des fichiers CSV : {str(e)}")
        return False
