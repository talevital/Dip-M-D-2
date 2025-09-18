import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Callable
from loguru import logger
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import scipy.stats as stats


class DataNormalizer:
    """Classe pour la normalisation et standardisation des données."""
    
    def __init__(self):
        self.logger = logger
        self.scalers = {}
        self.normalization_stats = {}
    
    def normalize_numerical(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                          method: str = 'standard', **kwargs) -> pd.DataFrame:
        """
        Normalise les colonnes numériques.
        
        Args:
            df (pd.DataFrame): DataFrame à normaliser
            columns (List[str]): Colonnes à normaliser
            method (str): 'standard', 'minmax', 'robust', 'log', 'boxcox'
            **kwargs: Arguments additionnels pour les scalers
            
        Returns:
            pd.DataFrame: DataFrame normalisé
        """
        df_normalized = df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        
        self.logger.info(f"Début de la normalisation avec méthode: {method}")
        
        for col in columns:
            if col not in df.columns or df[col].dtype not in ['int64', 'float64']:
                continue
                
            if method == 'standard':
                scaler = StandardScaler(**kwargs)
                df_normalized[col] = scaler.fit_transform(df_normalized[[col]])
                self.scalers[f"{col}_standard"] = scaler
                
            elif method == 'minmax':
                scaler = MinMaxScaler(**kwargs)
                df_normalized[col] = scaler.fit_transform(df_normalized[[col]])
                self.scalers[f"{col}_minmax"] = scaler
                
            elif method == 'robust':
                scaler = RobustScaler(**kwargs)
                df_normalized[col] = scaler.fit_transform(df_normalized[[col]])
                self.scalers[f"{col}_robust"] = scaler
                
            elif method == 'log':
                # Normalisation log avec gestion des valeurs négatives
                if (df_normalized[col] <= 0).any():
                    df_normalized[col] = df_normalized[col] - df_normalized[col].min() + 1
                df_normalized[col] = np.log(df_normalized[col])
                
            elif method == 'boxcox':
                # Transformation Box-Cox
                if (df_normalized[col] <= 0).any():
                    df_normalized[col] = df_normalized[col] - df_normalized[col].min() + 1
                df_normalized[col] = stats.boxcox(df_normalized[col])[0]
        
        self.normalization_stats['numerical_normalized'] = True
        self.logger.info("Normalisation numérique terminée")
        return df_normalized
    
    def standardize_categorical(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                              method: str = 'label', **kwargs) -> pd.DataFrame:
        """
        Standardise les colonnes catégorielles.
        
        Args:
            df (pd.DataFrame): DataFrame à standardiser
            columns (List[str]): Colonnes catégorielles
            method (str): 'label', 'onehot', 'frequency'
            **kwargs: Arguments additionnels
            
        Returns:
            pd.DataFrame: DataFrame standardisé
        """
        df_standardized = df.copy()
        columns = columns or df.select_dtypes(include=['object']).columns.tolist()
        
        self.logger.info(f"Début de la standardisation catégorielle avec méthode: {method}")
        
        for col in columns:
            if col not in df.columns:
                continue
                
            if method == 'label':
                # Encodage par étiquettes
                df_standardized[col] = pd.Categorical(df_standardized[col]).codes
                
            elif method == 'onehot':
                # Encodage one-hot
                dummies = pd.get_dummies(df_standardized[col], prefix=col)
                df_standardized = pd.concat([df_standardized, dummies], axis=1)
                df_standardized.drop(col, axis=1, inplace=True)
                
            elif method == 'frequency':
                # Encodage par fréquence
                freq_map = df_standardized[col].value_counts(normalize=True).to_dict()
                df_standardized[col] = df_standardized[col].map(freq_map)
        
        self.normalization_stats['categorical_standardized'] = True
        self.logger.info("Standardisation catégorielle terminée")
        return df_standardized
    
    def normalize_dates(self, df: pd.DataFrame, date_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Normalise les colonnes de dates.
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            date_columns (List[str]): Colonnes de dates
            
        Returns:
            pd.DataFrame: DataFrame avec dates normalisées
        """
        df_normalized = df.copy()
        
        self.logger.info("Début de la normalisation des dates")
        
        for col in date_columns or []:
            if col not in df.columns:
                continue
                
            try:
                # Conversion en datetime
                df_normalized[col] = pd.to_datetime(df_normalized[col], errors='coerce')
                
                # Extraction des composants temporels
                df_normalized[f"{col}_year"] = df_normalized[col].dt.year
                df_normalized[f"{col}_month"] = df_normalized[col].dt.month
                df_normalized[f"{col}_day"] = df_normalized[col].dt.day
                df_normalized[f"{col}_dayofweek"] = df_normalized[col].dt.dayofweek
                
            except Exception as e:
                self.logger.warning(f"Impossible de normaliser la colonne {col}: {e}")
        
        self.normalization_stats['dates_normalized'] = True
        self.logger.info("Normalisation des dates terminée")
        return df_normalized
    
    def apply_custom_normalization(self, df: pd.DataFrame, 
                                 normalization_func: Callable,
                                 columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Applique une fonction de normalisation personnalisée.
        
        Args:
            df (pd.DataFrame): DataFrame à traiter
            normalization_func (Callable): Fonction de normalisation
            columns (List[str]): Colonnes à traiter
            
        Returns:
            pd.DataFrame: DataFrame normalisé
        """
        df_normalized = df.copy()
        columns = columns or df.columns.tolist()
        
        self.logger.info("Application de normalisation personnalisée")
        
        for col in columns:
            if col in df.columns:
                df_normalized[col] = normalization_func(df_normalized[col])
        
        self.normalization_stats['custom_normalization_applied'] = True
        self.logger.info("Normalisation personnalisée terminée")
        return df_normalized
    
    def normalize_data(self, df: pd.DataFrame,
                       numerical_method: str = 'standard',
                       categorical_method: str = 'label',
                       normalize_dates: bool = True,
                       **kwargs) -> pd.DataFrame:
        """
        Pipeline complet de normalisation des données.
        
        Args:
            df (pd.DataFrame): DataFrame à normaliser
            numerical_method (str): Méthode pour les colonnes numériques
            categorical_method (str): Méthode pour les colonnes catégorielles
            normalize_dates (bool): Normaliser les dates
            **kwargs: Arguments additionnels
            
        Returns:
            pd.DataFrame: DataFrame normalisé
        """
        self.logger.info("Début du pipeline de normalisation")
        df_normalized = df.copy()
        
        # Normalisation numérique
        df_normalized = self.normalize_numerical(df_normalized, method=numerical_method, **kwargs)
        
        # Standardisation catégorielle
        df_normalized = self.standardize_categorical(df_normalized, method=categorical_method, **kwargs)
        
        # Normalisation des dates
        if normalize_dates:
            date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
            if date_columns:
                df_normalized = self.normalize_dates(df_normalized, date_columns)
        
        self.logger.info("Pipeline de normalisation terminé")
        return df_normalized
