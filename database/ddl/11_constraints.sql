-- ============================================================================
-- Nom du fichier : database/ddl/11_constraints.sql
-- Description     : Déclaration des contraintes de clés étrangères (FK).
-- ============================================================================

-- Note: Ce script est execute en dernier pour eviter les problemes de dependances cycliques.

-- 1. Table agences
ALTER TABLE oltp.agences
    ADD CONSTRAINT fk_agences_region FOREIGN KEY (id_region)
    REFERENCES oltp.regions (id_region) ON DELETE RESTRICT;

-- 2. Table employes
ALTER TABLE oltp.employes
    ADD CONSTRAINT fk_employes_agence FOREIGN KEY (id_agence)
    REFERENCES oltp.agences (id_agence) ON DELETE RESTRICT;

-- 3. Table entreprises
ALTER TABLE oltp.entreprises
    ADD CONSTRAINT fk_entreprises_agence FOREIGN KEY (id_agence)
    REFERENCES oltp.agences (id_agence) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_entreprises_conseiller FOREIGN KEY (id_conseiller)
    REFERENCES oltp.employes (id_employe) ON DELETE RESTRICT;

-- 4. Table comptes
ALTER TABLE oltp.comptes
    ADD CONSTRAINT fk_comptes_entreprise FOREIGN KEY (id_entreprise)
    REFERENCES oltp.entreprises (id_entreprise) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_comptes_parent FOREIGN KEY (id_compte_courant_parent)
    REFERENCES oltp.comptes (id_compte) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_comptes_conseiller FOREIGN KEY (id_conseiller)
    REFERENCES oltp.employes (id_employe) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_comptes_agence FOREIGN KEY (id_agence)
    REFERENCES oltp.agences (id_agence) ON DELETE RESTRICT;

-- 5. Table transactions
ALTER TABLE oltp.transactions
    ADD CONSTRAINT fk_transactions_compte FOREIGN KEY (id_compte)
    REFERENCES oltp.comptes (id_compte) ON DELETE RESTRICT;

-- 6. Table programmes_credits
ALTER TABLE oltp.programmes_credits
    ADD CONSTRAINT fk_programmes_famille FOREIGN KEY (id_famille)
    REFERENCES oltp.familles_credits (id_famille) ON DELETE RESTRICT;

-- 7. Table produits_credits
ALTER TABLE oltp.produits_credits
    ADD CONSTRAINT fk_produits_programme FOREIGN KEY (id_programme)
    REFERENCES oltp.programmes_credits (id_programme) ON DELETE RESTRICT;

-- 8. Table contrats_credits
ALTER TABLE oltp.contrats_credits
    ADD CONSTRAINT fk_contrats_entreprise FOREIGN KEY (id_entreprise)
    REFERENCES oltp.entreprises (id_entreprise) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_contrats_produit FOREIGN KEY (id_produit)
    REFERENCES oltp.produits_credits (id_produit) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_contrats_conseiller FOREIGN KEY (id_conseiller)
    REFERENCES oltp.employes (id_employe) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_contrats_agence FOREIGN KEY (id_agence)
    REFERENCES oltp.agences (id_agence) ON DELETE RESTRICT;

-- 9. Table garanties
ALTER TABLE oltp.garanties
    ADD CONSTRAINT fk_garanties_contrat FOREIGN KEY (id_contrat)
    REFERENCES oltp.contrats_credits (id_contrat) ON DELETE RESTRICT;

-- 10. Table souscriptions_digitales
ALTER TABLE oltp.souscriptions_digitales
    ADD CONSTRAINT fk_souscriptions_entreprise FOREIGN KEY (id_entreprise)
    REFERENCES oltp.entreprises (id_entreprise) ON DELETE RESTRICT,
    ADD CONSTRAINT fk_souscriptions_solution FOREIGN KEY (id_solution)
    REFERENCES oltp.solutions_digitales (id_solution) ON DELETE RESTRICT;

-- 11. Table connexions_digitales
ALTER TABLE oltp.connexions_digitales
    ADD CONSTRAINT fk_connexions_souscription FOREIGN KEY (id_entreprise, id_solution)
    REFERENCES oltp.souscriptions_digitales (id_entreprise, id_solution) ON DELETE RESTRICT;
