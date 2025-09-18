#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

from api.db import get_session
from api.models import UploadedFile
from api.parsers import detect_type, read_preview
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from utils.helpers import DataProfiler
from loguru import logger

def test_etl_pipeline(file_id: int):
    """Test the ETL pipeline for a specific file"""
    try:
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                print(f"File {file_id} not found")
                return
            
            if not os.path.exists(uf.stored_path):
                print(f"File {uf.stored_path} not found")
                return
            
            print(f"Testing ETL for file: {uf.original_name}")
            print(f"Path: {uf.stored_path}")
            
            # Initialize ETL components
            cleaner = DataCleaner()
            normalizer = DataNormalizer()
            enricher = DataEnricher()
            profiler = DataProfiler()
            
            # Read original file
            ftype = detect_type(uf.original_name, uf.content_type)
            print(f"Detected type: {ftype}")
            
            df_original = read_preview(uf.stored_path, ftype)
            print(f"Original data shape: {df_original.shape}")
            print(f"Original columns: {list(df_original.columns)}")
            
            # Profile original data
            profile_original = profiler.profile_dataframe(df_original)
            print("Original profiling completed")
            
            # Apply ETL transformations
            print("Starting cleaning...")
            df_cleaned = cleaner.clean_data(
                df_original,
                missing_strategy='fill',
                remove_duplicates=True,
                handle_outliers=True,
                fix_inconsistencies=True
            )
            print(f"Cleaning completed: {len(df_original)} -> {len(df_cleaned)} rows")
            
            print("Starting normalization...")
            df_normalized = normalizer.normalize_data(
                df_cleaned,
                numerical_method='standard',
                categorical_method='label',
                normalize_dates=True
            )
            print(f"Normalization completed: {len(df_normalized.columns)} columns")
            
            print("Starting enrichment...")
            # Apply enrichment with default transformations
            conditions = {}
            if 'pib_millions' in df_normalized.columns and 'population_millions' in df_normalized.columns:
                conditions['pib_par_habitant'] = lambda df: df['pib_millions'] / df['population_millions']
            if 'export_millions' in df_normalized.columns and 'import_millions' in df_normalized.columns:
                conditions['balance_commerciale'] = lambda df: df['export_millions'] - df['import_millions']
            
            aggregations = None
            if len(df_normalized.select_dtypes(include=['number']).columns) > 0:
                group_col = 'pays' if 'pays' in df_normalized.columns else df_normalized.columns[0]
                num_cols = df_normalized.select_dtypes(include=['number']).columns[:3]
                if len(num_cols) > 0:
                    aggregations = {
                        'group_by': group_col,
                        'aggregations': {col: ['mean', 'sum'] for col in num_cols},
                        'prefix': 'agg'
                    }
            
            time_features = None
            if 'date_creation' in df_normalized.columns:
                time_features = {
                    'date_column': 'date_creation',
                    'features': ['year', 'month', 'quarter', 'is_weekend']
                }
            
            df_enriched = enricher.enrich_data(
                df_normalized,
                conditional_columns=conditions,
                aggregations=aggregations,
                time_features=time_features
            )
            print(f"Enrichment completed: {len(df_normalized.columns)} -> {len(df_enriched.columns)} columns")
            
            # Profile final data
            profile_final = profiler.profile_dataframe(df_enriched)
            print("Final profiling completed")
            
            # Save transformed data
            output_dir = os.path.join(os.path.dirname(uf.stored_path), "..", "transformed")
            os.makedirs(output_dir, exist_ok=True)
            
            output_filename = f"transformed_{uf.original_name}"
            output_path = os.path.join(output_dir, output_filename)
            df_enriched.to_csv(output_path, index=False)
            print(f"Data saved to: {output_path}")
            
            print("ETL pipeline completed successfully!")
            
    except Exception as e:
        print(f"Error in ETL pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_id = int(sys.argv[1])
        test_etl_pipeline(file_id)
    else:
        print("Usage: python test_etl.py <file_id>")
















