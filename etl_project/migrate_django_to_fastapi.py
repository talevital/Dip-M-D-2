"""
Script de migration des données Django vers FastAPI
Migration des utilisateurs et profils depuis Django vers SQLAlchemy
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
sys.path.append('/Users/angevitaloura/Documents/GitHub/Dip-M-D-2/back-end')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dip_backend.settings')
django.setup()

from django.contrib.auth.models import User as DjangoUser
from authentication.models import UserProfile as DjangoProfile, LoginAttempt as DjangoLoginAttempt

# Configuration FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth.models import User, UserProfile, LoginAttempt, Base
from auth.auth import get_password_hash

# Configuration de la base de données FastAPI
DATABASE_URL = "sqlite:///./auth_migrated.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def migrate_users():
    """Migrer les utilisateurs Django vers FastAPI"""
    db = SessionLocal()
    try:
        print("🔄 Début de la migration des utilisateurs...")
        
        # Migrer les utilisateurs Django
        django_users = DjangoUser.objects.all()
        migrated_count = 0
        
        for django_user in django_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = db.query(User).filter(User.email == django_user.email).first()
            if existing_user:
                print(f"⚠️  Utilisateur {django_user.email} déjà migré, ignoré")
                continue
            
            # Créer l'utilisateur FastAPI
            fastapi_user = User(
                id=django_user.id,
                username=django_user.username,
                email=django_user.email,
                first_name=django_user.first_name,
                last_name=django_user.last_name,
                hashed_password=django_user.password,  # Django utilise déjà bcrypt
                is_active=django_user.is_active,
                is_staff=django_user.is_staff,
                is_superuser=django_user.is_superuser,
                created_at=django_user.date_joined,
                last_login=django_user.last_login
            )
            
            db.add(fastapi_user)
            migrated_count += 1
            
            # Migrer le profil si il existe
            try:
                django_profile = DjangoProfile.objects.get(user=django_user)
                fastapi_profile = UserProfile(
                    user_id=django_user.id,
                    role=django_profile.role,
                    phone=django_profile.phone,
                    organization=django_profile.organization,
                    bio=django_profile.bio,
                    avatar=str(django_profile.avatar) if django_profile.avatar else None,
                    language=django_profile.language,
                    timezone=django_profile.timezone,
                    currency=django_profile.currency,
                    theme=django_profile.theme,
                    email_notifications=django_profile.email_notifications,
                    push_notifications=django_profile.push_notifications,
                    weekly_reports=django_profile.weekly_reports,
                    monthly_reports=django_profile.monthly_reports,
                    created_at=django_profile.created_at,
                    updated_at=django_profile.updated_at
                )
                db.add(fastapi_profile)
                print(f"✅ Profil migré pour {django_user.email}")
            except DjangoProfile.DoesNotExist:
                # Créer un profil par défaut
                fastapi_profile = UserProfile(user_id=django_user.id)
                db.add(fastapi_profile)
                print(f"📝 Profil par défaut créé pour {django_user.email}")
        
        db.commit()
        print(f"✅ Migration terminée: {migrated_count} utilisateurs migrés avec succès!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la migration: {e}")
        raise
    finally:
        db.close()

def migrate_login_attempts():
    """Migrer les tentatives de connexion Django vers FastAPI"""
    db = SessionLocal()
    try:
        print("🔄 Début de la migration des tentatives de connexion...")
        
        django_attempts = DjangoLoginAttempt.objects.all()
        migrated_count = 0
        
        for django_attempt in django_attempts:
            # Vérifier si la tentative existe déjà
            existing_attempt = db.query(LoginAttempt).filter(
                LoginAttempt.email == django_attempt.email,
                LoginAttempt.attempted_at == django_attempt.attempted_at
            ).first()
            
            if existing_attempt:
                continue
            
            fastapi_attempt = LoginAttempt(
                user_id=django_attempt.user.id if django_attempt.user else None,
                email=django_attempt.email,
                ip_address=django_attempt.ip_address,
                success=django_attempt.success,
                failure_reason=django_attempt.failure_reason,
                attempted_at=django_attempt.attempted_at
            )
            
            db.add(fastapi_attempt)
            migrated_count += 1
        
        db.commit()
        print(f"✅ Migration terminée: {migrated_count} tentatives de connexion migrées!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la migration des tentatives: {e}")
        raise
    finally:
        db.close()

def verify_migration():
    """Vérifier la migration"""
    db = SessionLocal()
    try:
        print("🔍 Vérification de la migration...")
        
        # Compter les utilisateurs
        fastapi_users = db.query(User).count()
        django_users = DjangoUser.objects.count()
        
        print(f"📊 Utilisateurs Django: {django_users}")
        print(f"📊 Utilisateurs FastAPI: {fastapi_users}")
        
        # Compter les profils
        fastapi_profiles = db.query(UserProfile).count()
        django_profiles = DjangoProfile.objects.count()
        
        print(f"📊 Profils Django: {django_profiles}")
        print(f"📊 Profils FastAPI: {fastapi_profiles}")
        
        # Compter les tentatives de connexion
        fastapi_attempts = db.query(LoginAttempt).count()
        django_attempts = DjangoLoginAttempt.objects.count()
        
        print(f"📊 Tentatives Django: {django_attempts}")
        print(f"📊 Tentatives FastAPI: {fastapi_attempts}")
        
        if fastapi_users == django_users:
            print("✅ Migration des utilisateurs réussie!")
        else:
            print("⚠️  Nombre d'utilisateurs différent")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
    finally:
        db.close()

def create_test_user():
    """Créer un utilisateur de test pour vérifier le système"""
    db = SessionLocal()
    try:
        print("🧪 Création d'un utilisateur de test...")
        
        # Vérifier si l'utilisateur test existe déjà
        test_user = db.query(User).filter(User.email == "test@dip.com").first()
        if test_user:
            print("⚠️  Utilisateur test déjà existant")
            return
        
        # Créer l'utilisateur test
        test_user = User(
            username="testuser",
            email="test@dip.com",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("testpassword123"),
            is_active=True,
            is_verified=True,
            is_staff=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Créer le profil test
        test_profile = UserProfile(
            user_id=test_user.id,
            role="admin",
            organization="DIP Test Organization",
            language="fr",
            timezone="Africa/Abidjan"
        )
        
        db.add(test_profile)
        db.commit()
        
        print(f"✅ Utilisateur test créé: {test_user.email}")
        print(f"   ID: {test_user.id}")
        print(f"   Username: {test_user.username}")
        print(f"   Password: testpassword123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création de l'utilisateur test: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Début de la migration Django → FastAPI")
    print("=" * 50)
    
    try:
        # Migrer les utilisateurs
        migrate_users()
        print()
        
        # Migrer les tentatives de connexion
        migrate_login_attempts()
        print()
        
        # Vérifier la migration
        verify_migration()
        print()
        
        # Créer un utilisateur de test
        create_test_user()
        print()
        
        print("🎉 Migration terminée avec succès!")
        print("=" * 50)
        print("📝 Prochaines étapes:")
        print("1. Tester l'API d'authentification FastAPI")
        print("2. Mettre à jour le frontend")
        print("3. Supprimer Django une fois tout testé")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)


