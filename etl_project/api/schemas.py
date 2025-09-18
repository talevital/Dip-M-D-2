from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class FileMetadata(BaseModel):
    original_name: str
    content_type: str
    size_bytes: int
    row_count: int
    col_count: int
    columns: List[str]


class PreviewResponse(BaseModel):
    metadata: FileMetadata
    rows: List[Dict[str, Any]]


class UploadResponse(PreviewResponse):
    file_id: int


class TransformOptions(BaseModel):
    # Missing values
    missing_strategy: Optional[str] = "fill"  # none|drop|fill|interpolate|group_fill
    # Outliers
    handle_outliers: Optional[bool] = True
    outliers_method: Optional[str] = "winsorize"  # winsorize|iqr|zscore
    # Duplicates
    remove_duplicates: Optional[bool] = True
    # Inconsistencies
    fix_inconsistencies: Optional[bool] = True
    # Normalization
    numerical_method: Optional[str] = "standard"  # standard|minmax|robust|log|boxcox
    categorical_method: Optional[str] = "label"   # label|onehot|frequency
    normalize_dates: Optional[bool] = True
    # Column-level overrides
    columns_numeric: Optional[List[str]] = None
    columns_categorical: Optional[List[str]] = None
    date_columns: Optional[List[str]] = None
    # Names correction
    names_correction_enabled: Optional[bool] = False
    names_columns: Optional[List[str]] = None
    # Name clustering
    cluster_names_enabled: Optional[bool] = False
    cluster_names_columns: Optional[List[str]] = None
    cluster_threshold: Optional[float] = 0.85
    # Text processing
    text_processing_enabled: Optional[bool] = False
    text_columns: Optional[List[str]] = None
    extract_text_features: Optional[bool] = True
    extract_keywords: Optional[bool] = False
    detect_topics: Optional[bool] = False
    # Multiple choice processing
    multiple_choice_enabled: Optional[bool] = False
    multiple_choice_columns: Optional[Dict[str, List[str]]] = None
    multiple_choice_threshold: Optional[float] = 0.8


class TransformPreviewRequest(BaseModel):
    options: TransformOptions


class TransformPreviewResponse(BaseModel):
    metadata: FileMetadata
    preview: List[Dict[str, Any]]
    clusters: Optional[Dict[str, Dict[str, List[str]]]] = None
    text_features: Optional[Dict[str, List[str]]] = None
    topics: Optional[Dict[str, List[str]]] = None
    keywords: Optional[Dict[str, List[str]]] = None


