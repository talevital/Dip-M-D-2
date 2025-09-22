"""
API ETL intégrée avec authentification FastAPI
Migration depuis Django vers FastAPI
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import pandas as pd
import os
import shutil
import io
from datetime import datetime

# Imports ETL existants
from api.db import get_engine, get_session
from api.models import Base, UploadedFile, UploadedRow
from api.schemas import (
    FileMetadata, UploadResponse, PreviewResponse,
    TransformPreviewRequest, TransformPreviewResponse
)
from api.parsers import parse_file_and_preview, detect_type, read_preview
from api.advanced_routes import include_advanced_routes

# ETL components
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from utils.helpers import DataProfiler
from etl.utils.names import NameStandardizer
from etl.utils.name_clustering import cluster_by_threshold
from etl.utils.text_processor import TextProcessor, MultiChoiceProcessor, apply_text_processing

# Imports d'authentification
from auth.models import User
from auth.auth import verify_token
from auth.database import get_db as get_auth_db

# Import du module de recherche de pays
from api.country_search import router as country_search_router

# Import logging
from loguru import logger

# Configuration de sécurité
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db = Depends(get_auth_db)
) -> User:
    """Obtenir l'utilisateur actuel à partir du token JWT"""
    token_data = verify_token(credentials.credentials)
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtenir l'utilisateur actuel actif"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_app() -> FastAPI:
    app = FastAPI(
        title="DIP Unified API", 
        description="API unifiée ETL + Authentification",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Helper to convert numpy/pandas objects to JSON-serializable Python types
    def to_native(obj):
        try:
            import numpy as np
            import pandas as pd
        except Exception:
            np = None
            pd = None

        # Scalars
        if obj is None:
            return None
        if isinstance(obj, (bool, int, float, str)):
            return obj
        # numpy scalar types
        if np and hasattr(np, 'integer') and isinstance(obj, np.integer):
            return int(obj)
        if np and hasattr(np, 'floating') and isinstance(obj, np.floating):
            return float(obj)
        if np and hasattr(np, 'bool_') and isinstance(obj, np.bool_):
            return bool(obj)
        # pandas scalar types
        if pd and hasattr(pd, 'Timestamp') and isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        # Collections
        if isinstance(obj, (list, tuple)):
            return [to_native(item) for item in obj]
        if isinstance(obj, dict):
            return {key: to_native(value) for key, value in obj.items()}
        # pandas Series
        if pd and hasattr(pd, 'Series') and isinstance(obj, pd.Series):
            return obj.tolist()
        # pandas DataFrame
        if pd and hasattr(pd, 'DataFrame') and isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        # Default fallback
        return str(obj)

    # Routes d'authentification (sans protection)
    @app.post("/auth/register")
    async def register_user(user_data: dict):
        """Rediriger vers l'API d'authentification"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8001/register", json=user_data)
            return response.json()

    @app.post("/auth/login")
    async def login_user(user_data: dict):
        """Rediriger vers l'API d'authentification"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8001/login", json=user_data)
            return response.json()

    @app.post("/auth/refresh")
    async def refresh_token(refresh_data: dict):
        """Rediriger vers l'API d'authentification"""
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8001/refresh", json=refresh_data)
            return response.json()

    # Routes ETL protégées par authentification
    @app.get("/")
    def root():
        return {"message": "DIP Unified API - ETL + Authentication", "version": "1.0.0"}

    @app.get("/files")
    def list_files(
        limit: int = 50, 
        offset: int = 0,
        current_user: User = Depends(get_current_active_user)
    ):
        """Liste des fichiers uploadés (protégé)"""
        with get_session() as session:
            files = session.query(UploadedFile).offset(offset).limit(limit).all()
            return {
                "files": [
                    {
                        "id": f.id,
                        "original_name": f.original_name,
                        "content_type": f.content_type,
                        "size_bytes": f.size_bytes,
                        "row_count": f.row_count,
                        "col_count": f.col_count,
                        "columns": f.columns,
                        "created_at": f.created_at.isoformat(),
                        "uploaded_by": f.uploaded_by  # Ajouter le champ uploaded_by
                    }
                    for f in files
                ],
                "total": session.query(UploadedFile).count(),
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email
                }
            }

    @app.get("/files/{file_id}")
    def get_file(
        file_id: int,
        current_user: User = Depends(get_current_active_user)
    ):
        """Récupère les détails d'un fichier spécifique (protégé)"""
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            return {
                "id": uf.id,
                "original_name": uf.original_name,
                "stored_path": uf.stored_path,
                "content_type": uf.content_type,
                "size_bytes": uf.size_bytes,
                "row_count": uf.row_count,
                "col_count": uf.col_count,
                "columns": uf.columns,
                "created_at": uf.created_at.isoformat(),
                "uploaded_by": uf.uploaded_by,
                "user": {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email
                }
            }

    @app.post("/files/upload")
    async def upload_file(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_active_user)
    ):
        """Upload de fichier (protégé)"""
        try:
            # Créer le dossier uploads s'il n'existe pas
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Générer un nom de fichier unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(upload_dir, filename)
            
            # Sauvegarder le fichier
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Analyser le fichier
            ftype = detect_type(file.filename, file.content_type)
            df = read_preview(file_path, ftype)
            
            # Créer l'enregistrement en base
            with get_session() as session:
                uploaded_file = UploadedFile(
                    original_name=file.filename,
                    stored_path=file_path,
                    content_type=file.content_type,
                    size_bytes=os.path.getsize(file_path),
                    row_count=len(df),
                    col_count=len(df.columns),
                    columns=list(df.columns),
                    uploaded_by=current_user.id  # Associer à l'utilisateur
                )
                session.add(uploaded_file)
                session.commit()
                session.refresh(uploaded_file)
            
            logger.info(f"File uploaded: {file.filename} by user {current_user.username}")
            
            return {
                "message": "File uploaded successfully",
                "file_id": uploaded_file.id,
                "filename": file.filename,
                "size": os.path.getsize(file_path),
                "rows": len(df),
                "columns": len(df.columns),
                "user": {
                    "id": current_user.id,
                    "username": current_user.username
                }
            }
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    @app.get("/files/{file_id}/preview")
    def preview_file(
        file_id: int,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user)
    ):
        """Aperçu du fichier (protégé)"""
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="File not found on disk")
            
            try:
                ftype = detect_type(uf.original_name, uf.content_type)
                df = read_preview(uf.stored_path, ftype)
                
                preview_data = df.head(limit).to_dict('records')
                
                return {
                    "file_id": file_id,
                    "filename": uf.original_name,
                    "total_rows": len(df),
                    "columns": list(df.columns),
                    "preview": to_native(preview_data),
                    "user": {
                        "id": current_user.id,
                        "username": current_user.username
                    }
                }
                
            except Exception as e:
                logger.error(f"Preview error: {e}")
                raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

    @app.post("/files/{file_id}/transform")
    def transform_file(
        file_id: int, 
        options: dict,
        current_user: User = Depends(get_current_active_user)
    ):
        """Endpoint pour transformer un fichier avec le HybridDataProcessor (protégé)"""
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="Original file not found")
            
            try:
                from etl.transform.hybrid_processor import HybridDataProcessor
                ftype = detect_type(uf.original_name, uf.content_type)
                df_original = read_preview(uf.stored_path, ftype)
                processor = HybridDataProcessor()
                config = {
                    'processing_mode': options.get('processing_mode', 'automatic'),
                    'handle_missing': options.get('missing_strategy', 'mean') != 'none',
                    'missing_strategy': options.get('missing_strategy', 'mean'),
                    'missing_threshold': options.get('missing_threshold', 0.5),
                    'group_by': options.get('group_by'),
                    'detect_outliers': options.get('handle_outliers', False),
                    'outlier_methods': [options.get('outlier_detection', 'iqr')],
                    'outlier_method': options.get('outliers_method', 'winsorize'),
                    'remove_duplicates': options.get('remove_duplicates', False),
                    'fix_inconsistencies': options.get('fix_inconsistencies', False),
                    'normalize_numerical': options.get('normalize_numerical', False),
                    'normalization_method': options.get('numerical_method', 'standard'),
                    'normalize_by_group': options.get('normalize_by_group', False),
                    'group_normalization_method': options.get('group_normalization_method', 'minmax'),
                    'encode_categorical': options.get('encode_categorical', False),
                    'encoding_method': options.get('categorical_method', 'label'),
                    'max_categories': options.get('max_categories', 50),
                    'normalize_dates': options.get('normalize_dates', False),
                    'extract_date_features': options.get('extract_date_features', False),
                    'date_format': options.get('date_format', '%Y-%m-%d'),
                    'apply_transformations': options.get('apply_transformations', False),
                    'transformations': options.get('transformations', []),
                    'transform_columns': options.get('transform_columns', [])
                }
                df_processed = processor.process_data_hybrid(df_original, config)
                report = processor.get_processing_report()
                output_dir = os.path.join(os.path.dirname(uf.stored_path), 'processed')
                os.makedirs(output_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_filename = f"processed_{uf.id}_{timestamp}.csv"
                output_path = os.path.join(output_dir, output_filename)
                df_processed.to_csv(output_path, index=False)
                
                logger.info(f"File transformed: {uf.original_name} by user {current_user.username}")
                
                return {
                    'success': True,
                    'original_shape': list(df_original.shape),
                    'processed_shape': list(df_processed.shape),
                    'processing_report': report,
                    'outlier_stats': processor.outlier_stats,
                    'output_path': output_path,
                    'processed_at': datetime.now().isoformat(),
                    'summary': {
                        'rows_processed': int(len(df_processed)),
                        'columns_processed': int(len(df_processed.columns)),
                        'outliers_detected': int(sum(len(stats.get('iqr', {}).get('outliers', [])) for stats in processor.outlier_stats.values())),
                        'processing_mode': config.get('processing_mode', 'automatic')
                    },
                    'user': {
                        'id': current_user.id,
                        'username': current_user.username
                    }
                }
            except Exception as e:
                logger.error(f"Erreur lors de la transformation du fichier {file_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Erreur de transformation: {str(e)}")

    @app.get("/files/{file_id}/export-hybrid")
    def export_file_hybrid(
        file_id: int, 
        format: str = "csv", 
        options: dict = None,
        current_user: User = Depends(get_current_active_user)
    ):
        """Export d'un fichier transformé avec le HybridDataProcessor (protégé)"""
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="Original file not found")
            
            try:
                from etl.transform.hybrid_processor import HybridDataProcessor
                ftype = detect_type(uf.original_name, uf.content_type)
                df_original = read_preview(uf.stored_path, ftype)
                processor = HybridDataProcessor()
                config = options or {
                    'processing_mode': 'automatic',
                    'handle_missing': True,
                    'missing_strategy': 'mean',
                    'detect_outliers': True,
                    'outlier_methods': ['iqr'],
                    'outlier_method': 'winsorize',
                    'remove_duplicates': True,
                    'fix_inconsistencies': True,
                    'normalize_numerical': True,
                    'normalization_method': 'standard',
                    'encode_categorical': True,
                    'encoding_method': 'label',
                    'normalize_dates': True,
                    'extract_date_features': True
                }
                df_processed = processor.process_data_hybrid(df_original, config)
                export_dir = os.path.join(os.path.dirname(uf.stored_path), 'exports')
                os.makedirs(export_dir, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = os.path.splitext(uf.original_name)[0]
                
                if format.lower() == "csv":
                    filename = f"{base_name}_processed_{timestamp}.csv"
                    file_path = os.path.join(export_dir, filename)
                    df_processed.to_csv(file_path, index=False)
                    media_type = "text/csv"
                    
                elif format.lower() == "xlsx":
                    filename = f"{base_name}_processed_{timestamp}.xlsx"
                    file_path = os.path.join(export_dir, filename)
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        df_processed.to_excel(writer, sheet_name='Données traitées', index=False)
                        if processor.outlier_stats:
                            outlier_summary = []
                            for col, stats in processor.outlier_stats.items():
                                for method, result in stats.items():
                                    outlier_summary.append({
                                        'Colonne': col,
                                        'Méthode': method,
                                        'Outliers détectés': result['count'],
                                        'Pourcentage': f"{result['percentage']:.2f}%"
                                    })
                            if outlier_summary:
                                outlier_df = pd.DataFrame(outlier_summary)
                                outlier_df.to_excel(writer, sheet_name='Statistiques outliers', index=False)
                        processing_info = pd.DataFrame([
                            {'Paramètre': 'Mode de traitement', 'Valeur': config.get('processing_mode', 'automatic')},
                            {'Paramètre': 'Stratégie valeurs manquantes', 'Valeur': config.get('missing_strategy', 'mean')},
                            {'Paramètre': 'Méthode normalisation', 'Valeur': config.get('normalization_method', 'standard')},
                            {'Paramètre': 'Méthode encodage', 'Valeur': config.get('encoding_method', 'label')},
                            {'Paramètre': 'Suppression doublons', 'Valeur': config.get('remove_duplicates', True)},
                            {'Paramètre': 'Correction incohérences', 'Valeur': config.get('fix_inconsistencies', True)},
                            {'Paramètre': 'Traitement des dates', 'Valeur': config.get('normalize_dates', True)},
                            {'Paramètre': 'Lignes traitées', 'Valeur': len(df_processed)},
                            {'Paramètre': 'Colonnes traitées', 'Valeur': len(df_processed.columns)},
                            {'Paramètre': 'Date de traitement', 'Valeur': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                            {'Paramètre': 'Utilisateur', 'Valeur': current_user.username}
                        ])
                        processing_info.to_excel(writer, sheet_name='Informations traitement', index=False)
                    media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    raise HTTPException(status_code=400, detail=f"Format non supporté: {format}")
                
                logger.info(f"File exported: {filename} by user {current_user.username}")
                
                return FileResponse(
                    path=file_path,
                    filename=filename,
                    media_type=media_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'export du fichier {file_id}: {e}")
                raise HTTPException(status_code=500, detail=f"Erreur d'export: {str(e)}")

    # Inclure les routes de recherche de pays AVANT les routes avancées
    app.include_router(country_search_router)
    
    # Inclure les routes avancées existantes
    include_advanced_routes(app)

    return app

# Créer l'application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
