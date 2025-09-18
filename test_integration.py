#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration complète des fonctionnalités avancées
"""

import requests
import json
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

# Configuration
API_BASE = "http://127.0.0.1:8000"
TEST_DATA_SIZE = 100

def create_test_data():
    """Crée des données de test pour les tests"""
    np.random.seed(42)
    
    data = {
        'date': pd.date_range('2023-01-01', periods=TEST_DATA_SIZE, freq='D'),
        'sales': np.random.randint(1000, 5000, TEST_DATA_SIZE),
        'profit': np.random.randint(100, 1000, TEST_DATA_SIZE),
        'category': np.random.choice(['A', 'B', 'C', 'D'], TEST_DATA_SIZE),
        'region': np.random.choice(['North', 'South', 'East', 'West'], TEST_DATA_SIZE),
        'temperature': np.random.normal(20, 5, TEST_DATA_SIZE),
        'humidity': np.random.normal(60, 10, TEST_DATA_SIZE)
    }
    
    df = pd.DataFrame(data)
    
    # Ajouter quelques inconsistances pour tester la détection
    df.loc[10:15, 'sales'] = df.loc[10:15, 'sales'].astype(str) + ',00'  # Format avec virgule
    df.loc[20:25, 'date'] = df.loc[20:25, 'date'].dt.strftime('%d/%m/%Y')  # Format de date différent
    
    return df

def test_upload_advanced():
    """Test de l'upload avancé"""
    print("🧪 Test de l'upload avancé...")
    
    # Créer des données de test
    df = create_test_data()
    
    # Sauvegarder en CSV temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_file = f.name
    
    try:
        # Upload du fichier
        with open(temp_file, 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            response = requests.post(f"{API_BASE}/api/advanced/upload-advanced", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload réussi: {result['message']}")
            print(f"   - Inconsistances détectées: {result['inconsistencies_count']}")
            print(f"   - Session ID: {result['session_id']}")
            return result['session_id']
        else:
            print(f"❌ Erreur upload: {response.status_code} - {response.text}")
            return None
            
    finally:
        # Nettoyer le fichier temporaire
        os.unlink(temp_file)

def test_analytics(session_id):
    """Test des analytics avancées"""
    print(f"🧪 Test des analytics pour la session {session_id}...")
    
    response = requests.get(f"{API_BASE}/api/advanced/analytics/{session_id}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Analytics récupérées avec succès")
        
        if 'statistics' in result:
            print(f"   - Variables numériques: {len(result['statistics'])}")
        
        if 'insights' in result:
            insights = result['insights']
            print(f"   - Qualité des données: {insights.get('data_quality', {}).get('quality_score', 'N/A')}")
        
        return True
    else:
        print(f"❌ Erreur analytics: {response.status_code} - {response.text}")
        return False

def test_chart_creation(session_id):
    """Test de création de graphiques"""
    print(f"🧪 Test de création de graphiques pour la session {session_id}...")
    
    # Test création d'un graphique en ligne
    chart_config = {
        'type': 'line',
        'x_col': 'date',
        'y_cols': ['sales', 'profit'],
        'title': 'Évolution des Ventes et Profits'
    }
    
    response = requests.post(
        f"{API_BASE}/api/advanced/create-chart/{session_id}",
        json=chart_config
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Graphique créé: {result['title']}")
        print(f"   - Type: {result['chart_type']}")
        print(f"   - ID: {result['chart_id']}")
        return result['chart_id']
    else:
        print(f"❌ Erreur création graphique: {response.status_code} - {response.text}")
        return None

def test_chart_list(session_id):
    """Test de la liste des graphiques"""
    print(f"🧪 Test de la liste des graphiques pour la session {session_id}...")
    
    response = requests.get(f"{API_BASE}/api/advanced/charts/{session_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Liste des graphiques récupérée: {result['total']} graphiques")
        
        for chart in result['charts']:
            print(f"   - {chart['title']} ({chart['chart_type']})")
        
        return True
    else:
        print(f"❌ Erreur liste graphiques: {response.status_code} - {response.text}")
        return False

def test_recommendations(session_id):
    """Test des recommandations"""
    print(f"🧪 Test des recommandations pour la session {session_id}...")
    
    response = requests.get(f"{API_BASE}/api/advanced/recommendations/{session_id}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Recommandations générées: {result['total']} suggestions")
        
        for rec in result['recommendations']:
            print(f"   - {rec['title']}: {rec['description']}")
        
        return True
    else:
        print(f"❌ Erreur recommandations: {response.status_code} - {response.text}")
        return False

def test_session_info(session_id):
    """Test des informations de session"""
    print(f"🧪 Test des informations de session {session_id}...")
    
    response = requests.get(f"{API_BASE}/api/advanced/session/{session_id}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Informations de session récupérées")
        print(f"   - Shape des données: {result['data_shape']}")
        print(f"   - Nombre de graphiques: {result['charts_count']}")
        print(f"   - Corrections appliquées: {result['corrections_applied']}")
        return True
    else:
        print(f"❌ Erreur informations session: {response.status_code} - {response.text}")
        return False

def test_api_health():
    """Test de santé de l'API"""
    print("🧪 Test de santé de l'API...")
    
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code == 200:
            print("✅ API accessible et documentation disponible")
            return True
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'intégration des fonctionnalités avancées")
    print("=" * 70)
    
    # Test de santé de l'API
    if not test_api_health():
        print("\n❌ L'API n'est pas accessible. Vérifiez qu'elle est démarrée sur le port 8000.")
        return
    
    print("\n" + "=" * 70)
    
    # Test d'upload
    session_id = test_upload_advanced()
    if not session_id:
        print("\n❌ Échec du test d'upload. Arrêt des tests.")
        return
    
    print("\n" + "=" * 70)
    
    # Tests des fonctionnalités avancées
    tests = [
        (test_analytics, session_id),
        (test_chart_creation, session_id),
        (test_chart_list, session_id),
        (test_recommendations, session_id),
        (test_session_info, session_id)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func, *args in tests:
        try:
            if test_func(*args):
                passed += 1
        except Exception as e:
            print(f"❌ Erreur lors du test {test_func.__name__}: {e}")
        print()
    
    print("=" * 70)
    print(f"📊 Résultats des tests: {passed}/{total} réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'intégration est complète.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
    
    print("\n🔗 Accédez à la page Dataviz: http://localhost:3000/dataviz")
    print("📚 Documentation API: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()

