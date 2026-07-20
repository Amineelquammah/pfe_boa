# Dictionnaire de Données : Base de Données OLTP PostgreSQL
## Plateforme Décisionnelle Business Banking (Bank of Africa)

---

### A. RÉFÉRENTIEL ORGANISATION

#### 1. Table `REGIONS`
*   **Rôle métier** : Stocker la liste des 7 directions régionales géographiques de la banque pour consolider les performances commerciales et les analyses de risques territoriaux.
*   **Principaux acteurs** : Directeur Général, Directeur Régional, Analyste BI (pour le reporting géomarketing).
*   **Futurs liens** : Liée aux tables `AGENCES` (1 à N) et `ENTREPRISES` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Region**.
*   **Volume estimé** : 7 enregistrements (fixe).

**Règles métier associées :**
*   Le nom de la région doit être unique.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID de la région | `id_region` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de la région |
| Nom de la région | `nom_region` | `VARCHAR(50)` | Non | - | Non | Non | UNIQUE, CHECK | Nom de la région administrative marocaine |

---

#### 2. Table `AGENCES`
*   **Rôle métier** : Représenter les 10 agences physiques du réseau Business Banking de BOA.
*   **Principaux acteurs** : Directeur d'Agence, Directeur Régional, Analyste BI (évaluation de la rentabilité opérationnelle du réseau).
*   **Futurs liens** : Liée à `REGIONS` (N à 1), `EMPLOYES` (1 à N) et `ENTREPRISES` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Agence**.
*   **Volume estimé** : 10 enregistrements (fixe).

**Règles métier associées :**
*   Chaque agence appartient obligatoirement à une seule région de la banque.
*   Le nom d'agence doit être unique.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID de l'agence | `id_agence` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de l'agence |
| Nom de l'agence | `nom_agence` | `VARCHAR(50)` | Non | - | Non | Non | UNIQUE | Nom distinct de l'agence BOA |
| Ville | `ville` | `VARCHAR(50)` | Non | - | Non | Non | - | Ville d'implantation de l'agence |
| ID de la région | `id_region` | `INTEGER` | Non | - | Non | Oui | FK sur `REGIONS` | Clé de rattachement de la région |

---

#### 3. Table `EMPLOYES`
*   **Rôle métier** : Gérer les ressources humaines des agences (Directeurs, Conseillers Entreprises et Chargés de caisse).
*   **Principaux acteurs** : Directeur d'Agence (rattachement hiérarchique), Conseiller (acteur commercial).
*   **Futurs liens** : Liée à `AGENCES` (N à 1) et `ENTREPRISES` (1 à N via le conseiller).
*   **Utilisation DWH** : Source de la dimension **Dim_Employe**.
*   **Volume estimé** : ~50 employés.

**Règles métier associées :**
*   Chaque employé appartient à une seule agence.
*   Le rôle doit être limité à un domaine spécifique : 'Directeur d\'agence', 'Conseiller Entreprises' ou 'Chargé de caisse'.
*   La matricule de l'employé est unique et obligatoire.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Employé | `id_employe` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Clé primaire unique |
| Matricule | `matricule` | `VARCHAR(20)` | Non | - | Non | Non | UNIQUE | Code d'identification RH unique |
| Nom | `nom` | `VARCHAR(50)` | Non | - | Non | Non | - | Nom de famille de l'employé |
| Prénom | `prenom` | `VARCHAR(50)` | Non | - | Non | Non | - | Prénom de l'employé |
| Rôle | `role` | `VARCHAR(30)` | Non | - | Non | Non | CHECK (rôle RH) | Rôle : Directeur d'agence, Conseiller Entreprises, Chargé de caisse |
| Date recrutement | `date_recrutement`| `DATE` | Non | - | Non | Non | - | Date d'embauche de l'employé |
| ID de l'agence | `id_agence` | `INTEGER` | Non | - | Non | Oui | FK sur `AGENCES` | Agence d'affectation de l'employé |

---

### B. RÉFÉRENTIEL ENTREPRISES

#### 4. Table `ENTREPRISES`
*   **Rôle métier** : Stocker l'ensemble des informations d'identité, financières et de segmentation commerciale des entreprises clientes (TPE, PME, Grandes Entreprises).
*   **Principaux acteurs** : Conseiller Entreprises (gestionnaire principal), Directeur d'Agence, Analyste Risques.
*   **Futurs liens** : Liée à `REGIONS` (N à 1), `AGENCES` (N à 1), `EMPLOYES` (N à 1 - Conseiller), `COMPTES` (1 à N) et `CONTRATS_CREDITS` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Entreprise**.
*   **Volume estimé** : ~2 000 entreprises.

**Règles métier associées :**
*   Une entreprise appartient à une seule agence et possède un seul conseiller attitré.
*   L'ICE (Identifiant Commun de l'Entreprise) est unique et obligatoire.
*   Le segment de l'entreprise doit être obligatoirement : 'TPE', 'PME' ou 'Grande Entreprise'.
*   La ville de l'entreprise doit correspondre à sa région d'implantation.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Entreprise | `id_entreprise` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique interne |
| ICE | `ice` | `VARCHAR(15)` | Non | - | Non | Non | UNIQUE | Identifiant Commun de l'Entreprise (15 car.) |
| Raison sociale | `raison_sociale` | `VARCHAR(100)` | Non | - | Non | Non | - | Nom officiel légal de l'entreprise |
| Secteur d'activité| `secteur_activite`| `VARCHAR(50)` | Non | - | Non | Non | CHECK (secteurs) | Commerce, BTP, Services, Industrie, Agriculture, Technologies |
| Forme juridique | `forme_juridique` | `VARCHAR(20)` | Non | - | Non | Non | CHECK (formes) | SARL, SA, SNC, EURL, etc. |
| Date de création | `date_creation` | `DATE` | Non | - | Non | Non | - | Date officielle de création administrative |
| Ville | `ville` | `VARCHAR(50)` | Non | - | Non | Non | - | Ville de domiciliation de l'entreprise |
| ID de la région | `id_region` | `INTEGER` | Non | - | Non | Oui | FK sur `REGIONS` | Région administrative associée |
| ID de l'agence | `id_agence` | `INTEGER` | Non | - | Non | Oui | FK sur `AGENCES` | Agence de rattachement |
| ID Conseiller | `id_conseiller` | `INTEGER` | Non | - | Non | Oui | FK sur `EMPLOYES` | Conseiller gérant le portefeuille client |
| Chiffre d'affaires| `chiffre_affaires`| `NUMERIC(15,2)` | Non | - | Non | Non | CHECK (CA >= 0) | Chiffre d'affaires annuel en Dirhams (MAD) |
| Nbr d'employés | `nombre_employes` | `INTEGER` | Non | - | Non | Non | CHECK (Nbr > 0) | Nombre de salariés déclarés |
| Segment | `segment` | `VARCHAR(20)` | Non | - | Non | Non | CHECK (segment) | Classification : TPE, PME, Grande Entreprise |

---

### C. DOMAINE DÉPÔTS

#### 5. Table `COMPTES`
*   **Rôle métier** : Gérer les comptes de dépôts ouverts pour les entreprises (comptes courants et comptes de placement DAT).
*   **Principaux acteurs** : Conseiller Entreprises (suivi de portefeuille), Chargé de caisse (opérations), Entreprise (flux).
*   **Futurs liens** : Liée à `ENTREPRISES` (N à 1), `COMPTES` (DAT à compte courant - N à 1) et `TRANSACTIONS` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Produit_Depot** (pour le type) et de la table de faits **Fait_Depots** (pour les encours).
*   **Volume estimé** : ~2 500 comptes.

**Règles métier associées :**
*   Un compte appartient à une seule entreprise.
*   Le type de compte est restreint à 'COURANT' ou 'DAT'.
*   Un DAT est obligatoirement rattaché à un compte courant actif (via `id_compte_courant_parent`).
*   Le RIB du compte est unique et composé de 24 caractères.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Compte | `id_compte` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de compte |
| RIB | `rib` | `VARCHAR(24)` | Non | - | Non | Non | UNIQUE | Relevé d'Identité Bancaire (24 car.) |
| ID Entreprise | `id_entreprise` | `INTEGER` | Non | - | Non | Oui | FK sur `ENTREPRISES` | Propriétaire du compte |
| Type de compte | `type_compte` | `VARCHAR(10)` | Non | - | Non | Non | CHECK (type) | Type : COURANT, DAT |
| Date d'ouverture | `date_ouverture` | `DATE` | Non | - | Non | Non | - | Date d'ouverture administrative du compte |
| Solde actuel | `solde_actuel` | `NUMERIC(15,2)` | Non | 0.00 | Non | Non | - | Solde comptable actuel du compte |
| Statut | `statut` | `VARCHAR(10)` | Non | 'ACTIF' | Non | Non | CHECK (statut) | Statut : ACTIF, INACTIF |
| ID Compte parent | `id_compte_courant_parent` | `INTEGER` | Oui | NULL | Non | Oui | FK sur `COMPTES` | Compte courant support pour un DAT |

---

#### 6. Table `TRANSACTIONS`
*   **Rôle métier** : Enregistrer l'ensemble des flux transactionnels créditeurs et débiteurs effectués sur les comptes courants.
*   **Principaux acteurs** : Entreprise (initiateur), Chargé de caisse (opérations physiques), Plateforme digitale (opérations en ligne).
*   **Futurs liens** : Liée à `COMPTES` (N à 1).
*   **Utilisation DWH** : Source de la table de faits **Fait_Transactions**.
*   **Volume estimé** : ~150 000 transactions.

**Règles métier associées :**
*   Une transaction concerne un unique compte courant.
*   Le type de transaction est limité à : 'VIREMENT', 'VERSEMENT', 'RETRAIT', 'PRELEVEMENT'.
*   Le sens doit être 'DEBIT' (retrait de fonds) ou 'CREDIT' (apport de fonds).
*   Le montant de la transaction doit être strictement supérieur à zéro.
*   Le canal de transaction doit être 'PHYSIQUE' ou 'DIGITAL'.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Transaction | `id_transaction` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique |
| Référence unique | `reference_unique` | `VARCHAR(50)` | Non | - | Non | Non | UNIQUE | Numéro de transaction unique BOA |
| ID Compte | `id_compte` | `INTEGER` | Non | - | Non | Oui | FK sur `COMPTES` | Compte courant impacté |
| Date & Heure | `date_heure_transaction` | `TIMESTAMP` | Non | - | Non | Non | - | Horodatage précis de la transaction |
| Type transaction | `type_transaction` | `VARCHAR(20)` | Non | - | Non | Non | CHECK (type) | VIREMENT, VERSEMENT, RETRAIT, PRELEVEMENT |
| Sens | `sens` | `VARCHAR(6)` | Non | - | Non | Non | CHECK (DEBIT/CREDIT)| Impact comptable (Débit ou Crédit) |
| Montant | `montant` | `NUMERIC(15,2)` | Non | - | Non | Non | CHECK (montant > 0) | Montant unitaire de l'opération en MAD |
| Canal | `canal` | `VARCHAR(10)` | Non | - | Non | Non | CHECK (canal) | Canal d'initiation (PHYSIQUE / DIGITAL) |

---

### D. DOMAINE CRÉDITS (CATALOGUE & CONTRATS)

#### 7. Table `FAMILLES_CREDITS`
*   **Rôle métier** : Catégoriser le catalogue de financements de BOA en grandes familles d'engagements.
*   **Principaux acteurs** : Analyste Risques, Analyste BI (pour le reporting macro).
*   **Futurs liens** : Liée à `PROGRAMMES_CREDITS` (1 à N).
*   **Utilisation DWH** : Parent de la hiérarchie dans **Dim_Produit_Credit**.
*   **Volume estimé** : 3 enregistrements (Trésorerie, Investissement, Commerce International).

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Famille | `id_famille` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de famille |
| Code Famille | `code_famille` | `VARCHAR(20)` | Non | - | Non | Non | UNIQUE | Code unique (TRESORERIE, INVEST, COMMERCE_INT) |
| Nom de la famille| `nom_famille` | `VARCHAR(50)` | Non | - | Non | Non | - | Nom complet (ex: Crédits de Trésorerie) |

---

#### 8. Table `PROGRAMMES_CREDITS`
*   **Rôle métier** : Regrouper les produits de crédits selon des programmes spécifiques d'accompagnement ou des typologies de financement.
*   **Principaux acteurs** : Analyste Risques, Analyste BI.
*   **Futurs liens** : Liée à `FAMILLES_CREDITS` (N à 1) et `PRODUITS_CREDITS` (1 à N).
*   **Utilisation DWH** : Niveau intermédiaire de la hiérarchie dans **Dim_Produit_Credit**.
*   **Volume estimé** : ~10 programmes (ex: Maroc PME, TAMWILCOM, Crédits de Signature, etc.).

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Programme | `id_programme` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de programme |
| Code Programme | `code_programme` | `VARCHAR(30)` | Non | - | Non | Non | UNIQUE | Code unique (ex: TAMWILCOM, DECOUVERT) |
| Nom du programme | `nom_programme` | `VARCHAR(100)` | Non | - | Non | Non | - | Nom complet (ex: Programme de Financement Tamwilcom) |
| ID Famille | `id_famille` | `INTEGER` | Non | - | Non | Oui | FK sur `FAMILLES_CREDITS`| Rattachement à la famille de crédit |

---

#### 9. Table `PRODUITS_CREDITS`
*   **Rôle métier** : Définir la liste des produits de financement distribués par BOA.
*   **Principaux acteurs** : Conseiller Entreprises, Analyste Risques, Entreprise.
*   **Futurs liens** : Liée à `PROGRAMMES_CREDITS` (N à 1) et `CONTRATS_CREDITS` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Produit_Credit**.
*   **Volume estimé** : ~20 produits.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Produit | `id_produit` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de produit |
| Code Produit | `code_produit` | `VARCHAR(30)` | Non | - | Non | Non | UNIQUE | Code unique (ex: CAP_ENERGIE, CREDIT_SPOT) |
| Nom du produit | `nom_produit` | `VARCHAR(100)` | Non | - | Non | Non | - | Nom commercial officiel (ex: CAP Energie) |
| ID Programme | `id_programme` | `INTEGER` | Non | - | Non | Oui | FK sur `PROGRAMMES_CREDITS`| Rattachement au programme de crédit |

---

#### 10. Table `CONTRATS_CREDITS`
*   **Rôle métier** : Enregistrer les contrats d'engagements de prêts accordés aux entreprises clientes.
*   **Principaux acteurs** : Conseiller (gestionnaire), Analyste Risques (suivi NPL), Entreprise (emprunteur).
*   **Futurs liens** : Liée à `ENTREPRISES` (N à 1), `PRODUITS_CREDITS` (N à 1), `AGENCES` (N à 1), `EMPLOYES` (N à 1 - Conseiller), `GARANTIES` (1 à N).
*   **Utilisation DWH** : Source de la table de faits **Fait_Credits**.
*   **Volume estimé** : ~1 000 contrats de crédits.

**Règles métier associées :**
*   Un contrat de crédit appartient à une seule entreprise cliente.
*   Le contrat hérite du conseiller et de l'agence de rattachement de l'entreprise.
*   L'encours restant dû doit être inférieur ou égal au montant accordé, et supérieur ou égal à zéro.
*   Le statut du crédit est restreint à : 'ACTIF', 'REMBOURSE' ou 'NPL'.
*   La date d'échéance doit être strictement supérieure à la date d'octroi.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Contrat | `id_contrat` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique du contrat |
| Référence contrat| `reference_contrat`| `VARCHAR(50)` | Non | - | Non | Non | UNIQUE | Référence unique de dossier BOA |
| ID Entreprise | `id_entreprise` | `INTEGER` | Non | - | Non | Oui | FK sur `ENTREPRISES` | Entreprise bénéficiaire |
| ID Produit | `id_produit` | `INTEGER` | Non | - | Non | Oui | FK sur `PRODUITS_CREDITS`| Produit de crédit souscrit |
| Montant accordé | `montant_accorde` | `NUMERIC(15,2)` | Non | - | Non | Non | CHECK (montant > 0)| Capital débloqué initial en MAD |
| Encours restant dû| `encours_restant_du`| `NUMERIC(15,2)`| Non | - | Non | Non | CHECK (encours >= 0) | Capital restant à rembourser en MAD |
| Date d'octroi | `date_octroi` | `DATE` | Non | - | Non | Non | - | Date de signature et déblocage |
| Date d'échéance | `date_echeance` | `DATE` | Non | - | Non | Non | CHECK (date) | Date de fin de remboursement contractuelle |
| Taux d'intérêt | `taux_interet` | `NUMERIC(5,2)` | Non | - | Non | Non | CHECK (taux >= 0) | Taux d'intérêt annuel appliqué |
| Statut du crédit | `statut_credit` | `VARCHAR(15)` | Non | 'ACTIF' | Non | Non | CHECK (statut) | Statut : ACTIF, REMBOURSE, NPL |
| ID Conseiller | `id_conseiller` | `INTEGER` | Non | - | Non | Oui | FK sur `EMPLOYES` | Conseiller affecté (hérité) |
| ID de l'agence | `id_agence` | `INTEGER` | Non | - | Non | Oui | FK sur `AGENCES` | Agence de l'octroi (héritée) |

---

#### 11. Table `GARANTIES`
*   **Rôle métier** : Gérer les garanties réelles ou personnelles souscrites par les entreprises pour couvrir les risques liés aux contrats de crédits.
*   **Principaux acteurs** : Analyste Risques (suivi de la couverture), Conseiller Entreprises.
*   **Futurs liens** : Liée à `CONTRATS_CREDITS` (N à 1).
*   **Utilisation DWH** : Rôle d'analyse du risque rattaché à **Fait_Credits** (Calcul de la couverture).
*   **Volume estimé** : ~800 garanties.

**Règles métier associées :**
*   Une garantie doit être rattachée à un contrat de crédit actif ou en NPL.
*   Le type de garantie doit être l'un des suivants : 'AVAL', 'CAUTION_ADMIN', 'CAUTION_FIN', 'GARANTIE_BANCAIRE'.
*   Le montant garanti doit être strictement supérieur à zéro.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Garantie | `id_garantie` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique de garantie |
| Réf Garantie | `reference_garantie`| `VARCHAR(50)` | Non | - | Non | Non | UNIQUE | Référence unique du contrat de garantie |
| ID Contrat Crédit| `id_contrat` | `INTEGER` | Non | - | Non | Oui | FK sur `CONTRATS_CREDITS`| Contrat de crédit couvert |
| Type de garantie | `type_garantie` | `VARCHAR(30)` | Non | - | Non | Non | CHECK (type) | AVAL, CAUTION_ADMIN, CAUTION_FIN, GARANTIE_BANCAIRE |
| Montant garanti | `montant_garanti` | `NUMERIC(15,2)` | Non | - | Non | Non | CHECK (montant > 0) | Valeur financière de la garantie en MAD |
| Date constitution | `date_constitution`| `DATE` | Non | - | Non | Non | - | Date d'enregistrement de la garantie |

---

### E. DOMAINE DIGITAL

#### 12. Table `SOLUTIONS_DIGITALES`
*   **Rôle métier** : Définir le catalogue des services de banque en ligne destinés aux entreprises de BOA.
*   **Principaux acteurs** : Analyste BI, Conseiller (commercialisation).
*   **Futurs liens** : Liée à `SOUSCRIPTIONS_DIGITALES` (1 à N).
*   **Utilisation DWH** : Source de la dimension **Dim_Solution_Digitale**.
*   **Volume estimé** : 5 enregistrements (DabaPay Pro, BusinessOnline.ma, CreditBusinessOnline, WhatsApp Business, KODI).

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Solution | `id_solution` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique |
| Nom de la solution| `nom_solution` | `VARCHAR(50)` | Non | - | Non | Non | UNIQUE | Nom de la solution (DabaPay Pro, etc.) |
| Type de canal | `type_canal` | `VARCHAR(20)` | Non | - | Non | Non | - | Nature du canal (WEB, MOBILE, ASSISTANT) |

---

#### 13. Table `SOUSCRIPTIONS_DIGITALES`
*   **Rôle métier** : Suivre l'abonnement/l'adhésion des entreprises clientes aux différentes solutions digitales de la banque.
*   **Principaux acteurs** : Conseiller Entreprises, Entreprise.
*   **Futurs liens** : Liée à `ENTREPRISES` (N à 1), `SOLUTIONS_DIGITALES` (N à 1) et `CONNEXIONS_DIGITALES` (1 à N).
*   **Utilisation DWH** : Rôle d'axe d'analyse et de fait pour l'équipement digital.
*   **Volume estimé** : ~1 500 souscriptions.

**Règles métier associées :**
*   Une souscription lie une unique entreprise à une unique solution digitale active.
*   Le statut de la souscription est limité à 'ACTIF' ou 'RESILIE'.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Souscription | `id_souscription` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant unique |
| ID Entreprise | `id_entreprise` | `INTEGER` | Non | - | Non | Oui | FK sur `ENTREPRISES` | Entreprise ayant souscrit |
| ID Solution | `id_solution` | `INTEGER` | Non | - | Non | Oui | FK sur `SOLUTIONS_DIGITALES`| Service digital souscrit |
| Date souscription| `date_souscription`| `DATE` | Non | - | Non | Non | - | Date de signature du contrat d'adhésion |
| Statut | `statut` | `VARCHAR(10)` | Non | 'ACTIF' | Non | Non | CHECK (statut) | Statut de l'accès (ACTIF, RESILIE) |

---

#### 14. Table `CONNEXIONS_DIGITALES`
*   **Rôle métier** : Enregistrer l'activité et l'historique d'utilisation (logs) des solutions digitales par les entreprises souscriptrices.
*   **Principaux acteurs** : Entreprise (acteur direct), Analyste BI (pour le reporting d'adoption).
*   **Futurs liens** : Liée à `SOUSCRIPTIONS_DIGITALES` (N à 1).
*   **Utilisation DWH** : Source de la table de faits **Fait_Digital**.
*   **Volume estimé** : ~100 000 connexions.

**Règles métier associées :**
*   Chaque connexion est associée à une souscription valide.
*   Le nombre d'opérations effectuées lors de la session doit être supérieur ou égal à zéro.

| Nom logique | Nom physique | Type PostgreSQL | Nullable | Défaut | PK | FK | Contraintes | Description métier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ID Connexion | `id_connexion` | `SERIAL` | Non | - | Oui | Non | UNIQUE | Identifiant de log unique |
| ID Souscription | `id_souscription` | `INTEGER` | Non | - | Non | Oui | FK sur `SOUSCRIPTIONS_DIGITALES`| Accès digital utilisé |
| Date & Heure | `date_heure_connexion`| `TIMESTAMP` | Non | - | Non | Non | - | Horodatage de connexion de l'utilisateur |
| Nbr Opérations | `nombre_operations`| `INTEGER` | Non | 0 | Non | Non | CHECK (Ops >= 0) | Nombre de transactions passées sur la session |

---

### F. SYNTHÈSE DES MAPPINGS DATA WAREHOUSE & VOLUMES

Le tableau suivant résume le rôle de chaque table OLTP dans la modélisation du Data Warehouse et les volumes cibles associés.

| Table OLTP | Utilisation DWH | Volume de Données Estimé |
| :--- | :--- | :--- |
| `REGIONS` | **Dim_Region** | 7 |
| `AGENCES` | **Dim_Agence** | 10 |
| `EMPLOYES` | **Dim_Employe** | ~50 |
| `ENTREPRISES` | **Dim_Entreprise** | ~2 000 |
| `COMPTES` | **Dim_Produit_Depot** (type) + **Fait_Depots** (solde) | ~2 500 |
| `TRANSACTIONS` | **Fait_Transactions** | ~150 000 |
| `FAMILLES_CREDITS` | **Dim_Produit_Credit** (hiérarchie macro) | 3 |
| `PROGRAMMES_CREDITS` | **Dim_Produit_Credit** (hiérarchie programme) | ~10 |
| `PRODUITS_CREDITS` | **Dim_Produit_Credit** (hiérarchie produit) | ~20 |
| `CONTRATS_CREDITS` | **Dim_Produit_Credit** + **Fait_Credits** (encours) | ~1 000 |
| `GARANTIES` | **Fait_Credits** (attribut de couverture du fait) | ~800 |
| `SOLUTIONS_DIGITALES` | **Dim_Solution_Digitale** | 5 |
| `SOUSCRIPTIONS_DIGITALES`| **Dim_Solution_Digitale** + **Fait_Digital** (flag souscript.)| ~1 500 |
| `CONNEXIONS_DIGITALES` | **Fait_Digital** | ~100 000 |
