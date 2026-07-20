-- ============================================================================
-- Nom du fichier : database/ddl/04_entreprises.sql
-- Description     : Création de la table entreprises dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.entreprises (
    id_entreprise SERIAL,
    ice VARCHAR(15) NOT NULL,
    raison_sociale VARCHAR(100) NOT NULL,
    forme_juridique VARCHAR(20) NOT NULL,
    secteur_activite VARCHAR(50) NOT NULL,
    segment VARCHAR(20) NOT NULL,
    chiffre_affaires NUMERIC(15,2) NOT NULL,
    nombre_employes INTEGER NOT NULL,
    date_creation DATE NOT NULL,
    ville VARCHAR(50) NOT NULL,
    adresse VARCHAR(200) NULL,
    telephone VARCHAR(20) NULL,
    email VARCHAR(100) NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    id_agence INTEGER NOT NULL,
    id_conseiller INTEGER NOT NULL,
    CONSTRAINT pk_entreprises PRIMARY KEY (id_entreprise),
    CONSTRAINT uq_entreprises_ice UNIQUE (ice)
);

COMMENT ON TABLE oltp.entreprises IS 'Table des clients professionnels Business Banking';
