# -*- coding: utf-8 -*-
import psycopg2
import os
import re

# Lire .env manuellement pour éviter les dépendances externes
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
env_vars = {}
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env_vars[key.strip()] = val.strip()

host = env_vars.get("DB_HOST", "localhost")
port = env_vars.get("DB_PORT", "5432")
dbname = env_vars.get("DB_DATABASE", "pfe_boa_db")
user = env_vars.get("DB_USER", "postgres")
password = env_vars.get("DB_PASSWORD", "admin")

conn_str = f"host={host} port={port} dbname={dbname} user={user} password={password}"

# Mot de passe par défaut : admin123 (Hachage bcrypt pré-calculé)
DEFAULT_HASH = "$2b$12$cspWO0yynSZZeMqocQIxz.kDp8FyTCUX4Yfk18Wypy5zqGGnam8N."

def clean_username(name: str) -> str:
    """Nettoie une chaîne pour en faire un nom d'utilisateur valide."""
    name = name.lower()
    # Supprimer les accents
    name = re.sub(r'[àáâãäå]', 'a', name)
    name = re.sub(r'[èéêë]', 'e', name)
    name = re.sub(r'[ìíîï]', 'i', name)
    name = re.sub(r'[òóôõö]', 'o', name)
    name = re.sub(r'[ùúûü]', 'u', name)
    name = re.sub(r'[ç]', 'c', name)
    # Remplacer tout caractère non-alphanumérique par un tiret bas
    name = re.sub(r'[^a-z0-9_]', '_', name)
    # Supprimer les tirets bas consécutifs
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

try:
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    
    print("Vidage préalable des données d'authentification...")
    cursor.execute("TRUNCATE TABLE oltp.role_permissions CASCADE;")
    cursor.execute("TRUNCATE TABLE oltp.utilisateurs CASCADE;")
    cursor.execute("TRUNCATE TABLE oltp.permissions CASCADE;")
    cursor.execute("TRUNCATE TABLE oltp.roles CASCADE;")
    conn.commit()

    # 1. Insertion des Permissions
    permissions = [
        ("VIEW_DASHBOARD", "Acces au tableau de bord principal consolidé"),
        ("VIEW_CREDITS", "Consultation des Data Marts credits et NPL"),
        ("VIEW_DEPOTS", "Consultation des Data Marts depots et DAT"),
        ("VIEW_REPORTS", "Acces aux rapports standard"),
        ("EXPORT_REPORTS", "Droit de telechargement des rapports PDF/Excel"),
        ("USE_DECISION_ASSISTANT", "Utilisation de l'AI Decision Assistant"),
        ("VIEW_AUDIT", "Consultation de la journalisation d'audit"),
        ("ADMIN_SYSTEM", "Administration des utilisateurs et des permissions")
    ]
    
    perm_ids = {}
    for code, desc in permissions:
        cursor.execute(
            "INSERT INTO oltp.permissions (code_permission, description) VALUES (%s, %s) RETURNING id_permission;",
            (code, desc)
        )
        perm_ids[code] = cursor.fetchone()[0]
        
    print(f"{len(permissions)} permissions insérées.")

    # 2. Insertion des Rôles
    roles = [
        ("ADMINISTRATEUR", "Administrateur"),
        ("DIRECTEUR_GENERAL", "Directeur Général"),
        ("DIRECTEUR_REGIONAL", "Directeur Régional"),
        ("DIRECTEUR_AGENCE", "Directeur d'Agence")
    ]
    
    role_ids = {}
    for code, nom in roles:
        cursor.execute(
            "INSERT INTO oltp.roles (code_role, nom_role) VALUES (%s, %s) RETURNING id_role;",
            (code, nom)
        )
        role_ids[code] = cursor.fetchone()[0]
        
    print(f"{len(roles)} rôles insérés.")

    # 3. Association Rôles-Permissions
    role_perms = {
        "ADMINISTRATEUR": [
            "VIEW_DASHBOARD", "VIEW_CREDITS", "VIEW_DEPOTS", "VIEW_REPORTS", 
            "EXPORT_REPORTS", "USE_DECISION_ASSISTANT", "VIEW_AUDIT", "ADMIN_SYSTEM"
        ],
        "DIRECTEUR_GENERAL": [
            "VIEW_DASHBOARD", "VIEW_CREDITS", "VIEW_DEPOTS", "VIEW_REPORTS", 
            "EXPORT_REPORTS", "USE_DECISION_ASSISTANT"
        ],
        "DIRECTEUR_REGIONAL": [
            "VIEW_DASHBOARD", "VIEW_CREDITS", "VIEW_DEPOTS", "VIEW_REPORTS", 
            "EXPORT_REPORTS", "USE_DECISION_ASSISTANT"
        ],
        "DIRECTEUR_AGENCE": [
            "VIEW_DASHBOARD", "VIEW_CREDITS", "VIEW_DEPOTS", "VIEW_REPORTS", 
            "USE_DECISION_ASSISTANT"
        ]
    }
    
    for r_code, p_list in role_perms.items():
        r_id = role_ids[r_code]
        for p_code in p_list:
            p_id = perm_ids[p_code]
            cursor.execute(
                "INSERT INTO oltp.role_permissions (id_role, id_permission) VALUES (%s, %s);",
                (r_id, p_id)
            )
            
    print("Liaisons Rôles-Permissions créées.")

    # 4. Insertion des Utilisateurs
    
    # A. Administrateur (compte technique non rattaché)
    cursor.execute(
        """
        INSERT INTO oltp.utilisateurs (username, email, password_hash, id_role, nom, prenom, telephone_professionnel)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """,
        ("admin", "admin@boa.ma", DEFAULT_HASH, role_ids["ADMINISTRATEUR"], "Système", "Admin", "+212522000000")
    )
    print("Compte Administrateur 'admin' créé.")

    # B. Directeur Général
    cursor.execute("SELECT id_employe, nom, prenom, email_professionnel, telephone FROM oltp.employes WHERE fonction = 'Directeur Général' LIMIT 1;")
    dg_emp = cursor.fetchone()
    if dg_emp:
        emp_id, nom, prenom, email, tel = dg_emp
        cursor.execute(
            """
            INSERT INTO oltp.utilisateurs (username, email, password_hash, id_role, id_employe, nom, prenom, telephone_professionnel)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            ("dg_boa", email, DEFAULT_HASH, role_ids["DIRECTEUR_GENERAL"], emp_id, nom, prenom, tel)
        )
        print("Compte Directeur Général 'dg_boa' créé (lié à l'employé).")
    else:
        print("Avertissement: Aucun employé de fonction 'Directeur Général' trouvé.")

    # C. Directeurs Régionaux
    cursor.execute("SELECT id_region, nom_region FROM oltp.regions;")
    regions_list = cursor.fetchall()
    
    # Mapping des usernames par région
    region_mapping = {
        "Casablanca-Settat": "casablanca",
        "Rabat-Salé-Kénitra": "rabat",
        "Fès-Meknès": "fes",
        "Marrakech-Safi": "marrakech",
        "Tanger-Tétouan-Al Hoceïma": "tanger",
        "Oriental": "oriental",
        "Sud": "agadir"
    }
    
    for id_reg, nom_reg in regions_list:
        sub_name = region_mapping.get(nom_reg, clean_username(nom_reg))
        username = f"dr_{sub_name}"
        
        # Trouver l'employé correspondant
        cursor.execute(
            "SELECT id_employe, nom, prenom, email_professionnel, telephone FROM oltp.employes WHERE fonction = 'Directeur Régional' AND id_region = %s LIMIT 1;",
            (id_reg,)
        )
        emp = cursor.fetchone()
        if emp:
            emp_id, nom, prenom, email, tel = emp
            cursor.execute(
                """
                INSERT INTO oltp.utilisateurs (username, email, password_hash, id_role, id_employe, id_region, nom, prenom, telephone_professionnel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (username, email, DEFAULT_HASH, role_ids["DIRECTEUR_REGIONAL"], emp_id, id_reg, nom, prenom, tel)
            )
            print(f"Compte DR '{username}' créé (lié à l'employé).")
        else:
            print(f"Avertissement: Aucun Directeur Régional trouvé en base pour la région {nom_reg} (ID: {id_reg}).")

    # D. Directeurs d'Agence
    cursor.execute("SELECT id_agence, nom_agence FROM oltp.agences;")
    agences_list = cursor.fetchall()
    
    for id_ag, nom_ag in agences_list:
        # Nettoyer le nom de l'agence pour faire un username
        clean_ag_name = clean_username(nom_ag.replace("BOA", "").replace("Agence", ""))
        username = f"da_{clean_ag_name}"
        
        # Trouver l'employé correspondant
        cursor.execute(
            "SELECT id_employe, nom, prenom, email_professionnel, telephone FROM oltp.employes WHERE fonction = 'Directeur d''Agence' AND id_agence = %s LIMIT 1;",
            (id_ag,)
        )
        emp = cursor.fetchone()
        if emp:
            emp_id, nom, prenom, email, tel = emp
            cursor.execute(
                """
                INSERT INTO oltp.utilisateurs (username, email, password_hash, id_role, id_employe, id_agence, nom, prenom, telephone_professionnel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (username, email, DEFAULT_HASH, role_ids["DIRECTEUR_AGENCE"], emp_id, id_ag, nom, prenom, tel)
            )
            print(f"Compte DA '{username}' créé (lié à l'employé).")
        else:
            print(f"Avertissement: Aucun Directeur d'Agence trouvé en base pour l'agence {nom_ag} (ID: {id_ag}).")

    conn.commit()
    print("\nInitialisation des données de test d'authentification terminée avec succès !")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Erreur durant l'initialisation : {e}")
