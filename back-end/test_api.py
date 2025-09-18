#!/usr/bin/env python3
"""
Script de test pour l'API Django DIP
Teste tous les endpoints d'authentification
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api/auth"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def print_response(title, response):
    """Affiche la réponse de manière formatée"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    """Teste tous les endpoints de l'API"""
    
    print("🚀 Test de l'API Django DIP - Authentification")
    print("="*60)
    
    # 1. Test d'inscription d'un nouvel utilisateur
    print("\n1️⃣ Test d'inscription d'un nouvel utilisateur")
    registration_data = {
        "email": "test@dip.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPassword123!",
        "password_confirm": "TestPassword123!",
        "phone": "+225 0123456789",
        "organization": "DIP Test Organization",
        "role": "user"
    }
    
    response = requests.post(f"{BASE_URL}/register/", 
                           headers=HEADERS, 
                           json=registration_data)
    print_response("Inscription utilisateur", response)
    
    if response.status_code == 201:
        user_data = response.json()
        access_token = user_data.get('access')
        refresh_token = user_data.get('refresh')
        print(f"✅ Utilisateur créé avec succès!")
        print(f"🔑 Access Token: {access_token[:50]}...")
        print(f"🔄 Refresh Token: {refresh_token[:50]}...")
    else:
        print("❌ Échec de l'inscription")
        return
    
    # 2. Test de connexion
    print("\n2️⃣ Test de connexion")
    login_data = {
        "email": "test@dip.com",
        "password": "TestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/login/", 
                           headers=HEADERS, 
                           json=login_data)
    print_response("Connexion utilisateur", response)
    
    if response.status_code == 200:
        login_data = response.json()
        access_token = login_data.get('access')
        refresh_token = login_data.get('refresh')
        print(f"✅ Connexion réussie!")
        print(f"🔑 Access Token: {access_token[:50]}...")
    else:
        print("❌ Échec de la connexion")
        return
    
    # Headers avec authentification
    auth_headers = HEADERS.copy()
    auth_headers['Authorization'] = f'Bearer {access_token}'
    
    # 3. Test de récupération du profil
    print("\n3️⃣ Test de récupération du profil")
    response = requests.get(f"{BASE_URL}/profile/", headers=auth_headers)
    print_response("Profil utilisateur", response)
    
    # 4. Test de mise à jour du profil
    print("\n4️⃣ Test de mise à jour du profil")
    update_data = {
        "first_name": "Test Updated",
        "last_name": "User Updated",
        "phone": "+225 0987654321",
        "organization": "DIP Updated Organization"
    }
    
    response = requests.put(f"{BASE_URL}/profile/update/", 
                          headers=auth_headers, 
                          json=update_data)
    print_response("Mise à jour profil", response)
    
    # 5. Test de récupération des détails du profil
    print("\n5️⃣ Test de récupération des détails du profil")
    response = requests.get(f"{BASE_URL}/profile/details/", headers=auth_headers)
    print_response("Détails profil", response)
    
    # 6. Test de mise à jour des détails du profil
    print("\n6️⃣ Test de mise à jour des détails du profil")
    profile_update_data = {
        "language": "fr",
        "timezone": "Africa/Abidjan",
        "currency": "XOF",
        "theme": "dark",
        "email_notifications": True,
        "weekly_reports": True,
        "monthly_reports": False
    }
    
    response = requests.put(f"{BASE_URL}/profile/details/update/", 
                          headers=auth_headers, 
                          json=profile_update_data)
    print_response("Mise à jour détails profil", response)
    
    # 7. Test de changement de mot de passe
    print("\n7️⃣ Test de changement de mot de passe")
    password_data = {
        "current_password": "TestPassword123!",
        "new_password": "NewTestPassword123!",
        "new_password_confirm": "NewTestPassword123!"
    }
    
    response = requests.post(f"{BASE_URL}/change-password/", 
                          headers=auth_headers, 
                          json=password_data)
    print_response("Changement de mot de passe", response)
    
    # 8. Test de rafraîchissement du token
    print("\n8️⃣ Test de rafraîchissement du token")
    refresh_data = {
        "refresh": refresh_token
    }
    
    response = requests.post(f"{BASE_URL}/token/refresh/", 
                          headers=HEADERS, 
                          json=refresh_data)
    print_response("Rafraîchissement token", response)
    
    if response.status_code == 200:
        new_tokens = response.json()
        new_access_token = new_tokens.get('access')
        print(f"✅ Token rafraîchi avec succès!")
        print(f"🔑 Nouveau Access Token: {new_access_token[:50]}...")
        
        # Mettre à jour les headers avec le nouveau token
        auth_headers['Authorization'] = f'Bearer {new_access_token}'
    
    # 9. Test de récupération de l'historique des connexions
    print("\n9️⃣ Test de récupération de l'historique des connexions")
    response = requests.get(f"{BASE_URL}/login-history/", headers=auth_headers)
    print_response("Historique des connexions", response)
    
    # 10. Test de déconnexion
    print("\n🔟 Test de déconnexion")
    logout_data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(f"{BASE_URL}/logout/", 
                          headers=auth_headers, 
                          json=logout_data)
    print_response("Déconnexion", response)
    
    # 11. Test avec des données invalides
    print("\n1️⃣1️⃣ Test avec des données invalides")
    invalid_login_data = {
        "email": "test@dip.com",
        "password": "WrongPassword"
    }
    
    response = requests.post(f"{BASE_URL}/login/", 
                          headers=HEADERS, 
                          json=invalid_login_data)
    print_response("Connexion avec mot de passe incorrect", response)
    
    print("\n" + "="*60)
    print("🎉 Tests terminés!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Assurez-vous que le serveur Django est démarré sur le port 8001.")
        print("💡 Commande: python manage.py runserver 0.0.0.0:8001")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        sys.exit(1)
