-- ============================================================================
-- Nom du fichier : database/ddl/09_garanties.sql
-- Description     : Création de la table garanties dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.garanties (
    id_garantie SERIAL,
    numero_garantie VARCHAR(50) NOT NULL,
    id_contrat INTEGER NOT NULL,
    type_garantie VARCHAR(50) NOT NULL,
    valeur NUMERIC(15,2) NOT NULL,
    date_affectation DATE NOT NULL,
    CONSTRAINT pk_garanties PRIMARY KEY (id_garantie),
    CONSTRAINT uq_garanties_ref UNIQUE (numero_garantie)
);

COMMENT ON TABLE oltp.garanties IS 'Garanties et suretes prises en couverture de credit';
