-- ============================================================================
-- Nom du fichier : database/ddl/12_indexes.sql
-- Description     : Déclaration des index de performance B-Tree.
-- ============================================================================

-- 1. Index sur les Clés Étrangères (FK) pour optimiser les requêtes de jointures
CREATE INDEX idx_agences_region ON oltp.agences (id_region);
CREATE INDEX idx_employes_agence ON oltp.employes (id_agence);
CREATE INDEX idx_entreprises_agence ON oltp.entreprises (id_agence);
CREATE INDEX idx_entreprises_conseiller ON oltp.entreprises (id_conseiller);
CREATE INDEX idx_comptes_entreprise ON oltp.comptes (id_entreprise);
CREATE INDEX idx_transactions_compte ON oltp.transactions (id_compte);
CREATE INDEX idx_programmes_famille ON oltp.programmes_credits (id_famille);
CREATE INDEX idx_produits_programme ON oltp.produits_credits (id_programme);
CREATE INDEX idx_contrats_entreprise ON oltp.contrats_credits (id_entreprise);
CREATE INDEX idx_contrats_produit ON oltp.contrats_credits (id_produit);
CREATE INDEX idx_contrats_conseiller ON oltp.contrats_credits (id_conseiller);
CREATE INDEX idx_contrats_agence ON oltp.contrats_credits (id_agence);
CREATE INDEX idx_garanties_contrat ON oltp.garanties (id_contrat);
CREATE INDEX idx_souscriptions_entreprise ON oltp.souscriptions_digitales (id_entreprise);
CREATE INDEX idx_souscriptions_solution ON oltp.souscriptions_digitales (id_solution);
CREATE INDEX idx_connexions_souscription ON oltp.connexions_digitales (id_entreprise, id_solution);

-- 2. Index de recherche d'identité métier
CREATE INDEX idx_entreprises_ice ON oltp.entreprises (ice);

-- 3. Index temporels pour le filtrage ETL incrémental et l'analyse chronologique
CREATE INDEX idx_transactions_date ON oltp.transactions (date_transaction);
CREATE INDEX idx_connexions_date ON oltp.connexions_digitales (date_connexion);
