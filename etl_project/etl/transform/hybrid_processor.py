"""
Module hybride combinant AutomaticDataProcessor et DataPreprocessor
Intègre les meilleures fonctionnalités des deux approches
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from loguru import logger
from scipy import stats
from scipy.stats import boxcox
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import IsolationForest
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Imports optionnels pour la visualisation
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    logger.warning("Matplotlib/Seaborn non disponible - fonctionnalités de visualisation désactivées")

class HybridDataProcessor:
    """
    Processeur hybride combinant les meilleures fonctionnalités des deux approches
    """
    
    def __init__(self):
        self.logger = logger
        self.processing_stats = {}
        self.scalers = {}
        self.encoders = {}
        self.outlier_stats = {}
        
    # ==================== DÉTECTION D'OUTLIERS AVANCÉE (du script Stata) ====================
    
    def detect_outliers_comprehensive(self, df: pd.DataFrame, 
                                    columns: Optional[List[str]] = None,
                                    methods: List[str] = ['iqr', 'zscore', 'isolation_forest'],
                                    group_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Détection complète des outliers avec plusieurs méthodes
        
        Args:
            df: DataFrame à analyser
            columns: Colonnes à analyser
            methods: Méthodes de détection ['iqr', 'zscore', 'isolation_forest']
            group_by: Colonne de groupement
        """
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        outlier_results = {}
        
        for col in columns:
            if col not in df.columns:
                continue
                
            col_results = {}
            
            # Méthode IQR (du script Stata)
            if 'iqr' in methods:
                if group_by:
                    grouped = df.groupby(group_by)[col]
                    q25 = grouped.quantile(0.25)
                    q75 = grouped.quantile(0.75)
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    
                    outlier_mask = (
                        (df[col] < lower_bound[df[group_by]]) | 
                        (df[col] > upper_bound[df[group_by]])
                    )
                else:
                    q25 = df[col].quantile(0.25)
                    q75 = df[col].quantile(0.75)
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                
                col_results['iqr'] = {
                    'outliers': df[outlier_mask].index.tolist(),
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(df)) * 100,
                    'bounds': {'lower': lower_bound, 'upper': upper_bound}
                }
            
            # Méthode Z-score (du script Stata)
            if 'zscore' in methods:
                if group_by:
                    grouped = df.groupby(group_by)[col]
                    mean_val = grouped.transform('mean')
                    std_val = grouped.transform('std')
                    z_scores = np.abs((df[col] - mean_val) / std_val)
                else:
                    mean_val = df[col].mean()
                    std_val = df[col].std()
                    z_scores = np.abs((df[col] - mean_val) / std_val)
                
                outlier_mask = z_scores > 3
                col_results['zscore'] = {
                    'outliers': df[outlier_mask].index.tolist(),
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(df)) * 100,
                    'z_scores': z_scores.tolist()
                }
            
            # Méthode Isolation Forest (moderne)
            if 'isolation_forest' in methods:
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = iso_forest.fit_predict(df[[col]])
                outlier_mask = outlier_labels == -1
                
                col_results['isolation_forest'] = {
                    'outliers': df[outlier_mask].index.tolist(),
                    'count': outlier_mask.sum(),
                    'percentage': (outlier_mask.sum() / len(df)) * 100
                }
            
            outlier_results[col] = col_results
            
            # Logging détaillé
            self.logger.info(f"Outliers détectés pour {col}:")
            for method, result in col_results.items():
                self.logger.info(f"  {method.upper()}: {result['count']} outliers ({result['percentage']:.2f}%)")
        
        self.outlier_stats = outlier_results
        return outlier_results
    
    def plot_outliers_comprehensive(self, df: pd.DataFrame, column: str, 
                                  outlier_results: Optional[Dict] = None):
        """
        Visualisation complète des outliers (du script Stata amélioré)
        """
        if not HAS_PLOTTING:
            self.logger.warning("Visualisation non disponible - matplotlib non installé")
            return
            
        if outlier_results is None:
            outlier_results = self.outlier_stats.get(column, {})
        
        if not outlier_results:
            self.logger.warning(f"Aucun résultat d'outliers pour {column}")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Analyse complète des outliers - {column}', fontsize=16)
        
        # Box plot original
        axes[0, 0].boxplot(df[column].dropna())
        axes[0, 0].set_title('Box Plot Original')
        axes[0, 0].set_ylabel(column)
        
        # Histogramme avec outliers marqués
        axes[0, 1].hist(df[column].dropna(), bins=30, alpha=0.7, color='blue')
        if 'iqr' in outlier_results:
            outliers_iqr = df.loc[outlier_results['iqr']['outliers'], column]
            axes[0, 1].hist(outliers_iqr, bins=10, alpha=0.7, color='red', label='Outliers IQR')
        axes[0, 1].set_title('Distribution avec Outliers')
        axes[0, 1].legend()
        
        # Scatter plot avec outliers
        axes[1, 0].scatter(range(len(df)), df[column], alpha=0.6, color='blue')
        if 'iqr' in outlier_results:
            outliers_iqr = outlier_results['iqr']['outliers']
            axes[1, 0].scatter(outliers_iqr, df.loc[outliers_iqr, column], 
                              color='red', s=50, label='Outliers IQR')
        axes[1, 0].set_title('Scatter Plot avec Outliers')
        axes[1, 0].legend()
        
        # Comparaison des méthodes
        methods = list(outlier_results.keys())
        counts = [outlier_results[method]['count'] for method in methods]
        axes[1, 1].bar(methods, counts, color=['blue', 'green', 'red'][:len(methods)])
        axes[1, 1].set_title('Comparaison des Méthodes de Détection')
        axes[1, 1].set_ylabel('Nombre d\'outliers')
        
        plt.tight_layout()
        plt.show()
    
    # ==================== TRANSFORMATIONS AVANCÉES (du script Stata) ====================
    
    def apply_transformations(self, df: pd.DataFrame, 
                            columns: List[str],
                            transformations: List[str] = ['log', 'boxcox', 'sqrt']) -> pd.DataFrame:
        """
        Application de transformations avancées (du script Stata)
        
        Args:
            df: DataFrame à transformer
            columns: Colonnes à transformer
            transformations: Types de transformations
        """
        df_transformed = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            data = df[col].dropna()
            
            for transform_type in transformations:
                if transform_type == 'log':
                    # Transformation logarithmique
                    if (data <= 0).any():
                        df_transformed[f'{col}_log'] = np.log(data + 1)
                    else:
                        df_transformed[f'{col}_log'] = np.log(data)
                        
                elif transform_type == 'boxcox':
                    # Transformation Box-Cox
                    if (data <= 0).any():
                        data_positive = data + 1
                    else:
                        data_positive = data
                    
                    try:
                        transformed_data, lambda_param = boxcox(data_positive)
                        df_transformed[f'{col}_boxcox'] = transformed_data
                        self.logger.info(f"Box-Cox pour {col}: lambda = {lambda_param:.4f}")
                    except Exception as e:
                        self.logger.warning(f"Erreur Box-Cox pour {col}: {e}")
                        df_transformed[f'{col}_boxcox'] = data_positive
                        
                elif transform_type == 'sqrt':
                    # Transformation racine carrée
                    df_transformed[f'{col}_sqrt'] = np.sqrt(np.abs(data))
                    
                elif transform_type == 'square':
                    # Transformation carrée
                    df_transformed[f'{col}_square'] = data ** 2
        
        return df_transformed
    
    # ==================== NORMALISATION PAR GROUPE (du script Stata) ====================
    
    def normalize_by_group(self, df: pd.DataFrame, 
                          columns: List[str], 
                          group_by: str,
                          method: str = 'minmax') -> pd.DataFrame:
        """
        Normalisation par groupe (du script Stata)
        
        Args:
            df: DataFrame à normaliser
            columns: Colonnes à normaliser
            group_by: Colonne de groupement
            method: 'minmax' ou 'standard'
        """
        df_normalized = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            if method == 'minmax':
                # Min-Max par groupe
                min_val = df_normalized.groupby(group_by)[col].transform('min')
                max_val = df_normalized.groupby(group_by)[col].transform('max')
                df_normalized[f'{col}_N'] = (df_normalized[col] - min_val) / (max_val - min_val)
                
            elif method == 'standard':
                # Standardisation par groupe
                mean_val = df_normalized.groupby(group_by)[col].transform('mean')
                std_val = df_normalized.groupby(group_by)[col].transform('std')
                df_normalized[f'{col}_S'] = (df_normalized[col] - mean_val) / std_val
        
        return df_normalized
    
    # ==================== PIPELINE COMPLET HYBRIDE ====================
    
    def process_data_hybrid(self, df: pd.DataFrame,
                           config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Pipeline complet hybride combinant les deux approches
        """
        if config is None:
            config = self.get_hybrid_config()
        
        self.logger.info("Début du traitement hybride des données")
        df_processed = df.copy()
        
        # 1. Détection complète des outliers
        outlier_results = {}
        if config.get('detect_outliers', True):
            outlier_results = self.detect_outliers_comprehensive(
                df_processed,
                columns=config.get('outlier_columns'),
                methods=config.get('outlier_methods', ['iqr', 'zscore']),
                group_by=config.get('group_by')
            )
        
        # 2. Gestion des valeurs manquantes (AutomaticDataProcessor)
        if config.get('handle_missing', True):
            df_processed = self.handle_missing_values(
                df_processed,
                strategy=config.get('missing_strategy', 'mean'),
                group_by=config.get('group_by'),
                threshold=config.get('missing_threshold', 0.5)
            )
        
        # 3. Suppression des doublons
        if config.get('remove_duplicates', True):
            df_processed = self.remove_duplicates(df_processed)
        
        # 4. Traitement des outliers
        if config.get('handle_outliers', True):
            df_processed = self.handle_outliers_hybrid(
                df_processed,
                method=config.get('outlier_method', 'winsorize'),
                outlier_results=outlier_results
            )
        
        # 5. Transformations avancées
        if config.get('apply_transformations', False):
            df_processed = self.apply_transformations(
                df_processed,
                columns=config.get('transform_columns', []),
                transformations=config.get('transformations', ['log'])
            )
        
        # 6. Normalisation par groupe (Stata) ou globale
        if config.get('normalize_by_group', False):
            df_processed = self.normalize_by_group(
                df_processed,
                columns=config.get('normalize_columns', []),
                group_by=config.get('group_by'),
                method=config.get('group_normalization_method', 'minmax')
            )
        elif config.get('normalize_global', True):
            df_processed = self.normalize_numerical(
                df_processed,
                method=config.get('normalization_method', 'standard')
            )
        
        # 7. Encodage des catégories
        if config.get('encode_categorical', True):
            df_processed = self.encode_categorical(
                df_processed,
                method=config.get('encoding_method', 'label'),
                max_categories=config.get('max_categories', 50)
            )
        
        # 8. Normalisation des dates
        if config.get('normalize_dates', True):
            df_processed = self.normalize_dates(
                df_processed,
                date_columns=config.get('date_columns'),
                format=config.get('date_format', '%Y-%m-%d'),
                extract_features=config.get('extract_date_features', True)
            )
        
        self.logger.info(f"Traitement hybride terminé: {len(df)} -> {len(df_processed)} lignes")
        return df_processed
    
    def get_hybrid_config(self) -> Dict[str, Any]:
        """
        Configuration hybride par défaut
        """
        return {
            # Détection d'outliers (Stata)
            'detect_outliers': True,
            'outlier_methods': ['iqr', 'zscore'],
            'outlier_columns': None,  # Toutes les colonnes numériques
            
            # Gestion des valeurs manquantes (AutomaticDataProcessor)
            'handle_missing': True,
            'missing_strategy': 'mean',
            'missing_threshold': 0.5,
            
            # Nettoyage
            'remove_duplicates': True,
            'handle_outliers': True,
            'outlier_method': 'winsorize',
            
            # Transformations (Stata)
            'apply_transformations': False,
            'transformations': ['log'],
            
            # Normalisation
            'normalize_by_group': False,  # Utiliser la méthode Stata
            'normalize_global': True,     # Utiliser la méthode moderne
            'group_normalization_method': 'minmax',
            'normalization_method': 'standard',
            
            # Encodage
            'encode_categorical': True,
            'encoding_method': 'label',
            'max_categories': 50,
            
            # Dates
            'normalize_dates': True,
            'extract_date_features': True,
            'date_format': '%Y-%m-%d',
            
            # Groupement
            'group_by': None
        }
    
    # ==================== MÉTHODES HÉRITÉES DE AutomaticDataProcessor ====================
    
    def handle_missing_values(self, df: pd.DataFrame, 
                            strategy: str = 'mean',
                            columns: Optional[List[str]] = None,
                            group_by: Optional[str] = None,
                            threshold: float = 0.5) -> pd.DataFrame:
        """Héritée de AutomaticDataProcessor"""
        df_clean = df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            missing_count = df[col].isnull().sum()
            missing_ratio = missing_count / len(df)
            
            if missing_count == 0:
                continue
                
            if missing_ratio > threshold:
                df_clean = df_clean.drop(columns=[col])
                continue
            
            if strategy == 'mean':
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == 'median':
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif strategy == 'mode':
                mode_value = df_clean[col].mode()
                df_clean[col] = df_clean[col].fillna(mode_value[0] if len(mode_value) > 0 else 0)
            elif strategy == 'group_mean' and group_by:
                df_clean[col] = df_clean.groupby(group_by)[col].transform(
                    lambda x: x.fillna(x.mean())
                )
            elif strategy == 'knn':
                imputer = KNNImputer(n_neighbors=5)
                df_clean[col] = imputer.fit_transform(df_clean[[col]]).flatten()
        
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame,
                         subset: Optional[List[str]] = None,
                         keep: str = 'first') -> pd.DataFrame:
        """Héritée de AutomaticDataProcessor"""
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_count - len(df_clean)
        
        self.logger.info(f"Suppression de {removed_count} doublons")
        return df_clean
    
    def handle_outliers_hybrid(self, df: pd.DataFrame,
                              method: str = 'winsorize',
                              outlier_results: Optional[Dict] = None) -> pd.DataFrame:
        """Traitement des outliers basé sur les résultats de détection"""
        df_clean = df.copy()
        
        if outlier_results is None:
            outlier_results = self.outlier_stats
        
        for col, methods_results in outlier_results.items():
            if col not in df.columns:
                continue
            
            if method == 'winsorize':
                # Utiliser les bornes IQR si disponibles
                if 'iqr' in methods_results:
                    bounds = methods_results['iqr']['bounds']
                    df_clean[col] = df_clean[col].clip(
                        lower=bounds['lower'], 
                        upper=bounds['upper']
                    )
                else:
                    # Winsorisation par défaut
                    lower_limit = df_clean[col].quantile(0.05)
                    upper_limit = df_clean[col].quantile(0.95)
                    df_clean[col] = df_clean[col].clip(lower=lower_limit, upper=upper_limit)
            
            elif method == 'cap':
                # Capping aux percentiles
                lower_percentile = df_clean[col].quantile(0.05)
                upper_percentile = df_clean[col].quantile(0.95)
                df_clean[col] = df_clean[col].clip(lower=lower_percentile, upper=upper_percentile)
                
            elif method == 'remove':
                # Supprimer tous les outliers détectés
                all_outliers = set()
                for method_result in methods_results.values():
                    all_outliers.update(method_result['outliers'])
                df_clean = df_clean.drop(index=list(all_outliers))
                
            elif method == 'transform':
                # Transformation logarithmique
                df_clean[col] = np.log1p(df_clean[col])
        
        return df_clean
    
    def normalize_numerical(self, df: pd.DataFrame,
                           method: str = 'standard',
                           columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Héritée de AutomaticDataProcessor"""
        df_normalized = df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            data = df[col].dropna()
            if len(data) == 0:
                continue
            
            if method == 'standard':
                scaler = StandardScaler()
                df_normalized[col] = scaler.fit_transform(data.values.reshape(-1, 1)).flatten()
            elif method == 'minmax':
                scaler = MinMaxScaler()
                df_normalized[col] = scaler.fit_transform(data.values.reshape(-1, 1)).flatten()
            elif method == 'robust':
                median = data.median()
                mad = np.median(np.abs(data - median))
                df_normalized[col] = (data - median) / mad
            
            self.scalers[col] = scaler
        
        return df_normalized
    
    def encode_categorical(self, df: pd.DataFrame,
                          method: str = 'label',
                          columns: Optional[List[str]] = None,
                          max_categories: int = 50) -> pd.DataFrame:
        """Héritée de AutomaticDataProcessor"""
        df_encoded = df.copy()
        columns = columns or df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            unique_count = df[col].nunique()
            
            if method == 'label':
                encoder = LabelEncoder()
                df_encoded[col] = encoder.fit_transform(df[col].astype(str))
            elif method == 'onehot':
                if unique_count > max_categories:
                    self.logger.warning(f"Trop de catégories pour {col}, utilisation du label encoding")
                    encoder = LabelEncoder()
                    df_encoded[col] = encoder.fit_transform(df[col].astype(str))
                else:
                    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                    encoded_data = encoder.fit_transform(df[[col]])
                    encoded_df = pd.DataFrame(encoded_data, columns=[f"{col}_{cat}" for cat in encoder.categories_[0]])
                    df_encoded = pd.concat([df_encoded.drop(columns=[col]), encoded_df], axis=1)
            elif method == 'frequency':
                freq_map = df[col].value_counts(normalize=True)
                df_encoded[col] = df[col].map(freq_map)
            
            self.encoders[col] = encoder
        
        return df_encoded
    
    def normalize_dates(self, df: pd.DataFrame,
                       date_columns: Optional[List[str]] = None,
                       format: str = '%Y-%m-%d',
                       extract_features: bool = True) -> pd.DataFrame:
        """Normalisation des dates"""
        df_normalized = df.copy()
        
        # Détection automatique des colonnes de dates
        if not date_columns:
            date_columns = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        pd.to_datetime(df[col].dropna().iloc[:5])
                        date_columns.append(col)
                    except:
                        continue
        
        self.logger.info(f"Normalisation des dates: {date_columns}")
        
        for col in date_columns:
            if col not in df.columns:
                continue
                
            # Conversion en datetime
            df_normalized[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Formatage selon le format spécifié
            df_normalized[col] = df_normalized[col].dt.strftime(format)
            
            # Extraction de features temporelles
            if extract_features:
                df_normalized[f'{col}_year'] = pd.to_datetime(df[col], errors='coerce').dt.year
                df_normalized[f'{col}_month'] = pd.to_datetime(df[col], errors='coerce').dt.month
                df_normalized[f'{col}_day'] = pd.to_datetime(df[col], errors='coerce').dt.day
                df_normalized[f'{col}_weekday'] = pd.to_datetime(df[col], errors='coerce').dt.weekday
                df_normalized[f'{col}_quarter'] = pd.to_datetime(df[col], errors='coerce').dt.quarter
        
        return df_normalized
    
    def get_processing_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de traitement
        """
        return {
            'processing_stats': self.processing_stats,
            'scalers_count': len(self.scalers),
            'encoders_count': len(self.encoders),
            'outlier_stats': self.outlier_stats,
            'processed_at': datetime.now().isoformat()
        }


# ==================== FONCTIONS UTILITAIRES ====================

def process_file_hybrid(file_path: str, 
                       config: Optional[Dict[str, Any]] = None,
                       output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Traite un fichier avec le processeur hybride
    """
    processor = HybridDataProcessor()
    
    try:
        # Chargement des données
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Format de fichier non supporté")
        
        # Traitement hybride
        df_processed = processor.process_data_hybrid(df, config)
        
        # Sauvegarde si spécifié
        if output_path:
            if output_path.endswith('.csv'):
                df_processed.to_csv(output_path, index=False)
            elif output_path.endswith('.xlsx'):
                df_processed.to_excel(output_path, index=False)
        
        return {
            'success': True,
            'original_shape': df.shape,
            'processed_shape': df_processed.shape,
            'outlier_stats': processor.outlier_stats,
            'processing_report': processor.get_processing_report(),
            'output_path': output_path
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement hybride: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Test du module hybride
    processor = HybridDataProcessor()
    
    # Données de test
    test_data = pd.DataFrame({
        'numeric_col': [1, 2, 3, np.nan, 5, 100, 7, 8, 9, 10],
        'categorical_col': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
        'group_col': ['G1', 'G1', 'G2', 'G2', 'G1', 'G2', 'G1', 'G2', 'G1', 'G2']
    })
    
    # Configuration hybride
    config = {
        'detect_outliers': True,
        'outlier_methods': ['iqr', 'zscore'],
        'handle_missing': True,
        'missing_strategy': 'mean',
        'normalize_by_group': True,
        'group_by': 'group_col',
        'group_normalization_method': 'minmax'
    }
    
    # Traitement hybride
    processed_data = processor.process_data_hybrid(test_data, config)
    print("Données traitées avec le processeur hybride:")
    print(processed_data.head())
