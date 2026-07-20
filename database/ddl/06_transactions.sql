-- ============================================================================
-- Nom du fichier : database/ddl/06_transactions.sql
-- Description     : Création de la table transactions dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.transactions (
    id_transaction BIGSERIAL,
    reference_transaction VARCHAR(50) NOT NULL,
    id_compte INTEGER NOT NULL,
    id_entreprise INTEGER NOT NULL,
    id_agence INTEGER NOT NULL,
    id_conseiller INTEGER NOT NULL,
    date_transaction DATE NOT NULL,
    heure_transaction VARCHAR(8) NOT NULL,
    type_transaction VARCHAR(50) NOT NULL,
    canal VARCHAR(50) NOT NULL,
    sens VARCHAR(6) NOT NULL,
    montant NUMERIC(15,2) NOT NULL,
    solde_avant NUMERIC(15,2) NOT NULL,
    solde_apres NUMERIC(15,2) NOT NULL,
    statut VARCHAR(20) NOT NULL,
    CONSTRAINT pk_transactions PRIMARY KEY (id_transaction),
    CONSTRAINT uq_transactions_ref UNIQUE (reference_transaction),
    CONSTRAINT chk_transactions_sens CHECK (sens IN ('DEBIT', 'CREDIT'))
);

COMMENT ON TABLE oltp.transactions IS 'Historique des flux financiers passes sur les comptes';
