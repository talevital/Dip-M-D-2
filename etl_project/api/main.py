from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import List, Optional
import pandas as pd
import os
import shutil
import io
from datetime import datetime

from .db import get_engine, get_session
from .models import Base, UploadedFile, UploadedRow
from .schemas import (
    FileMetadata, UploadResponse, PreviewResponse,
    TransformPreviewRequest, TransformPreviewResponse
)
from .parsers import parse_file_and_preview, detect_type, read_preview
from .advanced_routes import include_advanced_routes

# ETL components
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from utils.helpers import DataProfiler
from etl.utils.names import NameStandardizer
from etl.utils.name_clustering import cluster_by_threshold
from etl.utils.text_processor import TextProcessor, MultiChoiceProcessor, apply_text_processing

# Import logging
from loguru import logger


def create_app() -> FastAPI:
    app = FastAPI(title="ETL Upload API", version="0.1.0")

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
        if 'np' in locals() and np is not None:
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            if isinstance(obj, (np.bool_,)):
                return bool(obj)
            if isinstance(obj, (np.ndarray,)):
                return [to_native(x) for x in obj.tolist()]
        # pandas types
        if 'pd' in locals() and pd is not None:
            if isinstance(obj, (pd.Timestamp,)):
                return obj.isoformat()
            if isinstance(obj, (pd.Series,)):
                return to_native(obj.to_dict())
            if isinstance(obj, (pd.DataFrame,)):
                return [to_native(r) for r in obj.to_dict(orient='records')]
            if isinstance(obj, pd.Categorical):
                return list(obj)
            if hasattr(obj, 'dtype') and isinstance(obj.dtype, pd.CategoricalDtype):
                return str(obj)
            if hasattr(obj, 'dtype') and 'Float64DType' in str(type(obj.dtype)):
                return str(obj)
        # dict
        if isinstance(obj, dict):
            return {str(to_native(k)): to_native(v) for k, v in obj.items()}
        # list/tuple
        if isinstance(obj, (list, tuple, set)):
            return [to_native(x) for x in obj]
        # fallback to string
        try:
            return str(obj)
        except Exception:
            return None

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    engine = get_engine()
    Base.metadata.create_all(engine)
    
    # Inclure les routes avancées
    include_advanced_routes(app)

    upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    upload_dir = os.path.abspath(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)

    @app.post("/upload", response_model=UploadResponse)
    async def upload_file(file: UploadFile = File(...)):
        filename = file.filename or "uploaded_file"
        content_type = file.content_type or "application/octet-stream"

        # Save temp file
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        stored_name = f"{ts}_{filename}"
        stored_path = os.path.join(upload_dir, stored_name)
        try:
            with open(stored_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            await file.close()

        # Parse & preview
        try:
            preview = parse_file_and_preview(stored_path, filename, content_type)
        except ValueError as e:
            os.remove(stored_path)
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            os.remove(stored_path)
            raise HTTPException(status_code=500, detail=f"Parsing error: {e}")

        # Persist metadata and first rows
        with get_session() as session:
            uf = UploadedFile(
                original_name=filename,
                stored_path=stored_path,
                content_type=content_type,
                size_bytes=preview.metadata.size_bytes,
                row_count=preview.metadata.row_count,
                col_count=preview.metadata.col_count,
                columns=preview.metadata.columns,
            )
            session.add(uf)
            session.flush()

            # store first 100 rows to JSON table for quick preview
            for i, row in enumerate(preview.rows[:100]):
                session.add(UploadedRow(file_id=uf.id, row_index=i, data=row))

            session.commit()

            return UploadResponse(
                file_id=uf.id,
                metadata=preview.metadata,
                rows=preview.rows,
            )

    @app.get("/files/{file_id}/preview", response_model=PreviewResponse)
    def get_preview(file_id: int, rows: int = 10):
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            # Clamp requested rows between 1 and 100 (we store up to 100 rows)
            try:
                requested_rows = int(rows)
            except Exception:
                requested_rows = 10
            requested_rows = max(1, min(100, requested_rows))
            rows = (
                session.query(UploadedRow)
                .filter(UploadedRow.file_id == file_id)
                .order_by(UploadedRow.row_index)
                .limit(requested_rows)
                .all()
            )
            rows_json = [r.data for r in rows]
            md = FileMetadata(
                original_name=uf.original_name,
                content_type=uf.content_type,
                size_bytes=uf.size_bytes,
                row_count=uf.row_count,
                col_count=uf.col_count,
                columns=uf.columns,
            )
            return PreviewResponse(metadata=md, rows=rows_json)

    @app.get("/files")
    def list_files(limit: int = 50, offset: int = 0):
        with get_session() as session:
            # Get total count
            total_count = session.query(UploadedFile).count()
            
            # Get paginated items
            q = (
                session.query(UploadedFile)
                .order_by(UploadedFile.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            items = []
            for uf in q.all():
                items.append({
                    "id": uf.id,
                    "original_name": uf.original_name,
                    "content_type": uf.content_type,
                    "size_bytes": uf.size_bytes,
                    "row_count": uf.row_count,
                    "col_count": uf.col_count,
                    "created_at": uf.created_at.isoformat(),
                })
            return {
                "items": items, 
                "limit": limit, 
                "offset": offset,
                "total_count": total_count,
                "total_pages": (total_count + limit - 1) // limit,
                "current_page": (offset // limit) + 1
            }

    @app.delete("/files/{file_id}")
    def delete_file(file_id: int):
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Delete stored file
            try:
                if os.path.exists(uf.stored_path):
                    os.remove(uf.stored_path)
            except Exception as e:
                logger.warning(f"Failed to delete file {uf.stored_path}: {e}")
            
            # Delete from database (cascade will handle uploaded_rows)
            session.delete(uf)
            session.commit()
            
            return {"message": "File deleted successfully"}

    @app.get("/files/{file_id}/export")
    def export_file(file_id: int, format: str = "csv"):
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="Original file not found")
            
            try:
                # Initialize ETL components
                cleaner = DataCleaner()
                normalizer = DataNormalizer()
                enricher = DataEnricher()
                profiler = DataProfiler()
                
                # Read original file
                ftype = detect_type(uf.original_name, uf.content_type)
                df_original = read_preview(uf.stored_path, ftype)
                
                # Profile original data
                profile_original = profiler.profile_dataframe(df_original)
                
                # Apply ETL transformations
                logger.info(f"Starting ETL pipeline for file {file_id}")
                
                df_cleaned = cleaner.clean_data(
                    df_original,
                    missing_strategy='fill',
                    remove_duplicates=True,
                    handle_outliers=True,
                    fix_inconsistencies=True
                )
                logger.info(f"Cleaning completed: {len(df_original)} -> {len(df_cleaned)} rows")
                
                df_normalized = normalizer.normalize_data(
                    df_cleaned,
                    numerical_method='standard',
                    categorical_method='label',
                    normalize_dates=True
                )
                logger.info(f"Normalization completed: {len(df_normalized.columns)} columns")
                
                # Apply enrichment with default transformations
                conditions = {}
                if 'pib_millions' in df_normalized.columns and 'population_millions' in df_normalized.columns:
                    conditions['pib_par_habitant'] = lambda df: df['pib_millions'] / df['population_millions']
                if 'export_millions' in df_normalized.columns and 'import_millions' in df_normalized.columns:
                    conditions['balance_commerciale'] = lambda df: df['export_millions'] - df['import_millions']
                
                aggregations = None
                if len(df_normalized.select_dtypes(include=['number']).columns) > 0:
                    group_col = 'pays' if 'pays' in df_normalized.columns else df_normalized.columns[0]
                    num_cols = df_normalized.select_dtypes(include=['number']).columns[:3]
                    if len(num_cols) > 0:
                        aggregations = {
                            'group_by': group_col,
                            'aggregations': {col: ['mean', 'sum'] for col in num_cols},
                            'prefix': 'agg'
                        }
                
                time_features = None
                if 'date_creation' in df_normalized.columns:
                    time_features = {
                        'date_column': 'date_creation',
                        'features': ['year', 'month', 'quarter', 'is_weekend']
                    }
                
                df_enriched = enricher.enrich_data(
                    df_normalized,
                    conditional_columns=conditions,
                    aggregations=aggregations,
                    time_features=time_features
                )
                logger.info(f"Enrichment completed: {len(df_normalized.columns)} -> {len(df_enriched.columns)} columns")
                
                # Profile final data
                profile_final = profiler.profile_dataframe(df_enriched)
                # Build a compact profile for API
                compact_profile = {
                    "basic_info": profile_final.get("basic_info", {}),
                    "data_types": {
                        "dtype_counts": (profile_final.get("data_types", {}) or {}).get("dtype_counts", {})
                    },
                    "missing_values": profile_final.get("missing_values", {}),
                    "duplicates": profile_final.get("duplicates", {}),
                }
                
                # Export based on format
                if format.lower() == "csv":
                    output = io.StringIO()
                    df_enriched.to_csv(output, index=False)
                    output.seek(0)
                    
                    return StreamingResponse(
                        io.BytesIO(output.getvalue().encode()),
                        media_type="text/csv",
                        headers={"Content-Disposition": f"attachment; filename=transformed_{uf.original_name}"}
                    )
                
                elif format.lower() == "json":
                    data_records = df_enriched.to_dict(orient="records")
                    meta = {
                        "original_rows": len(df_original),
                        "transformed_rows": len(df_enriched),
                        "original_columns": len(df_original.columns),
                        "transformed_columns": len(df_enriched.columns),
                        "cleaning_stats": {
                            "rows_removed": len(df_original) - len(df_cleaned),
                            "duplicates_removed": profile_original.get('duplicates', {}).get('total_duplicates', 0),
                            "missing_values_filled": profile_original.get('missing_values', {}).get('total_missing', 0)
                        },
                        "transformation_summary": {
                            "numerical_normalized": len([c for c in df_normalized.columns if c.endswith('_normalized')]),
                            "categorical_encoded": len([c for c in df_normalized.columns if c.endswith('_encoded')]),
                            "new_features_created": len(df_enriched.columns) - len(df_normalized.columns)
                        }
                    }
                    meta["profile"] = compact_profile
                    return {
                        "data": to_native(data_records),
                        "metadata": to_native(meta)
                    }
                
                else:
                    raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'json'")
                    
            except Exception as e:
                logger.error(f"Export error: {e}")
                raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

    @app.post("/files/{file_id}/transform-preview", response_model=TransformPreviewResponse)
    def transform_preview(file_id: int, body: TransformPreviewRequest, rows: int = 10):
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="Original file not found")

            try:
                # Read and detect type
                ftype = detect_type(uf.original_name, uf.content_type)
                df = read_preview(uf.stored_path, ftype)

                # Apply options
                opts = body.options
                cleaner = DataCleaner()
                normalizer = DataNormalizer()
                enricher = DataEnricher()

                # Cleaning (apply steps individually to avoid wrong kwargs propagation)
                df_clean = df.copy()
                # Missing values
                ms = (opts.missing_strategy or 'none')
                if ms != 'none':
                    df_clean = cleaner.handle_missing_values(df_clean, strategy=ms)
                # Duplicates
                if bool(opts.remove_duplicates):
                    df_clean = cleaner.remove_duplicates(df_clean)
                # Outliers
                if bool(opts.handle_outliers):
                    df_clean = cleaner.handle_outliers(df_clean, method=(opts.outliers_method or 'winsorize'))
                # Inconsistencies
                if bool(opts.fix_inconsistencies):
                    df_clean = cleaner.fix_inconsistencies(df_clean)

                # Normalization
                df_norm = normalizer.normalize_data(
                    df_clean,
                    numerical_method=opts.numerical_method or 'standard',
                    categorical_method=opts.categorical_method or 'label',
                    normalize_dates=bool(opts.normalize_dates)
                )

                # Names correction (optional)
                if bool(getattr(opts, 'names_correction_enabled', False)):
                    std = NameStandardizer(os.path.join(os.path.dirname(__file__), '..', 'resources', 'names_reference.csv'))
                    for col in (opts.names_columns or []):
                        if col in df_norm.columns:
                            df_norm[col] = df_norm[col].astype(str).map(lambda v: std.standardize_full_name(v))

                # Optional: name clustering summary (does not modify data; returns clusters)
                clusters_summary = {}
                if bool(getattr(opts, 'cluster_names_enabled', False)):
                    cols = (opts.cluster_names_columns or [])
                    thr = float(getattr(opts, 'cluster_threshold', 0.85) or 0.85)
                    for col in cols:
                        if col in df_norm.columns:
                            sample = df_norm[col].astype(str).dropna().head(500).tolist()
                            clusters = cluster_by_threshold(sample, threshold=thr)
                            # Only keep clusters with size > 1
                            clusters_summary[col] = [c for c in clusters if len(c) > 1][:20]

                # Text processing (optional)
                text_features = {}
                topics = {}
                keywords = {}
                if bool(getattr(opts, 'text_processing_enabled', False)):
                    text_processor = TextProcessor()
                    text_cols = opts.text_columns or []
                    
                    for col in text_cols:
                        if col in df_norm.columns:
                            # Extract text features
                            if bool(getattr(opts, 'extract_text_features', True)):
                                features_df = pd.DataFrame([
                                    text_processor.extract_text_features(str(text))
                                    for text in df_norm[col]
                                ])
                                # Add features to dataframe
                                for feature in features_df.columns:
                                    df_norm[f"{col}_{feature}"] = features_df[feature]
                            
                            # Extract keywords
                            if bool(getattr(opts, 'extract_keywords', False)):
                                texts = df_norm[col].dropna().astype(str).tolist()
                                if texts:
                                    extracted_keywords = text_processor.extract_keywords(texts[:100])  # Limit for performance
                                    keywords[col] = extracted_keywords[:10]  # Keep top 10
                            
                            # Detect topics
                            if bool(getattr(opts, 'detect_topics', False)):
                                texts = df_norm[col].dropna().astype(str).tolist()
                                if len(texts) > 5:
                                    detected_topics, _ = text_processor.detect_topics(texts[:100])  # Limit for performance
                                    topics[col] = detected_topics[:5]  # Keep top 5 topics

                # Multiple choice processing (optional)
                if bool(getattr(opts, 'multiple_choice_enabled', False)):
                    multi_processor = MultiChoiceProcessor(text_processor)
                    multi_cols = opts.multiple_choice_columns or {}
                    threshold = float(getattr(opts, 'multiple_choice_threshold', 0.8) or 0.8)
                    
                    for col, possible_values in multi_cols.items():
                        if col in df_norm.columns:
                            df_norm = multi_processor.standardize_multiple_choice(
                                df_norm, col, possible_values, threshold
                            )

                # No enrichment by default in preview; keep fast
                try:
                    requested_rows = int(rows)
                except Exception:
                    requested_rows = 10
                requested_rows = max(1, min(100, requested_rows))
                df_preview = df_norm.head(requested_rows)

                md = FileMetadata(
                    original_name=uf.original_name,
                    content_type=uf.content_type,
                    size_bytes=uf.size_bytes,
                    row_count=len(df_norm),
                    col_count=len(df_norm.columns),
                    columns=[str(c) for c in df_norm.columns]
                )

                resp = TransformPreviewResponse(
                    metadata=md,
                    preview=to_native(df_preview.to_dict(orient='records'))
                )
                # Attach additional data in returned dict (pydantic to dict handled by FastAPI)
                return {
                    **resp.model_dump(), 
                    "clusters": to_native(clusters_summary),
                    "text_features": to_native(text_features),
                    "topics": to_native(topics),
                    "keywords": to_native(keywords)
                }

            except Exception as e:
                logger.error(f"Transform preview error: {e}")
                raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

    @app.post("/files/{file_id}/run-etl")
    def run_etl_pipeline(file_id: int):
        """Run the complete ETL pipeline on a file and save results"""
        with get_session() as session:
            uf = session.get(UploadedFile, file_id)
            if not uf:
                raise HTTPException(status_code=404, detail="File not found")
            
            if not os.path.exists(uf.stored_path):
                raise HTTPException(status_code=404, detail="Original file not found")
            
            try:
                # Import ETL modules dynamically to avoid startup issues
                import subprocess
                import sys
                
                # Run the ETL pipeline as a subprocess
                result = subprocess.run([
                    sys.executable, 
                    "test_etl.py", 
                    str(file_id)
                ], capture_output=True, text=True, cwd=os.getcwd())
                
                if result.returncode != 0:
                    logger.error(f"ETL subprocess failed: {result.stderr}")
                    raise HTTPException(status_code=500, detail=f"ETL pipeline failed: {result.stderr}")
                
                # Check if output file was created
                output_dir = os.path.join(os.path.dirname(uf.stored_path), "..", "transformed")
                output_filename = f"transformed_{uf.original_name}"
                output_path = os.path.join(output_dir, output_filename)
                
                if not os.path.exists(output_path):
                    raise HTTPException(status_code=500, detail="ETL completed but output file not found")
                
                return {
                    "message": "ETL pipeline completed successfully",
                    "output_file": output_path,
                    "logs": result.stdout
                }
                    
            except Exception as e:
                logger.error(f"ETL pipeline error: {e}")
                raise HTTPException(status_code=500, detail=f"ETL pipeline failed: {str(e)}")

    # ===== SCORING ENDPOINTS =====
    
    @app.get("/api/scoring/countries")
    def get_all_countries_scores(year: Optional[int] = None):
        """Récupère les scores de tous les pays"""
        try:
            from etl.ml.supervised_classifier import process_file_scoring
            
            # Utiliser les données de test pour l'instant
            result = process_file_scoring("test_data", year)
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=result.get('error', 'Erreur de scoring'))
            
            return {
                "success": True,
                "year": year,
                "countries": result['global_scores'],
                "summary": result['summary']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des scores: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")
    
    @app.get("/api/scoring/countries/{country_code}")
    def get_country_scores(country_code: str, year: Optional[int] = None):
        """Récupère les scores d'un pays spécifique"""
        try:
            from etl.ml.supervised_classifier import get_country_scores
            
            result = get_country_scores("test_data", country_code, year)
            
            if not result['success']:
                raise HTTPException(status_code=404, detail=result.get('error', 'Pays non trouvé'))
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du score du pays {country_code}: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")
    
    @app.get("/api/scoring/dimensions/{country_code}")
    def get_country_dimensions(country_code: str, year: Optional[int] = None):
        """Récupère le détail des dimensions pour un pays"""
        try:
            from etl.ml.supervised_classifier import get_country_scores
            
            result = get_country_scores("test_data", country_code, year)
            
            if not result['success']:
                raise HTTPException(status_code=404, detail=result.get('error', 'Pays non trouvé'))
            
            return {
                "success": True,
                "country": result['country'],
                "country_code": country_code,
                "year": year,
                "dimensions": result['data']['dimensions']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des dimensions pour {country_code}: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")
    
    @app.get("/api/scoring/history/{country_code}")
    def get_country_evolution(country_code: str):
        """Récupère l'évolution des scores d'un pays sur la période"""
        try:
            from etl.ml.supervised_classifier import get_country_scores
            
            result = get_country_scores("test_data", country_code)
            
            if not result['success']:
                raise HTTPException(status_code=404, detail=result.get('error', 'Pays non trouvé'))
            
            return {
                "success": True,
                "country": result['country'],
                "country_code": country_code,
                "evolution": result['evolution']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'évolution pour {country_code}: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")
    
    @app.get("/api/scoring/uemoa")
    def get_uemoa_scores(year: Optional[int] = None):
        """Récupère les scores des pays UEMOA"""
        try:
            from etl.ml.supervised_classifier import process_file_scoring
            
            result = process_file_scoring("test_data", year)
            
            if not result['success']:
                raise HTTPException(status_code=500, detail=result.get('error', 'Erreur de scoring'))
            
            # Filtrer pour les pays UEMOA uniquement
            uemoa_countries = ["Bénin", "Burkina Faso", "Côte d'Ivoire", "Guinée-Bissau", 
                              "Mali", "Niger", "Sénégal", "Togo"]
            
            uemoa_scores = {country: result['global_scores'][country] 
                           for country in uemoa_countries 
                           if country in result['global_scores']}
            
            return {
                "success": True,
                "year": year,
                "uemoa_countries": uemoa_scores,
                "ranking": sorted(uemoa_scores.items(), 
                                key=lambda x: x[1]['global_score'], 
                                reverse=True)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des scores UEMOA: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de scoring: {str(e)}")

    return app


app = create_app()


