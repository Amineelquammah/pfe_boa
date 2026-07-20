# Modèle Logique de Données (MLD) : Structure Relationnelle Source
## Plateforme Décisionnelle Business Banking (Bank of Africa)

---

### 1. Introduction & Règles de Transformation Merise

Ce Modèle Logique de Données (MLD) est la traduction directe du MCD Merise selon les règles de dérivation relationnelle :
1.  **Entités** : Chaque entité du MCD est convertie en une relation (table physique) identifiée par sa clé primaire (PK).
2.  **Associations un-à-plusieurs (1,N)** : La clé primaire de l'entité côté "1" migre comme clé étrangère (FK) dans la table issue de l'entité côté "N" (ex: `id_region` de `regions` migre dans `agences`).
3.  **Associations plusieurs-à-plusieurs (N,N)** : L'association sémantique est transformée en une table associative pivot contenant les clés primaires des entités participantes comme clés étrangères composées ou clé primaire artificielle (ex: `souscriptions_digitales`).
4.  **Héritage / Rattachement** : Les entités opérationnelles d'une entreprise héritent fonctionnellement des relations d'affectation de cette dernière (clés étrangères `id_conseiller` et `id_agence` portées par les contrats de crédits et de comptes).
5.  **Nomenclature** : Tous les noms de tables, de colonnes et de clés sont traduits en minuscules et structurés au format `snake_case` pour assurer une compatibilité optimale avec PostgreSQL.

---

### 2. Schémas Relationnels Détaillés par Domaine

#### A. Référentiel Organisation Bancaire

##### Table `regions`
*   **Utilisation DWH** : Dimension (**Dim_Region**)
*   **Volume cible** : 7 régions
*   **Schéma relationnel** :
    *   `regions (id_region [PK], nom_region)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_region` | Primary Key | `SERIAL` | Non | - | Identifiant unique de la région |
| `nom_region` | Attribut | `VARCHAR(50)` | Non | UNIQUE | Nom de la direction régionale BOA |

---

##### Table `agences`
*   **Utilisation DWH** : Dimension (**Dim_Agence**)
*   **Volume cible** : 10 agences
*   **Schéma relationnel** :
    *   `agences (id_agence [PK], nom_agence, ville, id_region [FK -> regions])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_agence` | Primary Key | `SERIAL` | Non | - | Identifiant unique de l'agence |
| `nom_agence` | Attribut | `VARCHAR(50)` | Non | UNIQUE | Nom distinctif de l'agence |
| `ville` | Attribut | `VARCHAR(50)` | Non | - | Ville d'implantation de l'agence |
| `id_region` | Foreign Key | `INTEGER` | Non | FK sur `regions.id_region` | ID de la région de rattachement |

---

##### Table `employes`
*   **Utilisation DWH** : Dimension (**Dim_Employe**)
*   **Volume cible** : ~50 employés
*   **Schéma relationnel** :
    *   `employes (id_employe [PK], matricule, nom, prenom, role, date_recrutement, id_agence [FK -> agences])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_employe` | Primary Key | `SERIAL` | Non | - | Identifiant unique de l'employé |
| `matricule` | Attribut | `VARCHAR(20)` | Non | UNIQUE | Matricule RH unique de l'employé |
| `nom` | Attribut | `VARCHAR(50)` | Non | - | Nom de famille de l'employé |
| `prenom` | Attribut | `VARCHAR(50)` | Non | - | Prénom de l'employé |
| `role` | Attribut | `VARCHAR(30)` | Non | CHECK (rôle RH) | Rôle : Directeur d'agence, Conseiller Entreprises, Chargé de caisse |
| `date_recrutement`| Attribut | `DATE` | Non | - | Date d'embauche de l'employé |
| `id_agence` | Foreign Key | `INTEGER` | Non | FK sur `agences.id_agence` | ID de l'agence d'affectation |

*Contrainte CHECK sur role* : `role IN ('Directeur d''agence', 'Conseiller Entreprises', 'Chargé de caisse')`

---

#### B. Référentiel Entreprises

##### Table `entreprises`
*   **Utilisation DWH** : Dimension (**Dim_Entreprise**)
*   **Volume cible** : ~2 000 entreprises
*   **Schéma relationnel** :
    *   `entreprises (id_entreprise [PK], ice, raison_sociale, secteur_activite, forme_juridique, date_creation, ville, id_region [FK -> regions], id_agence [FK -> agences], id_conseiller [FK -> employes], chiffre_affaires_annuel, nombre_employes, segment)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_entreprise` | Primary Key | `SERIAL` | Non | - | Identifiant interne unique de l'entreprise |
| `ice` | Attribut | `VARCHAR(15)` | Non | UNIQUE | Identifiant Commun de l'Entreprise (15 car.) |
| `raison_sociale` | Attribut | `VARCHAR(100)` | Non | - | Nom légal ou raison sociale de l'entreprise |
| `secteur_activite`| Attribut | `VARCHAR(50)` | Non | CHECK (secteurs)| Secteur : Commerce, BTP, Services, Industrie, Agriculture, Technologies |
| `forme_juridique` | Attribut | `VARCHAR(20)` | Non | CHECK (formes) | Forme légale (SARL, SA, SNC, EURL) |
| `date_creation` | Attribut | `DATE` | Non | - | Date de création administrative officielle |
| `ville` | Attribut | `VARCHAR(50)` | Non | - | Ville de siège de l'entreprise |
| `id_region` | Foreign Key | `INTEGER` | Non | FK sur `regions.id_region` | Région administrative de domiciliation |
| `id_agence` | Foreign Key | `INTEGER` | Non | FK sur `agences.id_agence` | Agence physique de rattachement |
| `id_conseiller` | Foreign Key | `INTEGER` | Non | FK sur `employes.id_employe`| Conseiller entreprise gérant le portefeuille |
| `chiffre_affaires_annuel`| Attribut| `NUMERIC(15,2)`| Non | CHECK (CA >= 0) | Chiffre d'affaires annuel de l'entreprise en MAD |
| `nombre_employes` | Attribut | `INTEGER` | Non | CHECK (nbr > 0) | Effectif de l'entreprise |
| `segment` | Attribut | `VARCHAR(20)` | Non | CHECK (segment) | Classement commercial : TPE, PME, Grande Entreprise |

*Contraintes CHECK sectorielles et juridiques* :
*   `secteur_activite IN ('Commerce', 'BTP', 'Services', 'Industrie', 'Agriculture', 'Technologies')`
*   `segment IN ('TPE', 'PME', 'Grande Entreprise')`

---

#### C. Domaine Dépôts

##### Table `comptes`
*   **Utilisation DWH** : Dimension (**Dim_Produit_Depot**) + Fait (**Fait_Depots**) pour les soldes
*   **Volume cible** : ~2 500 comptes
*   **Schéma relationnel** :
    *   `comptes (id_compte [PK], rib, id_entreprise [FK -> entreprises], type_compte, date_ouverture, solde_actuel, statut, id_compte_courant_parent [FK -> comptes])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_compte` | Primary Key | `SERIAL` | Non | - | Identifiant unique du compte de dépôt |
| `rib` | Attribut | `VARCHAR(24)` | Non | UNIQUE | Numéro de RIB de 24 caractères |
| `id_entreprise` | Foreign Key | `INTEGER` | Non | FK sur `entreprises.id_entreprise`| Entreprise détentrice du compte |
| `type_compte` | Attribut | `VARCHAR(10)` | Non | CHECK (type) | Type : COURANT, DAT |
| `date_ouverture` | Attribut | `DATE` | Non | - | Date d'ouverture contractuelle du compte |
| `solde_actuel` | Attribut | `NUMERIC(15,2)` | Non | DEFAULT 0.00 | Solde disponible actuel en MAD |
| `statut` | Attribut | `VARCHAR(10)` | Non | DEFAULT 'ACTIF' | Statut du compte (ACTIF, INACTIF) |
| `id_compte_courant_parent`| Foreign Key| `INTEGER` | Oui | FK sur `comptes.id_compte`| Compte courant pivot associé (requis pour les DAT) |

*Contraintes CHECK* :
*   `type_compte IN ('COURANT', 'DAT')`
*   `statut IN ('ACTIF', 'INACTIF')`

---

##### Table `transactions`
*   **Utilisation DWH** : Fait (**Fait_Transactions**)
*   **Volume cible** : ~150 000 transactions
*   **Schéma relationnel** :
    *   `transactions (id_transaction [PK], reference_unique, id_compte [FK -> comptes], date_heure_transaction, type_transaction, sens, montant, canal)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_transaction` | Primary Key | `SERIAL` | Non | - | Identifiant interne unique de transaction |
| `reference_unique` | Attribut | `VARCHAR(50)` | Non | UNIQUE | Référence opérationnelle unique BOA |
| `id_compte` | Foreign Key | `INTEGER` | Non | FK sur `comptes.id_compte` | Compte courant impacté |
| `date_heure_transaction`| Attribut| `TIMESTAMP` | Non | - | Date et heure précises de validation |
| `type_transaction`| Attribut | `VARCHAR(20)` | Non | CHECK (type) | VIREMENT, VERSEMENT, RETRAIT, PRELEVEMENT |
| `sens` | Attribut | `VARCHAR(6)` | Non | CHECK (sens) | Impact comptable : DEBIT, CREDIT |
| `montant` | Attribut | `NUMERIC(15,2)` | Non | CHECK (montant > 0) | Montant financier de la transaction en MAD |
| `canal` | Attribut | `VARCHAR(10)` | Non | CHECK (canal) | Canal d'exécution (PHYSIQUE, DIGITAL) |

---

#### D. Domaine Crédits

##### Table `familles_credits`
*   **Utilisation DWH** : Dimension (**Dim_Produit_Credit**) (Hiérarchie)
*   **Volume cible** : 3 familles
*   **Schéma relationnel** :
    *   `familles_credits (id_famille [PK], code_famille, nom_famille)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_famille` | Primary Key | `SERIAL` | Non | - | Identifiant unique de famille de crédit |
| `code_famille` | Attribut | `VARCHAR(20)` | Non | UNIQUE | Code unique macro (TRESORERIE, INVEST, COMMERCE_INT) |
| `nom_famille` | Attribut | `VARCHAR(50)` | Non | - | Libellé de la famille commerciale de crédit |

---

##### Table `programmes_credits`
*   **Utilisation DWH** : Dimension (**Dim_Produit_Credit**) (Hiérarchie)
*   **Volume cible** : ~10 programmes
*   **Schéma relationnel** :
    *   `programmes_credits (id_programme [PK], code_programme, nom_programme, id_famille [FK -> familles_credits])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_programme` | Primary Key | `SERIAL` | Non | - | Identifiant unique de programme |
| `code_programme` | Attribut | `VARCHAR(30)` | Non | UNIQUE | Code du programme (ex: TAMWILCOM, MAROC_PME) |
| `nom_programme` | Attribut | `VARCHAR(100)` | Non | - | Libellé complet descriptif du programme |
| `id_famille` | Foreign Key | `INTEGER` | Non | FK sur `familles_credits.id_famille`| Macro-famille associée |

---

##### Table `produits_credits`
*   **Utilisation DWH** : Dimension (**Dim_Produit_Credit**) (Hiérarchie)
*   **Volume cible** : ~20 produits
*   **Schéma relationnel** :
    *   `produits_credits (id_produit [PK], code_produit, nom_produit, id_programme [FK -> programmes_credits])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_produit` | Primary Key | `SERIAL` | Non | - | Identifiant unique du produit de crédit |
| `code_produit` | Attribut | `VARCHAR(30)` | Non | UNIQUE | Code produit unitaire (ex: CAP_ENERGIE, DECOUVERT) |
| `nom_produit` | Attribut | `VARCHAR(100)` | Non | - | Nom commercial officiel |
| `id_programme` | Foreign Key | `INTEGER` | Non | FK sur `programmes_credits.id_programme`| Programme commercial associé |

---

##### Table `contrats_credits`
*   **Utilisation DWH** : Dimension (**Dim_Produit_Credit**) (pour le produit) + Fait (**Fait_Credits**) pour les encours
*   **Volume cible** : ~1 000 contrats
*   **Schéma relationnel** :
    *   `contrats_credits (id_contrat [PK], reference_contrat, id_entreprise [FK -> entreprises], id_produit [FK -> produits_credits], montant_accorde, encours_restant_du, date_octroi, date_echeance, taux_interet, statut_credit, id_conseiller [FK -> employes], id_agence [FK -> agences])`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_contrat` | Primary Key | `SERIAL` | Non | - | Identifiant unique du contrat crédit |
| `reference_contrat` | Attribut | `VARCHAR(50)` | Non | UNIQUE | Référence de dossier de financement unique BOA |
| `id_entreprise` | Foreign Key | `INTEGER` | Non | FK sur `entreprises.id_entreprise`| Entreprise emprunteuse détentrice |
| `id_produit` | Foreign Key | `INTEGER` | Non | FK sur `produits_credits.id_produit`| Produit de crédit souscrit |
| `montant_accorde` | Attribut | `NUMERIC(15,2)` | Non | CHECK (montant > 0) | Capital total débloqué initialement en MAD |
| `encours_restant_du`| Attribut| `NUMERIC(15,2)` | Non | CHECK (encours >= 0)| Capital restant dû à ce jour en MAD |
| `date_octroi` | Attribut | `DATE` | Non | - | Date officielle de signature et décaissement |
| `date_echeance` | Attribut | `DATE` | Non | CHECK (date) | Date de fin de remboursement |
| `taux_interet` | Attribut | `NUMERIC(5,2)` | Non | CHECK (taux >= 0) | Taux d'intérêt annuel appliqué contractuellement |
| `statut_credit` | Attribut | `VARCHAR(15)` | Non | CHECK (statut) | Statut du dossier : ACTIF, REMBOURSE, NPL |
| `id_conseiller` | Foreign Key | `INTEGER` | Non | FK sur `employes.id_employe`| Conseiller en charge (hérité de l'entreprise) |
| `id_agence` | Foreign Key | `INTEGER` | Non | FK sur `agences.id_agence` | Agence d'affectation (héritée de l'entreprise) |

*Contraintes CHECK additionnelles* :
*   `statut_credit IN ('ACTIF', 'REMBOURSE', 'NPL')`
*   `CHECK (date_echeance > date_octroi)`
*   `CHECK (encours_restant_du <= montant_accorde)`

---

##### Table `garanties`
*   **Utilisation DWH** : Fait (**Fait_Credits**) (attribut analytique de couverture)
*   **Volume cible** : ~800 garanties
*   **Schéma relationnel** :
    *   `garanties (id_garantie [PK], reference_garantie, id_contrat [FK -> contrats_credits], type_garantie, montant_garanti, date_constitution)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_garantie` | Primary Key | `SERIAL` | Non | - | Identifiant unique de garantie |
| `reference_garantie` | Attribut | `VARCHAR(50)` | Non | UNIQUE | Numéro unique du contrat de garantie BOA |
| `id_contrat` | Foreign Key | `INTEGER` | Non | FK sur `contrats_credits.id_contrat`| Contrat de crédit couvert |
| `type_garantie` | Attribut | `VARCHAR(30)` | Non | CHECK (type) | AVAL, CAUTION_ADMIN, CAUTION_FIN, GARANTIE_BANCAIRE |
| `montant_garanti` | Attribut | `NUMERIC(15,2)` | Non | CHECK (montant > 0) | Valeur financière de la garantie en MAD |
| `date_constitution` | Attribut | `DATE` | Non | - | Date officielle de constitution de la sûreté |

*Contrainte CHECK sur type* : `type_garantie IN ('AVAL', 'CAUTION_ADMIN', 'CAUTION_FIN', 'GARANTIE_BANCAIRE')`

---

#### E. Domaine Digital

##### Table `solutions_digitales`
*   **Utilisation DWH** : Dimension (**Dim_Solution_Digitale**)
*   **Volume cible** : 5 solutions
*   **Schéma relationnel** :
    *   `solutions_digitales (id_solution [PK], nom_solution, type_canal)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_solution` | Primary Key | `SERIAL` | Non | - | Identifiant unique du service digital |
| `nom_solution` | Attribut | `VARCHAR(50)` | Non | UNIQUE | DabaPay Pro, BusinessOnline.ma, WhatsApp Business, etc. |
| `type_canal` | Attribut | `VARCHAR(20)` | Non | - | Canal de support (WEB, MOBILE, ASSISTANT) |

---

##### Table `souscriptions_digitales`
*   **Utilisation DWH** : Dimension (**Dim_Solution_Digitale**) + Fait (**Fait_Digital**)
*   **Volume cible** : ~1 500 souscriptions
*   **Schéma relationnel** :
    *   `souscriptions_digitales (id_souscription [PK], id_entreprise [FK -> entreprises], id_solution [FK -> solutions_digitales], date_souscription, statut)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_souscription` | Primary Key | `SERIAL` | Non | - | Identifiant unique de la souscription pivot |
| `id_entreprise` | Foreign Key | `INTEGER` | Non | FK sur `entreprises.id_entreprise`| Entreprise souscriptrice |
| `id_solution` | Foreign Key | `INTEGER` | Non | FK sur `solutions_digitales.id_solution`| Service digital souscrit |
| `date_souscription`| Attribut | `DATE` | Non | - | Date d'activation de la souscription |
| `statut` | Attribut | `VARCHAR(10)` | Non | DEFAULT 'ACTIF' | Statut de l'abonnement (ACTIF, RESILIE) |

*Contrainte CHECK sur statut* : `statut IN ('ACTIF', 'RESILIE')`
*Contrainte d'unicité* : UNIQUE (`id_entreprise`, `id_solution`) (une entreprise souscrit au plus une fois à un service digital donné)

---

##### Table `connexions_digitales`
*   **Utilisation DWH** : Fait (**Fait_Digital**)
*   **Volume cible** : ~100 000 connexions
*   **Schéma relationnel** :
    *   `connexions_digitales (id_connexion [PK], id_souscription [FK -> souscriptions_digitales], date_heure_connexion, nombre_operations)`

| Colonne Physique | Rôle technique | Type de données | Nullable | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id_connexion` | Primary Key | `SERIAL` | Non | - | Identifiant unique de log de connexion |
| `id_souscription` | Foreign Key | `INTEGER` | Non | FK sur `souscriptions_digitales.id_souscription`| Contrat de souscription utilisé |
| `date_heure_connexion`| Attribut | `TIMESTAMP`| Non | - | Date et heure de connexion |
| `nombre_operations`| Attribut | `INTEGER` | Non | DEFAULT 0 | Volume de transactions ou requêtes dans la session |

*Contrainte CHECK sur operations* : `CHECK (nombre_operations >= 0)`

---

### 3. Ordre Logique de Dépendance et de Création des Tables (Scripts DDL)

Pour garantir qu'aucune clé étrangère ne pointe vers une table inexistante lors de l'exécution du DDL (Data Definition Language) sous PostgreSQL, les tables doivent être créées dans l'ordre strict suivant :

```
1.  regions
      │
      ▼
2.  agences
      │
      ▼
3.  employes
      │
      ▼
4.  entreprises
      │
      ├───► 5. comptes ────► 6. transactions
      │
      ├───► 7. familles_credits ────► 8. programmes_credits ────► 9. produits_credits
      │                                                                   │
      │                                                                   ▼
      ├────────────────────────────────────────────────────────► 10. contrats_credits ────► 11. garanties
      │
      ├───► 12. solutions_digitales
      │            │
      │            ▼
      └──────► 13. souscriptions_digitales ────► 14. connexions_digitales
```

1.  `regions` (Aucune dépendance externe)
2.  `agences` (Dépend de `regions`)
3.  `employes` (Dépend de `agences`)
4.  `entreprises` (Dépend de `regions`, `agences` et `employes`)
5.  `comptes` (Dépend de `entreprises` et d'elle-même pour la filiation DAT/courant)
6.  `transactions` (Dépend de `comptes`)
7.  `familles_credits` (Aucune dépendance externe)
8.  `programmes_credits` (Dépend de `familles_credits`)
9.  `produits_credits` (Dépend de `programmes_credits`)
10. `contrats_credits` (Dépend de `entreprises`, `produits_credits`, `employes` et `agences`)
11. `garanties` (Dépend de `contrats_credits`)
12. `solutions_digitales` (Aucune dépendance externe)
13. `souscriptions_digitales` (Dépend de `entreprises` et `solutions_digitales`)
14. `connexions_digitales` (Dépend de `souscriptions_digitales`)
