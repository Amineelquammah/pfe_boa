# BOA - Data Warehouse

Ce projet contient l'ensemble de la chaîne décisionnelle et d'acquisition de données pour BOA Maroc.

## Contenu
* **data_generation/** : Scripts de simulation de données réalistes.
* **database/** : Scripts DDL de création de tables, contraintes, index et seeding.
* **etl/** : Pipeline d'ingestion staging, DWH et Data Marts.
* **documentation/** : Spécifications et documents de conception (MCD, MLD, dictionnaire de données).

## Exécution
1. Configuration de la base de données dans `.env`.
2. Lancer la génération des données :
   `python -m data_generation.main`
3. Lancer l'ETL de chargement :
   `python -m etl.main_etl`
