-- ============================================================================
-- Nom du fichier : database/ddl/13_utilisateurs_roles_permissions.sql
-- Description     : Création des tables d'authentification et d'habilitations.
-- ============================================================================

-- 1. Table des rôles
CREATE TABLE oltp.roles (
    id_role SERIAL,
    code_role VARCHAR(50) NOT NULL,
    nom_role VARCHAR(100) NOT NULL,
    CONSTRAINT pk_roles PRIMARY KEY (id_role),
    CONSTRAINT uq_roles_code UNIQUE (code_role)
);

COMMENT ON TABLE oltp.roles IS 'Rôles des utilisateurs pour le contrôle d''accès';

-- 2. Table des permissions
CREATE TABLE oltp.permissions (
    id_permission SERIAL,
    code_permission VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    CONSTRAINT pk_permissions PRIMARY KEY (id_permission),
    CONSTRAINT uq_permissions_code UNIQUE (code_permission)
);

COMMENT ON TABLE oltp.permissions IS 'Permissions fines applicables aux fonctionnalités';

-- 3. Table de liaison Rôles-Permissions (Relation M:N)
CREATE TABLE oltp.role_permissions (
    id_role INTEGER NOT NULL,
    id_permission INTEGER NOT NULL,
    CONSTRAINT pk_role_permissions PRIMARY KEY (id_role, id_permission),
    CONSTRAINT fk_role_permissions_role FOREIGN KEY (id_role) REFERENCES oltp.roles(id_role) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_permission FOREIGN KEY (id_permission) REFERENCES oltp.permissions(id_permission) ON DELETE CASCADE
);

COMMENT ON TABLE oltp.role_permissions IS 'Table de liaison entre les rôles et leurs permissions';

-- 4. Table des utilisateurs
CREATE TABLE oltp.utilisateurs (
    id_utilisateur SERIAL,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    id_role INTEGER NOT NULL,
    id_employe INTEGER NULL,
    id_agence INTEGER NULL,
    id_region INTEGER NULL,
    nom VARCHAR(50) NULL,
    prenom VARCHAR(50) NULL,
    telephone_professionnel VARCHAR(20) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    last_activity TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_utilisateurs PRIMARY KEY (id_utilisateur),
    CONSTRAINT uq_utilisateurs_username UNIQUE (username),
    CONSTRAINT uq_utilisateurs_email UNIQUE (email),
    CONSTRAINT fk_utilisateurs_role FOREIGN KEY (id_role) REFERENCES oltp.roles(id_role),
    CONSTRAINT fk_utilisateurs_employe FOREIGN KEY (id_employe) REFERENCES oltp.employes(id_employe) ON DELETE SET NULL,
    CONSTRAINT fk_utilisateurs_agence FOREIGN KEY (id_agence) REFERENCES oltp.agences(id_agence) ON DELETE SET NULL,
    CONSTRAINT fk_utilisateurs_region FOREIGN KEY (id_region) REFERENCES oltp.regions(id_region) ON DELETE SET NULL
);

COMMENT ON TABLE oltp.utilisateurs IS 'Comptes utilisateurs de la plateforme decisionnelle';

-- Index de performance sur les clés étrangères
CREATE INDEX idx_utilisateurs_role ON oltp.utilisateurs(id_role);
CREATE INDEX idx_utilisateurs_employe ON oltp.utilisateurs(id_employe);
CREATE INDEX idx_utilisateurs_agence ON oltp.utilisateurs(id_agence);
CREATE INDEX idx_utilisateurs_region ON oltp.utilisateurs(id_region);
