#!/usr/bin/env python3
"""
Test de l'API avec les nouvelles fonctionnalités de traitement textuel
"""

import requests
import json
import time

def test_text_processing_api():
    """Test de l'API avec traitement textuel"""
    
    # Attendre que le serveur soit prêt
    print("Attente du serveur...")
    time.sleep(3)
    
    # URL de base
    base_url = "http://127.0.0.1:8000"
    
    try:
        # Créer des données de test
        test_data = {
            "nom": ["Jean Dupont", "Marie Martin", "Pierre Durand", "Sophie Bernard"],
            "description": [
                "Développeur senior avec 10 ans d'expérience en Python et JavaScript",
                "Data scientist spécialisée en machine learning et analyse de données", 
                "Chef de projet agile avec expertise en gestion d'équipe",
                "UX/UI designer créative avec portfolio impressionnant"
            ],
            "pays": ["France", "france", "FRANCE", "Allemagne"],
            "statut": ["actif", "Actif", "ACTIF", "inactif"]
        }
        
        # Créer un fichier CSV temporaire
        import pandas as pd
        import tempfile
        import os
        
        df = pd.DataFrame(test_data)
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        print(f"Fichier de test créé: {temp_file.name}")
        
        # Upload du fichier
        with open(temp_file.name, 'rb') as f:
            files = {'file': ('test_text.csv', f, 'text/csv')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code != 200:
            print(f"Erreur upload: {response.status_code} - {response.text}")
            return
        
        upload_data = response.json()
        file_id = upload_data['file_id']
        print(f"Fichier uploadé avec ID: {file_id}")
        
        # Test de transformation avec traitement textuel
        transform_options = {
            "missing_strategy": "fill",
            "handle_outliers": True,
            "remove_duplicates": True,
            "fix_inconsistencies": True,
            "numerical_method": "standard",
            "categorical_method": "label",
            "normalize_dates": True,
            "text_processing_enabled": True,
            "text_columns": ["nom", "description"],
            "extract_text_features": True,
            "extract_keywords": True,
            "detect_topics": True,
            "multiple_choice_enabled": True,
            "multiple_choice_columns": {
                "statut": ["actif", "inactif", "suspendu"],
                "pays": ["France", "Allemagne", "Espagne"]
            },
            "multiple_choice_threshold": 0.8
        }
        
        print("Test de transformation avec traitement textuel...")
        response = requests.post(
            f"{base_url}/files/{file_id}/transform-preview",
            json={"options": transform_options}
        )
        
        if response.status_code != 200:
            print(f"Erreur transformation: {response.status_code} - {response.text}")
            return
        
        transform_data = response.json()
        print("✅ Transformation réussie!")
        
        # Afficher les résultats
        print(f"\nMétadonnées: {transform_data['metadata']['row_count']} lignes, {transform_data['metadata']['col_count']} colonnes")
        
        if 'keywords' in transform_data and transform_data['keywords']:
            print("\nMots-clés extraits:")
            for col, keywords in transform_data['keywords'].items():
                print(f"  {col}: {keywords[:5]}")
        
        if 'topics' in transform_data and transform_data['topics']:
            print("\nTopics détectés:")
            for col, topics in transform_data['topics'].items():
                print(f"  {col}: {topics[:3]}")
        
        # Nettoyer
        os.unlink(temp_file.name)
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_text_processing_api()















