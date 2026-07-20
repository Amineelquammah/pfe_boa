# -*- coding: utf-8 -*-
"""
Nom du fichier : data_generation/utils/database.py
Description     : Initialisation du moteur SQLAlchemy et de la session de base de données.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from data_generation.config.config import DATABASE_URL

# Initialisation du moteur de base de données PostgreSQL
# Configuration d'un pool de connexions robuste pour le bulk loading
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

# Session thread-safe pour les générateurs et le loader
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_connection():
    """
    Retourne une connexion brute pour les écritures rapides.
    """
    return engine.connect()
