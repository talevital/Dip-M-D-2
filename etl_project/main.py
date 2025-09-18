import pandas as pd
import numpy as np
from etl.extract.csv_extractor import CSVExtractor
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from etl.load.load_postgres import PostgreSQLLoader
from utils.helpers import DataProfiler
from loguru import logger
import os
from datetime import datetime

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}



def create_sample_data():
    """Crée des données d'exemple pour tester le pipeline ETL."""
    np.random.seed(42)
    
    # Données d'exemple pour l'analyse économique
    n_samples = 1000
    
    data = {
        'pays': np.random.choice(['Bénin', 'Burkina Faso', 'Côte d\'Ivoire', 'Sénégal', 'Mali'], n_samples),
        'annee': np.random.randint(2015, 2024, n_samples),
        'pib_millions': np.random.normal(50000, 20000, n_samples),
        'population_millions': np.random.normal(15, 8, n_samples),
        'inflation_taux': np.random.normal(2.5, 1.5, n_samples),
        'export_millions': np.random.normal(8000, 3000, n_samples),
        'import_millions': np.random.normal(10000, 4000, n_samples),
        'date_creation': pd.date_range('2023-01-01', periods=n_samples, freq='D')
    }
    
    # Ajout de valeurs manquantes et aberrantes pour tester le nettoyage
    df = pd.DataFrame(data)
    
    # Valeurs manquantes aléatoires
    missing_mask = np.random.random(n_samples) < 0.05
    df.loc[missing_mask, 'inflation_taux'] = np.nan
    
    # Valeurs aberrantes
    outlier_mask = np.random.random(n_samples) < 0.02
    df.loc[outlier_mask, 'pib_millions'] = df.loc[outlier_mask, 'pib_millions'] * 10
    
    # Doublons
    df = pd.concat([df, df.iloc[:10]], ignore_index=True)
    
    return df


def main():
    """Pipeline ETL principal pour tester l'extraction, transformation et chargement."""
    
    # Configuration du logging
    logger.add("etl_pipeline.log", rotation="1 day", retention="7 days")
    logger.info("=== DÉBUT DU PIPELINE ETL ===")
    
    try:
        # 1. CRÉATION DES DONNÉES D'EXEMPLE
        logger.info("Étape 1: Création des données d'exemple")
        df_original = create_sample_data()
        
        # Sauvegarde des données originales
        df_original.to_csv('sample_data_original.csv', index=False)
        logger.info(f"Données originales créées: {len(df_original)} lignes, {len(df_original.columns)} colonnes")
        
        # 2. EXTRACTION (simulation)
        logger.info("Étape 2: Extraction des données")
        csv_extractor = CSVExtractor()
        
        # Validation des données extraites
        validation_info = csv_extractor.validate_csv(df_original)
        logger.info(f"Validation: {validation_info['rows']} lignes, {validation_info['columns']} colonnes")
        
        # 3. PROFILAGE INITIAL
        logger.info("Étape 3: Profilage initial des données")
        profiler = DataProfiler()
        profile_initial = profiler.profile_dataframe(df_original)
        
        logger.info(f"Profil initial - Lignes: {profile_initial['basic_info']['rows']}, "
                   f"Colonnes: {profile_initial['basic_info']['columns']}, "
                   f"Valeurs manquantes: {profile_initial['missing_values']['total_missing']}")
        
        # 4. NETTOYAGE DES DONNÉES
        logger.info("Étape 4: Nettoyage des données")
        cleaner = DataCleaner()
        
        df_cleaned = cleaner.clean_data(
            df_original,
            missing_strategy='fill',
            remove_duplicates=True,
            handle_outliers=True,
            fix_inconsistencies=True
        )
        
        logger.info(f"Nettoyage terminé: {len(df_original)} -> {len(df_cleaned)} lignes")
        
        # 5. NORMALISATION DES DONNÉES
        logger.info("Étape 5: Normalisation des données")
        normalizer = DataNormalizer()
        
        df_normalized = normalizer.normalize_data(
            df_cleaned,
            numerical_method='standard',
            categorical_method='label',
            normalize_dates=True
        )
        
        logger.info(f"Normalisation terminée: {len(df_normalized.columns)} colonnes")
        
        # 6. ENRICHISSEMENT DES DONNÉES
        logger.info("Étape 6: Enrichissement des données")
        enricher = DataEnricher()
        
        # Exemple de colonnes conditionnelles
        conditions = {
            'pib_par_habitant': lambda df: df['pib_millions'] / df['population_millions'],
            'balance_commerciale': lambda df: df['export_millions'] - df['import_millions'],
            'pays_riche': lambda df: df['pib_millions'] > df['pib_millions'].median()
        }
        
        # Exemple d'agrégations
        aggregations = {
            'group_by': 'pays',
            'aggregations': {
                'pib_millions': ['mean', 'sum', 'count'],
                'population_millions': ['mean', 'sum']
            },
            'prefix': 'agg'
        }
        
        # Exemple de features temporelles
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
        
        logger.info(f"Enrichissement terminé: {len(df_normalized.columns)} -> {len(df_enriched.columns)} colonnes")
        
        # 7. PROFILAGE FINAL
        logger.info("Étape 7: Profilage final des données")
        profile_final = profiler.profile_dataframe(df_enriched)
        
        # Comparaison des profils
        comparison = profiler.compare_profiles(profile_initial, profile_final)
        logger.info(f"Changements détectés: {comparison['changes_detected']}")
        
        # 8. CHARGEMENT VERS POSTGRESQL (si configuré)
        logger.info("Étape 8: Chargement vers PostgreSQL")
        
        # Vérification de la variable d'environnement
        db_url = os.getenv('DATABASE_URL')
        
        if db_url:
            try:
                loader = PostgreSQLLoader(db_url)
                
                # Test de connexion
                if loader.test_connection():
                    # Chargement des données
                    success = loader.load_data(
                        df_enriched,
                        table_name='economic_data_etl',
                        if_exists='replace'
                    )
                    
                    if success:
                        logger.info("Chargement PostgreSQL réussi")
                        
                        # Récupération des informations de la table
                        table_info = loader.get_table_info('economic_data_etl')
                        if table_info:
                            logger.info(f"Table créée avec {table_info['column_count']} colonnes")
                        
                        loader.close_connection()
                    else:
                        logger.error("Échec du chargement PostgreSQL")
                else:
                    logger.warning("Connexion PostgreSQL échouée, chargement ignoré")
                    
            except Exception as e:
                logger.error(f"Erreur lors du chargement PostgreSQL: {e}")
        else:
            logger.warning("DATABASE_URL non configuré, chargement PostgreSQL ignoré")
        
        # 9. SAUVEGARDE DES RÉSULTATS
        logger.info("Étape 9: Sauvegarde des résultats")
        
        # Sauvegarde des données transformées
        df_enriched.to_csv('sample_data_transformed.csv', index=False)
        
        # Sauvegarde du profil final
        profiler.save_profile(profile_final, 'data_profile_final.json')
        
        # Sauvegarde de la comparaison
        with open('profile_comparison.json', 'w') as f:
            import json
            json.dump(comparison, f, indent=2, default=str)
        
        logger.info("=== PIPELINE ETL TERMINÉ AVEC SUCCÈS ===")
        
        # Résumé final
        print("\n" + "="*50)
        print("RÉSUMÉ DU PIPELINE ETL")
        print("="*50)
        print(f"Données originales: {len(df_original)} lignes, {len(df_original.columns)} colonnes")
        print(f"Données finales: {len(df_enriched)} lignes, {len(df_enriched.columns)} colonnes")
        print(f"Valeurs manquantes traitées: {profile_initial['missing_values']['total_missing']}")
        print(f"Doublons supprimés: {profile_initial['duplicates']['total_duplicates']}")
        print(f"Nouvelles colonnes créées: {len(df_enriched.columns) - len(df_original.columns)}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Erreur dans le pipeline ETL: {e}")
        raise


if __name__ == "__main__":
    main()
