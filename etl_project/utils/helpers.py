import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
from loguru import logger
import json
import os
from datetime import datetime


class DataProfiler:
    """Classe pour le profilage et la validation des données."""
    
    def __init__(self):
        self.logger = logger
        self.profile_stats = {}
    
    def profile_dataframe(self, df: pd.DataFrame, detailed: bool = True) -> Dict[str, Any]:
        """
        Génère un profil complet d'un DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame à profiler
            detailed (bool): Profil détaillé ou basique
            
        Returns:
            Dict[str, Any]: Profil des données
        """
        self.logger.info("Début du profilage des données")
        
        profile = {
            'basic_info': self._get_basic_info(df),
            'data_types': self._get_data_types_info(df),
            'missing_values': self._get_missing_values_info(df),
            'duplicates': self._get_duplicates_info(df),
            'statistical_summary': self._get_statistical_summary(df),
            'timestamp': datetime.now().isoformat()
        }
        
        if detailed:
            profile.update({
                'column_profiles': self._get_column_profiles(df),
                'data_quality': self._get_data_quality_metrics(df),
                'memory_usage': self._get_memory_usage(df)
            })
        
        self.profile_stats['last_profile'] = profile
        self.logger.info("Profilage des données terminé")
        
        return profile
    
    def _get_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informations de base sur le DataFrame."""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'shape': df.shape,
            'column_names': list(df.columns)
        }
    
    def _get_data_types_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informations sur les types de données."""
        dtype_counts = df.dtypes.value_counts().to_dict()
        dtype_details = {}
        
        for col in df.columns:
            dtype_details[col] = {
                'dtype': str(df[col].dtype),
                'unique_count': df[col].nunique(),
                'null_count': df[col].isnull().sum()
            }
        
        return {
            'dtype_counts': dtype_counts,
            'dtype_details': dtype_details
        }
    
    def _get_missing_values_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informations sur les valeurs manquantes."""
        missing_counts = df.isnull().sum()
        missing_percentages = (missing_counts / len(df)) * 100
        
        return {
            'total_missing': missing_counts.sum(),
            'missing_by_column': missing_counts.to_dict(),
            'missing_percentages': missing_percentages.to_dict(),
            'columns_with_missing': missing_counts[missing_counts > 0].index.tolist()
        }
    
    def _get_duplicates_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informations sur les doublons."""
        duplicate_count = df.duplicated().sum()
        
        return {
            'total_duplicates': duplicate_count,
            'duplicate_percentage': (duplicate_count / len(df)) * 100 if len(df) > 0 else 0,
            'has_duplicates': duplicate_count > 0
        }
    
    def _get_statistical_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Résumé statistique des colonnes numériques."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return {'numeric_columns': 0, 'summary': {}}
        
        summary = df[numeric_cols].describe().to_dict()
        
        return {
            'numeric_columns': len(numeric_cols),
            'summary': summary
        }
    
    def _get_column_profiles(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Profils détaillés par colonne."""
        column_profiles = {}
        
        for col in df.columns:
            col_profile = {
                'dtype': str(df[col].dtype),
                'unique_count': df[col].nunique(),
                'null_count': df[col].isnull().sum(),
                'null_percentage': (df[col].isnull().sum() / len(df)) * 100
            }
            
            # Informations spécifiques selon le type de données
            if df[col].dtype in ['int64', 'float64']:
                col_profile.update({
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean(),
                    'median': df[col].median(),
                    'std': df[col].std(),
                    'q25': df[col].quantile(0.25),
                    'q75': df[col].quantile(0.75)
                })
            elif df[col].dtype == 'object':
                col_profile.update({
                    'top_values': df[col].value_counts().head(5).to_dict(),
                    'value_counts': len(df[col].value_counts())
                })
            
            column_profiles[col] = col_profile
        
        return column_profiles
    
    def _get_data_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Métriques de qualité des données."""
        quality_metrics = {
            'completeness': {},
            'consistency': {},
            'validity': {}
        }
        
        # Complétude
        for col in df.columns:
            completeness = (len(df) - df[col].isnull().sum()) / len(df) * 100
            quality_metrics['completeness'][col] = completeness
        
        # Cohérence (pour les colonnes numériques)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            # Vérification des valeurs aberrantes avec IQR
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            quality_metrics['consistency'][col] = {
                'outliers_count': outliers,
                'outliers_percentage': (outliers / len(df)) * 100
            }
        
        return quality_metrics
    
    def _get_memory_usage(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Informations sur l'utilisation mémoire."""
        memory_usage = df.memory_usage(deep=True)
        
        return {
            'total_memory_mb': memory_usage.sum() / 1024 / 1024,
            'memory_by_column': (memory_usage / 1024 / 1024).to_dict(),
            'memory_efficiency': memory_usage.sum() / (len(df) * len(df.columns))
        }
    
    def save_profile(self, profile: Dict[str, Any], filepath: str):
        """
        Sauvegarde le profil dans un fichier JSON.
        
        Args:
            profile (Dict[str, Any]): Profil à sauvegarder
            filepath (str): Chemin du fichier de sauvegarde
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, default=str)
            
            self.logger.info(f"Profil sauvegardé dans {filepath}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du profil: {e}")
    
    def load_profile(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Charge un profil depuis un fichier JSON.
        
        Args:
            filepath (str): Chemin du fichier de profil
            
        Returns:
            Dict[str, Any]: Profil chargé
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            self.logger.info(f"Profil chargé depuis {filepath}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement du profil: {e}")
            return None
    
    def compare_profiles(self, profile1: Dict[str, Any], 
                        profile2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare deux profils de données.
        
        Args:
            profile1 (Dict[str, Any]): Premier profil
            profile2 (Dict[str, Any]): Deuxième profil
            
        Returns:
            Dict[str, Any]: Comparaison des profils
        """
        comparison = {
            'basic_info_comparison': {},
            'data_quality_comparison': {},
            'changes_detected': []
        }
        
        # Comparaison des informations de base
        basic1 = profile1.get('basic_info', {})
        basic2 = profile2.get('basic_info', {})
        
        comparison['basic_info_comparison'] = {
            'rows_change': basic2.get('rows', 0) - basic1.get('rows', 0),
            'columns_change': basic2.get('columns', 0) - basic1.get('columns', 0),
            'memory_change_mb': basic2.get('memory_usage_mb', 0) - basic1.get('memory_usage_mb', 0)
        }
        
        # Détection des changements
        if comparison['basic_info_comparison']['rows_change'] != 0:
            comparison['changes_detected'].append(f"Nombre de lignes: {comparison['basic_info_comparison']['rows_change']}")
        
        if comparison['basic_info_comparison']['columns_change'] != 0:
            comparison['changes_detected'].append(f"Nombre de colonnes: {comparison['basic_info_comparison']['columns_change']}")
        
        self.logger.info(f"Comparaison de profils terminée: {len(comparison['changes_detected'])} changements détectés")
        return comparison
