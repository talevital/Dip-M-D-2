"""
Schémas Pydantic pour l'authentification FastAPI
Validation et sérialisation des données
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_staff: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    role: str
    phone: Optional[str] = None
    organization: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    language: str
    timezone: str
    currency: str
    theme: str
    email_notifications: bool
    push_notifications: bool
    weekly_reports: bool
    monthly_reports: bool
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    role: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    currency: Optional[str] = None
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    weekly_reports: Optional[bool] = None
    monthly_reports: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

class LoginAttemptResponse(BaseModel):
    id: int
    email: str
    ip_address: Optional[str] = None
    success: bool
    failure_reason: Optional[str] = None
    attempted_at: datetime
    
    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


