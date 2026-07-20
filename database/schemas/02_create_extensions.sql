-- ============================================================================
-- Nom du fichier : database/schemas/02_create_extensions.sql
-- Description     : Activation des extensions PostgreSQL requises.
-- ============================================================================

-- Extension pour la génération automatique de clés UUID (si requis ultérieurement)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension pour les fonctions de chiffrement (si requis)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
