# Spécification de l'Architecture Physique PostgreSQL
## Plateforme Décisionnelle Business Banking (Bank of Africa)

---

### 1. Organisation de la Base de Données (Schémas)

Pour assurer une isolation stricte des données selon leur rôle dans le cycle de vie décisionnel, la base de données PostgreSQL sera organisée en **quatre schémas logiques** distincts :

```
[oltp]           ---> Base opérationnelle source (Modèle 3NF hautement normalisé)
  │
  ▼ (ETL Extraction)
[staging]        ---> Zone tampon (Tables miroir, nettoyage, pas de contraintes FK)
  │
  ▼ (ETL Transformation & Chargement)
[dwh]            ---> Data Warehouse centralisé (Schéma en étoile : Faits + Dimensions)
  │
  ▼ (Vues / SQL)
[datamarts]      ---> Sous-ensembles métiers ciblés (DM_Depots, DM_Credits, DM_Risques, etc.)
```

*   **`oltp`** : Héberge les tables opérationnelles de la banque (les 14 tables de transactions, comptes, crédits). C'est la source de vérité transactionnelle hautement normalisée (3NF) pour éviter toute redondance et garantir l'intégrité opérationnelle.
*   **`staging`** : Zone de transit temporaire utilisée par le pipeline ETL. Elle contient des répliques des tables OLTP sans clés étrangères ni contraintes de vérification, permettant d'extraire rapidement les données sources sans verrouiller la production. C'est ici que s'effectuent le nettoyage et le formatage initial.
*   **`dwh`** : Héberge le Data Warehouse centralisé modélisé en **schéma en étoile**. Les données y sont historisées et dénormalisées sous forme de dimensions (ex: `Dim_Entreprise`) et de tables de faits (ex: `Fait_Transactions`).
*   **`datamarts`** : Héberge des tables ou des vues spécialisées par domaine métier (Dépôts, Crédits, Risques, Digital) prêtes à être consommées directement par Power BI. C'est également ici que le scoring Machine Learning (Clustering) est rattaché aux entreprises.

---

### 2. Organisation des Tables par Domaine Métier (Schéma `oltp`)

Les 14 tables opérationnelles sont réparties dans le schéma `oltp` selon leur domaine d'application :

*   **Référentiel Organisation** :
    *   `regions` : Liste des 7 directions régionales.
    *   `agences` : Les 10 agences bancaires.
    *   `employes` : Les 50 directeurs, conseillers et chargés de caisse.
*   **Référentiel Entreprises** :
    *   `entreprises` : Les 2 000 clients moraux Business Banking.
*   **Domaine Dépôts** :
    *   `comptes` : Les 2 500 comptes courants et placements DAT.
    *   `transactions` : L'historique des 150 000 transactions sur comptes.
*   **Domaine Crédits** :
    *   `familles_credits` : Familles de crédit (Trésorerie, Investissement, Commerce International).
    *   `programmes_credits` : Programmes associés (Tamwilcom, Maroc PME, etc.).
    *   `produits_credits` : Produits distribuables (CAP Energie, Go Siyaha, Découvert, etc.).
    *   `contrats_credits` : Les 1 000 contrats de prêts débloqués.
    *   `garanties` : Les ~800 garanties prises en couverture des contrats.
*   **Domaine Digital** :
    *   `solutions_digitales` : Les 5 applications et canaux professionnels de BOA.
    *   `souscriptions_digitales` : Table pivot d'abonnement des entreprises aux applications.
    *   `connexions_digitales` : Log des 100 000 connexions et volume d'opérations associées.

---

### 3. Conventions des Types de Données PostgreSQL

Le choix des types physiques sous PostgreSQL répond à un objectif double de justesse métier et d'optimisation de l'espace de stockage :

| Type PostgreSQL | Utilisation & Justification | Exemple de colonne |
| :--- | :--- | :--- |
| **`SMALLSERIAL`** | Auto-incrément codé sur 2 octets (valeurs de 1 à 32 767). Utilisé pour les petites tables de paramétrage afin d'économiser l'indexation. | `regions.id_region`, `solutions_digitales.id_solution` |
| **`SERIAL`** | Auto-incrément standard sur 4 octets (valeurs jusqu'à 2,1 milliards). Idéal pour les clés primaires de la majorité des tables. | `agences.id_agence`, `entreprises.id_entreprise`, `comptes.id_compte` |
| **`BIGSERIAL`** | Auto-incrément sur 8 octets pour les tables à volumétrie exponentielle, évitant tout risque de saturation d'identifiant. | `transactions.id_transaction`, `connexions_digitales.id_connexion` |
| **`INTEGER`** | Entier standard sur 4 octets pour stocker les clés étrangères (FK) pointant vers des colonnes `SERIAL` et les quantités. | `comptes.id_entreprise`, `entreprises.nombre_employes` |
| **`NUMERIC(15,2)`** | Type à virgule fixe exact (15 chiffres significatifs, 2 décimales). Indispensable pour la monnaie (MAD) afin d'éviter les erreurs d'arrondis des types flottants. | `entreprises.chiffre_affaires`, `transactions.montant` |
| **`VARCHAR(N)`** | Chaîne de caractères de longueur variable avec limite matérielle, protégeant la base contre les dépassements d'espace. | `entreprises.ice` (`VARCHAR(15)`), `comptes.rib` (`VARCHAR(24)`) |
| **`DATE`** | Stockage pur de date (sans heure) pour les dates contractuelles et administratives. | `entreprises.date_creation`, `contrats_credits.date_octroi`, `transactions.date_transaction`, `connexions_digitales.date_connexion` |
| **`TIMESTAMP`** | Horodatage précis (date + heure + secondes) pour l'historisation des événements transactionnels ou applicatifs. | `date_echeance` (si applicable) |
| **`BOOLEAN`** | Booléen simple (True/False) pour les drapeaux d'état. | - |

---

### 4. Stratégie des Clés & Contraintes

#### A. Conventions de Nommage
*   **Clés Primaires (PK)** : Nommées systématiquement au format `id_[nom_singulier_table]` (ex: `id_entreprise` pour la table `entreprises`).
*   **Clés Étrangères (FK)** : Portent le même nom exact que la clé primaire de la table parente qu'elles pointent (ex: `id_agence` dans la table `entreprises` pointe vers `agences.id_agence`).
*   **Noms physiques** : Toujours rédigés en minuscules au format `snake_case`.

#### B. Contraintes Physiques
*   **`PRIMARY KEY`** : Garantie l'unicité et la non-nullité d'une colonne clé. Un index B-Tree est automatiquement créé par PostgreSQL sur cette colonne.
*   **`FOREIGN KEY`** : Maintient l'intégrité référentielle. Les suppressions parentes seront gérées par la contrainte `ON DELETE RESTRICT` par défaut pour empêcher la suppression accidentelle de données d'organisation (ex: interdire la suppression d'une agence si des employés y sont rattachés).
*   **`NOT NULL`** : Appliquée sur tous les attributs obligatoires (noms, montants, dates d'octroi) pour empêcher l'insertion de lignes incomplètes.
*   **`UNIQUE`** : Force l'unicité fonctionnelle (ex: `ice` unique pour `entreprises`, `rib` unique pour `comptes`, `reference_contrat` unique pour `contrats_credits`).
*   **`CHECK`** : Valide la cohérence des valeurs au moment de l'écriture en base (ex: `chiffre_affaires >= 0`, `role` parmi la liste RH définie, `statut` parmi le catalogue).

---

### 5. Stratégie d'Indexation (Performance en requêtage)

PostgreSQL crée automatiquement des index B-Tree sur les colonnes déclarées `PRIMARY KEY` ou `UNIQUE`. Pour optimiser les performances des opérations d'extraction (ETL) et des jointures, des index B-Tree additionnels seront créés sur :

*   **Toutes les Clés Étrangères (FK)** : Les requêtes de jointures entre tables parentes et enfants utilisent systématiquement ces clés.
    *   *Index requis* : `idx_agences_region`, `idx_employes_agence`, `idx_entreprises_agence`, `idx_entreprises_conseiller`, `idx_comptes_entreprise`, `idx_contrats_entreprise`, `idx_transactions_compte`.
*   **Les Colonnes de Recherche Fréquentes** :
    *   `entreprises.ice` : Utilisée pour l'identification unique et l'intégration des flux.
    *   `employes.matricule` : Utilisée pour le rapprochement RH.
*   **Les Colonnes Temporelles d'Analyse** :
    *   `transactions.date_transaction` : Clé d'extraction incrémentale pour l'ETL et pivot des analyses temporelles.
    *   `contrats_credits.date_octroi` / `date_echeance` : Suivi des échéanciers de remboursement.
    *   `connexions_digitales.date_connexion` : Analyse d'activité temporelle digitale.

---

### 6. Optimisations de Performance

*   **Index B-Tree** : Tous les index créés utiliseront la structure standard B-Tree de PostgreSQL, qui est particulièrement performante pour les comparaisons d'égalité (`=`) et de plage (`BETWEEN`, `>`, `<`).
*   **Vues Matérialisées (Materialized Views)** : Utilisées au niveau du schéma `datamarts` pour pré-calculer et stocker physiquement les agrégations complexes et chronophages (ex: somme mensuelle des encours de dépôts par agence). Ces vues seront rafraîchies quotidiennement à la fin du traitement batch de l'ETL (`REFRESH MATERIALIZED VIEW`).
*   **Optimisation ETL** :
    *   Lors du chargement initial massif (Initial Load), les contraintes de clés étrangères et les index pourront être temporairement désactivés ou créés après l'insertion pour accélérer le débit d'écriture de Python.
    *   Pour le chargement quotidien incrémental (Incremental Load), l'utilisation d'index sur la colonne `date_transaction` permettra à l'ETL de n'extraire que les transactions créées depuis la veille.

---

### 7. Préparation du Pipeline DWH & Data Lineage

Le transfert physique des données depuis le transactionnel jusqu'aux tableaux de bord Power BI respectera le flux suivant :

1.  **Extraction (OLTP $\rightarrow$ STAGING)** : Le pipeline Python extrait quotidiennement les nouvelles transactions et modifications d'états depuis le schéma `oltp`. Les données brutes sont écrites dans les tables miroirs du schéma `staging` sans contrôle de clé pour maximiser la vitesse.
2.  **Transformation (STAGING $\rightarrow$ DWH)** : Les scripts SQL/Python valident la cohérence temporelle, nettoient les valeurs nulles, traduisent les hiérarchies (ex: jointure entre produits, programmes et familles crédits pour générer `Dim_Produit_Credit`) et chargent les dimensions et tables de faits dans le schéma `dwh`.
3.  **Calcul IA & Data Marts (DWH $\rightarrow$ DATAMARTS)** : Le modèle de clustering K-Means Python s'exécute sur les données consolidées du DWH pour segmenter les entreprises. Le score (ID de cluster) est écrit dans les tables cibles du schéma `datamarts`. Les vues et tables spécialisées par domaine (Dépôts, Crédits, Risques, Digital) sont calculées et exposées.
4.  **Restitution (DATAMARTS $\rightarrow$ POWER BI)** : Power BI se connecte exclusivement au schéma `datamarts` via une passerelle de données (Gateway) en mode Import pour charger les modèles en étoile et afficher les indicateurs de pilotage.

---

### 8. Rappel des Volumes de Données Simulés

Les structures physiques sont optimisées pour supporter les volumétries suivantes sur l'historique de 3 ans (2022-2024) :
*   `regions` : 7
*   `agences` : 10
*   `employes` : ~50
*   `entreprises` : ~2 000
*   `comptes` : ~2 500
*   `transactions` : ~150 000
*   `familles_credits` : 3
*   `programmes_credits` : ~10
*   `produits_credits` : ~20
*   `contrats_credits` : ~1 000
*   `garanties` : ~800
*   `solutions_digitales` : 5
*   `souscriptions_digitales` : ~1 500
*   `connexions_digitales` : ~100 000

---

### 9. Validation de l'Architecture Physique

Cette architecture physique a été rigoureusement confrontée aux livrables précédents et est validée :
*   **Vision Générale & Cahier des Charges** : Alignement complet avec la structure organisationnelle figée de BOA (7 régions, 10 agences, 50 employés), le périmètre Business Banking, et la distribution temporelle sur 3 ans.
*   **Analyse Métier & Dictionnaire de Données** : Respect des règles d'affectation automatique (héritage des clés `id_agence` et `id_conseiller` par les contrats de crédits et comptes) et prise en compte de la hiérarchie complète du catalogue crédit.
*   **MCD & MLD** : Traduction exacte des entités et relations physiques avec typage adapté sous PostgreSQL.
