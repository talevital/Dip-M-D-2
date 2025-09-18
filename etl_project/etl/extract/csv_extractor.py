import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


class CSVExtractor:
    """Extracteur pour les fichiers CSV avec gestion d'erreurs et logging."""
    
    def __init__(self):
        self.logger = logger
    
    def read_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Lit un fichier CSV et retourne un DataFrame pandas.
        
        Args:
            file_path (str): Chemin vers le fichier CSV
            **kwargs: Arguments additionnels pour pd.read_csv()
            
        Returns:
            pd.DataFrame: DataFrame contenant les données du CSV
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            pd.errors.EmptyDataError: Si le fichier est vide
            pd.errors.ParserError: Si le fichier ne peut pas être parsé
        """
        try:
            # Vérification de l'existence du fichier
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
            self.logger.info(f"Début de lecture du fichier CSV: {file_path}")
            
            # Lecture du fichier CSV
            df = pd.read_csv(file_path, **kwargs)
            
            # Vérification que le DataFrame n'est pas vide
            if df.empty:
                raise pd.errors.EmptyDataError("Le fichier CSV est vide")
            
            self.logger.info(f"Fichier CSV lu avec succès: {len(df)} lignes, {len(df.columns)} colonnes")
            self.logger.debug(f"Colonnes détectées: {list(df.columns)}")
            
            return df
            
        except FileNotFoundError as e:
            self.logger.error(f"Erreur: Fichier non trouvé - {e}")
            raise
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Erreur: Fichier vide - {e}")
            raise
        except pd.errors.ParserError as e:
            self.logger.error(f"Erreur: Impossible de parser le fichier CSV - {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture du CSV: {e}")
            raise
    
    def validate_csv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valide la structure et le contenu d'un DataFrame CSV.
        
        Args:
            df (pd.DataFrame): DataFrame à valider
            
        Returns:
            Dict[str, Any]: Informations de validation
        """
        validation_info = {
            'rows': len(df),
            'columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'is_valid': True,
            'issues': []
        }
        
        # Vérifications de base
        if df.empty:
            validation_info['is_valid'] = False
            validation_info['issues'].append("DataFrame vide")
        
        if df.duplicated().sum() > 0:
            validation_info['issues'].append(f"{df.duplicated().sum()} lignes dupliquées détectées")
        
        # Vérification des valeurs manquantes
        missing_cols = [col for col, missing in validation_info['missing_values'].items() if missing > 0]
        if missing_cols:
            validation_info['issues'].append(f"Valeurs manquantes dans: {missing_cols}")
        
        self.logger.info(f"Validation terminée: {validation_info['rows']} lignes, {validation_info['columns']} colonnes")
        if validation_info['issues']:
            self.logger.warning(f"Problèmes détectés: {validation_info['issues']}")
        
        return validation_info
