"""
Script de création de graphiques avancé pour le projet DIP
Intégration des fonctionnalités de visualisation du projet Asam237/dataviz
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import logging
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedChartGenerator:
    """
    Générateur de graphiques avancé avec fonctionnalités interactives
    """
    
    def __init__(self):
        self.data = None
        self.charts = {}
        self.chart_configs = []
        
        # Configuration des couleurs
        self.color_palette = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
            '#8B5CF6', '#06B6D4', '#F97316', '#84CC16'
        ]
        
        # Configuration des styles
        plt.style.use('seaborn-v0_8')
        sns.set_palette(self.color_palette)
    
    def load_data(self, data: pd.DataFrame):
        """
        Charge les données pour la création de graphiques
        """
        self.data = data
        logger.info(f"Données chargées pour les graphiques: {data.shape}")
    
    def create_line_chart(self, x_col: str, y_cols: List[str], title: str = "Graphique en Ligne") -> Dict[str, Any]:
        """
        Crée un graphique en ligne interactif
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            fig = go.Figure()
            
            for i, y_col in enumerate(y_cols):
                fig.add_trace(go.Scatter(
                    x=self.data[x_col],
                    y=self.data[y_col],
                    mode='lines+markers',
                    name=y_col,
                    line=dict(color=self.color_palette[i % len(self.color_palette)], width=3),
                    marker=dict(size=6, line=dict(width=2, color='white'))
                ))
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                xaxis_title=x_col,
                yaxis_title="Valeur",
                hovermode='x unified',
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            chart_id = f"line_chart_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'line',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique en ligne: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_bar_chart(self, x_col: str, y_cols: List[str], title: str = "Graphique en Barres") -> Dict[str, Any]:
        """
        Crée un graphique en barres interactif
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            fig = go.Figure()
            
            for i, y_col in enumerate(y_cols):
                fig.add_trace(go.Bar(
                    x=self.data[x_col],
                    y=self.data[y_col],
                    name=y_col,
                    marker_color=self.color_palette[i % len(self.color_palette)],
                    text=self.data[y_col],
                    textposition='auto'
                ))
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                xaxis_title=x_col,
                yaxis_title="Valeur",
                barmode='group',
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            chart_id = f"bar_chart_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'bar',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique en barres: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_pie_chart(self, labels_col: str, values_col: str, title: str = "Graphique en Secteurs") -> Dict[str, Any]:
        """
        Crée un graphique en secteurs interactif
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            fig = go.Figure(data=[go.Pie(
                labels=self.data[labels_col],
                values=self.data[values_col],
                hole=0.3,
                marker_colors=self.color_palette[:len(self.data)]
            )])
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            chart_id = f"pie_chart_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'pie',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique en secteurs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_scatter_chart(self, x_col: str, y_col: str, title: str = "Graphique de Dispersion") -> Dict[str, Any]:
        """
        Crée un graphique de dispersion interactif
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            fig = go.Figure(data=go.Scatter(
                x=self.data[x_col],
                y=self.data[y_col],
                mode='markers',
                marker=dict(
                    size=10,
                    color=self.data[y_col],
                    colorscale='Viridis',
                    showscale=True,
                    line=dict(width=2, color='white')
                ),
                text=self.data.index,
                hovertemplate=f'<b>{x_col}</b>: %{{x}}<br><b>{y_col}</b>: %{{y}}<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                xaxis_title=x_col,
                yaxis_title=y_col,
                template='plotly_white',
                height=500
            )
            
            chart_id = f"scatter_chart_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'scatter',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique de dispersion: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_radar_chart(self, categories: List[str], values_cols: List[str], title: str = "Graphique Radar") -> Dict[str, Any]:
        """
        Crée un graphique radar interactif
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            fig = go.Figure()
            
            for i, values_col in enumerate(values_cols):
                values = self.data[values_col].tolist()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=values_col,
                    line_color=self.color_palette[i % len(self.color_palette)]
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max([max(self.data[col]) for col in values_cols])]
                    )),
                title=dict(text=title, font=dict(size=20)),
                template='plotly_white',
                height=500,
                showlegend=True
            )
            
            chart_id = f"radar_chart_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'radar',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du graphique radar: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_heatmap(self, title: str = "Matrice de Corrélation") -> Dict[str, Any]:
        """
        Crée une heatmap de corrélation
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            # Calculer la matrice de corrélation
            numeric_data = self.data.select_dtypes(include=[np.number])
            correlation_matrix = numeric_data.corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix.values,
                x=correlation_matrix.columns,
                y=correlation_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=correlation_matrix.values,
                texttemplate="%{text:.2f}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=20)),
                template='plotly_white',
                height=500
            )
            
            chart_id = f"heatmap_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'heatmap',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la heatmap: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_dashboard(self, charts_config: List[Dict[str, Any]], title: str = "Dashboard") -> Dict[str, Any]:
        """
        Crée un dashboard avec plusieurs graphiques
        """
        if self.data is None:
            return {'success': False, 'error': 'Aucune donnée chargée'}
        
        try:
            # Déterminer la grille
            num_charts = len(charts_config)
            if num_charts <= 2:
                rows, cols = 1, 2
            elif num_charts <= 4:
                rows, cols = 2, 2
            elif num_charts <= 6:
                rows, cols = 2, 3
            else:
                rows, cols = 3, 3
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[config.get('title', f'Graphique {i+1}') for i, config in enumerate(charts_config)],
                specs=[[{"secondary_y": False} for _ in range(cols)] for _ in range(rows)]
            )
            
            # Ajouter chaque graphique
            for i, config in enumerate(charts_config):
                row = (i // cols) + 1
                col = (i % cols) + 1
                
                chart_type = config.get('type', 'line')
                
                if chart_type == 'line':
                    fig.add_trace(
                        go.Scatter(
                            x=self.data[config['x_col']],
                            y=self.data[config['y_cols'][0]],
                            mode='lines+markers',
                            name=config['y_cols'][0]
                        ),
                        row=row, col=col
                    )
                elif chart_type == 'bar':
                    fig.add_trace(
                        go.Bar(
                            x=self.data[config['x_col']],
                            y=self.data[config['y_cols'][0]],
                            name=config['y_cols'][0]
                        ),
                        row=row, col=col
                    )
                elif chart_type == 'scatter':
                    fig.add_trace(
                        go.Scatter(
                            x=self.data[config['x_col']],
                            y=self.data[config['y_col']],
                            mode='markers',
                            name=f"{config['x_col']} vs {config['y_col']}"
                        ),
                        row=row, col=col
                    )
            
            fig.update_layout(
                title=dict(text=title, font=dict(size=24)),
                template='plotly_white',
                height=800,
                showlegend=False
            )
            
            chart_id = f"dashboard_{len(self.charts)}"
            self.charts[chart_id] = fig
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': 'dashboard',
                'title': title,
                'html': fig.to_html(include_plotlyjs='cdn')
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du dashboard: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def export_chart(self, chart_id: str, output_path: str, format: str = 'html') -> Dict[str, Any]:
        """
        Exporte un graphique vers un fichier
        """
        if chart_id not in self.charts:
            return {'success': False, 'error': 'Graphique non trouvé'}
        
        try:
            fig = self.charts[chart_id]
            
            if format.lower() == 'html':
                fig.write_html(output_path)
            elif format.lower() == 'png':
                fig.write_image(output_path, width=1200, height=800)
            elif format.lower() == 'pdf':
                fig.write_image(output_path, format='pdf', width=1200, height=800)
            elif format.lower() == 'json':
                fig.write_json(output_path)
            else:
                return {'success': False, 'error': f'Format non supporté: {format}'}
            
            logger.info(f"Graphique exporté vers {output_path}")
            return {
                'success': True,
                'output_path': output_path,
                'format': format
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_chart_list(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste de tous les graphiques créés
        """
        charts_list = []
        for chart_id, fig in self.charts.items():
            charts_list.append({
                'chart_id': chart_id,
                'title': fig.layout.title.text if fig.layout.title else 'Sans titre',
                'type': 'unknown'  # À améliorer pour détecter le type
            })
        return charts_list
    
    def generate_chart_recommendations(self) -> List[Dict[str, Any]]:
        """
        Génère des recommandations de graphiques basées sur les données
        """
        if self.data is None:
            return []
        
        recommendations = []
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        
        # Recommandations pour les données numériques
        if len(numeric_cols) >= 2:
            recommendations.append({
                'type': 'scatter',
                'title': 'Analyse de Corrélation',
                'description': f'Graphique de dispersion entre {numeric_cols[0]} et {numeric_cols[1]}',
                'config': {
                    'x_col': numeric_cols[0],
                    'y_col': numeric_cols[1]
                }
            })
        
        if len(numeric_cols) >= 1 and len(categorical_cols) >= 1:
            recommendations.append({
                'type': 'bar',
                'title': 'Comparaison par Catégorie',
                'description': f'Graphique en barres de {numeric_cols[0]} par {categorical_cols[0]}',
                'config': {
                    'x_col': categorical_cols[0],
                    'y_cols': [numeric_cols[0]]
                }
            })
        
        # Recommandation de heatmap si plusieurs colonnes numériques
        if len(numeric_cols) >= 3:
            recommendations.append({
                'type': 'heatmap',
                'title': 'Matrice de Corrélation',
                'description': 'Heatmap des corrélations entre toutes les variables numériques',
                'config': {}
            })
        
        return recommendations

# Fonctions utilitaires pour l'intégration avec l'API
def create_chart_from_config(data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée un graphique à partir d'une configuration
    """
    generator = AdvancedChartGenerator()
    generator.load_data(data)
    
    chart_type = config.get('type', 'line')
    
    if chart_type == 'line':
        return generator.create_line_chart(
            config['x_col'], 
            config['y_cols'], 
            config.get('title', 'Graphique en Ligne')
        )
    elif chart_type == 'bar':
        return generator.create_bar_chart(
            config['x_col'], 
            config['y_cols'], 
            config.get('title', 'Graphique en Barres')
        )
    elif chart_type == 'pie':
        return generator.create_pie_chart(
            config['labels_col'], 
            config['values_col'], 
            config.get('title', 'Graphique en Secteurs')
        )
    elif chart_type == 'scatter':
        return generator.create_scatter_chart(
            config['x_col'], 
            config['y_col'], 
            config.get('title', 'Graphique de Dispersion')
        )
    elif chart_type == 'radar':
        return generator.create_radar_chart(
            config['categories'], 
            config['values_cols'], 
            config.get('title', 'Graphique Radar')
        )
    else:
        return {'success': False, 'error': f'Type de graphique non supporté: {chart_type}'}

if __name__ == "__main__":
    # Test du générateur de graphiques
    generator = AdvancedChartGenerator()
    
    # Créer des données de test
    test_data = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=12, freq='M'),
        'sales': np.random.randint(1000, 5000, 12),
        'profit': np.random.randint(100, 1000, 12),
        'category': ['A', 'B', 'C'] * 4
    })
    
    generator.load_data(test_data)
    
    # Créer quelques graphiques de test
    line_result = generator.create_line_chart('date', ['sales'], 'Ventes Mensuelles')
    bar_result = generator.create_bar_chart('category', ['sales'], 'Ventes par Catégorie')
    
    print("Graphiques créés avec succès!")
    print(f"Graphiques disponibles: {len(generator.charts)}")

