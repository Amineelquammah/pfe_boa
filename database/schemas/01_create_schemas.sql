-- ============================================================================
-- Nom du fichier : database/schemas/01_create_schemas.sql
-- Description     : Initialisation des quatre couches logiques de la base.
-- ============================================================================

-- Connexion requise sur la base pfe_boa_db avant exécution.

-- 1. Couche transactionnelle (OLTP)
CREATE SCHEMA IF NOT EXISTS oltp;
COMMENT ON SCHEMA oltp IS 'Couche de stockage transactionnelle normalisee (source)';

-- 2. Couche staging (ETL Buffer)
CREATE SCHEMA IF NOT EXISTS staging;
COMMENT ON SCHEMA staging IS 'Couche tampon pour le chargement ETL (donnees brutes)';

-- 3. Couche entrepôt de données (DWH)
CREATE SCHEMA IF NOT EXISTS dwh;
COMMENT ON SCHEMA dwh IS 'Couche de stockage dimensionnel (schema en etoile)';

-- 4. Couche d''exposition (Data Marts)
CREATE SCHEMA IF NOT EXISTS datamarts;
COMMENT ON SCHEMA datamarts IS 'Couche d''exposition et restitution metier pour Power BI';
