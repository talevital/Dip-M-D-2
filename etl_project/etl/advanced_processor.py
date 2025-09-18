"""
Script de traitement de données avancé pour le projet DIP
Intégration des fonctionnalités du projet Asam237/dataviz
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedDataProcessor:
    """
    Processeur de données avancé avec fonctionnalités d'analyse intelligente
    """
    
    def __init__(self):
        self.data = None
        self.metadata = {}
        self.inconsistencies = {}
        self.statistics = {}
        
    def load_data(self, file_path: str, file_type: str = 'auto') -> Dict[str, Any]:
        """
        Charge les données depuis un fichier avec détection automatique du format
        """
        try:
            file_path = Path(file_path)
            
            if file_type == 'auto':
                file_type = file_path.suffix.lower()
            
            if file_type in ['.csv', '.txt']:
                self.data = pd.read_csv(file_path, encoding='utf-8')
            elif file_type in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            elif file_type in ['.json']:
                self.data = pd.read_json(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_type}")
            
            logger.info(f"Données chargées: {self.data.shape[0]} lignes, {self.data.shape[1]} colonnes")
            
            # Génération des métadonnées
            self.metadata = self._generate_metadata()
            
            return {
                'success': True,
                'rows': self.data.shape[0],
                'columns': self.data.shape[1],
                'metadata': self.metadata
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """
        Génère les métadonnées des données
        """
        if self.data is None:
            return {}
        
        metadata = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'created_at': datetime.now().isoformat()
        }
        
        # Analyse des types de données
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = self.data.select_dtypes(include=['object']).columns.tolist()
        datetime_columns = self.data.select_dtypes(include=['datetime64']).columns.tolist()
        
        metadata['column_types'] = {
            'numeric': numeric_columns,
            'categorical': categorical_columns,
            'datetime': datetime_columns
        }
        
        return metadata
    
    def detect_inconsistencies(self) -> Dict[str, List[Dict]]:
        """
        Détecte les inconsistances dans les données
        """
        if self.data is None:
            return {}
        
        inconsistencies = {}
        
        # Détection des formats de date inconsistants
        date_columns = [col for col in self.data.columns if 'date' in col.lower()]
        for col in date_columns:
            inconsistencies[col] = []
            for idx, value in self.data[col].items():
                if pd.notna(value) and isinstance(value, str):
                    try:
                        pd.to_datetime(value)
                    except:
                        inconsistencies[col].append({
                            'row': idx + 1,
                            'original': value,
                            'suggestion': 'Format de date invalide',
                            'type': 'Format de Date'
                        })
        
        # Détection des formats numériques inconsistants
        numeric_columns = self.data.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            inconsistencies[col] = []
            for idx, value in self.data[col].items():
                if pd.notna(value) and isinstance(value, str):
                    # Vérifier si c'est un nombre avec des virgules
                    if ',' in str(value) and str(value).replace(',', '').replace('.', '').isdigit():
                        cleaned_value = float(str(value).replace(',', '.'))
                        inconsistencies[col].append({
                            'row': idx + 1,
                            'original': value,
                            'suggestion': cleaned_value,
                            'type': 'Format de Nombre'
                        })
        
        # Détection des valeurs aberrantes (outliers)
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in inconsistencies:
                inconsistencies[col] = []
            
            Q1 = self.data[col].quantile(0.25)
            Q3 = self.data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = self.data[(self.data[col] < lower_bound) | (self.data[col] > upper_bound)]
            for idx in outliers.index:
                inconsistencies[col].append({
                    'row': idx + 1,
                    'original': self.data.loc[idx, col],
                    'suggestion': 'Valeur aberrante détectée',
                    'type': 'Outlier'
                })
        
        self.inconsistencies = inconsistencies
        return inconsistencies
    
    def apply_corrections(self, corrections: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Applique les corrections suggérées
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        corrected_data = self.data.copy()
        corrections_applied = 0
        
        for col, corrections_list in corrections.items():
            for correction in corrections_list:
                row_idx = correction['row'] - 1
                if row_idx < len(corrected_data) and col in corrected_data.columns:
                    if correction['type'] == 'Format de Nombre':
                        corrected_data.iloc[row_idx, corrected_data.columns.get_loc(col)] = correction['suggestion']
                        corrections_applied += 1
        
        self.data = corrected_data
        logger.info(f"{corrections_applied} corrections appliquées")
        
        return {
            'success': True,
            'corrections_applied': corrections_applied,
            'new_shape': self.data.shape
        }
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calcule les statistiques descriptives avancées
        """
        if self.data is None:
            return {}
        
        stats = {}
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = self.data[col].dropna()
            if len(col_data) > 0:
                stats[col] = {
                    'count': len(col_data),
                    'mean': float(col_data.mean()),
                    'median': float(col_data.median()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'q25': float(col_data.quantile(0.25)),
                    'q75': float(col_data.quantile(0.75)),
                    'skewness': float(col_data.skew()),
                    'kurtosis': float(col_data.kurtosis()),
                    'coefficient_variation': float(col_data.std() / col_data.mean()) if col_data.mean() != 0 else 0
                }
        
        self.statistics = stats
        return stats
    
    def calculate_correlations(self) -> Dict[str, Any]:
        """
        Calcule les corrélations entre variables numériques
        """
        if self.data is None:
            return {}
        
        numeric_data = self.data.select_dtypes(include=[np.number])
        correlation_matrix = numeric_data.corr()
        
        # Trouver les corrélations fortes (> 0.7)
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'var1': correlation_matrix.columns[i],
                        'var2': correlation_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'Forte' if abs(corr_value) > 0.8 else 'Modérée'
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }
    
    def detect_trends(self, column: str) -> Dict[str, Any]:
        """
        Détecte les tendances dans une colonne numérique
        """
        if self.data is None or column not in self.data.columns:
            return {}
        
        col_data = self.data[column].dropna()
        if len(col_data) < 2:
            return {}
        
        # Calcul de la tendance linéaire
        x = np.arange(len(col_data))
        y = col_data.values
        
        # Régression linéaire simple
        slope = np.corrcoef(x, y)[0, 1] * (np.std(y) / np.std(x))
        
        # Classification de la tendance
        if slope > 0.1:
            trend = 'increasing'
            trend_label = 'Croissante'
        elif slope < -0.1:
            trend = 'decreasing'
            trend_label = 'Décroissante'
        else:
            trend = 'stable'
            trend_label = 'Stable'
        
        # Calcul de la volatilité
        volatility = (col_data.std() / col_data.mean()) * 100 if col_data.mean() != 0 else 0
        
        # Prédiction simple
        recent_avg = col_data.tail(min(10, len(col_data))).mean()
        if trend == 'increasing':
            prediction = recent_avg * 1.1
        elif trend == 'decreasing':
            prediction = recent_avg * 0.9
        else:
            prediction = recent_avg
        
        return {
            'trend': trend,
            'trend_label': trend_label,
            'slope': float(slope),
            'volatility': float(volatility),
            'prediction': float(prediction),
            'recent_average': float(recent_avg)
        }
    
    def generate_insights(self) -> Dict[str, Any]:
        """
        Génère des insights automatiques sur les données
        """
        if self.data is None:
            return {}
        
        insights = {
            'data_quality': {},
            'recommendations': [],
            'observations': []
        }
        
        # Qualité des données
        total_cells = self.data.shape[0] * self.data.shape[1]
        missing_cells = self.data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100
        
        insights['data_quality'] = {
            'completeness': completeness,
            'missing_values': int(missing_cells),
            'total_cells': total_cells,
            'quality_score': 'Excellent' if completeness > 95 else 'Bon' if completeness > 80 else 'Moyen'
        }
        
        # Observations
        insights['observations'].append(f"Dataset de {self.data.shape[0]} lignes et {self.data.shape[1]} colonnes")
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            insights['observations'].append(f"{len(numeric_cols)} variables numériques détectées")
        
        # Recommandations
        if completeness < 80:
            insights['recommendations'].append("Considérez le nettoyage des valeurs manquantes")
        
        if len(numeric_cols) > 2:
            insights['recommendations'].append("Analysez les corrélations entre variables numériques")
        
        if len(self.data) > 1000:
            insights['recommendations'].append("Dataset volumineux - considérez l'échantillonnage pour les visualisations")
        
        return insights
    
    def export_processed_data(self, output_path: str, format: str = 'csv') -> Dict[str, Any]:
        """
        Exporte les données traitées
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée à exporter'}
        
        try:
            if format.lower() == 'csv':
                self.data.to_csv(output_path, index=False)
            elif format.lower() == 'excel':
                self.data.to_excel(output_path, index=False)
            elif format.lower() == 'json':
                self.data.to_json(output_path, orient='records', indent=2)
            else:
                return {'success': False, 'error': f'Format non supporté: {format}'}
            
            logger.info(f"Données exportées vers {output_path}")
            return {
                'success': True,
                'output_path': output_path,
                'rows_exported': self.data.shape[0],
                'columns_exported': self.data.shape[1]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de synthèse complet
        """
        if self.data is None:
            return {}
        
        # Calculer toutes les métriques
        stats = self.calculate_statistics()
        correlations = self.calculate_correlations()
        insights = self.generate_insights()
        
        report = {
            'metadata': self.metadata,
            'statistics': stats,
            'correlations': correlations,
            'insights': insights,
            'inconsistencies': self.inconsistencies,
            'generated_at': datetime.now().isoformat()
        }
        
        return report

# Fonctions utilitaires pour l'intégration avec l'API
def process_file_advanced(file_path: str) -> Dict[str, Any]:
    """
    Fonction principale pour traiter un fichier avec toutes les fonctionnalités avancées
    """
    processor = AdvancedDataProcessor()
    
    # Charger les données
    load_result = processor.load_data(file_path)
    if not load_result['success']:
        return load_result
    
    # Détecter les inconsistances
    inconsistencies = processor.detect_inconsistencies()
    
    # Calculer les statistiques
    statistics = processor.calculate_statistics()
    
    # Calculer les corrélations
    correlations = processor.calculate_correlations()
    
    # Générer les insights
    insights = processor.generate_insights()
    
    # Générer le rapport complet
    report = processor.get_summary_report()
    
    return {
        'success': True,
        'data_shape': processor.data.shape,
        'inconsistencies': inconsistencies,
        'statistics': statistics,
        'correlations': correlations,
        'insights': insights,
        'full_report': report
    }

if __name__ == "__main__":
    # Test du processeur
    processor = AdvancedDataProcessor()
    
    # Exemple d'utilisation
    result = process_file_advanced("sample_data.csv")
    print(json.dumps(result, indent=2, ensure_ascii=False))

