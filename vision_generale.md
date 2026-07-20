# Vision Générale du Projet : Plateforme Décisionnelle Business Banking
## Bank of Africa (BOA) - Simulation Académique

---

### 1. Contexte & Objectifs

Ce projet est une simulation académique inspirée de l'activité **Business Banking** de **Bank of Africa Maroc (BOA)**. L'objectif principal est de concevoir et de réaliser une plateforme décisionnelle de bout en bout (End-to-End BI & Analytics) pour piloter l'activité des entreprises clients de la banque.

La plateforme permettra aux décideurs (directions régionales, directeurs d'agences, analystes risques) de disposer d'indicateurs de pilotage précis, de modèles prédictifs et d'outils de reporting interactifs pour soutenir la croissance commerciale et la maîtrise du risque.

---

### 2. Sources de Données

> [!IMPORTANT]
> **Origine des données :**
> *   Ce projet utilise **exclusivement des données simulées**.
> *   Aucune donnée réelle ou confidentielle interne de Bank of Africa Maroc n'est utilisée ou partagée.
> *   Les données seront générées à l'aide d'un script **Python** (utilisant la bibliothèque **Faker** et des règles de distribution statistique inspirées de données publiques sectorielles marocaines).
> *   Le but est d'obtenir un jeu de données réaliste (2 000 entreprises, 150 000 transactions cohérentes dans le temps) respectant les contraintes métier bancaires.

---

### 3. Périmètre du Projet

Le périmètre fonctionnel et technique du projet est défini selon les limites suivantes :
*   **Simulation Académique** : Inspiré fonctionnellement des offres et de l'organisation de Bank of Africa Maroc.
*   **Business Banking Uniquement** : Le projet cible exclusivement le segment des entreprises. Les clients particuliers ne sont pas inclus dans cette version.
*   **Segmentation Clientèle** : Le projet couvre uniquement les types d'entreprises suivants :
    *   **TPE** (Très Petites Entreprises)
    *   **PME** (Petites et Moyennes Entreprises)
    *   **Grandes Entreprises**
*   **Domaines Métier Couverts** : Concentration exclusive sur deux domaines fonctionnels majeurs :
    *   **Dépôts Entreprises** (Comptes courants, dépôts à terme, cash management, transactions).
    *   **Crédits Entreprises** (Crédits de trésorerie, d'investissement, commerce international et garanties associées).

---

### 4. Objectifs Décisionnels

La plateforme décisionnelle vise à répondre aux objectifs métiers stratégiques suivants :
*   **Piloter les dépôts des entreprises** : Analyser les encours de collecte, les comptes courants et les dépôts à terme.
*   **Suivre la production des crédits** : Monitorer l'octroi, l'utilisation des lignes et l'évolution des encours de financements.
*   **Analyser les risques (NPL)** : Suivre les créances en souffrance (Non-Performing Loans) et les taux de défaut par segment ou secteur d'activité.
*   **Évaluer la performance commerciale des conseillers** : Mesurer l'activité commerciale et la réalisation des objectifs des gestionnaires de portefeuilles.
*   **Comparer les performances des agences et des régions** : Établir des benchmarks géographiques sur 7 régions et 10 agences.
*   **Mesurer l'adoption des services digitaux** : Suivre l'utilisation et la souscription aux canaux digitaux (BusinessOnline.ma, CreditBusinessOnline, DabaPay Pro, etc.).
*   **Segmenter les entreprises grâce au Machine Learning** : Classifier les entreprises via des algorithmes (K-Means) basés sur leur comportement financier et digital.

---

### 5. Organisation de la Banque & Acteurs

#### Structure Commerciale (Géographie)
*   **7 Régions** administratives :
    1.  Casablanca-Settat (2 agences)
    2.  Rabat-Salé-Kénitra (2 agences)
    3.  Sud (2 agences)
    4.  Fès-Meknès (1 agence)
    5.  Marrakech-Safi (1 agence)
    6.  Tanger-Tétouan-Al Hoceïma (1 agence)
    7.  Oriental (1 agence)
*   **10 Agences** réparties dans ces régions.
*   **50 Employés** au total au sein des agences. Les rôles opérationnels par agence sont strictement figés :
    *   **1 Directeur d'agence** : Supervise l'activité globale et les performances de son agence.
    *   **2 Conseillers Entreprises** : Gèrent chacun un portefeuille d'entreprises. Ils sont les pivots de la relation client.
    *   **1 Chargé de caisse** : Gère les opérations de caisse physiques au quotidien.

*Remarque : Les conseillers entreprises sont des employés de la banque. Il n'y aura pas de table séparée "Conseiller" ; leur rôle sera porté par la table générique des employés via un attribut fonctionnel.*

#### Gestion des Entreprises & Attribution
*   Chaque entreprise est rattachée à **une seule agence** et à **un seul conseiller entreprise** de cette agence.
*   Par transitivité et cohérence métier, **tous les comptes, crédits, services digitaux et transactions** initiés par une entreprise héritent automatiquement du conseiller entreprise qui lui est affecté.

---

### 6. Processus Métier & Offres

#### Domaine 1 : Dépôts & Cash Management
*   **Comptes Courants Entreprises** : Comptes pivots pour les flux de trésorerie courants.
*   **Dépôts à Terme (DAT)** : Placements de trésorerie avec taux d'intérêt et date d'échéance.
*   **Opérations de Cash Management / Transactions** : Encaissements, paiements, virements locaux/internationaux, gestion des flux.

#### Domaine 2 : Crédits & Engagements
*   **Crédits de Trésorerie** : Découvert, facilité de caisse, avance sur marché, crédit Spot.
*   **Crédits d'Investissement** : Crédit Moyen Long Terme, co-financements ou lignes dédiées (Maroc PME, TAMWILCOM, Green Invest, Go Siyaha, CAP Energie).
*   **Commerce International** : Crédits documentaires (Import/Export), crédit acheteur, crédit fournisseur.
*   **Garanties (Cautions/Sûretés)** : Aval, caution administrative ou financière, garantie bancaire.

#### Domaine 3 : Services Digitaux Entreprises
Suivi de la souscription et de l'usage des canaux digitaux professionnels de BOA :
*   **BusinessOnline.ma** (Portail web de gestion des comptes et flux).
*   **CreditBusinessOnline** (Suivi et demande de crédits en ligne).
*   **DabaPay Pro** (Paiement mobile commerçant/entreprise).
*   **WhatsApp Business** & **KODI** (Assistants virtuels et canaux d'interaction digitaux).

---

### 7. Technologies

Le socle technologique pour la réalisation du projet est composé de :
*   **PostgreSQL** : Système de gestion de base de données relationnelle pour le stockage OLTP et le Data Warehouse.
*   **Python** : Langage de programmation principal pour la simulation de données et l'implémentation de la logique ETL et IA.
*   **Pandas** : Bibliothèque d'analyse et de manipulation de données pour les transformations ETL.
*   **Faker** : Générateur de données fictives en Python.
*   **SQLAlchemy** : ORM et connecteur SQL pour interagir avec PostgreSQL depuis Python.
*   **Scikit-Learn** : Bibliothèque de Machine Learning pour l'implémentation du clustering K-Means.
*   **Power BI** : Outil de restitution décisionnelle et de création de tableaux de bord.
*   **Git** : Système de contrôle de version.
*   **VS Code** : Environnement de développement intégré (IDE).

---

### 8. Livrables du Projet

Les livrables attendus à l'issue du projet sont :
*   **Cahier des charges** : Spécification détaillée des besoins et indicateurs clés.
*   **Dictionnaire de données** : Modélisation conceptuelle détaillée des attributs.
*   **MCD, MLD et MPD** : Les modèles de données physiques et logiques (Merise) pour le système OLTP.
*   **Scripts PostgreSQL** : DDL de création de la base OLTP, du Data Warehouse et des Data Marts.
*   **Générateur Python** : Script Python de peuplement de la base OLTP à l'aide de Faker.
*   **Pipeline ETL** : Scripts d'extraction, de transformation et de chargement des données.
*   **Data Warehouse & Data Marts** : Structure décisionnelle déployée sous PostgreSQL.
*   **Modèle IA** : Script Python de segmentation K-Means et script d'intégration des clusters.
*   **Tableaux de bord Power BI** : Rapports de visualisation et de pilotage stratégique.
*   **Documentation technique** : Rapport de PFE complet décrivant la conception et la mise en œuvre.

---

### 9. Architecture Technique Globale & Flux de Données

Le projet respecte une architecture décisionnelle classique "End-to-End" :

```
+--------------------+
|  Python Generator  | ----> Génération des données simulées (Faker + Règles métier)
+--------------------+
          |
          v
+--------------------+
|  PostgreSQL OLTP   | ----> Base de données transactionnelle source (Modèle Normalisé 3NF)
+--------------------+
          |
          v
+--------------------+
|    Pipeline ETL    | ----> Extraction, Transformation & Chargement (Python / Pandas / SQL)
+--------------------+
          |
          v
+--------------------+
|   Data Warehouse   | ----> Stockage décisionnel centralisé (Schéma en étoile)
+--------------------+
          |          \
          v           v
+--------------------+ +---------------------+
|     Data Marts     | |  Machine Learning   | ----> Segmentation K-Means des entreprises
+--------------------+ +---------------------+ (Exports de clusters vers DWH/Data Marts)
          |           /
          v          v
+--------------------+
|      Power BI      | ----> Tableaux de bord interactifs de pilotage stratégique & opérationnel
+--------------------+
```

---

### 10. Feuille de Route du Projet (Roadmap)

Le projet sera mené en respectant strictement les 19 étapes méthodologiques validées :

1.  **Vision générale du projet** (Étape actuelle - Cadrage initial)
2.  **Cahier des charges** (Spécification détaillée des besoins et KPIs)
3.  **Analyse métier** (Cartographie des processus et règles fonctionnelles fines)
4.  **Dictionnaire de données** (Définition de tous les attributs de la base OLTP)
5.  **MCD** (Modèle Conceptuel de Données - Merise)
6.  **MLD** (Modèle Logique de Données)
7.  **MPD** (Modèle Physique de Données)
8.  **Architecture technique** (Spécifications logicielles, environnements et configurations)
9.  **Architecture décisionnelle** (Modélisation dimensionnelle du Data Warehouse et des Data Marts)
10. **Règles métier** (Définition des formules de calculs des KPIs, statuts de risques, etc.)
11. **Règles de génération** (Définition des lois de distribution et de cohérence pour Faker)
12. **PostgreSQL DDL** (Création de la base OLTP)
13. **Génération Python** (Script d'insertion de données de simulation)
14. **ETL** (Script Python de chargement de la base OLTP vers le Data Warehouse)
15. **Modélisation Data Warehouse & Data Marts** (Implémentation physique DWH/DM)
16. **Machine Learning** (Développement du modèle de clustering K-Means sous Python)
17. **Intégration du Scoring ML** (Rattachement des clusters au DWH / Data Marts)
18. **Power BI** (Construction des dashboards)
19. **Documentation finale** (Rapport de projet PFE complet)

---

Cette Vision Générale constitue le document de référence du projet. Toutes les étapes suivantes (analyse métier, modélisation, implémentation et restitution décisionnelle) devront rester cohérentes avec cette vision afin de garantir une architecture homogène, évolutive et adaptée aux besoins du Business Banking.
