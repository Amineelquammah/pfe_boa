-- ============================================================================
-- Nom du fichier : database/ddl/08_contrats_credits.sql
-- Description     : Création de la table contrats_credits dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.contrats_credits (
    id_contrat SERIAL,
    numero_contrat VARCHAR(20) NOT NULL,
    id_entreprise INTEGER NOT NULL,
    id_agence INTEGER NOT NULL,
    id_conseiller INTEGER NOT NULL,
    id_produit INTEGER NOT NULL,
    date_octroi DATE NOT NULL,
    date_echeance DATE NOT NULL,
    montant_principal NUMERIC(15,2) NOT NULL,
    taux_interet NUMERIC(5,2) NOT NULL,
    encours_restant NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    statut VARCHAR(20) NOT NULL,
    CONSTRAINT pk_contrats_credits PRIMARY KEY (id_contrat)
);

COMMENT ON TABLE oltp.contrats_credits IS 'Contrats de credits accordes aux clients professionnels';
