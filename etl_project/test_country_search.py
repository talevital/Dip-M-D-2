#!/usr/bin/env python3
"""
Script de test pour l'endpoint de recherche de pays
"""

import asyncio
import httpx
import json

async def test_country_search():
    """Test de l'endpoint de recherche de pays"""
    
    # URL de base de l'API
    base_url = "http://localhost:8000"
    
    # Tests à effectuer
    test_cases = [
        {"query": "France", "description": "Recherche par nom de pays"},
        {"query": "FR", "description": "Recherche par code pays"},
        {"query": "Senegal", "description": "Recherche pays africain"},
        {"query": "United States", "description": "Recherche pays avec espaces"},
    ]
    
    print("🧪 Test de l'endpoint de recherche de pays")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['description']}")
            print(f"🔍 Recherche: '{test_case['query']}'")
            
            try:
                # Test de l'endpoint de recherche unique
                response = await client.get(
                    f"{base_url}/search/country",
                    params={"q": test_case["query"]},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        country = data.get("country", {})
                        print(f"✅ Succès!")
                        print(f"   📍 Pays: {country.get('name', 'N/A')}")
                        print(f"   🗺️  Coordonnées: {country.get('lat', 'N/A')}, {country.get('lon', 'N/A')}")
                        print(f"   🆔 Place ID: {country.get('place_id', 'N/A')}")
                    else:
                        print(f"❌ Échec: {data.get('detail', 'Erreur inconnue')}")
                else:
                    print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                    
            except httpx.TimeoutException:
                print("⏰ Timeout - Le serveur met trop de temps à répondre")
            except httpx.ConnectError:
                print("🔌 Erreur de connexion - Le serveur n'est pas démarré")
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

async def test_multiple_countries():
    """Test de l'endpoint de recherche multiple"""
    
    print("\n🔍 Test de recherche multiple de pays")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{base_url}/search/countries",
                params={"q": "africa", "limit": 3},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    countries = data.get("countries", [])
                    print(f"✅ Trouvé {len(countries)} pays pour 'africa':")
                    for country in countries:
                        print(f"   📍 {country.get('name', 'N/A')}")
                else:
                    print(f"❌ Échec: {data.get('detail', 'Erreur inconnue')}")
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de l'API de recherche de pays")
    print("⚠️  Assurez-vous que le serveur API est démarré sur http://localhost:8000")
    print()
    
    # Exécuter les tests
    asyncio.run(test_country_search())
    asyncio.run(test_multiple_countries())




