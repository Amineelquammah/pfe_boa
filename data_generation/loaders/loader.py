# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/loaders/loader.py
Description     : Module de chargement des DataFrames dans la base PostgreSQL sous transaction unique.
"""

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from data_generation.utils.database import engine
from data_generation.utils.logger import logger

def load_data_to_postgres(data_dict: dict) -> bool:
    """
    Insère tous les DataFrames dans le schéma 'oltp' de PostgreSQL au sein d'une transaction unique.
    En cas d'erreur de contrainte ou d'accès, la transaction est annulée (rollback automatique).
    
    Args:
        data_dict (dict): Dictionnaire contenant les DataFrames à insérer.
        
    Returns:
        bool: True si l'insertion s'est déroulée avec succès.
    """
    logger.info("Démarrage du processus de chargement dans PostgreSQL...")
    
    # Ordre strict pour respecter les contraintes d'intégrité référentielle (FK)
    tables_order = [
        ("regions", "regions"),
        ("agences", "agences"),
        ("employes", "employes"),
        ("entreprises", "entreprises"),
        ("comptes", "comptes"),
        ("familles_credits", "familles_credits"),
        ("programmes_credits", "programmes_credits"),
        ("produits_credits", "produits_credits"),
        ("contrats_credits", "contrats_credits"),
        ("garanties", "garanties"),
        ("transactions", "transactions"),
        ("solutions_digitales", "solutions_digitales"),
        ("souscriptions_digitales", "souscriptions_digitales"),
        ("connexions_digitales", "connexions_digitales")
    ]
    
    # Utilisation du context manager d'engine.begin() pour garantir une transaction globale unique
    # Tout commit ou rollback est géré automatiquement à la sortie du bloc.
    with engine.begin() as connection:
        try:
            # 1. Vidage des tables existantes dans le sens inverse pour les dépendances
            logger.info("Vidage préalable des tables existantes (TRUNCATE CASCADE)...")
            for _, table_name in reversed(tables_order):
                connection.execute(text(f"TRUNCATE TABLE oltp.{table_name} CASCADE;"))
                
            # 2. Chargement successif de chaque DataFrame avec nettoyage des colonnes
            for key, table_name in tables_order:
                df = data_dict[key].copy()
                
                # Renommer les colonnes pour correspondre exactement aux spécifications DDL
                if key == "contrats_credits":
                    cols = ['id_contrat', 'numero_contrat', 'id_entreprise', 'id_agence', 'id_conseiller', 'id_produit', 'date_octroi', 'date_echeance', 'montant_principal', 'taux_interet', 'encours_restant', 'statut']
                    df = df[cols]
                elif key == "garanties":
                    cols = ['id_garantie', 'numero_garantie', 'id_contrat', 'type_garantie', 'valeur', 'date_affectation']
                    df = df[cols]
                elif key == "comptes":
                    cols = ['id_compte', 'numero_compte', 'rib', 'iban', 'type_compte', 'devise', 'date_ouverture', 'statut', 'solde_actuel', 'id_entreprise', 'id_agence', 'id_conseiller', 'id_compte_courant_parent', 'date_dernier_mouvement', 'classification']
                    df = df[cols]
                elif key == "regions":
                    cols = ['id_region', 'nom_region']
                    df = df[cols]
                elif key == "agences":
                    cols = ['id_agence', 'code_agence', 'nom_agence', 'ville', 'adresse', 'date_ouverture', 'statut', 'id_region']
                    df = df[cols]
                elif key == "employes":
                    cols = ['id_employe', 'matricule', 'nom', 'prenom', 'sexe', 'date_naissance', 'date_embauche', 'fonction', 'service', 'email_professionnel', 'telephone', 'statut', 'id_agence', 'id_region', 'manager_id']
                    df = df[cols]
                elif key == "entreprises":
                    cols = ['id_entreprise', 'ice', 'raison_sociale', 'forme_juridique', 'secteur_activite', 'segment', 'chiffre_affaires', 'nombre_employes', 'date_creation', 'ville', 'adresse', 'telephone', 'email', 'statut', 'id_agence', 'id_conseiller']
                    df = df[cols]
                elif key == "transactions":
                    cols = ['id_transaction', 'reference_transaction', 'id_compte', 'id_entreprise', 'id_agence', 'id_conseiller', 'date_transaction', 'heure_transaction', 'type_transaction', 'canal', 'sens', 'montant', 'solde_avant', 'solde_apres', 'statut']
                    df = df[cols]
                elif key == "solutions_digitales":
                    cols = ['id_solution', 'nom_solution', 'description', 'canal', 'statut']
                    df = df[cols]
                elif key == "souscriptions_digitales":
                    cols = ['id_souscription', 'id_entreprise', 'id_solution', 'date_souscription', 'statut', 'niveau_utilisation']
                    df = df[cols]
                elif key == "connexions_digitales":
                    cols = ['id_connexion', 'id_entreprise', 'id_solution', 'date_connexion', 'heure_connexion', 'duree_session', 'adresse_ip', 'navigateur', 'systeme', 'appareil', 'action_realisee', 'statut']
                    df = df[cols]
                    
                # Convert date columns to datetime objects for database compatibility
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        
                # Écriture brute rapide en base
                df.to_sql(
                    name=table_name,
                    con=connection,
                    schema="oltp",
                    if_exists="append",
                    index=False,
                    method="multi",
                    chunksize=2000
                )
                logger.info(f"Chargement réussi : table oltp.{table_name} ({len(df)} lignes).")
                
            logger.info("Toutes les données ont été chargées avec succès. Validation du commit.")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Échec de l'insertion en base : {str(e)}. Rollback automatique exécuté.")
            raise e
