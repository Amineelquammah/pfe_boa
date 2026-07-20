-- ============================================================================
-- Nom du fichier : database/ddl/01_regions.sql
-- Description     : Création de la table regions dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.regions (
    id_region SMALLSERIAL,
    nom_region VARCHAR(50) NOT NULL,
    CONSTRAINT pk_regions PRIMARY KEY (id_region),
    CONSTRAINT uq_regions_nom UNIQUE (nom_region)
);

COMMENT ON TABLE oltp.regions IS 'Table des regions administratives de la banque';
COMMENT ON COLUMN oltp.regions.id_region IS 'Identifiant unique de la region (Smallserial)';
COMMENT ON COLUMN oltp.regions.nom_region IS 'Nom de la direction regionale BOA';
