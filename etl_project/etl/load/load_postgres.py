import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Union
from loguru import logger
import os
from datetime import datetime


class PostgreSQLLoader:
    """Classe pour le chargement de données vers PostgreSQL avec SQLAlchemy."""
    
    def __init__(self, connection_string: str):
        """
        Initialise le chargeur PostgreSQL.
        
        Args:
            connection_string (str): Chaîne de connexion PostgreSQL
        """
        self.connection_string = connection_string
        self.engine = None
        self.logger = logger
        self.load_stats = {}
        
        try:
            self.engine = create_engine(connection_string)
            self.logger.info("Connexion PostgreSQL établie avec succès")
        except Exception as e:
            self.logger.error(f"Erreur de connexion PostgreSQL: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données.
        
        Returns:
            bool: True si la connexion fonctionne
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                self.logger.info("Test de connexion PostgreSQL réussi")
                return True
        except SQLAlchemyError as e:
            self.logger.error(f"Échec du test de connexion PostgreSQL: {e}")
            return False
    
    def create_table(self, table_name: str, df: pd.DataFrame, 
                     if_exists: str = 'replace', 
                     index: bool = False,
                     dtype: Optional[Dict] = None) -> bool:
        """
        Crée une table dans PostgreSQL basée sur un DataFrame.
        
        Args:
            table_name (str): Nom de la table
            df (pd.DataFrame): DataFrame source
            if_exists (str): 'fail', 'replace', 'append'
            index (bool): Inclure l'index du DataFrame
            dtype (Dict): Mapping des types de données
            
        Returns:
            bool: True si la création réussit
        """
        try:
            self.logger.info(f"Création de la table {table_name}")
            
            # Mapping des types pandas vers PostgreSQL
            if dtype is None:
                dtype = self._get_postgresql_dtypes(df)
            
            # Création de la table
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists=if_exists,
                index=index,
                dtype=dtype,
                method='multi',
                chunksize=1000
            )
            
            self.logger.info(f"Table {table_name} créée avec succès: {len(df)} lignes")
            self.load_stats[f'{table_name}_created'] = True
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erreur lors de la création de la table {table_name}: {e}")
            return False
    
    def load_data(self, df: pd.DataFrame, table_name: str,
                  if_exists: str = 'replace',
                  index: bool = False,
                  chunk_size: int = 1000) -> bool:
        """
        Charge un DataFrame dans une table PostgreSQL.
        
        Args:
            df (pd.DataFrame): DataFrame à charger
            table_name (str): Nom de la table de destination
            if_exists (str): 'fail', 'replace', 'append'
            index (bool): Inclure l'index du DataFrame
            chunk_size (int): Taille des chunks pour le chargement
            
        Returns:
            bool: True si le chargement réussit
        """
        try:
            self.logger.info(f"Début du chargement vers {table_name}: {len(df)} lignes")
            
            # Chargement par chunks pour optimiser la mémoire
            total_rows = 0
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i + chunk_size]
                
                df.to_sql(
                    name=table_name,
                    con=self.engine,
                    if_exists='append' if i > 0 else if_exists,
                    index=index,
                    method='multi',
                    chunksize=chunk_size
                )
                
                total_rows += len(chunk)
                self.logger.debug(f"Chunk chargé: {total_rows}/{len(df)} lignes")
            
            self.logger.info(f"Chargement terminé: {total_rows} lignes dans {table_name}")
            self.load_stats[f'{table_name}_loaded'] = total_rows
            return True
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erreur lors du chargement vers {table_name}: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Optional[pd.DataFrame]:
        """
        Exécute une requête SQL et retourne les résultats.
        
        Args:
            query (str): Requête SQL
            params (Dict): Paramètres de la requête
            
        Returns:
            pd.DataFrame: Résultats de la requête
        """
        try:
            self.logger.info(f"Exécution de la requête: {query[:100]}...")
            
            with self.engine.connect() as conn:
                result = pd.read_sql_query(query, conn, params=params)
                
            self.logger.info(f"Requête exécutée: {len(result)} lignes retournées")
            return result
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            return None
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """
        Récupère les informations d'une table.
        
        Args:
            table_name (str): Nom de la table
            
        Returns:
            Dict: Informations de la table
        """
        try:
            query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
            """
            
            result = self.execute_query(query)
            
            if result is not None:
                table_info = {
                    'table_name': table_name,
                    'columns': result.to_dict('records'),
                    'column_count': len(result)
                }
                
                self.logger.info(f"Informations de la table {table_name} récupérées")
                return table_info
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des infos de {table_name}: {e}")
        
        return None
    
    def _get_postgresql_dtypes(self, df: pd.DataFrame) -> Dict:
        """
        Génère le mapping des types pandas vers PostgreSQL.
        
        Args:
            df (pd.DataFrame): DataFrame source
            
        Returns:
            Dict: Mapping des types de données
        """
        dtype_mapping = {}
        
        for col, dtype in df.dtypes.items():
            if dtype == 'int64':
                dtype_mapping[col] = Integer
            elif dtype == 'float64':
                dtype_mapping[col] = Float
            elif dtype == 'object':
                # Estimation de la longueur maximale pour VARCHAR
                max_length = df[col].astype(str).str.len().max()
                if pd.isna(max_length):
                    max_length = 255
                dtype_mapping[col] = String(max_length)
            elif dtype == 'datetime64[ns]':
                dtype_mapping[col] = DateTime
        
        return dtype_mapping
    
    def close_connection(self):
        """Ferme la connexion à la base de données."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Connexion PostgreSQL fermée")
    
    def get_load_stats(self) -> Dict:
        """
        Récupère les statistiques de chargement.
        
        Returns:
            Dict: Statistiques de chargement
        """
        return self.load_stats.copy()
