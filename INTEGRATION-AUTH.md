# Intégration Django + Next.js - Authentification

Ce projet intègre un backend Django avec un frontend Next.js pour l'authentification des utilisateurs.

## 🏗️ Architecture

```
├── back-end/                 # Backend Django
│   ├── dip_backend/         # Configuration Django
│   ├── authentication/     # App d'authentification
│   └── requirements.txt     # Dépendances Python
├── dip-frontend/            # Frontend Next.js
│   ├── src/
│   │   ├── services/       # Services d'authentification
│   │   ├── contexts/       # Contexte React
│   │   ├── components/     # Composants d'auth
│   │   └── app/           # Pages Next.js
│   └── package.json        # Dépendances Node.js
└── test-integration.js     # Script de test
```

## 🚀 Démarrage rapide

### 1. Backend Django

```bash
cd back-end

# Créer l'environnement virtuel
python3 -m venv env
source env/bin/activate  # Sur Windows: env\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
cp env.example .env
# Éditer .env avec vos paramètres de base de données

# Appliquer les migrations
python manage.py makemigrations authentication
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver 8001
```

### 2. Frontend Next.js

```bash
cd dip-frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm run dev
```

### 3. Test de l'intégration

```bash
# Depuis la racine du projet
node test-integration.js
```

## 🔐 Fonctionnalités d'authentification

### Backend Django (Port 8001)

- **Inscription** : `POST /api/auth/register/`
- **Connexion** : `POST /api/auth/login/`
- **Profil** : `GET/PUT /api/auth/profile/`
- **Détails profil** : `GET/PUT /api/auth/profile/details/`
- **Changement mot de passe** : `POST /api/auth/change-password/`
- **Rafraîchissement token** : `POST /api/auth/token/refresh/`
- **Déconnexion** : `POST /api/auth/logout/`
- **Historique connexions** : `GET /api/auth/login-history/`

### Frontend Next.js (Port 3000)

- **Pages d'authentification** : `/auth/login`, `/auth/register`
- **Tableau de bord** : `/dashboard` (protégé)
- **Paramètres** : `/settings` (protégé)
- **Navigation avec auth** : Composant `AuthNavbar`
- **Protection des routes** : Composant `ProtectedRoute`

## 🛡️ Sécurité

- **JWT Tokens** : Authentification par tokens JWT
- **CORS** : Configuration CORS pour le frontend
- **Validation** : Validation des mots de passe côté serveur
- **Sessions** : Gestion des sessions utilisateur
- **Permissions** : Système de rôles (admin, user, guest)

## 📱 Utilisation

### Connexion
1. Aller sur `http://localhost:3000/auth/login`
2. Utiliser les identifiants de test ou créer un compte
3. Redirection automatique vers le tableau de bord

### Compte de test
- **Email** : `admin@dip.com`
- **Mot de passe** : `admin123`

### Navigation
- Le menu de navigation s'adapte selon le rôle utilisateur
- Les routes sont protégées automatiquement
- Déconnexion disponible dans le menu utilisateur

## 🔧 Configuration

### Variables d'environnement

**Backend (.env)** :
```
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_NAME=ma_base_dip
DATABASE_USER=postgres
DATABASE_PASSWORD=admin
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

**Frontend** :
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api/auth
```

## 🧪 Tests

Le script `test-integration.js` teste tous les endpoints d'authentification :

```bash
node test-integration.js
```

## 📝 Notes importantes

- **Base de données** : Le backend utilise la base PostgreSQL existante
- **Données** : Les données du site ne sont pas modifiées, seule l'authentification est ajoutée
- **Compatibilité** : Compatible avec l'architecture existante
- **Sécurité** : Tokens JWT avec expiration automatique

## 🆘 Dépannage

### Erreur de connexion
- Vérifier que le serveur Django est démarré sur le port 8001
- Vérifier la configuration CORS dans `settings.py`
- Vérifier les variables d'environnement

### Erreur de base de données
- Vérifier que PostgreSQL est démarré
- Vérifier les paramètres de connexion dans `.env`
- Appliquer les migrations : `python manage.py migrate`

### Erreur frontend
- Vérifier que Next.js est démarré sur le port 3000
- Vérifier la variable `NEXT_PUBLIC_API_URL`
- Vérifier les dépendances : `npm install`

