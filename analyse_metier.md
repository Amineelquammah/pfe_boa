# Analyse Métier : Plateforme Décisionnelle Business Banking
## Bank of Africa (BOA) - Simulation Académique

---

### 1. Présentation du Métier & Rôles des Acteurs

Le **Business Banking** est l'activité d'une institution bancaire qui s'adresse spécifiquement aux personnes morales (entreprises) et aux professionnels. Contrairement au Retail Banking (clients particuliers), le Business Banking gère des volumes financiers plus importants, des structures de comptes complexes et des produits de financement hautement personnalisés (crédits syndiqués, co-financements, crédits documentaires). 

Cette activité repose sur une relation de proximité forte portée par des experts dédiés qui analysent en permanence la santé financière et sectorielle de leurs clients afin de les accompagner dans leurs projets de croissance tout en maîtrisant l'exposition au risque de la banque.

Les principaux acteurs du processus décisionnel et opérationnel sont présentés ci-dessous :

*   **Entreprise (Client)** : Personne morale (TPE, PME ou Grande Entreprise) qui souscrit aux produits de dépôt, de crédit et de cash management de la banque pour gérer sa trésorerie opérationnelle et financer son cycle d'exploitation ou ses investissements.
*   **Conseiller Entreprises (Gestionnaire de Portefeuille)** : Employé de l'agence bancaire en charge de la relation commerciale avec un portefeuille d'entreprises. Il instruit les demandes de crédits, propose des solutions de placement (DAT) et de digitalisation, et assure le premier niveau d'analyse des risques de défaut de ses clients.
*   **Directeur d'Agence** : Manageur de l'agence. Il valide les octrois de crédits de premier niveau (dans la limite de ses délégations de pouvoir), supervise les objectifs de collecte et de production de crédits de ses conseillers, et veille à la rentabilité globale de son agence.
*   **Directeur Régional** : Responsable d'une des 7 directions régionales de la banque. Il pilote la performance commerciale et financière de l'ensemble des agences de sa région, arbitre les dossiers de crédit d'un montant élevé et déploie la stratégie globale de la banque au niveau régional.
*   **Analyste Risques** : Basé généralement au siège social ou au niveau régional. Il analyse le risque de contrepartie, valide de manière indépendante les dossiers d'octroi de crédit, suit le portefeuille des créances douteuses (NPL) et veille à l'adéquation des garanties (cautions, hypothèques) prises par la banque.
*   **Analyste BI (Business Intelligence)** : Garant technique et fonctionnel de la plateforme décisionnelle. Il conçoit et maintient le pipeline ETL, modélise le Data Warehouse et les Data Marts, intègre le scoring du modèle IA (Machine Learning) et met à disposition les tableaux de bord Power BI pour les différents profils métiers.

---

### 2. Les Deux Domaines Métier & Leurs Cycles de Vie

Le projet s'organise de manière étanche autour de deux grands domaines opérationnels.

#### A. Domaine Dépôts & Cash Management
Ce domaine concerne la collecte des ressources auprès des entreprises et la gestion de leurs transactions quotidiennes.

```
+-------------+      +----------------------+      +------------------------+
| Entreprise  | ---> | Ouverture du Compte  | ---> | Utilisation du Compte  |
+-------------+      +----------------------+      +------------------------+
                                                               |
                                                               v
+-------------+      +----------------------+      +------------------------+
|  Reporting  | <--- | Dépôts à Terme (DAT) | <--- |  Cash Mgmt / Transac   |
+-------------+      +----------------------+      +------------------------+
```

*   **Entreprise** : Le client s'adresse à son conseiller entreprise pour formuler son besoin de gestion de flux.
*   **Ouverture du compte** : Attribution d'un compte courant entreprise, signature des conventions de compte et paramétrage des accès digitaux (BusinessOnline.ma).
*   **Utilisation du compte** : Le compte sert de support à l'ensemble des opérations courantes de l'entreprise.
*   **Transactions** : Réalisation de flux entrants et sortants (virements nationaux/internationaux, paiements fournisseurs, encaissements clients, versements d'espèces).
*   **Cash Management** : Optimisation de la trésorerie de l'entreprise via la mise en place de flux automatisés, de solutions de paiement de masse ou d'encaissement (DabaPay Pro).
*   **DAT (Dépôts à Terme)** : En cas d'excédent de trésorerie sur le compte courant, l'entreprise souscrit à un compte bloqué rémunéré (DAT) avec un taux d'intérêt négocié et une date d'échéance fixée.
*   **Reporting** : Extraction des données transactionnelles et des soldes pour alimenter les analyses de collecte de la banque.

#### B. Domaine Crédits & Engagements
Ce domaine concerne le financement du cycle d'exploitation (court terme) et des investissements (moyen/long terme) des entreprises.

```
+--------------------+      +--------------------+      +--------------------+
| Demande de crédit  | ---> |  Analyse du risque | ---> | Validation / Octroi|
+--------------------+      +--------------------+      +--------------------+
                                                                   |
                                                                   v
+--------------------+      +--------------------+      +--------------------+
| Remboursement /    | <--- |   Suivi / Traite   | <--- |   Décaissement     |
| Clôture (NPL / OK) |      |   des Échéances    |      |    des fonds       |
+--------------------+      +--------------------+      +--------------------+
```

*   **Demande de crédit** : L'entreprise soumet un dossier de financement (ex. demande de facilité de caisse, crédit d'investissement, crédit documentaire) via son conseiller ou en ligne (CreditBusinessOnline).
*   **Analyse** : Le conseiller instruit le dossier (analyse des états financiers, calcul des ratios d'endettement, valorisation des garanties proposées) et l'analyste risques émet un avis.
*   **Validation** : Le comité de crédit compétent approuve ou refuse la demande. En cas d'accord, les contrats de prêt et de garanties (cautions, avals) sont signés.
*   **Décaissement** : Déblocage des fonds sur le compte courant de l'entreprise (ou émission de la ligne de caution/lettre de crédit).
*   **Suivi** : Monitorage périodique du crédit par le conseiller (suivi des impayés, réévaluation annuelle des dossiers, analyse sectorielle).
*   **Échéances** : Passage régulier des échéances de crédit selon le tableau d'amortissement (mensuel, trimestriel ou à l'échéance pour les crédits Spots).
*   **Remboursement** : Prélèvements automatiques des traites (capital + intérêts + taxes) sur le compte courant.
*   **Clôture** : 
    *   *Scénario Standard* : Remboursement intégral du crédit à l'échéance finale et mainlevée des garanties.
    *   *Scénario Dégradé (NPL)* : En cas d'impayé persistant (> 90 jours), le dossier bascule en créance douteuse (Non-Performing Loan), le recouvrement contentieux est engagé, et les provisions financières sont constituées.

---

### 3. Processus Métier Détaillés

Voici la description étape par étape des 7 processus opérationnels indispensables au système :

#### Processus 1 : Ouverture d'un compte courant
1.  **Entretien commercial** : Le conseiller qualifie l'entreprise (ICE, Chiffre d'Affaires, Secteur) et procède à la segmentation commerciale initiale (TPE/PME/GE).
2.  **Constitution du dossier juridique** : Collecte des statuts, du PV de nomination des dirigeants, du registre du commerce et des pièces d'identité des signataires.
3.  **Création du tiers** : Saisie de l'entreprise dans le système d'information bancaire (OLTP). Rattachement obligatoire de l'entreprise à l'agence et au conseiller.
4.  **Ouverture du compte courant** : Génération du RIB et affectation du compte courant à l'entreprise.
5.  **Héritage** : Le compte courant hérite automatiquement de l'agence et du conseiller affectés à l'entreprise.

#### Processus 2 : Création d'un Dépôt à Terme (DAT)
1.  **Négociation des conditions** : L'entreprise et son conseiller conviennent du montant à placer, de la durée de blocage (ex. 3, 6, 12 mois) et du taux d'intérêt créditeur.
2.  **Vérification de la provision** : Le conseiller s'assure que le solde disponible sur le compte courant de l'entreprise est supérieur ou égal au montant du placement négocié.
3.  **Création du compte DAT** : Enregistrement du contrat de DAT dans le système transactionnel.
4.  **Débit du compte courant** : Transfert des fonds du compte courant vers le compte DAT.
5.  **Héritage** : Le DAT hérite obligatoirement du compte courant support de l'opération (et par conséquent du conseiller et de l'agence).

#### Processus 3 : Octroi d'un crédit entreprise
1.  **Dépôt du dossier** : L'entreprise formule sa demande de crédit de trésorerie, d'investissement ou d'international.
2.  **Instruction et analyse financière** : Le conseiller saisit le dossier de crédit, évalue le besoin en fonds de roulement ou le plan de financement et enregistre les garanties (avals, cautions).
3.  **Décision du comité** : Soumission du dossier au comité d'octroi pour validation.
4.  **Déblocage (Décaissement)** : Signature des contrats, prise effective des garanties en base et déblocage des fonds sur le compte courant de l'entreprise.
5.  **Rattachement** : Le contrat de crédit hérite du conseiller et de l'agence de l'entreprise cliente.

#### Processus 4 : Utilisation des services digitaux
1.  **Souscription** : L'entreprise adhère à un ou plusieurs services (ex: BusinessOnline.ma).
2.  **Création des accès** : Génération des identifiants et affectation des profils d'utilisateurs habilités au sein de l'entreprise.
3.  **Connexion** : L'entreprise accède à la plateforme digitale (génération d'un log de connexion avec date et heure).
4.  **Transaction/Opération digitale** : Réalisation d'une opération (consultation, virement, suivi de crédit) générant un log d'événement digital.

#### Processus 5 : Réalisation d'une transaction bancaire
1.  **Initiation** : Une transaction (ex. virement sortant) est initiée par l'entreprise (en agence ou via BusinessOnline.ma).
2.  **Contrôle de provision** : Le système vérifie la provision sur le compte courant de l'entreprise (en tenant compte d'une éventuelle facilité de caisse accordée).
3.  **Exécution** : Enregistrement de la transaction (débit du compte émetteur, crédit du compte destinataire).
4.  **Génération de l'écriture** : Stockage de la transaction avec date, heure, montant, type d'opération (virement, versement, retrait) et sens (débit/crédit).

#### Processus 6 : Suivi du portefeuille entreprises
1.  **Visualisation** : Le conseiller se connecte à son tableau de bord Power BI pour consulter la situation de son portefeuille (somme des dépôts, somme des encours de crédits).
2.  **Alerte** : Le système met en évidence les entreprises sous-équipées en services digitaux ou présentant des baisses anormales d'encours de dépôts.
3.  **Planification d'actions** : Le conseiller planifie des rendez-vous commerciaux pour proposer des réajustements de lignes de découvert ou des souscriptions à des produits de placement (DAT).

#### Processus 7 : Analyse du risque
1.  **Suivi des impayés** : L'analyste risques surveille quotidiennement via le système décisionnel les comptes débiteurs non autorisés et les échéances de crédits impayées.
2.  **Classification NPL** : Si un impayé atteint 90 jours consécutifs, le système OLTP classe automatiquement le crédit en statut "NPL" (Non-Performing Loan).
3.  **Valorisation des provisions** : Calcul du montant à provisionner en fonction de l'encours restant dû et des garanties enregistrées.
4.  **Évaluation globale** : Analyse sectorielle et géographique du taux NPL pour identifier des concentrations de risques.

---

### 4. Règles Métier Structurelles et Fonctionnelles

Pour garantir l'intégrité de la modélisation et du simulateur de données, les règles de gestion suivantes sont formellement édictées :

*   **Règle d'appartenance commerciale (1)** : Une entreprise appartient à une seule agence et à un seul conseiller entreprise de cette agence.
*   **Règle d'affectation des comptes (2)** : Tout compte ouvert (compte courant) appartient à une entreprise unique et hérite directement de son conseiller et de son agence.
*   **Règle de filiation des placements (3)** : Un compte Dépôt à Terme (DAT) est obligatoirement lié à un compte courant actif de la même entreprise.
*   **Règle d'affectation des crédits (4)** : Tout contrat de crédit est obligatoirement rattaché à une entreprise cliente (et par conséquent à son conseiller de portefeuille).
*   **Règle de ciblage produit (5)** : Certains produits de financement sont soumis à des contraintes de segment (ex. les lignes de financement subventionnées comme *Maroc PME* ou *Go Siyaha* sont exclusivement réservées aux TPE et PME, tandis que les *Crédits Acheteurs* complexes sont réservés aux Grandes Entreprises).
*   **Règle d'attribution des transactions (6)** : Toute transaction financière est liée à un compte courant unique.
*   **Règle d'attribution digitale (7)** : Toute connexion ou transaction digitale est liée à une souscription active d'une entreprise à un service digital.

---

### 5. Flux Métier d'Information (Data Lineage)

Le flux logique de l'information décisionnelle se présente ainsi :

```
[Entreprise] ---> Génère des flux opérationnels (Crédits, Dépôts, Digital)
      |
      v
[Agence / Conseiller] ---> Saisissent et structurent les contrats et clients dans le SI
      |
      v
[Compte Courant / DAT] ---> Enregistrent les flux financiers et transactions courantes
      |
      v
[Base PostgreSQL OLTP] ---> Stocke les données dans un modèle transactionnel normalisé (3NF)
      |
      v
[Pipeline ETL (Python/Pandas)] ---> Extrait, nettoie, calcule les KPIs et charge les données
      |
      v
[Data Warehouse (DWH)] ---> Stocke l'historique dénormalisé en schéma en étoile (Dim & Faits)
      |
      v
[Data Marts / K-Means ML] ---> Filtrent les données par domaine et ajoutent le scoring IA
      |
      v
[Tableaux de bord Power BI] ---> Restituent les KPIs interactifs aux utilisateurs finaux
```

---

### 6. Sources de Données à Simuler

Les futures données nécessaires à l'alimentation du système décisionnel seront modélisées et générées artificiellement :
*   **Entreprises** : Raison sociale, ICE (identifiant fiscal unique à 9 chiffres pour la simulation), secteur d'activité (Commerce, BTP, Services, Industrie, Agriculture, Technologies), forme juridique (SARL, SA, SNC), date de création, chiffre d'affaires annuel, nombre d'employés, segment (TPE, PME, GE), région et ville d'implantation.
*   **Employés** : Identifiant, nom, prénom, rôle (Directeur d'agence, Conseiller Entreprises, Chargé de caisse), date de recrutement, agence d'affectation.
*   **Agences** : Identifiant, nom de l'agence, ville, direction régionale de rattachement.
*   **Comptes** : Numéro de compte (format RIB simulé), solde actuel, date d'ouverture, statut (Actif/Inactif), type de compte (Courant, DAT).
*   **Crédits** : Numéro de contrat, montant accordé, encours restant dû, date d'octroi, date d'échéance, type de crédit, statut du crédit (Actif, Remboursé, NPL).
*   **Transactions** : Référence unique, RIB du compte associé, date et heure, type de transaction (Virement, Versement, Retrait, Prélèvement), sens (Débit/Crédit), montant, canal d'exécution (Agence, Digital).
*   **Solutions Digitales** : Identifiant du service (DabaPay Pro, BusinessOnline.ma, etc.), logs de connexion (date, heure) et volume d'opérations digitales réalisées.

---

### 7. Glossaire Métier

*   **DAT (Dépôt à Terme)** : Compte de placement bloqué sur une période déterminée, rapportant des intérêts à un taux fixé lors de la souscription.
*   **Compte Courant Entreprise** : Compte de dépôt à vue utilisé par une entreprise pour ses encaissements et décaissements quotidiens.
*   **Cash Management** : Ensemble de services et d'outils proposés par la banque pour aider les entreprises à optimiser leurs flux financiers et leur gestion de trésorerie (ex: centralisation de trésorerie).
*   **NPL (Non-Performing Loan - Créance Douteuse)** : Crédit bancaire pour lequel l'emprunteur est en défaut de paiement (absence de remboursement d'intérêts ou de capital) depuis au moins 90 jours consécutifs.
*   **Encours** : Solde restant dû d'un crédit à une date donnée, ou solde créditeur global d'un compte de dépôt.
*   **Collecte (ou Dépôts)** : Ensemble des fonds déposés par les clients dans les comptes de la banque. Constitue une ressource financière pour l'établissement.
*   **BusinessOnline.ma** : Portail de banque par internet de Bank of Africa destiné aux clients entreprises pour la gestion de leurs opérations et de leur trésorerie.
*   **DabaPay Pro** : Solution de paiement mobile de Bank of Africa destinée aux commerçants et aux professionnels pour accepter les encaissements via smartphone.
*   **Conseiller Entreprises** : Gestionnaire de clientèle commerciale bancaire, spécialisé dans l'accompagnement et la vente de produits financiers aux entreprises.
*   **Agence** : Point de vente physique de la banque assurant la relation de proximité avec la clientèle.
*   **Région** : Direction régionale de la banque regroupant un ensemble d'agences sur un territoire géographique donné.

---

### 8. Validation de Cohérence

Ce document a été vérifié et s'aligne rigoureusement sur les livrables précédents :
1.  **Vision Générale** : Respect de la portée Business Banking, de la simulation 100 % fictive, de la structure des 7 régions et 10 agences et de l'organisation figée à 50 employés.
2.  **Cahier des Charges Fonctionnel** : Reprise exacte des 6 domaines de KPIs cibles et intégration de la logique temporelle trimestrielle/annuelle pour l'historique 2022-2024.
