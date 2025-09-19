# 🚀 Plateforme DIP - Guide de démarrage unifié

## 🎯 Démarrage rapide

### Option 1 : Tout en un (recommandé)
```bash
./start_unified.sh
```
Démarre automatiquement :
- ✅ Serveur FastAPI unifié (authentification + ETL)
- ✅ Frontend Next.js
- ✅ Accès complet à la plateforme

### Option 2 : Serveur API seulement
```bash
./start_api.sh
```
Démarre uniquement le serveur FastAPI unifié.

## 🔗 Accès aux services

Une fois démarré, accédez à :

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur complète |
| **API FastAPI** | http://localhost:8000 | API backend unifiée |
| **Documentation** | http://localhost:8000/docs | Documentation interactive de l'API |

## 🔐 Connexion

**Identifiants par défaut :**
- **Email :** `admin@dip.com`
- **Mot de passe :** `admin123`

## 📁 Fonctionnalités ETL

| Page | URL | Description |
|------|-----|-------------|
| **Dashboard** | http://localhost:3000 | Vue d'ensemble |
| **Fichiers** | http://localhost:3000/etl/files | Liste des fichiers uploadés |
| **Upload** | http://localhost:3000/etl/upload | Upload de nouveaux fichiers |
| **Dataviz** | http://localhost:3000/dataviz | Visualisations |

## 🛠️ Commandes manuelles

Si vous préférez démarrer manuellement :

### Serveur FastAPI unifié
```bash
cd etl_project
source venv/bin/activate
uvicorn api.main_integrated:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Next.js
```bash
cd dip-frontend
npm run dev
```

## 🔧 Résolution de problèmes

### Problème : "Aucun fichier uploadé"
**Solution :** Connectez-vous d'abord via http://localhost:3000/auth/login

### Problème : Erreur 403 Forbidden
**Solution :** Vérifiez que vous êtes connecté avec un token valide

### Problème : Serveur ne démarre pas
**Solution :** Vérifiez que les ports 3000 et 8000 sont libres

## 📊 Test de l'API

Testez directement l'API avec curl :
```bash
# Connexion
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@dip.com", "password": "admin123"}'

# Liste des fichiers (avec token)
curl -X GET "http://localhost:8000/files" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎉 C'est tout !

Votre plateforme DIP est maintenant unifiée et prête à l'emploi !


