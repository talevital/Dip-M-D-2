#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration complète
"""

import requests
import json
import time

def test_integration():
    """Test de l'intégration complète"""
    
    # URL de l'API ETL
    base_url = "http://localhost:8000"
    
    print("🧪 Test de l'intégration complète...")
    
    # 1. Vérifier que l'API ETL est accessible
    try:
        response = requests.get(f"{base_url}/files")
        if response.status_code == 200:
            print("✅ API ETL accessible")
            files = response.json()
            if files.get('items'):
                file_id = files['items'][0]['id']
                print(f"📁 Fichier de test trouvé: ID {file_id}")
                
                # 2. Tester l'endpoint de transformation
                transform_config = {
                    "processing_mode": "hybrid",
                    "missing_strategy": "mean",
                    "handle_outliers": True,
                    "outliers_method": "winsorize",
                    "outlier_detection": "iqr",
                    "remove_duplicates": True,
                    "fix_inconsistencies": True,
                    "normalize_numerical": True,
                    "numerical_method": "standard",
                    "encode_categorical": True,
                    "categorical_method": "label",
                    "normalize_dates": True,
                    "extract_date_features": True
                }
                
                print("🔄 Test de la transformation...")
                transform_response = requests.post(
                    f"{base_url}/files/{file_id}/transform",
                    json={"options": transform_config},
                    headers={"Content-Type": "application/json"}
                )
                
                if transform_response.status_code == 200:
                    result = transform_response.json()
                    print("✅ Transformation réussie!")
                    print(f"📊 Résultats:")
                    print(f"   - Shape original: {result['original_shape']}")
                    print(f"   - Shape traité: {result['processed_shape']}")
                    print(f"   - Outliers détectés: {result['summary']['outliers_detected']}")
                    print(f"   - Mode de traitement: {result['summary']['processing_mode']}")
                    print(f"   - Fichier de sortie: {result['output_path']}")
                    
                    return True
                else:
                    print(f"❌ Erreur de transformation: {transform_response.status_code}")
                    print(f"   Détails: {transform_response.text}")
                    return False
            else:
                print("⚠️  Aucun fichier trouvé pour le test")
                return False
        else:
            print(f"❌ API ETL non accessible: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API ETL")
        print("   Assurez-vous que l'API ETL est démarrée sur le port 8000")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    if success:
        print("\n🎉 Test d'intégration réussi!")
        print("   Votre système de traitement automatique est opérationnel!")
    else:
        print("\n💥 Test d'intégration échoué!")
        print("   Vérifiez les logs pour plus de détails.")