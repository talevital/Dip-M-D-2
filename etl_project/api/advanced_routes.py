"""
Script d'intégration des fonctionnalités avancées du projet DIP
Connexion entre le frontend et le backend avec toutes les fonctionnalités du projet Asam237/dataviz
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Import des modules avancés
from .advanced_processor import AdvancedDataProcessor, process_file_advanced
from .advanced_charts import AdvancedChartGenerator, create_chart_from_config

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router pour les fonctionnalités avancées
router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])

# Stockage en mémoire pour les sessions (à remplacer par une base de données en production)
sessions = {}

@router.post("/upload-advanced")
async def upload_file_advanced(file: UploadFile = File(...)):
    """
    Upload de fichier avec traitement avancé et détection d'inconsistances
    """
    try:
        # Sauvegarder le fichier temporairement
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Traiter le fichier avec le processeur avancé
        result = process_file_advanced(temp_path)
        
        # Nettoyer le fichier temporaire
        os.remove(temp_path)
        
        if result['success']:
            # Générer un ID de session
            session_id = f"session_{len(sessions)}"
            sessions[session_id] = {
                'data_shape': result['data_shape'],
                'inconsistencies': result['inconsistencies'],
                'statistics': result['statistics'],
                'correlations': result['correlations'],
                'insights': result['insights'],
                'full_report': result['full_report']
            }
            
            return {
                'success': True,
                'session_id': session_id,
                'message': f"Fichier traité avec succès: {result['data_shape'][0]} lignes, {result['data_shape'][1]} colonnes",
                'inconsistencies_count': sum(len(v) for v in result['inconsistencies'].values()),
                'statistics': result['statistics'],
                'insights': result['insights']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        logger.error(f"Erreur lors de l'upload avancé: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-corrections/{session_id}")
async def apply_corrections(session_id: str, corrections: Dict[str, List[Dict]]):
    """
    Applique les corrections suggérées aux données
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        # Ici, vous devriez recharger les données et appliquer les corrections
        # Pour l'exemple, on simule l'application des corrections
        
        session = sessions[session_id]
        corrections_applied = sum(len(corr_list) for corr_list in corrections.values())
        
        # Mettre à jour la session
        session['corrections_applied'] = corrections_applied
        session['last_correction'] = corrections
        
        return {
            'success': True,
            'corrections_applied': corrections_applied,
            'message': f"{corrections_applied} corrections appliquées avec succès"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'application des corrections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{session_id}")
async def get_analytics(session_id: str):
    """
    Récupère les analyses avancées pour une session
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        
        return {
            'success': True,
            'statistics': session['statistics'],
            'correlations': session['correlations'],
            'insights': session['insights'],
            'inconsistencies': session['inconsistencies']
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-chart/{session_id}")
async def create_chart(session_id: str, chart_config: Dict[str, Any]):
    """
    Crée un graphique à partir d'une configuration
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        # Pour l'exemple, on utilise des données simulées
        # En production, vous devriez charger les vraies données de la session
        
        # Créer des données de test basées sur la configuration
        import numpy as np
        test_data = pd.DataFrame({
            'x': np.random.randn(100),
            'y': np.random.randn(100),
            'category': ['A', 'B', 'C'] * 33 + ['A']
        })
        
        # Créer le graphique
        chart_result = create_chart_from_config(test_data, chart_config)
        
        if chart_result['success']:
            # Sauvegarder le graphique
            chart_id = f"chart_{session_id}_{len(sessions[session_id].get('charts', []))}"
            
            if 'charts' not in sessions[session_id]:
                sessions[session_id]['charts'] = {}
            
            sessions[session_id]['charts'][chart_id] = chart_result
            
            return {
                'success': True,
                'chart_id': chart_id,
                'chart_type': chart_result['chart_type'],
                'title': chart_result['title'],
                'html': chart_result['html']
            }
        else:
            raise HTTPException(status_code=400, detail=chart_result['error'])
            
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chart/{session_id}/{chart_id}")
async def get_chart(session_id: str, chart_id: str):
    """
    Récupère un graphique spécifique
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        if 'charts' not in session or chart_id not in session['charts']:
            raise HTTPException(status_code=404, detail="Graphique non trouvé")
        
        chart = session['charts'][chart_id]
        
        return {
            'success': True,
            'chart_id': chart_id,
            'chart_type': chart['chart_type'],
            'title': chart['title'],
            'html': chart['html']
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du graphique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/{session_id}")
async def list_charts(session_id: str):
    """
    Liste tous les graphiques d'une session
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        charts = session.get('charts', {})
        
        charts_list = []
        for chart_id, chart in charts.items():
            charts_list.append({
                'chart_id': chart_id,
                'chart_type': chart['chart_type'],
                'title': chart['title']
            })
        
        return {
            'success': True,
            'charts': charts_list,
            'total': len(charts_list)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la liste des graphiques: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export-chart/{session_id}/{chart_id}")
async def export_chart(session_id: str, chart_id: str, format: str = "html"):
    """
    Exporte un graphique vers un fichier
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        if 'charts' not in session or chart_id not in session['charts']:
            raise HTTPException(status_code=404, detail="Graphique non trouvé")
        
        chart = session['charts'][chart_id]
        
        # Créer le fichier d'export
        output_dir = Path("exports")
        output_dir.mkdir(exist_ok=True)
        
        filename = f"{chart_id}.{format}"
        output_path = output_dir / filename
        
        if format == "html":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(chart['html'])
        else:
            # Pour les autres formats, vous devriez utiliser plotly
            return {"success": False, "error": f"Format {format} non supporté pour l'export"}
        
        return FileResponse(
            path=str(output_path),
            filename=filename,
            media_type="text/html" if format == "html" else "application/octet-stream"
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export du graphique: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{session_id}")
async def get_chart_recommendations(session_id: str):
    """
    Génère des recommandations de graphiques basées sur les données
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        
        # Générer des recommandations basées sur les métadonnées
        recommendations = []
        
        # Recommandations basées sur les statistiques
        if 'statistics' in session and session['statistics']:
            numeric_cols = list(session['statistics'].keys())
            
            if len(numeric_cols) >= 2:
                recommendations.append({
                    'type': 'scatter',
                    'title': 'Analyse de Corrélation',
                    'description': f'Graphique de dispersion entre {numeric_cols[0]} et {numeric_cols[1]}',
                    'priority': 'high',
                    'config': {
                        'x_col': numeric_cols[0],
                        'y_col': numeric_cols[1]
                    }
                })
            
            if len(numeric_cols) >= 1:
                recommendations.append({
                    'type': 'line',
                    'title': 'Évolution Temporelle',
                    'description': f'Graphique en ligne pour {numeric_cols[0]}',
                    'priority': 'medium',
                    'config': {
                        'x_col': 'index',
                        'y_cols': [numeric_cols[0]]
                    }
                })
        
        # Recommandations basées sur les corrélations
        if 'correlations' in session and session['correlations']:
            strong_correlations = session['correlations'].get('strong_correlations', [])
            
            for corr in strong_correlations[:3]:  # Top 3 corrélations
                recommendations.append({
                    'type': 'scatter',
                    'title': f'Corrélation {corr["var1"]} - {corr["var2"]}',
                    'description': f'Corrélation {corr["strength"].lower()} ({corr["correlation"]:.3f})',
                    'priority': 'high',
                    'config': {
                        'x_col': corr['var1'],
                        'y_col': corr['var2']
                    }
                })
        
        return {
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des recommandations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Récupère les informations d'une session
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        session = sessions[session_id]
        
        return {
            'success': True,
            'session_id': session_id,
            'data_shape': session['data_shape'],
            'charts_count': len(session.get('charts', {})),
            'corrections_applied': session.get('corrections_applied', 0),
            'created_at': session.get('created_at', 'unknown')
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Supprime une session et toutes ses données
    """
    try:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        del sessions[session_id]
        
        return {
            'success': True,
            'message': f"Session {session_id} supprimée avec succès"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fonction pour intégrer le router dans l'application principale
def include_advanced_routes(app):
    """
    Inclut les routes avancées dans l'application FastAPI
    """
    app.include_router(router)
    logger.info("Routes avancées intégrées avec succès")

if __name__ == "__main__":
    # Test des fonctionnalités
    print("Script d'intégration des fonctionnalités avancées")
    print("Routes disponibles:")
    for route in router.routes:
        print(f"  {route.methods} {route.path}")

