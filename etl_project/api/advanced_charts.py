"""
Module de génération de graphiques avancés pour l'API ETL
Version simplifiée pour permettre le démarrage du serveur
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class AdvancedChartGenerator:
    """
    Générateur de graphiques avancés pour la visualisation des données
    """
    
    def __init__(self):
        self.chart_configs = {}
        self.available_charts = [
            'bar', 'line', 'scatter', 'histogram', 'box', 'pie'
        ]
    
    def create_chart(self, data: pd.DataFrame, chart_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un graphique basé sur le type et la configuration
        """
        try:
            if chart_type not in self.available_charts:
                return {
                    'success': False,
                    'error': f"Type de graphique non supporté: {chart_type}"
                }
            
            # Configuration par défaut
            default_config = {
                'title': f'Graphique {chart_type}',
                'x_axis': data.columns[0] if len(data.columns) > 0 else None,
                'y_axis': data.columns[1] if len(data.columns) > 1 else None,
                'color': '#3498db'
            }
            
            # Fusionner avec la configuration fournie
            final_config = {**default_config, **config}
            
            # Générer les données du graphique
            chart_data = self._generate_chart_data(data, chart_type, final_config)
            
            return {
                'success': True,
                'chart_type': chart_type,
                'config': final_config,
                'data': chart_data,
                'metadata': {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'generated_at': pd.Timestamp.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_chart_data(self, data: pd.DataFrame, chart_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère les données spécifiques au type de graphique
        """
        if chart_type == 'bar':
            return self._generate_bar_data(data, config)
        elif chart_type == 'line':
            return self._generate_line_data(data, config)
        elif chart_type == 'scatter':
            return self._generate_scatter_data(data, config)
        elif chart_type == 'histogram':
            return self._generate_histogram_data(data, config)
        elif chart_type == 'box':
            return self._generate_box_data(data, config)
        elif chart_type == 'pie':
            return self._generate_pie_data(data, config)
        else:
            return {'error': 'Type de graphique non implémenté'}
    
    def _generate_bar_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un graphique en barres"""
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        
        if x_col and y_col and x_col in data.columns and y_col in data.columns:
            return {
                'x': data[x_col].tolist(),
                'y': data[y_col].tolist(),
                'labels': data[x_col].tolist()
            }
        else:
            # Utiliser les premières colonnes disponibles
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                return {
                    'x': list(range(len(data))),
                    'y': data[numeric_cols[0]].tolist(),
                    'labels': [str(i) for i in range(len(data))]
                }
            return {'error': 'Pas de colonnes numériques disponibles'}
    
    def _generate_line_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un graphique linéaire"""
        return self._generate_bar_data(data, config)  # Même logique pour l'instant
    
    def _generate_scatter_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un graphique de dispersion"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            return {
                'x': data[numeric_cols[0]].tolist(),
                'y': data[numeric_cols[1]].tolist()
            }
        return {'error': 'Au moins 2 colonnes numériques requises'}
    
    def _generate_histogram_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un histogramme"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            hist, bins = np.histogram(data[col].dropna(), bins=10)
            return {
                'values': hist.tolist(),
                'bins': bins.tolist(),
                'column': col
            }
        return {'error': 'Aucune colonne numérique disponible'}
    
    def _generate_box_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un graphique en boîte"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            return {
                'values': data[col].dropna().tolist(),
                'column': col,
                'stats': {
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'median': float(data[col].median()),
                    'q1': float(data[col].quantile(0.25)),
                    'q3': float(data[col].quantile(0.75))
                }
            }
        return {'error': 'Aucune colonne numérique disponible'}
    
    def _generate_pie_data(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les données pour un graphique en secteurs"""
        categorical_cols = data.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            value_counts = data[col].value_counts()
            return {
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist()
            }
        return {'error': 'Aucune colonne catégorielle disponible'}

def create_chart_from_config(data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée un graphique à partir d'une configuration
    """
    try:
        generator = AdvancedChartGenerator()
        chart_type = config.get('type', 'bar')
        return generator.create_chart(data, chart_type, config)
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }






