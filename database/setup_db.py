# -*- coding: utf-8 -*-
"""
Nom du fichier : database/setup_db.py
Description     : Script d'initialisation de la base de données, des schémas et des tables DDL.
"""

import pg8000
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def run_sql_file(conn, file_path):
    print(f"Executing: {file_path.name} ...")
    with open(file_path, "r", encoding="utf-8") as f:
        sql = f.read()
    
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        # Ignore errors if tables or schemas already exist, but print other errors
        err_msg = str(e)
        if "déjà" not in err_msg and "already exists" not in err_msg:
            print(f"Error in {file_path.name}: {err_msg}")
    cursor.close()

def setup():
    # 1. Connect to postgres default DB to create pfe_boa_db
    print("Connecting to default postgres database...")
    try:
        conn = pg8000.connect(
            user="postgres",
            password="admin",
            host="localhost",
            port=5432,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'pfe_boa_db'")
        if not cursor.fetchone():
            print("Creating database pfe_boa_db...")
            cursor.execute("CREATE DATABASE pfe_boa_db;")
        else:
            print("Database pfe_boa_db already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during database creation phase: {str(e)}")
        return

    # 2. Connect to pfe_boa_db to run schemas and DDLs
    print("Connecting to pfe_boa_db...")
    try:
        conn = pg8000.connect(
            user="postgres",
            password="admin",
            host="localhost",
            port=5432,
            database="pfe_boa_db"
        )
        conn.autocommit = True # autocommit is safer for running DDL script batches
        
        # Run schemas
        schemas_path = BASE_DIR / "database" / "schemas"
        run_sql_file(conn, schemas_path / "01_create_schemas.sql")
        run_sql_file(conn, schemas_path / "02_create_extensions.sql")
        
        # Run DDLs
        ddl_path = BASE_DIR / "database" / "ddl"
        ddl_files = sorted(ddl_path.glob("*.sql"))
        for ddl_file in ddl_files:
            run_sql_file(conn, ddl_file)
            
        print("Database schemas and DDL tables created successfully!")
        conn.close()
    except Exception as e:
        print(f"Error during table creation phase: {str(e)}")

if __name__ == "__main__":
    setup()
