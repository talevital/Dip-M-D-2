#!/usr/bin/env python3
"""
Script de test rapide pour vérifier le tableau de bord avec des données réelles
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"

def test_dashboard_with_real_data():
    """Test du tableau de bord avec des données réelles"""
    print("🧪 Test du tableau de bord avec des données réelles...")
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{API_BASE}/docs")
        if response.status_code != 200:
            print("❌ L'API n'est pas accessible")
            return False
    except:
        print("❌ Impossible de se connecter à l'API")
        return False
    
    print("✅ API accessible")
    
    # Upload du fichier de test
    try:
        with open("test_data.csv", "rb") as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            response = requests.post(f"{API_BASE}/api/advanced/upload-advanced", files=files)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ Fichier uploadé avec succès (Session: {session_id})")
            print(f"   - Lignes: {result['data_shape'][0]}")
            print(f"   - Colonnes: {result['data_shape'][1]}")
            print(f"   - Inconsistances: {result['inconsistencies_count']}")
        else:
            print(f"❌ Erreur upload: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'upload: {e}")
        return False
    
    # Tester les analytics
    try:
        response = requests.get(f"{API_BASE}/api/advanced/analytics/{session_id}")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Analytics récupérées")
            
            if 'statistics' in analytics:
                print(f"   - Variables numériques: {len(analytics['statistics'])}")
                for col, stats in analytics['statistics'].items():
                    print(f"     * {col}: Moyenne={stats['mean']:.2f}, Min={stats['min']:.2f}, Max={stats['max']:.2f}")
            
            if 'insights' in analytics:
                insights = analytics['insights']
                print(f"   - Qualité des données: {insights.get('data_quality', {}).get('quality_score', 'N/A')}")
        else:
            print(f"❌ Erreur analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur analytics: {e}")
    
    # Tester la création d'un graphique
    try:
        chart_config = {
            'type': 'line',
            'x_col': 'Mois',
            'y_cols': ['Valeur_USD'],
            'title': 'Évolution des Valeurs USD par Mois'
        }
        
        response = requests.post(
            f"{API_BASE}/api/advanced/create-chart/{session_id}",
            json=chart_config
        )
        
        if response.status_code == 200:
            chart_result = response.json()
            print(f"✅ Graphique créé: {chart_result['title']}")
            print(f"   - Type: {chart_result['chart_type']}")
            print(f"   - ID: {chart_result['chart_id']}")
        else:
            print(f"❌ Erreur création graphique: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur création graphique: {e}")
    
    print("\n🎉 Test terminé !")
    print("📊 Accédez au tableau de bord: http://localhost:3000/dataviz")
    print("   - Onglet 'Tableau de bord' pour voir les métriques réelles")
    print("   - Onglet 'Graphiques' pour créer des visualisations")
    print("   - Onglet 'Analytics' pour les analyses avancées")
    
    return True

if __name__ == "__main__":
    test_dashboard_with_real_data()

