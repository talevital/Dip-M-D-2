"""
Modèles SQLAlchemy pour l'authentification FastAPI
Migration depuis Django vers FastAPI
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relations
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    login_attempts = relationship("LoginAttempt", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    role = Column(String(10), default="user")  # admin, user, guest
    phone = Column(String(20), nullable=True)
    organization = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    language = Column(String(5), default="fr")
    timezone = Column(String(50), default="Africa/Abidjan")
    currency = Column(String(3), default="XOF")
    theme = Column(String(10), default="light")
    
    # Préférences de notification
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=False)
    weekly_reports = Column(Boolean, default=True)
    monthly_reports = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="profile")

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    email = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)
    success = Column(Boolean, default=False)
    failure_reason = Column(String(255), nullable=True)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="login_attempts")


