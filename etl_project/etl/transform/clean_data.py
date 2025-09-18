import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from loguru import logger
from scipy import stats


class DataCleaner:
    """Classe pour le nettoyage et la préparation des données."""
    
    def __init__(self):
        self.logger = logger
        self.cleaning_stats = {}
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'drop', 
                            columns: Optional[List[str]] = None, 
                            fill_value: Optional[Union[str, int, float]] = None,
                            group_by: Optional[str] = None) -> pd.DataFrame:
        """
        Gère les valeurs manquantes selon différentes stratégies.
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            strategy (str): 'drop', 'fill', 'interpolate', 'group_fill'
            columns (List[str]): Colonnes à traiter (None = toutes)
            fill_value: Valeur de remplissage pour strategy='fill'
            group_by (str): Colonne de groupement pour strategy='group_fill'
            
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        df_clean = df.copy()
        columns = columns or df.columns.tolist()
        
        self.logger.info(f"Début du traitement des valeurs manquantes avec stratégie: {strategy}")
        
        for col in columns:
            if col not in df.columns:
                self.logger.warning(f"Colonne {col} non trouvée, ignorée")
                continue
                
            missing_count = df[col].isnull().sum()
            if missing_count == 0:
                continue
                
            self.logger.info(f"Traitement de {col}: {missing_count} valeurs manquantes")
            
            if strategy == 'drop':
                df_clean = df_clean.dropna(subset=[col])
                
            elif strategy == 'fill':
                if fill_value is not None:
                    df_clean[col] = df_clean[col].fillna(fill_value)
                else:
                    # Remplissage intelligent selon le type de données
                    if df[col].dtype in ['int64', 'float64']:
                        df_clean[col] = df_clean[col].fillna(df[col].median())
                    else:
                        df_clean[col] = df_clean[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown')
                        
            elif strategy == 'interpolate':
                if df[col].dtype in ['int64', 'float64']:
                    df_clean[col] = df_clean[col].interpolate(method='linear')
                    
            elif strategy == 'group_fill' and group_by:
                if group_by in df.columns:
                    df_clean[col] = df_clean.groupby(group_by)[col].transform(
                        lambda x: x.fillna(x.median() if x.dtype in ['int64', 'float64'] else x.mode()[0] if len(x.mode()) > 0 else 'Unknown')
                    )
        
        self.cleaning_stats['missing_values_handled'] = True
        self.logger.info("Traitement des valeurs manquantes terminé")
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None, 
                         keep: str = 'first') -> pd.DataFrame:
        """
        Supprime les doublons du DataFrame.
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            subset (List[str]): Colonnes pour identifier les doublons
            keep (str): 'first', 'last', ou False
            
        Returns:
            pd.DataFrame: DataFrame sans doublons
        """
        initial_rows = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed_rows = initial_rows - len(df_clean)
        
        self.logger.info(f"Suppression de {removed_rows} doublons sur {initial_rows} lignes")
        self.cleaning_stats['duplicates_removed'] = removed_rows
        
        return df_clean
    
    def handle_outliers(self, df: pd.DataFrame, columns: Optional[List[str]] = None,
                       method: str = 'winsorize', threshold: float = 0.05) -> pd.DataFrame:
        """
        Gère les valeurs aberrantes avec différentes méthodes.
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            columns (List[str]): Colonnes numériques à traiter
            method (str): 'winsorize', 'iqr', 'zscore'
            threshold (float): Seuil pour la détection
            
        Returns:
            pd.DataFrame: DataFrame avec valeurs aberrantes traitées
        """
        df_clean = df.copy()
        columns = columns or df.select_dtypes(include=[np.number]).columns.tolist()
        
        self.logger.info(f"Début du traitement des valeurs aberrantes avec méthode: {method}")
        
        for col in columns:
            if col not in df.columns or df[col].dtype not in ['int64', 'float64']:
                continue
                
            if method == 'winsorize':
                df_clean[col] = stats.mstats.winsorize(df_clean[col], limits=[threshold, threshold])
                
            elif method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
                df_clean.loc[outliers, col] = df_clean[col].median()
                
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(df_clean[col].dropna()))
                outliers = z_scores > 3
                df_clean.loc[outliers.index[outliers], col] = df_clean[col].median()
        
        self.cleaning_stats['outliers_handled'] = True
        self.logger.info("Traitement des valeurs aberrantes terminé")
        return df_clean
    
    def fix_inconsistencies(self, df: pd.DataFrame, 
                           string_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Corrige les incohérences dans les données.
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            string_columns (List[str]): Colonnes de texte à standardiser
            
        Returns:
            pd.DataFrame: DataFrame avec incohérences corrigées
        """
        df_clean = df.copy()
        string_columns = string_columns or df.select_dtypes(include=['object']).columns.tolist()
        
        self.logger.info("Début de la correction des incohérences")
        
        for col in string_columns:
            if col not in df.columns:
                continue
                
            # Standardisation des chaînes
            df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()
            
            # Remplacement des valeurs vides
            df_clean[col] = df_clean[col].replace(['', 'nan', 'none', 'null'], np.nan)
            
            # Correction des espaces multiples
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True)
        
        self.cleaning_stats['inconsistencies_fixed'] = True
        self.logger.info("Correction des incohérences terminée")
        return df_clean
    
    def clean_data(self, df: pd.DataFrame, 
                   missing_strategy: str = 'fill',
                   remove_duplicates: bool = True,
                   handle_outliers: bool = True,
                   fix_inconsistencies: bool = True,
                   **kwargs) -> pd.DataFrame:
        """
        Pipeline complet de nettoyage des données.
        
        Args:
            df (pd.DataFrame): DataFrame à nettoyer
            missing_strategy (str): Stratégie pour les valeurs manquantes
            remove_duplicates (bool): Supprimer les doublons
            handle_outliers (bool): Traiter les valeurs aberrantes
            fix_inconsistencies (bool): Corriger les incohérences
            **kwargs: Arguments additionnels pour les méthodes spécifiques
            
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        self.logger.info("Début du pipeline de nettoyage des données")
        df_clean = df.copy()
        
        # Traitement des valeurs manquantes
        if missing_strategy != 'none':
            df_clean = self.handle_missing_values(df_clean, strategy=missing_strategy, **kwargs)
        
        # Suppression des doublons
        if remove_duplicates:
            df_clean = self.remove_duplicates(df_clean, **kwargs)
        
        # Traitement des valeurs aberrantes
        if handle_outliers:
            df_clean = self.handle_outliers(df_clean, **kwargs)
        
        # Correction des incohérences
        if fix_inconsistencies:
            df_clean = self.fix_inconsistencies(df_clean, **kwargs)
        
        self.logger.info(f"Pipeline de nettoyage terminé: {len(df)} -> {len(df_clean)} lignes")
        return df_clean
