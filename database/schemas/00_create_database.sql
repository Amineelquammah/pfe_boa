-- ============================================================================
-- Nom du fichier : database/schemas/00_create_database.sql
-- Description     : Création physique de la base de données principale.
-- ============================================================================

-- Note: Ce script doit être exécuté par un superutilisateur (ex: postgres).
-- S'assurer qu'aucune connexion n'est active lors de la suppression (si applicable).

-- DROP DATABASE IF EXISTS pfe_boa_db;

CREATE DATABASE pfe_boa_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_Morocco.1252'
    LC_CTYPE = 'French_Morocco.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

COMMENT ON DATABASE pfe_boa_db IS 'Base de donnees decisionnelle Business Banking BOA Maroc';
