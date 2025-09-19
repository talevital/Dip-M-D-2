"""
Application FastAPI pour l'authentification
Migration depuis Django vers FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from loguru import logger

# Imports locaux
from auth.models import User, UserProfile, LoginAttempt
from auth.schemas import (
    UserCreate, UserLogin, UserResponse, UserProfileResponse, 
    UserProfileUpdate, Token, LoginAttemptResponse, ChangePasswordRequest
)
from auth.database import get_db, create_tables
from auth.auth import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, verify_token, get_client_ip
)

# Configuration de sécurité
security = HTTPBearer()

# Application FastAPI
app = FastAPI(
    title="DIP Authentication API",
    description="API d'authentification pour le système DIP",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dépendances d'authentification
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """Obtenir l'utilisateur actuel à partir du token JWT"""
    token_data = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtenir l'utilisateur actuel actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Endpoints d'authentification
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    try:
        # Vérifier si l'utilisateur existe déjà
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Créer l'utilisateur
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Créer le profil utilisateur
        profile = UserProfile(user_id=db_user.id)
        db.add(profile)
        db.commit()
        
        logger.info(f"New user registered: {user.email}")
        return db_user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@app.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Connexion utilisateur"""
    try:
        # Trouver l'utilisateur par email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            # Enregistrer la tentative échouée
            client_ip = get_client_ip(request)
            login_attempt = LoginAttempt(
                email=user_credentials.email,
                ip_address=client_ip,
                success=False,
                failure_reason="Invalid credentials"
            )
            db.add(login_attempt)
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Enregistrer la tentative réussie
        client_ip = get_client_ip(request)
        login_attempt = LoginAttempt(
            user_id=user.id,
            email=user_credentials.email,
            ip_address=client_ip,
            success=True
        )
        db.add(login_attempt)
        db.commit()
        
        # Générer les tokens
        access_token = create_access_token(data={"user_id": user.id})
        refresh_token = create_refresh_token(data={"user_id": user.id})
        
        logger.info(f"User logged in: {user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@app.post("/refresh", response_model=Token)
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Rafraîchir le token d'accès"""
    try:
        token_data = verify_token(refresh_token, "refresh")
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Générer un nouveau token d'accès
        access_token = create_access_token(data={"user_id": user.id})
        new_refresh_token = create_refresh_token(data={"user_id": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Récupérer le profil utilisateur"""
    return current_user

@app.get("/profile/details", response_model=UserProfileResponse)
def get_user_profile_details(
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """Récupérer les détails du profil utilisateur"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@app.put("/profile/details", response_model=UserProfileResponse)
def update_user_profile_details(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mettre à jour les détails du profil utilisateur"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Mettre à jour seulement les champs fournis
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    
    return profile

@app.get("/login-history", response_model=List[LoginAttemptResponse])
def get_login_history(
    current_user: User = Depends(get_current_active_user), 
    db: Session = Depends(get_db)
):
    """Récupérer l'historique des connexions"""
    attempts = db.query(LoginAttempt).filter(
        LoginAttempt.user_id == current_user.id
    ).order_by(LoginAttempt.attempted_at.desc()).limit(50).all()
    
    return attempts

@app.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Changer le mot de passe"""
    # Vérifier le mot de passe actuel
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Mettre à jour le mot de passe
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

@app.post("/logout")
def logout_user(current_user: User = Depends(get_current_active_user)):
    """Déconnexion utilisateur (côté client)"""
    return {"message": "Logged out successfully"}

# Endpoints d'administration (admin seulement)
@app.get("/users", response_model=List[UserResponse])
def list_users(
    limit: int = 50, 
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Liste des utilisateurs (admin seulement)"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(offset).limit(limit).all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Détails d'un utilisateur (admin seulement)"""
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

# Créer les tables au démarrage
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("Authentication API started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


