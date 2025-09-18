# Backend Django - DIP (Dashboard d'Intelligence Publique)

## Description

Backend Django avec authentification par mot de passe pour le système DIP. Ce backend fournit une API REST complète pour la gestion des utilisateurs et l'authentification.

## Fonctionnalités

- ✅ **Authentification par mot de passe** avec JWT
- ✅ **Inscription et connexion** des utilisateurs
- ✅ **Gestion des profils** utilisateur
- ✅ **Système de rôles** (admin, user, guest)
- ✅ **Tracking des connexions** et sécurité
- ✅ **API REST** complète
- ✅ **Interface d'administration** Django
- ✅ **CORS configuré** pour le frontend Next.js

## Installation

1. **Activer l'environnement virtuel** :
```bash
source ../env/bin/activate
```

2. **Installer les dépendances** :
```bash
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement** :
```bash
cp env.example .env
# Éditer le fichier .env avec vos paramètres
```

4. **Appliquer les migrations** :
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Créer un superutilisateur** :
```bash
python manage.py createsuperuser
```

6. **Démarrer le serveur** :
```bash
python manage.py runserver
```

## Configuration de la base de données

Le backend utilise votre base PostgreSQL existante (`ma_base_dip`). Les tables Django seront créées dans cette base de données.

## Endpoints API

### Authentification
- `POST /api/auth/register/` - Inscription d'un nouvel utilisateur
- `POST /api/auth/login/` - Connexion (obtention des tokens JWT)
- `POST /api/auth/logout/` - Déconnexion
- `POST /api/auth/token/refresh/` - Rafraîchissement du token

### Profil utilisateur
- `GET /api/auth/profile/` - Récupérer le profil de l'utilisateur connecté
- `PUT /api/auth/profile/update/` - Mettre à jour le profil
- `GET /api/auth/profile/details/` - Détails du profil
- `PUT /api/auth/profile/details/update/` - Mettre à jour les détails

### Sécurité
- `POST /api/auth/change-password/` - Changer le mot de passe
- `GET /api/auth/login-history/` - Historique des connexions

### Administration (admin seulement)
- `GET /api/auth/users/` - Liste des utilisateurs
- `GET /api/auth/users/{id}/` - Détails d'un utilisateur

## Modèles de données

### User
- Modèle utilisateur personnalisé basé sur AbstractUser
- Champs : email, username, first_name, last_name, role, phone, organization
- Rôles : admin, user, guest

### UserProfile
- Profil étendu avec préférences utilisateur
- Champs : bio, avatar, language, timezone, currency, theme, notifications

### LoginAttempt
- Tracking des tentatives de connexion pour la sécurité
- Champs : user, email, ip_address, success, failure_reason, attempted_at

## Sécurité

- **JWT tokens** avec expiration configurable
- **Validation des mots de passe** avec les validators Django
- **Tracking des connexions** avec adresse IP
- **Protection CORS** configurée
- **Permissions** basées sur les rôles

## Interface d'administration

Accédez à l'interface d'administration Django à l'adresse :
`http://localhost:8000/admin/`

## Intégration avec le frontend

Le backend est configuré pour fonctionner avec votre frontend Next.js :
- CORS activé pour `http://localhost:3000`
- Tokens JWT pour l'authentification
- API REST compatible avec les services frontend existants

## Variables d'environnement

```env
# Base de données
DB_NAME=ma_base_dip
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

