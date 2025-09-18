import pytest
import pandas as pd
import numpy as np
from etl.extract.csv_extractor import CSVExtractor
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from utils.helpers import DataProfiler


class TestETLPipeline:
    """Tests unitaires pour le pipeline ETL."""
    
    @pytest.fixture
    def sample_data(self):
        """Crée des données de test."""
        np.random.seed(42)
        
        data = {
            'pays': ['Bénin', 'Burkina Faso', 'Côte d\'Ivoire', 'Sénégal', 'Mali'] * 20,
            'annee': np.random.randint(2015, 2024, 100),
            'pib_millions': np.random.normal(50000, 20000, 100),
            'population_millions': np.random.normal(15, 8, 100),
            'inflation_taux': np.random.normal(2.5, 1.5, 100),
            'export_millions': np.random.normal(8000, 3000, 100),
            'import_millions': np.random.normal(10000, 4000, 100)
        }
        
        df = pd.DataFrame(data)
        
        # Ajout de valeurs manquantes pour tester
        df.loc[0:5, 'inflation_taux'] = np.nan
        df.loc[10:15, 'pib_millions'] = np.nan
        
        # Ajout de doublons
        df = pd.concat([df, df.iloc[:5]], ignore_index=True)
        
        return df
    
    def test_csv_extractor(self, sample_data, tmp_path):
        """Test de l'extracteur CSV."""
        # Sauvegarde des données de test
        csv_path = tmp_path / "test_data.csv"
        sample_data.to_csv(csv_path, index=False)
        
        # Test de l'extracteur
        extractor = CSVExtractor()
        df_extracted = extractor.read_csv(str(csv_path))
        
        # Vérifications
        assert len(df_extracted) == len(sample_data)
        assert list(df_extracted.columns) == list(sample_data.columns)
        
        # Test de validation
        validation_info = extractor.validate_csv(df_extracted)
        assert validation_info['is_valid'] == True
        assert validation_info['rows'] == len(sample_data)
        assert validation_info['columns'] == len(sample_data.columns)
    
    def test_data_cleaner(self, sample_data):
        """Test du nettoyeur de données."""
        cleaner = DataCleaner()
        
        # Test du nettoyage complet
        df_cleaned = cleaner.clean_data(
            sample_data,
            missing_strategy='fill',
            remove_duplicates=True,
            handle_outliers=True,
            fix_inconsistencies=True
        )
        
        # Vérifications
        assert len(df_cleaned) <= len(sample_data)  # Doublons supprimés
        assert df_cleaned.isnull().sum().sum() == 0  # Pas de valeurs manquantes
        
        # Vérification des statistiques de nettoyage
        assert cleaner.cleaning_stats['missing_values_handled'] == True
        assert cleaner.cleaning_stats['duplicates_removed'] > 0
        assert cleaner.cleaning_stats['outliers_handled'] == True
        assert cleaner.cleaning_stats['inconsistencies_fixed'] == True
    
    def test_data_normalizer(self, sample_data):
        """Test du normaliseur de données."""
        normalizer = DataNormalizer()
        
        # Test de la normalisation
        df_normalized = normalizer.normalize_data(
            sample_data,
            numerical_method='standard',
            categorical_method='label',
            normalize_dates=False
        )
        
        # Vérifications
        assert len(df_normalized) == len(sample_data)
        
        # Vérification que les colonnes numériques sont normalisées
        numeric_cols = sample_data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in df_normalized.columns:
                # Vérification que la moyenne est proche de 0 (standardisation)
                assert abs(df_normalized[col].mean()) < 0.1
        
        # Vérification des statistiques de normalisation
        assert normalizer.normalization_stats['numerical_normalized'] == True
        assert normalizer.normalization_stats['categorical_standardized'] == True
    
    def test_data_enricher(self, sample_data):
        """Test de l'enrichisseur de données."""
        enricher = DataEnricher()
        
        # Test de l'enrichissement avec colonnes conditionnelles
        conditions = {
            'pib_par_habitant': lambda df: df['pib_millions'] / df['population_millions'],
            'balance_commerciale': lambda df: df['export_millions'] - df['import_millions']
        }
        
        df_enriched = enricher.enrich_data(
            sample_data,
            conditional_columns=conditions
        )
        
        # Vérifications
        assert len(df_enriched) == len(sample_data)
        assert 'pib_par_habitant' in df_enriched.columns
        assert 'balance_commerciale' in df_enriched.columns
        
        # Vérification des calculs
        expected_pib_par_habitant = sample_data['pib_millions'] / sample_data['population_millions']
        pd.testing.assert_series_equal(
            df_enriched['pib_par_habitant'],
            expected_pib_par_habitant,
            check_names=False
        )
        
        # Vérification des statistiques d'enrichissement
        assert enricher.enrichment_stats['conditional_columns_created'] == 2
    
    def test_data_profiler(self, sample_data):
        """Test du profileur de données."""
        profiler = DataProfiler()
        
        # Test du profilage
        profile = profiler.profile_dataframe(sample_data)
        
        # Vérifications
        assert 'basic_info' in profile
        assert 'data_types' in profile
        assert 'missing_values' in profile
        assert 'duplicates' in profile
        assert 'statistical_summary' in profile
        
        # Vérification des informations de base
        assert profile['basic_info']['rows'] == len(sample_data)
        assert profile['basic_info']['columns'] == len(sample_data.columns)
        
        # Vérification des valeurs manquantes
        assert profile['missing_values']['total_missing'] > 0
        
        # Vérification des doublons
        assert profile['duplicates']['has_duplicates'] == True
    
    def test_end_to_end_pipeline(self, sample_data):
        """Test du pipeline ETL complet."""
        # 1. Extraction (simulation)
        extractor = CSVExtractor()
        validation_info = extractor.validate_csv(sample_data)
        
        # 2. Nettoyage
        cleaner = DataCleaner()
        df_cleaned = cleaner.clean_data(sample_data)
        
        # 3. Normalisation
        normalizer = DataNormalizer()
        df_normalized = normalizer.normalize_data(df_cleaned)
        
        # 4. Enrichissement
        enricher = DataEnricher()
        conditions = {
            'pib_par_habitant': lambda df: df['pib_millions'] / df['population_millions']
        }
        df_enriched = enricher.enrich_data(df_normalized, conditional_columns=conditions)
        
        # 5. Profilage final
        profiler = DataProfiler()
        profile_final = profiler.profile_dataframe(df_enriched)
        
        # Vérifications finales
        assert len(df_enriched) > 0
        assert 'pib_par_habitant' in df_enriched.columns
        assert profile_final['basic_info']['columns'] > len(sample_data.columns)
        
        # Vérification que les données sont propres
        assert df_enriched.isnull().sum().sum() == 0  # Pas de valeurs manquantes
        assert df_enriched.duplicated().sum() == 0  # Pas de doublons


if __name__ == "__main__":
    pytest.main([__file__])
