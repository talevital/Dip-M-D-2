import os
import pandas as pd
import json
from typing import List, Dict, Any
from .schemas import FileMetadata, PreviewResponse


def detect_type(filename: str, content_type: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".csv"]:
        return "csv"
    if ext in [".xlsx", ".xls"]:
        return "excel"
    if ext in [".json"] and "geojson" not in filename.lower():
        return "json"
    if ext in [".geojson"] or "geo+json" in content_type:
        return "geojson"
    raise ValueError("Unsupported file type")


def read_preview(path: str, ftype: str) -> pd.DataFrame:
    if ftype == "csv":
        return pd.read_csv(path)
    if ftype == "excel":
        return pd.read_excel(path)
    if ftype == "json":
        with open(path, "r") as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        return df
    if ftype == "geojson":
        import geopandas as gpd
        gdf = gpd.read_file(path)
        return pd.DataFrame(gdf.drop(columns=gdf.geometry.name))
    raise ValueError("Unsupported file type")


def parse_file_and_preview(path: str, filename: str, content_type: str) -> PreviewResponse:
    ftype = detect_type(filename, content_type)
    df = read_preview(path, ftype)
    df_head = df.head(100)
    rows = df_head.to_dict(orient="records")
    size = os.path.getsize(path)
    md = FileMetadata(
        original_name=filename,
        content_type=content_type,
        size_bytes=size,
        row_count=len(df),
        col_count=len(df.columns),
        columns=[str(c) for c in df.columns],
    )
    return PreviewResponse(metadata=md, rows=rows)


