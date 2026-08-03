# Spécification de la Conception Physique PostgreSQL (DDL)
## Plateforme Décisionnelle Business Banking (Bank of Africa)

---

### 1. Architecture des Schémas PostgreSQL

Pour organiser au mieux le cycle de vie de la donnée au sein du SGBD PostgreSQL, la base de données utilisera quatre schémas logiques distincts :

*   **`oltp`** : Contient le modèle relationnel opérationnel normalisé (3NF). C'est la source transactionnelle du projet, regroupant les 14 tables de référence, de contrats et de flux.
*   **`staging`** : Zone de transit temporaire pour le pipeline ETL. Elle accueille les copies conformes des tables de l'OLTP sans aucune contrainte de clés étrangères afin de fluidifier l'extraction des données sans risquer de bloquer la base de production.
*   **`dwh`** : Héberge le modèle de données décisionnel dénormalisé en **schéma en étoile** (les 9 dimensions et les 4 tables de faits).
*   **`datamarts`** : Exposition finale des données structurées et agrégées par domaine métier (Dépôts, Crédits, Risques, Digital, Performance) prêtes à être lues par Power BI.

---

### 2. Organisation de l'Arborescence des Scripts SQL

Les scripts SQL de création de la base de données, des schémas, des extensions, des tables opérationnelles (DDL), des contraintes et des index seront organisés de manière modulaire au sein de l'arborescence du projet. Cette structure permet un déploiement incrémental et reproductible sous PostgreSQL :

```
database/
├── schemas/
│   ├── 00_create_database.sql      # Création physique de la base de données
│   ├── 01_create_schemas.sql       # Initialisation des schémas oltp, staging, dwh, datamarts
│   └── 02_extensions.sql           # Activation des extensions nécessaires (ex: uuid-ossp, pgcrypto)
└── ddl/
    ├── 01_regions.sql              # Table regions (oltp)
    ├── 02_agences.sql              # Table agences (oltp)
    ├── 03_employes.sql             # Table employes (oltp)
    ├── 04_entreprises.sql          # Table entreprises (oltp)
    ├── 05_comptes.sql              # Table comptes (oltp)
    ├── 06_transactions.sql         # Table transactions (oltp)
    ├── 07_catalogue_credits.sql    # Tables familles_credits, programmes_credits, produits_credits
    ├── 08_contrats_credits.sql     # Table contrats_credits (oltp)
    ├── 09_garanties.sql            # Table garanties (oltp)
    ├── 10_digital.sql              # Tables solutions_digitales, souscriptions_digitales, connexions_digitales
    ├── 11_constraints.sql          # Déclaration globale des contraintes ALTER TABLE (FK, CHECK)
    └── 12_indexes.sql              # Déclaration globale de la création des index physiques (B-Tree)
```

---

### 3. Ordre Logique de Création des Tables (Graphe des Dépendances)

L'exécution des scripts DDL doit respecter un ordre strict en raison des dépendances physiques (clés étrangères). Aucune table enfant ne doit être créée avant sa table parente :

```
1.  regions (Aucune dépendance)
      │
      ▼
2.  agences (Dépend de regions)
      │
      ▼
3.  employes (Dépend de agences)
      │
      ▼
4.  entreprises (Dépend de agences, employes)
      │
      ├───► 5. comptes (Dépend de entreprises et d'elle-même pour la hiérarchie DAT/Courant)
      │           │
      │           ▼
      │        6. transactions (Dépend de comptes)
      │
      ├───► 7. familles_credits (Aucune dépendance)
      │           │
      │           ▼
      │        8. programmes_credits (Dépend de familles_credits)
      │           │
      │           ▼
      │        9. produits_credits (Dépend de programmes_credits)
      │           │
      │           ▼
      ├──────► 10. contrats_credits (Dépend de entreprises, produits_credits, employes, agences)
      │           │
      │           ▼
      │        11. garanties (Dépend de contrats_credits)
      │
      └───► 12. solutions_digitales (Aucune dépendance)
                  │
                  ▼
               13. souscriptions_digitales (Dépend de entreprises, solutions_digitales)
                  │
                  ▼
               14. connexions_digitales (Dépend de souscriptions_digitales)
```

---

### 4. Conventions PostgreSQL (Nomenclature & Typage)

#### A. Choix des Types de Données Physiques
*   **`SMALLSERIAL`** : Auto-incrément codé sur 2 octets (valeurs de 1 à 32 767). Idéal pour optimiser le stockage des clés primaires de petites tables de configuration (`regions`, `solutions_digitales`).
*   **`SERIAL`** : Auto-incrément standard sur 4 octets. Utilisé pour la majorité des identifiants uniques (`agences`, `employes`, `entreprises`, `comptes`, `contrats_credits`, `garanties`, `programmes_credits`, `produits_credits`, `souscriptions_digitales`).
*   **`BIGSERIAL`** : Auto-incrément codé sur 8 octets pour les tables à très forte volumétrie transactionnelle afin d'écarter tout risque de saturation (`transactions`, `connexions_digitales`).
*   **`INTEGER`** : Stockage des clés étrangères pointant vers des colonnes de type `SERIAL` ou les entiers métier (effectifs).
*   **`NUMERIC(15,2)`** : Type décimal à virgule fixe exact (15 chiffres au total, 2 décimales). Choix obligatoire pour les montants financiers (chiffre d'affaires, soldes, transactions, crédits, garanties) pour empêcher les erreurs d'arrondis induites par les types flottants.
*   **`VARCHAR(N)`** : Chaîne de caractères de longueur variable optimisant l'occupation de la mémoire vive (ex: `ice` en `VARCHAR(15)`, `rib` en `VARCHAR(24)`).
*   **`DATE`** : Stockage d'une date sans composante horaire (date de création, date d'octroi, date d'échéance).
*   **`TIMESTAMP`** : Stockage combiné date + heure précis à la seconde (logs de connexions, horodatage des transactions).
*   **`BOOLEAN`** : Indicateurs booléens (True/False).

#### B. Règles de Nomenclature
*   **Noms physiques** : Écrits intégralement en minuscules au format `snake_case` (ex: `raison_sociale`, `chiffre_affaires`).
*   **Clés Primaires (PK)** : Nommées systématiquement au format `id_[nom_singulier_table]` (ex: `id_entreprise`).
*   **Clés Étrangères (FK)** : Reprennent exactement le même nom physique que la clé primaire de la table de référence parent (ex: `id_entreprise` dans `comptes` pointe sur `entreprises.id_entreprise`).

---

### 5. Contraintes d'Intégrité Référentielle et de Cohérence

Le déploiement des scripts SQL respectera l'implémentation physique des contraintes suivantes :
*   **`PRIMARY KEY`** : Appliquée sur la colonne identifiante de chaque table. Crée automatiquement un index physique B-Tree.
*   **`FOREIGN KEY`** : Définie sur les colonnes clés étrangères pour lier les tables.
    *   *Règle physique de suppression* : Par défaut, application de la clause `ON DELETE RESTRICT` sur les relations parent-enfant d'organisation (ex: interdire la suppression d'une agence s'il y a des entreprises ou des employés rattachés) afin de prévenir les ruptures d'intégrité en base.
*   **`UNIQUE`** : Imposée sur les identifiants uniques métiers pour éviter les doublons accidentels (`ice` dans `entreprises`, `rib` dans `comptes`, `reference_unique` dans `transactions`, `reference_contrat` dans `contrats_credits`, `reference_garantie` dans `garanties`, `matricule` dans `employes`).
*   **`CHECK`** : Établie au niveau physique PostgreSQL pour bloquer les valeurs erronées au moment de l'écriture en base :
    *   `chiffre_affaires >= 0` et `nombre_employes > 0`
    *   `solde_actuel >= -facilite_caisse` (le cas échéant)
    *   `montant_principal > 0` et `encours_restant >= 0` et `encours_restant <= montant_principal`
    *   `date_echeance > date_octroi`
    *   `role IN ('Directeur d''agence', 'Conseiller Entreprises', 'Chargé de caisse')`
    *   `secteur_activite IN ('Commerce', 'BTP', 'Services', 'Industrie', 'Agriculture', 'Technologies')`
    *   `type_compte IN ('COURANT', 'DAT')`
    *   `type_transaction IN ('VIREMENT', 'VERSEMENT', 'RETRAIT', 'PRELEVEMENT')`
    *   `sens IN ('DEBIT', 'CREDIT')`
    *   `canal IN ('PHYSIQUE', 'DIGITAL')`
*   **`NOT NULL`** : Appliquée sur tous les attributs structurels pour garantir la complétude des données.

---

### 6. Stratégie d'Indexation Physique

En complément des index générés par défaut sur les PK et contraintes UNIQUE, les index B-Tree suivants seront créés explicitement dans le script `12_indexes.sql` :

1.  **Index sur les Clés Étrangères (FK)** : Indispensables pour accélérer les temps de réponse des requêtes de jointures de l'ETL.
    *   `idx_agences_region` sur `agences(id_region)`
    *   `idx_employes_agence` sur `employes(id_agence)`
    *   `idx_entreprises_agence` sur `entreprises(id_agence)`
    *   `idx_entreprises_conseiller` sur `entreprises(id_conseiller)`
    *   `idx_comptes_entreprise` sur `comptes(id_entreprise)`
    *   `idx_contrats_entreprise` sur `contrats_credits(id_entreprise)`
    *   `idx_transactions_compte` sur `transactions(id_compte)`
2.  **Index sur les colonnes de recherche** :
    *   `idx_entreprises_ice` sur `entreprises(ice)`
3.  **Index Temporels (Analyse et ETL incrémental)** :
    *   `idx_transactions_date` sur `transactions(date_heure_transaction)`
    *   `idx_connexions_date` sur `connexions_digitales(date_heure_connexion)`

---

### 7. Préparation des Flux ETL

Les données opérationnelles suivront le flux physique suivant :
1.  Le script de simulation peuple le schéma `oltp`.
2.  Le pipeline d'extraction ETL vide et charge les données du jour de `oltp` vers `staging` à l'aide de requêtes de sélection basées sur les index temporels (`idx_transactions_date`).
3.  L'ETL de transformation lit `staging`, applique les règles de nettoyage de données et les calculs de clés substituts décisionnelles, puis peuple le schéma de l'entrepôt `dwh`.
4.  Les requêtes SQL d'agrégation mettent à jour les tables du schéma `datamarts`.
5.  Power BI interroge le schéma `datamarts` pour mettre à jour les tableaux de bord.

---

### 8. Validation de Cohérence

Le présent document de Conception Physique PostgreSQL (DDL) est validé et s'aligne rigoureusement sur les livrables d'amont :
*   **Vision Générale & Cahier des Charges** : Respect strict du périmètre Business Banking et de l'architecture technique globale.
*   **Analyse Métier & Dictionnaire de Données** : Reprise fidèle de l'ensemble des règles fonctionnelles d'affectation et des typages physiques de données.
*   **MCD & MLD** : Traduction exacte des 14 tables logiques et des relations sémantiques en instructions de création physique DDL.
*   **Architecture Décisionnelle** : Cadrage des flux d'alimentation vers le Data Warehouse.
