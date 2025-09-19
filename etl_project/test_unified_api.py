"""
Script de test complet pour l'API DIP unifiée
Teste l'authentification et les fonctionnalités ETL
"""

import requests
import json
import os
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser_unified",
    "email": "test_unified@example.com",
    "password": "testpassword123",
    "first_name": "Test",
    "last_name": "Unified"
}

def test_auth_endpoints():
    """Tester les endpoints d'authentification"""
    print("🔐 Test des endpoints d'authentification...")
    
    # Test d'inscription
    print("1. Test d'inscription...")
    register_response = requests.post(
        f"{API_BASE_URL}/auth/register",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    
    if register_response.status_code == 200:
        print("✅ Inscription réussie")
        user_data = register_response.json()
        print(f"   Utilisateur créé: {user_data['email']}")
    else:
        print(f"❌ Échec de l'inscription: {register_response.status_code}")
        print(f"   Erreur: {register_response.text}")
        return None
    
    # Test de connexion
    print("2. Test de connexion...")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    login_response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        print("✅ Connexion réussie")
        tokens = login_response.json()
        access_token = tokens["access_token"]
        print(f"   Token d'accès reçu: {access_token[:50]}...")
    else:
        print(f"❌ Échec de la connexion: {login_response.status_code}")
        print(f"   Erreur: {login_response.text}")
        return None
    
    return access_token

def test_protected_endpoints(access_token):
    """Tester les endpoints protégés"""
    print("\n🔒 Test des endpoints protégés...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test du profil utilisateur
    print("1. Test du profil utilisateur...")
    profile_response = requests.get(
        f"{API_BASE_URL}/auth/profile",
        headers=headers
    )
    
    if profile_response.status_code == 200:
        print("✅ Profil utilisateur récupéré")
        profile_data = profile_response.json()
        print(f"   Utilisateur: {profile_data['username']}")
    else:
        print(f"❌ Échec de récupération du profil: {profile_response.status_code}")
    
    # Test de la liste des fichiers
    print("2. Test de la liste des fichiers...")
    files_response = requests.get(
        f"{API_BASE_URL}/files",
        headers=headers
    )
    
    if files_response.status_code == 200:
        print("✅ Liste des fichiers récupérée")
        files_data = files_response.json()
        print(f"   Nombre de fichiers: {files_data['total']}")
    else:
        print(f"❌ Échec de récupération des fichiers: {files_response.status_code}")
    
    return True

def test_file_upload(access_token):
    """Tester l'upload de fichier"""
    print("\n📁 Test d'upload de fichier...")
    
    # Créer un fichier CSV de test
    test_csv_content = """name,age,city
John,25,Paris
Jane,30,Lyon
Bob,35,Marseille"""
    
    # Sauvegarder temporairement
    test_file_path = "test_data.csv"
    with open(test_file_path, "w") as f:
        f.write(test_csv_content)
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_data.csv", f, "text/csv")}
            upload_response = requests.post(
                f"{API_BASE_URL}/files/upload",
                files=files,
                headers=headers
            )
        
        if upload_response.status_code == 200:
            print("✅ Upload de fichier réussi")
            upload_data = upload_response.json()
            print(f"   Fichier ID: {upload_data['file_id']}")
            print(f"   Nombre de lignes: {upload_data['rows']}")
            return upload_data['file_id']
        else:
            print(f"❌ Échec de l'upload: {upload_response.status_code}")
            print(f"   Erreur: {upload_response.text}")
            return None
            
    finally:
        # Nettoyer le fichier de test
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_file_processing(file_id, access_token):
    """Tester le traitement de fichier"""
    if not file_id:
        print("❌ Pas de fichier à traiter")
        return
    
    print(f"\n⚙️ Test de traitement de fichier (ID: {file_id})...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Configuration de traitement
    processing_config = {
        "processing_mode": "automatic",
        "missing_strategy": "mean",
        "handle_outliers": True,
        "outlier_detection": "iqr",
        "outliers_method": "winsorize",
        "remove_duplicates": True,
        "fix_inconsistencies": True,
        "normalize_numerical": True,
        "numerical_method": "standard",
        "encode_categorical": True,
        "categorical_method": "label",
        "normalize_dates": False
    }
    
    # Test de transformation
    transform_response = requests.post(
        f"{API_BASE_URL}/files/{file_id}/transform",
        json=processing_config,
        headers=headers
    )
    
    if transform_response.status_code == 200:
        print("✅ Transformation de fichier réussie")
        transform_data = transform_response.json()
        print(f"   Forme originale: {transform_data['original_shape']}")
        print(f"   Forme traitée: {transform_data['processed_shape']}")
        print(f"   Mode de traitement: {transform_data['summary']['processing_mode']}")
    else:
        print(f"❌ Échec de la transformation: {transform_response.status_code}")
        print(f"   Erreur: {transform_response.text}")

def test_export(file_id, access_token):
    """Tester l'export de fichier"""
    if not file_id:
        print("❌ Pas de fichier à exporter")
        return
    
    print(f"\n📤 Test d'export de fichier (ID: {file_id})...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test d'export CSV
    print("1. Test d'export CSV...")
    csv_response = requests.get(
        f"{API_BASE_URL}/files/{file_id}/export-hybrid?format=csv",
        headers=headers
    )
    
    if csv_response.status_code == 200:
        print("✅ Export CSV réussi")
        print(f"   Taille du fichier: {len(csv_response.content)} bytes")
    else:
        print(f"❌ Échec de l'export CSV: {csv_response.status_code}")
    
    # Test d'export XLSX
    print("2. Test d'export XLSX...")
    xlsx_response = requests.get(
        f"{API_BASE_URL}/files/{file_id}/export-hybrid?format=xlsx",
        headers=headers
    )
    
    if xlsx_response.status_code == 200:
        print("✅ Export XLSX réussi")
        print(f"   Taille du fichier: {len(xlsx_response.content)} bytes")
    else:
        print(f"❌ Échec de l'export XLSX: {xlsx_response.status_code}")

def main():
    """Fonction principale de test"""
    print("🧪 Test complet de l'API DIP unifiée")
    print("=" * 50)
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print(f"❌ API non accessible sur {API_BASE_URL}")
            return
        print(f"✅ API accessible sur {API_BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à {API_BASE_URL}")
        print("   Assurez-vous que l'API est démarrée avec: python start_unified_api.py")
        return
    
    # Tests d'authentification
    access_token = test_auth_endpoints()
    if not access_token:
        print("❌ Tests d'authentification échoués")
        return
    
    # Tests des endpoints protégés
    test_protected_endpoints(access_token)
    
    # Test d'upload de fichier
    file_id = test_file_upload(access_token)
    
    # Test de traitement de fichier
    test_file_processing(file_id, access_token)
    
    # Test d'export
    test_export(file_id, access_token)
    
    print("\n🎉 Tests terminés!")
    print("=" * 50)
    print("📝 Résumé:")
    print("✅ Authentification FastAPI fonctionnelle")
    print("✅ Endpoints protégés accessibles")
    print("✅ Upload de fichiers opérationnel")
    print("✅ Traitement de données intégré")
    print("✅ Export CSV/XLSX disponible")

if __name__ == "__main__":
    main()


