import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Callable
from loguru import logger


class DataEnricher:
    """Classe pour l'enrichissement et la transformation des données."""
    
    def __init__(self):
        self.logger = logger
        self.enrichment_stats = {}
    
    def create_conditional_columns(self, df: pd.DataFrame, 
                                 conditions: Dict[str, Callable],
                                 new_column_names: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Crée des colonnes conditionnelles basées sur des fonctions.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            conditions (Dict[str, Callable]): Dictionnaire {nom_colonne: fonction_condition}
            new_column_names (Dict[str, str]): Mapping des noms de colonnes
            
        Returns:
            pd.DataFrame: DataFrame enrichi
        """
        df_enriched = df.copy()
        
        self.logger.info("Début de la création de colonnes conditionnelles")
        
        for col_name, condition_func in conditions.items():
            try:
                new_col_name = new_column_names.get(col_name, col_name) if new_column_names else col_name
                df_enriched[new_col_name] = condition_func(df_enriched)
                self.logger.debug(f"Colonne conditionnelle créée: {new_col_name}")
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la création de la colonne {col_name}: {e}")
        
        self.enrichment_stats['conditional_columns_created'] = len(conditions)
        self.logger.info(f"Création de {len(conditions)} colonnes conditionnelles terminée")
        return df_enriched
    
    def create_aggregated_features(self, df: pd.DataFrame,
                                  group_by: Union[str, List[str]],
                                  aggregations: Dict[str, List[str]],
                                  prefix: str = 'agg') -> pd.DataFrame:
        """
        Crée des features agrégées par groupe.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            group_by (Union[str, List[str]]): Colonne(s) de groupement
            aggregations (Dict[str, List[str]]): {colonne: [fonctions_agrégation]}
            prefix (str): Préfixe pour les nouvelles colonnes
            
        Returns:
            pd.DataFrame: DataFrame avec features agrégées
        """
        df_enriched = df.copy()
        
        self.logger.info(f"Début de la création de features agrégées par {group_by}")
        
        for col, agg_funcs in aggregations.items():
            if col not in df.columns:
                self.logger.warning(f"Colonne {col} non trouvée, ignorée")
                continue
                
            try:
                agg_df = df_enriched.groupby(group_by)[col].agg(agg_funcs).reset_index()
                
                # Renommage des colonnes
                agg_df.columns = [group_by] + [f"{prefix}_{col}_{func}" for func in agg_funcs]
                
                # Fusion avec le DataFrame original
                df_enriched = df_enriched.merge(agg_df, on=group_by, how='left')
                
            except Exception as e:
                self.logger.error(f"Erreur lors de l'agrégation de {col}: {e}")
        
        self.enrichment_stats['aggregated_features_created'] = True
        self.logger.info("Création de features agrégées terminée")
        return df_enriched
    
    def create_time_based_features(self, df: pd.DataFrame,
                                  date_column: str,
                                  features: List[str] = None) -> pd.DataFrame:
        """
        Crée des features basées sur le temps.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            date_column (str): Colonne de date
            features (List[str]): Features à créer ['day_of_week', 'month', 'quarter', 'year', 'is_weekend']
            
        Returns:
            pd.DataFrame: DataFrame avec features temporelles
        """
        df_enriched = df.copy()
        
        if date_column not in df.columns:
            self.logger.error(f"Colonne de date {date_column} non trouvée")
            return df_enriched
        
        try:
            # Conversion en datetime si nécessaire
            df_enriched[date_column] = pd.to_datetime(df_enriched[date_column])
            
            features = features or ['day_of_week', 'month', 'quarter', 'year', 'is_weekend']
            
            if 'day_of_week' in features:
                df_enriched[f'{date_column}_day_of_week'] = df_enriched[date_column].dt.dayofweek
                
            if 'month' in features:
                df_enriched[f'{date_column}_month'] = df_enriched[date_column].dt.month
                
            if 'quarter' in features:
                df_enriched[f'{date_column}_quarter'] = df_enriched[date_column].dt.quarter
                
            if 'year' in features:
                df_enriched[f'{date_column}_year'] = df_enriched[date_column].dt.year
                
            if 'is_weekend' in features:
                df_enriched[f'{date_column}_is_weekend'] = df_enriched[date_column].dt.dayofweek.isin([5, 6])
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la création des features temporelles: {e}")
        
        self.enrichment_stats['time_features_created'] = True
        self.logger.info("Création de features temporelles terminée")
        return df_enriched
    
    def create_interaction_features(self, df: pd.DataFrame,
                                   feature_pairs: List[tuple],
                                   operations: List[str] = None) -> pd.DataFrame:
        """
        Crée des features d'interaction entre colonnes.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            feature_pairs (List[tuple]): Paires de colonnes pour les interactions
            operations (List[str]): Opérations ['multiply', 'divide', 'add', 'subtract']
            
        Returns:
            pd.DataFrame: DataFrame avec features d'interaction
        """
        df_enriched = df.copy()
        
        self.logger.info("Début de la création de features d'interaction")
        
        operations = operations or ['multiply']
        
        for col1, col2 in feature_pairs:
            if col1 not in df.columns or col2 not in df.columns:
                self.logger.warning(f"Colonnes {col1} ou {col2} non trouvées, ignorées")
                continue
                
            try:
                for op in operations:
                    if op == 'multiply':
                        df_enriched[f'{col1}_x_{col2}'] = df_enriched[col1] * df_enriched[col2]
                    elif op == 'divide':
                        df_enriched[f'{col1}_div_{col2}'] = df_enriched[col1] / df_enriched[col2]
                    elif op == 'add':
                        df_enriched[f'{col1}_plus_{col2}'] = df_enriched[col1] + df_enriched[col2]
                    elif op == 'subtract':
                        df_enriched[f'{col1}_minus_{col2}'] = df_enriched[col1] - df_enriched[col2]
                        
            except Exception as e:
                self.logger.error(f"Erreur lors de la création de l'interaction {col1}-{col2}: {e}")
        
        self.enrichment_stats['interaction_features_created'] = True
        self.logger.info("Création de features d'interaction terminée")
        return df_enriched
    
    def create_binning_features(self, df: pd.DataFrame,
                               columns: List[str],
                               bins: Union[int, List[List[float]]] = 10,
                               labels: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Crée des features de binning pour les colonnes numériques.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            columns (List[str]): Colonnes à biner
            bins (Union[int, List[List[float]]]): Nombre de bins ou bins personnalisés
            labels (List[str]): Labels pour les bins
            
        Returns:
            pd.DataFrame: DataFrame avec features de binning
        """
        df_enriched = df.copy()
        
        self.logger.info("Début de la création de features de binning")
        
        for col in columns:
            if col not in df.columns or df[col].dtype not in ['int64', 'float64']:
                self.logger.warning(f"Colonne {col} non trouvée ou non numérique, ignorée")
                continue
                
            try:
                df_enriched[f'{col}_binned'] = pd.cut(df_enriched[col], bins=bins, labels=labels)
                
            except Exception as e:
                self.logger.error(f"Erreur lors du binning de {col}: {e}")
        
        self.enrichment_stats['binning_features_created'] = True
        self.logger.info("Création de features de binning terminée")
        return df_enriched
    
    def enrich_data(self, df: pd.DataFrame,
                    conditional_columns: Optional[Dict[str, Callable]] = None,
                    aggregations: Optional[Dict] = None,
                    time_features: Optional[Dict] = None,
                    interaction_features: Optional[List[tuple]] = None,
                    binning_features: Optional[Dict] = None) -> pd.DataFrame:
        """
        Pipeline complet d'enrichissement des données.
        
        Args:
            df (pd.DataFrame): DataFrame à enrichir
            conditional_columns (Dict[str, Callable]): Colonnes conditionnelles
            aggregations (Dict): Configuration des agrégations
            time_features (Dict): Configuration des features temporelles
            interaction_features (List[tuple]): Paires de colonnes pour interactions
            binning_features (Dict): Configuration du binning
            
        Returns:
            pd.DataFrame: DataFrame enrichi
        """
        self.logger.info("Début du pipeline d'enrichissement des données")
        df_enriched = df.copy()
        
        # Colonnes conditionnelles
        if conditional_columns:
            df_enriched = self.create_conditional_columns(df_enriched, conditional_columns)
        
        # Features agrégées
        if aggregations:
            df_enriched = self.create_aggregated_features(df_enriched, **aggregations)
        
        # Features temporelles
        if time_features:
            df_enriched = self.create_time_based_features(df_enriched, **time_features)
        
        # Features d'interaction
        if interaction_features:
            df_enriched = self.create_interaction_features(df_enriched, interaction_features)
        
        # Features de binning
        if binning_features:
            df_enriched = self.create_binning_features(df_enriched, **binning_features)
        
        self.logger.info(f"Pipeline d'enrichissement terminé: {len(df.columns)} -> {len(df_enriched.columns)} colonnes")
        return df_enriched
