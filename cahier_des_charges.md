# Cahier des Charges Fonctionnel : Plateforme Décisionnelle Business Banking
## Bank of Africa (BOA) - Simulation Académique

---

### 1. Introduction & Périmètre du Projet

Ce cahier des charges fonctionnel définit les exigences détaillées pour la conception et l'implémentation de la **Plateforme Décisionnelle Business Banking**. Il sert de guide et de référence pour toutes les étapes techniques subséquentes (modélisation de données, ETL, Machine Learning et restitution Power BI).

#### Périmètre du Projet
*   **Segment de clientèle cible** : Le projet cible **exclusivement** le segment Business Banking (les clients particuliers sont formellement exclus de cette version). Les entreprises ciblées appartiennent aux segments suivants :
    *   **TPE** (Très Petites Entreprises)
    *   **PME** (Petites et Moyennes Entreprises)
    *   **Grandes Entreprises**
*   **Domaines fonctionnels couverts** : 
    *   **Dépôts Entreprises** (Comptes courants, dépôts à terme, cash management et flux).
    *   **Crédits Entreprises** (Crédits de trésorerie, d'investissement, commerce international et garanties).
*   **Origine des données** : 100 % simulées à l'aide de scripts Python/Faker (aucune donnée interne de Bank of Africa Maroc n'est utilisée).

---

### 2. Exigences Fonctionnelles de la Plateforme

Le système décisionnel final devra implémenter et assurer les fonctionnalités suivantes :
1.  **Pilotage des Dépôts** : Suivi des ressources collectées, de la stabilité des dépôts et de la nature des comptes ouverts.
2.  **Pilotage des Crédits** : Monitorage de la production de nouveaux financements, des encours et de la typologie des crédits octroyés.
3.  **Suivi des Performances Commerciales** : Évaluation de la performance des collaborateurs (conseillers), des agences et des régions géographiques.
4.  **Suivi des Risques** : Identification, quantification et localisation des créances douteuses ou compromises (NPL) ainsi que des garanties associées.
5.  **Suivi de la Digitalisation** : Analyse de l'adhésion des entreprises aux canaux digitaux de la banque et de la fréquence de leur utilisation.
6.  **Segmentation Intelligente des Entreprises** : Regroupement automatisé des clients par caractéristiques financières et comportementales (via clustering K-Means).
7.  **Aide à la Décision via Power BI** : Fourniture de rapports interactifs dynamiques permettant de filtrer les résultats et de guider les choix stratégiques.

---

### 3. Spécifications Détaillées des KPIs par Domaine

Les tableaux de bord de la plateforme devront calculer et restituer les indicateurs clés de performance suivants, organisés en six domaines :

#### A. Dépôts
*   **Nombre de comptes ouverts** : Nombre total de comptes créés sur la période de référence.
*   **Nombre de comptes actifs** : Nombre de comptes ayant enregistré au moins une opération de flux (débit ou crédit) au cours du dernier trimestre.
*   **Encours des comptes courants** : Somme des soldes des comptes courants des entreprises à l'instant de l'analyse.
*   **Encours des DAT (Dépôts à Terme)** : Encours total placé sur les comptes bloqués avec rémunération.
*   **Collecte nette** : Différence entre les dépôts totaux (nouveaux comptes + flux créditeurs) et les retraits totaux (flux débiteurs) sur un trimestre donné.
*   **Évolution trimestrielle des dépôts** : Taux de croissance de l'encours global d'un trimestre à l'autre.
*   **Axes d'analyse (dimensions de croisement)** : 
    *   Géographie : Région, Agence.
    *   Organisation commerciale : Conseiller Entreprises.
    *   Comportement : Secteur d'activité de l'entreprise, Segment (TPE/PME/GE).

#### B. Crédits
*   **Nombre de crédits accordés** : Nombre de contrats d'engagement de crédits signés et débloqués.
*   **Production de crédits** : Volume financier total des nouveaux crédits accordés et débloqués sur le trimestre.
*   **Encours des crédits** : Capital restant dû global sur tous les crédits actifs à l'instant de l'analyse.
*   **Crédit moyen** : Montant moyen de la production de crédit par contrat ($\text{Production} / \text{Nombre de crédits accordés}$).
*   **Évolution trimestrielle de la production** : Taux de variation du montant des nouveaux crédits débloqués par rapport au trimestre précédent.
*   **Axes d'analyse (dimensions de croisement)** :
    *   Type de produit : Crédit de trésorerie (Découvert, Spot, etc.), Crédit d'investissement (CAP Energie, TAMWILCOM, etc.), Commerce international (Crédit documentaire Import/Export, etc.).
    *   Secteur d'activité de l'entreprise, Segment (TPE/PME/GE).
    *   Géographie : Région, Agence.
    *   Commercial : Conseiller Entreprises.

#### C. Performance Commerciale
*   **Nombre d'entreprises par conseiller** : Taille du portefeuille client géré par chaque collaborateur commercial.
*   **Dépôts gérés par conseiller** : Encours cumulé des dépôts (comptes courants + DAT) des entreprises du portefeuille du conseiller.
*   **Crédits gérés par conseiller** : Encours cumulé des crédits actifs des entreprises du portefeuille du conseiller.
*   **Performance des agences** : Comparatif des encours de dépôts, de crédits et du taux d'adoption digital agrégés au niveau de chaque agence.
*   **Performance des régions** : Suivi des indicateurs agrégés au niveau des 7 directions régionales.
*   **Classement des conseillers** : Palmarès des conseillers selon la collecte nette de dépôts et la production de crédits.
*   **Classement des agences** : Classement des 10 agences selon la rentabilité commerciale (Dépôts + Crédits).

#### D. Risques
*   **Nombre de crédits NPL** : Nombre de dossiers de crédit classés en créance douteuse ou compromise (Non-Performing Loans).
*   **Taux NPL** : Ratio financier mesurant la qualité du portefeuille crédit ($\text{Encours NPL} / \text{Encours total de crédits}$).
*   **Encours douteux** : Montant financier brut des crédits classés en souffrance (impayés de plus de 90 jours).
*   **Axes d'analyse (dimensions de croisement)** :
    *   Secteur d'activité de l'entreprise.
    *   Géographie : Région, Agence.
    *   Commercial : Conseiller Entreprises.
    *   Segment de l'entreprise.

#### E. Digital Banking
*   **Canaux suivis** : DabaPay Pro, BusinessOnline.ma, CreditBusinessOnline, WhatsApp Business, KODI.
*   **Taux d'adoption** : Pourcentage d'entreprises équipées d'au moins un service digital ($\text{Entreprises connectées} / \text{Total entreprises}$).
*   **Nombre d'utilisateurs actifs** : Nombre d'entreprises s'étant connectées à l'un des services au moins une fois par mois.
*   **Nombre de connexions** : Volume cumulé des connexions aux différentes plateformes sur le trimestre.
*   **Nombre d'opérations réalisées** : Nombre de transactions initiées via les canaux digitaux (virements initiés, demandes de crédit en ligne soumises, etc.).
*   **Évolution trimestrielle de l'utilisation** : Taux de croissance des connexions et des opérations d'un trimestre sur l'autre.
*   **Axes d'analyse (dimensions de croisement)** : Région, Agence, Segment client (TPE/PME/GE).

#### F. Intelligence Artificielle (Clustering)
*   **Nombre de clusters** : Nombre optimal de groupes d'entreprises identifiés par le modèle K-Means.
*   **Taille de chaque cluster** : Nombre d'entreprises affectées à chaque segment IA.
*   **Répartition des entreprises** : Proportion de TPE/PME/GE par cluster.
*   **Profil moyen des clusters** : Valeurs moyennes des attributs clés (chiffre d'affaires moyen, encours de dépôts moyen, encours de crédits moyen, taux d'adoption digital moyen) pour chaque groupe.
*   **Répartition des risques par cluster** : Taux NPL moyen au sein de chaque groupe.
*   **Adoption des services digitaux par cluster** : Taux d'adoption moyen des services digitaux pour chaque groupe.

---

### 4. Profils Utilisateurs & Cas d'Usage

Les besoins d'information de la banque sont structurés selon 6 profils utilisateurs distincts :

| Profil | Objectifs stratégiques / opérationnels | Indicateurs clés consultés | Tableaux de bord accessibles |
| :--- | :--- | :--- | :--- |
| **1. Directeur Général (DG)** | - Suivre la santé financière globale de la banque<br>- Évaluer les grandes tendances de collecte et d'octroi | - Encours global Dépôts/Crédits<br>- Taux NPL global<br>- Taux d'adoption digital de la banque | - Dashboard Stratégique Général<br>- Dashboard Risques consolidés |
| **2. Directeur Régional** | - Suivre les performances de son territoire<br>- Identifier les agences sous-performantes | - Collecte nette par agence<br>- Production de crédit de la région<br>- Taux NPL régional | - Dashboard Performance Régionale & Agences<br>- Dashboard Digitalisation Régionale |
| **3. Directeur d'Agence** | - Manager son équipe de conseillers<br>- Assurer la rentabilité de l'agence | - Encours par conseiller<br>- Classement de son agence<br>- Alertes sur les dossiers à risque localement | - Dashboard Performance Agence<br>- Dashboard Dépôts/Crédits de l'agence |
| **4. Conseiller Entreprises**| - Gérer et fidéliser son portefeuille de clients<br>- Développer sa production commerciale | - Collecte nette de son portefeuille<br>- Taux d'équipement digital de ses clients<br>- Encours douteux par client | - Dashboard Portefeuille Conseiller<br>- Vue détaillée par Entreprise |
| **5. Analyste Risques** | - Minimiser les pertes sur créances<br>- Suivre la qualité des garanties | - Taux NPL sectoriel et régional<br>- Montant des encours douteux<br>- Taux de couverture des garanties | - Dashboard Risques & NPL<br>- Dashboard IA (Segments de risque) |
| **6. Analyste BI** | - Assurer la maintenance et la justesse des calculs<br>- Fournir des analyses ponctuelles | - Métadonnées d'exécution ETL<br>- Volumétrie des tables<br>- Ratios de cohérence inter-systèmes | - Dashboard Technique / Métadonnées<br>- Accès total aux Data Marts |

---

### 5. Historique, Fréquence et Analyses Temporelles

#### A. Historique de Simulation
Le jeu de données simulé couvrira une période de **3 années complètes** :
*   **Date de début** : 01/01/2022
*   **Date de fin** : 31/12/2024
Les transactions financières, les contrats de crédits et les historiques de connexions digitales seront distribués de manière continue sur cet horizon temporel.

#### B. Fréquence des Données
*   **Alimentation (ETL)** : Les données opérationnelles de la base PostgreSQL OLTP seront extraites et chargées dans le Data Warehouse via un traitement **batch quotidien**.
*   **Restitution** : Bien que la base soit mise à jour quotidiennement, l'analyse stratégique sera configurée pour des restitutions consolidées de niveau **trimestriel** et **annuel**.

#### C. Spécifications Temporelles (Hiérarchie de Temps)
Pour permettre des comparaisons temporelles et des calculs d'évolution (Time Intelligence), la table `Dim_Temps` du Data Warehouse devra obligatoirement contenir les attributs suivants :
1.  **Date** : Clé primaire (format DATE ou ID AAAAMMJJ).
2.  **Mois** : Nom et numéro du mois (ex. "Janvier", 1).
3.  **Trimestre** : Libellé standardisé (T1, T2, T3, T4).
4.  **Numéro de trimestre** : Valeur numérique (1, 2, 3, 4).
5.  **Libellé du trimestre** : Format texte simple pour l'affichage (ex. "Trimestre 1").
6.  **Année** : Valeur numérique (ex. 2023).
7.  **Année-Trimestre** : Concaténation standardisée pour les tris chronologiques (ex. "2023-T1").

---

### 6. Cohérence avec les Livrables Futurs

Ce cahier des charges constitue la référence fonctionnelle obligatoire pour toute la suite du projet.
*   **Modèles de données (MCD/MLD/MPD)** : Ils devront intégrer les entités nécessaires pour capturer tous les attributs requis pour les calculs de KPIs (ex: types de crédits, flags d'activité de comptes, canaux digitaux).
*   **Architecture Décisionnelle (DWH / Data Marts)** : Le schéma en étoile devra comporter des dimensions conformes aux axes d'analyse exigés, et des tables de faits capables de calculer les mesures de dépôts, de crédits, de transactions, de risques et de digitalisation.
*   **Visualisation (Power BI)** : Les pages de tableaux de bord refléteront directement la structure des domaines de KPIs (Dépôts, Crédits, Performance, Risque, Digitalisation, IA) et s'adapteront aux profils de sécurité requis pour chaque type d'utilisateur.
