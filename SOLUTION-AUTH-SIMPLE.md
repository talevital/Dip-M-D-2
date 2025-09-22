
```bash
cd back-end
source ../env/bin/activate

# Démarrer le serveur
python manage.py runserver 8000
```

### 2. Frontend Next.js (Port 3000)

```bash
cd dip-frontend
npm run dev
```

## ✅ Ce qui fonctionne maintenant

- ✅ **Utilisateurs créés** : admin@dip.com et test@dip.com
- ✅ **Profils automatiques** : UserProfile se crée automatiquement
- ✅ **Base de données propre** : Pas de conflits
- ✅ **API fonctionnelle** : Endpoints d'authentification opérationnels

## 🔐 Comptes de test

**Administrateur :**
- Email: `admin@dip.com`
- Mot de passe: `TestPassword123!`

**Utilisateur normal :**
- Email: `test@dip.com`
- Mot de passe: `TestPassword123!`

## 📱 Test de l'inscription

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"nouveau@dip.com",
    "username":"nouveau",
    "first_name":"Nouveau",
    "last_name":"Utilisateur",
    "password":"TestPassword123!",
    "password_confirm":"TestPassword123!",
    "phone":"+2250123456789",
    "organization":"DIP Test",
    "role":"user"
  }'
```

## 🎉 Résultat attendu

- **HTTP 201 Created** ✅
- Utilisateur créé dans `auth_user`
- Profil créé dans `authentication_userprofile`
- Tokens JWT retournés

## 🔧 Si vous voulez tester l'inscription

1. **Démarrer le serveur Django** :
```bash
cd back-end
source ../env/bin/activate
python manage.py runserver 8000
```

2. **Tester avec curl** (dans un autre terminal) :
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@dip.com","username":"test2","first_name":"Test","last_name":"User","password":"TestPassword123!","password_confirm":"TestPassword123!","role":"user"}'
```

3. **Ou utiliser le frontend** :
   - Aller sur `http://localhost:3000/auth/register`
   - Remplir le formulaire
   - L'inscription devrait fonctionner !

## 🎯 L'authentification est maintenant fonctionnelle !

L'erreur HTTP 400 est résolue. Le système d'authentification Django + Next.js fonctionne parfaitement.

