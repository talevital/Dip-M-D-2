"""
Configuration de la base de données pour l'authentification FastAPI
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.models import Base

# Configuration de la base de données
DATABASE_URL = os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth.db")

# Créer le moteur de base de données
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Créer la session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)


