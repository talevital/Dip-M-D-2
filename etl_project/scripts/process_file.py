#!/usr/bin/env python3
"""
Script Python pour traiter les fichiers avec le HybridDataProcessor
Appelé depuis l'API Next.js
"""

import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Ajouter le chemin du projet ETL
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from etl.transform.hybrid_processor import HybridDataProcessor, process_file_hybrid
except ImportError as e:
    print(f"Erreur d'import: {e}", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python process_file.py <file_path> <config_json>'
        }))
        sys.exit(1)
    
    file_path = sys.argv[1]
    config_json = sys.argv[2]
    
    try:
        # Parser la configuration
        config = json.loads(config_json)
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            print(json.dumps({
                'success': False,
                'error': f'Fichier non trouvé: {file_path}'
            }))
            sys.exit(1)
        
        # Charger les données
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            print(json.dumps({
                'success': False,
                'error': 'Format de fichier non supporté'
            }))
            sys.exit(1)
        
        # Initialiser le processeur hybride
        processor = HybridDataProcessor()
        
        # Traitement des données
        processed_df = processor.process_data_hybrid(df, config)
        
        # Générer le rapport de traitement
        report = processor.get_processing_report()
        
        # Sauvegarder les données traitées
        output_dir = '/tmp/processed_data'
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_id = os.path.basename(file_path).split('.')[0]
        output_path = os.path.join(output_dir, f'processed_{file_id}_{timestamp}.csv')
        
        processed_df.to_csv(output_path, index=False)
        
        # Fonction pour convertir les types numpy en types Python natifs
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        # Retourner les résultats
        result = {
            'success': True,
            'original_shape': list(df.shape),
            'processed_shape': list(processed_df.shape),
            'processing_report': convert_numpy_types(report),
            'outlier_stats': convert_numpy_types(processor.outlier_stats),
            'output_path': output_path,
            'processed_at': datetime.now().isoformat(),
            'summary': {
                'rows_processed': int(len(processed_df)),
                'columns_processed': int(len(processed_df.columns)),
                'outliers_detected': int(sum(len(stats.get('iqr', {}).get('outliers', [])) for stats in processor.outlier_stats.values())),
                'processing_mode': config.get('processing_mode', 'automatic')
            }
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': f'Erreur lors du traitement: {str(e)}'
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
