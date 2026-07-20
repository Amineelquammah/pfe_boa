-- ============================================================================
-- Nom du fichier : database/ddl/02_agences.sql
-- Description     : Création de la table agences dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.agences (
    id_agence SERIAL,
    code_agence VARCHAR(20) NOT NULL,
    nom_agence VARCHAR(100) NOT NULL,
    ville VARCHAR(50) NOT NULL,
    adresse VARCHAR(200) NOT NULL,
    date_ouverture DATE NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'Active',
    id_region SMALLINT NOT NULL,
    CONSTRAINT pk_agences PRIMARY KEY (id_agence),
    CONSTRAINT uq_agences_nom UNIQUE (nom_agence),
    CONSTRAINT uq_agences_code UNIQUE (code_agence)
);

COMMENT ON TABLE oltp.agences IS 'Table des agences physiques du reseau BOA';
