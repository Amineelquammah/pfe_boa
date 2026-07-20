-- ============================================================================
-- Nom du fichier : database/ddl/07_catalogue_credits.sql
-- Description     : Création du catalogue de crédit (familles, programmes, produits).
-- ============================================================================

-- 1. Table familles_credits
CREATE TABLE oltp.familles_credits (
    id_famille SMALLSERIAL,
    code_famille VARCHAR(20) NOT NULL,
    nom_famille VARCHAR(50) NOT NULL,
    CONSTRAINT pk_familles_credits PRIMARY KEY (id_famille),
    CONSTRAINT uq_familles_credits_code UNIQUE (code_famille)
);

COMMENT ON TABLE oltp.familles_credits IS 'Macro-categories d''engagements financiers';


-- 2. Table programmes_credits
CREATE TABLE oltp.programmes_credits (
    id_programme SERIAL,
    code_programme VARCHAR(30) NOT NULL,
    nom_programme VARCHAR(100) NOT NULL,
    id_famille SMALLINT NOT NULL,
    CONSTRAINT pk_programmes_credits PRIMARY KEY (id_programme),
    CONSTRAINT uq_programmes_credits_code UNIQUE (code_programme)
);

COMMENT ON TABLE oltp.programmes_credits IS 'Programmes specifiques ou lignes d''accompagnement';


-- 3. Table produits_credits
CREATE TABLE oltp.produits_credits (
    id_produit SERIAL,
    code_produit VARCHAR(30) NOT NULL,
    nom_produit VARCHAR(100) NOT NULL,
    description VARCHAR(500) NULL,
    duree_min INTEGER NULL,
    duree_max INTEGER NULL,
    taux_min NUMERIC(5,2) NULL,
    taux_max NUMERIC(5,2) NULL,
    montant_min NUMERIC(15,2) NULL,
    montant_max NUMERIC(15,2) NULL,
    devise VARCHAR(3) NOT NULL DEFAULT 'MAD',
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    id_programme INTEGER NOT NULL,
    CONSTRAINT pk_produits_credits PRIMARY KEY (id_produit),
    CONSTRAINT uq_produits_credits_code UNIQUE (code_produit)
);

COMMENT ON TABLE oltp.produits_credits IS 'Catalogue des produits distribues par agence';
