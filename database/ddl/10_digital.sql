-- ============================================================================
-- Nom du fichier : database/ddl/10_digital.sql
-- Description     : Création des tables du domaine digital (solutions, souscriptions, connexions).
-- ============================================================================

-- 1. Table solutions_digitales
CREATE TABLE oltp.solutions_digitales (
    id_solution SMALLSERIAL,
    nom_solution VARCHAR(50) NOT NULL,
    description VARCHAR(500) NULL,
    canal VARCHAR(50) NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    CONSTRAINT pk_solutions_digitales PRIMARY KEY (id_solution),
    CONSTRAINT uq_solutions_nom UNIQUE (nom_solution)
);

COMMENT ON TABLE oltp.solutions_digitales IS 'Catalogue des solutions digitales proposees aux clients';


-- 2. Table souscriptions_digitales
CREATE TABLE oltp.souscriptions_digitales (
    id_souscription SERIAL,
    id_entreprise INTEGER NOT NULL,
    id_solution SMALLINT NOT NULL,
    date_souscription DATE NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'ACTIF',
    niveau_utilisation VARCHAR(20) NOT NULL DEFAULT 'MOYEN',
    CONSTRAINT pk_souscriptions_digitales PRIMARY KEY (id_souscription),
    CONSTRAINT uq_souscriptions_pivot UNIQUE (id_entreprise, id_solution),
    CONSTRAINT chk_souscriptions_statut CHECK (statut IN ('ACTIF', 'RESILIE'))
);

COMMENT ON TABLE oltp.souscriptions_digitales IS 'Table pivot d''adhesion des entreprises aux services digitaux';


-- 3. Table connexions_digitales
CREATE TABLE oltp.connexions_digitales (
    id_connexion BIGSERIAL,
    id_entreprise INTEGER NOT NULL,
    id_solution SMALLINT NOT NULL,
    date_connexion DATE NOT NULL,
    heure_connexion VARCHAR(8) NOT NULL,
    duree_session INTEGER NOT NULL,
    adresse_ip VARCHAR(45) NOT NULL,
    navigateur VARCHAR(50) NOT NULL,
    systeme VARCHAR(50) NOT NULL,
    appareil VARCHAR(50) NOT NULL,
    action_realisee VARCHAR(100) NOT NULL,
    statut VARCHAR(20) NOT NULL,
    CONSTRAINT pk_connexions_digitales PRIMARY KEY (id_connexion)
);

COMMENT ON TABLE oltp.connexions_digitales IS 'Logs de connexions et volumes d''operations digitales';
