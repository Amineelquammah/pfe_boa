-- ============================================================================
-- Nom du fichier : database/ddl/03_employes.sql
-- Description     : Création de la table employes dans le schéma oltp.
-- ============================================================================

CREATE TABLE oltp.employes (
    id_employe SERIAL,
    matricule VARCHAR(20) NOT NULL,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    sexe VARCHAR(1) NULL,
    date_naissance DATE NULL,
    date_embauche DATE NOT NULL,
    fonction VARCHAR(50) NOT NULL,
    service VARCHAR(50) NOT NULL,
    email_professionnel VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'Actif',
    id_agence INTEGER NULL,
    id_region INTEGER NULL,
    manager_id INTEGER NULL,
    CONSTRAINT pk_employes PRIMARY KEY (id_employe),
    CONSTRAINT uq_employes_matricule UNIQUE (matricule)
);

COMMENT ON TABLE oltp.employes IS 'Table des ressources humaines de la banque';
