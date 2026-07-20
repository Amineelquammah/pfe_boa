-- ============================================================================
-- Nom du fichier : database/ddl/05_comptes.sql
-- Description     : Création de la table comptes dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.comptes (
    id_compte SERIAL,
    numero_compte VARCHAR(20) NOT NULL,
    rib VARCHAR(24) NOT NULL,
    iban VARCHAR(34) NOT NULL,
    type_compte VARCHAR(10) NOT NULL,
    devise VARCHAR(3) NOT NULL DEFAULT 'MAD',
    date_ouverture DATE NOT NULL,
    statut VARCHAR(10) NOT NULL DEFAULT 'ACTIF',
    solde_actuel NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    id_entreprise INTEGER NOT NULL,
    id_agence INTEGER NULL,
    id_conseiller INTEGER NULL,
    id_compte_courant_parent INTEGER NULL,
    date_dernier_mouvement DATE NULL,
    classification VARCHAR(20) NULL,
    CONSTRAINT pk_comptes PRIMARY KEY (id_compte),
    CONSTRAINT uq_comptes_rib UNIQUE (rib)
);

COMMENT ON TABLE oltp.comptes IS 'Table des comptes de depots et placements (DAT) des clients';
