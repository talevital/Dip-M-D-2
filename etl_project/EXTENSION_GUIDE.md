# Guide d'Extension du Projet ETL Python

## 🚀 Guide Étape par Étape pour Ajouter Excel, SQL et GeoJSON

Ce guide vous accompagne dans l'extension du projet ETL pour supporter de nouveaux formats de données.

---

## 📊 Étape 1 : Ajout du Support Excel

### 1.1 Créer l'Extracteur Excel

```python
# etl/extract/excel_extractor.py
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger


class ExcelExtractor:
    """Extracteur pour les fichiers Excel avec gestion d'erreurs et logging."""
    
    def __init__(self):
        self.logger = logger
    
    def read_excel(self, file_path: str, sheet_name: Optional[Union[str, int, List]] = 0, 
                   **kwargs) -> pd.DataFrame:
        """
        Lit un fichier Excel et retourne un DataFrame pandas.
        
        Args:
            file_path (str): Chemin vers le fichier Excel
            sheet_name: Nom ou index de la feuille à lire (0 par défaut)
            **kwargs: Arguments additionnels pour pd.read_excel()
            
        Returns:
            pd.DataFrame: DataFrame contenant les données Excel
        """
        try:
            # Vérification de l'existence du fichier
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
            self.logger.info(f"Début de lecture du fichier Excel: {file_path}")
            
            # Lecture du fichier Excel
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            
            # Gestion des feuilles multiples
            if isinstance(df, dict):
                self.logger.info(f"Fichier Excel avec {len(df)} feuilles détecté")
                # Retourner la première feuille par défaut
                df = list(df.values())[0]
            
            # Vérification que le DataFrame n'est pas vide
            if df.empty:
                raise pd.errors.EmptyDataError("Le fichier Excel est vide")
            
            self.logger.info(f"Fichier Excel lu avec succès: {len(df)} lignes, {len(df.columns)} colonnes")
            self.logger.debug(f"Colonnes détectées: {list(df.columns)}")
            
            return df
            
        except FileNotFoundError as e:
            self.logger.error(f"Erreur: Fichier non trouvé - {e}")
            raise
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Erreur: Fichier vide - {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture Excel: {e}")
            raise
    
    def get_sheet_names(self, file_path: str) -> List[str]:
        """
        Récupère la liste des noms de feuilles dans un fichier Excel.
        
        Args:
            file_path (str): Chemin vers le fichier Excel
            
        Returns:
            List[str]: Liste des noms de feuilles
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            self.logger.info(f"Feuilles détectées: {sheet_names}")
            return sheet_names
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture des feuilles: {e}")
            return []
    
    def read_multiple_sheets(self, file_path: str, sheet_names: Optional[List[str]] = None,
                           **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Lit plusieurs feuilles d'un fichier Excel.
        
        Args:
            file_path (str): Chemin vers le fichier Excel
            sheet_names (List[str]): Noms des feuilles à lire (None = toutes)
            **kwargs: Arguments additionnels pour pd.read_excel()
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionnaire {nom_feuille: DataFrame}
        """
        try:
            if sheet_names is None:
                sheet_names = self.get_sheet_names(file_path)
            
            self.logger.info(f"Lecture de {len(sheet_names)} feuilles: {sheet_names}")
            
            sheets_data = pd.read_excel(file_path, sheet_name=sheet_names, **kwargs)
            
            self.logger.info(f"Lecture terminée: {len(sheets_data)} feuilles chargées")
            return sheets_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture multiple: {e}")
            raise
```

### 1.2 Ajouter les Tests Excel

```python
# Dans tests/test_etl.py
def test_excel_extractor(self, tmp_path):
    """Test de l'extracteur Excel."""
    # Créer un fichier Excel de test
    df_test = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    excel_path = tmp_path / "test_data.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        df_test.to_excel(writer, sheet_name='Sheet1', index=False)
        df_test.to_excel(writer, sheet_name='Sheet2', index=False)
    
    # Test de l'extracteur
    extractor = ExcelExtractor()
    df_extracted = extractor.read_excel(str(excel_path))
    
    # Vérifications
    assert len(df_extracted) == len(df_test)
    assert list(df_extracted.columns) == list(df_test.columns)
    
    # Test des noms de feuilles
    sheet_names = extractor.get_sheet_names(str(excel_path))
    assert 'Sheet1' in sheet_names
    assert 'Sheet2' in sheet_names
```

---

## 🗄️ Étape 2 : Ajout du Support SQL

### 2.1 Créer l'Extracteur SQL

```python
# etl/extract/sql_extractor.py
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Dict, Any, List
from loguru import logger


class SQLExtractor:
    """Extracteur pour les bases de données SQL avec gestion d'erreurs et logging."""
    
    def __init__(self, connection_string: str):
        """
        Initialise l'extracteur SQL.
        
        Args:
            connection_string (str): Chaîne de connexion SQLAlchemy
        """
        self.connection_string = connection_string
        self.engine = None
        self.logger = logger
        
        try:
            self.engine = create_engine(connection_string)
            self.logger.info("Connexion SQL établie avec succès")
        except Exception as e:
            self.logger.error(f"Erreur de connexion SQL: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Exécute une requête SQL et retourne un DataFrame.
        
        Args:
            query (str): Requête SQL
            params (Dict): Paramètres de la requête
            
        Returns:
            pd.DataFrame: Résultats de la requête
        """
        try:
            self.logger.info(f"Exécution de la requête: {query[:100]}...")
            
            with self.engine.connect() as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            self.logger.info(f"Requête exécutée: {len(df)} lignes retournées")
            return df
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erreur lors de l'exécution de la requête: {e}")
            raise
    
    def get_table_schema(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère le schéma d'une table.
        
        Args:
            table_name (str): Nom de la table
            schema (str): Nom du schéma (optionnel)
            
        Returns:
            Dict[str, Any]: Informations sur le schéma
        """
        try:
            if schema:
                full_table_name = f"{schema}.{table_name}"
            else:
                full_table_name = table_name
            
            query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            {f"AND table_schema = '{schema}'" if schema else ""}
            ORDER BY ordinal_position;
            """
            
            schema_df = self.execute_query(query)
            
            schema_info = {
                'table_name': full_table_name,
                'columns': schema_df.to_dict('records'),
                'column_count': len(schema_df)
            }
            
            self.logger.info(f"Schéma de {full_table_name} récupéré: {schema_info['column_count']} colonnes")
            return schema_info
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du schéma: {e}")
            return {}
    
    def get_table_data(self, table_name: str, schema: Optional[str] = None,
                      limit: Optional[int] = None, where_clause: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère les données d'une table.
        
        Args:
            table_name (str): Nom de la table
            schema (str): Nom du schéma (optionnel)
            limit (int): Limite du nombre de lignes
            where_clause (str): Clause WHERE personnalisée
            
        Returns:
            pd.DataFrame: Données de la table
        """
        try:
            if schema:
                full_table_name = f"{schema}.{table_name}"
            else:
                full_table_name = table_name
            
            query = f"SELECT * FROM {full_table_name}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            self.logger.info(f"Récupération des données de {full_table_name}")
            return self.execute_query(query)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des données: {e}")
            raise
    
    def list_tables(self, schema: Optional[str] = None) -> List[str]:
        """
        Liste toutes les tables disponibles.
        
        Args:
            schema (str): Nom du schéma (optionnel)
            
        Returns:
            List[str]: Liste des noms de tables
        """
        try:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
            """
            
            if schema:
                query += f" AND table_schema = '{schema}'"
            
            query += " ORDER BY table_name"
            
            tables_df = self.execute_query(query)
            table_names = tables_df['table_name'].tolist()
            
            self.logger.info(f"Tables trouvées: {len(table_names)}")
            return table_names
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la liste des tables: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données.
        
        Returns:
            bool: True si la connexion fonctionne
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                self.logger.info("Test de connexion SQL réussi")
                return True
        except SQLAlchemyError as e:
            self.logger.error(f"Échec du test de connexion SQL: {e}")
            return False
    
    def close_connection(self):
        """Ferme la connexion à la base de données."""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Connexion SQL fermée")
```

### 2.2 Ajouter les Tests SQL

```python
# Dans tests/test_etl.py
def test_sql_extractor(self):
    """Test de l'extracteur SQL."""
    # Nécessite une base de données de test
    connection_string = "sqlite:///test.db"
    
    # Créer une table de test
    engine = create_engine(connection_string)
    df_test = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'value': [10.5, 20.3, 15.7]
    })
    df_test.to_sql('test_table', engine, if_exists='replace', index=False)
    
    # Test de l'extracteur
    extractor = SQLExtractor(connection_string)
    
    # Test de connexion
    assert extractor.test_connection() == True
    
    # Test de récupération de données
    df_extracted = extractor.get_table_data('test_table')
    assert len(df_extracted) == len(df_test)
    
    # Test du schéma
    schema = extractor.get_table_schema('test_table')
    assert schema['column_count'] == 3
    
    # Nettoyage
    extractor.close_connection()
    engine.dispose()
```

---

## 🗺️ Étape 3 : Ajout du Support GeoJSON

### 3.1 Créer l'Extracteur GeoJSON

```python
# etl/extract/geojson_extractor.py
import pandas as pd
import geopandas as gpd
import json
from pathlib import Path
from typing import Optional, Dict, Any, Union
from loguru import logger


class GeoJSONExtractor:
    """Extracteur pour les fichiers GeoJSON avec gestion d'erreurs et logging."""
    
    def __init__(self):
        self.logger = logger
    
    def read_geojson(self, file_path: str, **kwargs) -> gpd.GeoDataFrame:
        """
        Lit un fichier GeoJSON et retourne un GeoDataFrame.
        
        Args:
            file_path (str): Chemin vers le fichier GeoJSON
            **kwargs: Arguments additionnels pour gpd.read_file()
            
        Returns:
            gpd.GeoDataFrame: GeoDataFrame contenant les données GeoJSON
        """
        try:
            # Vérification de l'existence du fichier
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
            
            self.logger.info(f"Début de lecture du fichier GeoJSON: {file_path}")
            
            # Lecture du fichier GeoJSON
            gdf = gpd.read_file(file_path, **kwargs)
            
            # Vérification que le GeoDataFrame n'est pas vide
            if gdf.empty:
                raise pd.errors.EmptyDataError("Le fichier GeoJSON est vide")
            
            self.logger.info(f"Fichier GeoJSON lu avec succès: {len(gdf)} entités, {len(gdf.columns)} colonnes")
            self.logger.debug(f"Colonnes détectées: {list(gdf.columns)}")
            self.logger.debug(f"Type de géométrie: {gdf.geometry.geom_type.unique()}")
            
            return gdf
            
        except FileNotFoundError as e:
            self.logger.error(f"Erreur: Fichier non trouvé - {e}")
            raise
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Erreur: Fichier vide - {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors de la lecture GeoJSON: {e}")
            raise
    
    def validate_geojson(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Valide la structure et le contenu d'un GeoDataFrame.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame à valider
            
        Returns:
            Dict[str, Any]: Informations de validation
        """
        validation_info = {
            'features': len(gdf),
            'columns': len(gdf.columns),
            'geometry_column': gdf.geometry.name,
            'geometry_types': gdf.geometry.geom_type.unique().tolist(),
            'crs': str(gdf.crs) if gdf.crs else None,
            'bounds': gdf.total_bounds.tolist() if len(gdf) > 0 else None,
            'missing_values': gdf.isnull().sum().to_dict(),
            'is_valid': True,
            'issues': []
        }
        
        # Vérifications de base
        if gdf.empty:
            validation_info['is_valid'] = False
            validation_info['issues'].append("GeoDataFrame vide")
        
        # Vérification de la colonne géométrie
        if gdf.geometry.isnull().sum() > 0:
            validation_info['issues'].append(f"{gdf.geometry.isnull().sum()} géométries manquantes")
        
        # Vérification de la validité des géométries
        invalid_geometries = ~gdf.geometry.is_valid
        if invalid_geometries.sum() > 0:
            validation_info['issues'].append(f"{invalid_geometries.sum()} géométries invalides")
        
        # Vérification des valeurs manquantes
        missing_cols = [col for col, missing in validation_info['missing_values'].items() if missing > 0]
        if missing_cols:
            validation_info['issues'].append(f"Valeurs manquantes dans: {missing_cols}")
        
        self.logger.info(f"Validation terminée: {validation_info['features']} entités, {validation_info['columns']} colonnes")
        if validation_info['issues']:
            self.logger.warning(f"Problèmes détectés: {validation_info['issues']}")
        
        return validation_info
    
    def extract_properties_to_dataframe(self, gdf: gpd.GeoDataFrame) -> pd.DataFrame:
        """
        Extrait les propriétés d'un GeoDataFrame vers un DataFrame pandas.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame source
            
        Returns:
            pd.DataFrame: DataFrame avec les propriétés (sans géométrie)
        """
        try:
            # Suppression de la colonne géométrie
            df = gdf.drop(columns=[gdf.geometry.name])
            
            self.logger.info(f"Propriétés extraites: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des propriétés: {e}")
            raise
    
    def get_spatial_statistics(self, gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
        """
        Calcule des statistiques spatiales sur un GeoDataFrame.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame à analyser
            
        Returns:
            Dict[str, Any]: Statistiques spatiales
        """
        try:
            stats = {
                'total_area': gdf.geometry.area.sum() if len(gdf) > 0 else 0,
                'total_length': gdf.geometry.length.sum() if len(gdf) > 0 else 0,
                'geometry_types_count': gdf.geometry.geom_type.value_counts().to_dict(),
                'bounds': {
                    'minx': gdf.total_bounds[0] if len(gdf) > 0 else None,
                    'miny': gdf.total_bounds[1] if len(gdf) > 0 else None,
                    'maxx': gdf.total_bounds[2] if len(gdf) > 0 else None,
                    'maxy': gdf.total_bounds[3] if len(gdf) > 0 else None
                },
                'centroid': gdf.geometry.centroid.mean() if len(gdf) > 0 else None
            }
            
            self.logger.info(f"Statistiques spatiales calculées")
            return stats
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des statistiques spatiales: {e}")
            return {}
    
    def convert_to_dataframe(self, gdf: gpd.GeoDataFrame, 
                           include_coordinates: bool = True) -> pd.DataFrame:
        """
        Convertit un GeoDataFrame en DataFrame pandas.
        
        Args:
            gdf (gpd.GeoDataFrame): GeoDataFrame à convertir
            include_coordinates (bool): Inclure les coordonnées des centroïdes
            
        Returns:
            pd.DataFrame: DataFrame pandas
        """
        try:
            df = gdf.drop(columns=[gdf.geometry.name])
            
            if include_coordinates and len(gdf) > 0:
                # Ajout des coordonnées des centroïdes
                centroids = gdf.geometry.centroid
                df['centroid_x'] = centroids.x
                df['centroid_y'] = centroids.y
            
            self.logger.info(f"Conversion en DataFrame: {len(df)} lignes, {len(df.columns)} colonnes")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion: {e}")
            raise
```

### 3.2 Ajouter les Tests GeoJSON

```python
# Dans tests/test_etl.py
def test_geojson_extractor(self, tmp_path):
    """Test de l'extracteur GeoJSON."""
    # Créer un fichier GeoJSON de test
    from shapely.geometry import Point, Polygon
    
    # Points de test
    points = [
        Point(0, 0),
        Point(1, 1),
        Point(2, 2)
    ]
    
    gdf_test = gpd.GeoDataFrame({
        'id': [1, 2, 3],
        'name': ['Point A', 'Point B', 'Point C'],
        'value': [10.5, 20.3, 15.7]
    }, geometry=points, crs='EPSG:4326')
    
    geojson_path = tmp_path / "test_data.geojson"
    gdf_test.to_file(geojson_path, driver='GeoJSON')
    
    # Test de l'extracteur
    extractor = GeoJSONExtractor()
    gdf_extracted = extractor.read_geojson(str(geojson_path))
    
    # Vérifications
    assert len(gdf_extracted) == len(gdf_test)
    assert list(gdf_extracted.columns) == list(gdf_test.columns)
    
    # Test de validation
    validation_info = extractor.validate_geojson(gdf_extracted)
    assert validation_info['is_valid'] == True
    assert validation_info['features'] == len(gdf_test)
    
    # Test de conversion en DataFrame
    df_converted = extractor.convert_to_dataframe(gdf_extracted)
    assert len(df_converted) == len(gdf_test)
    assert 'centroid_x' in df_converted.columns
    assert 'centroid_y' in df_converted.columns
```

---

## 🔧 Étape 4 : Intégration dans le Pipeline Principal

### 4.1 Mettre à Jour main.py

```python
# Dans main.py, ajouter les nouveaux extracteurs
from etl.extract.excel_extractor import ExcelExtractor
from etl.extract.sql_extractor import SQLExtractor
from etl.extract.geojson_extractor import GeoJSONExtractor

def main():
    # ... code existant ...
    
    # Exemple d'utilisation des nouveaux extracteurs
    if file_path.endswith('.xlsx'):
        extractor = ExcelExtractor()
        df = extractor.read_excel(file_path)
    elif file_path.endswith('.geojson'):
        extractor = GeoJSONExtractor()
        gdf = extractor.read_geojson(file_path)
        df = extractor.convert_to_dataframe(gdf)
    elif connection_string:
        extractor = SQLExtractor(connection_string)
        df = extractor.execute_query("SELECT * FROM your_table")
    else:
        extractor = CSVExtractor()
        df = extractor.read_csv(file_path)
    
    # ... reste du pipeline ...
```

### 4.2 Mettre à Jour requirements.txt

```txt
# Ajouter les nouvelles dépendances
openpyxl>=3.1.0
geopandas>=0.13.0
shapely>=2.0.0
fiona>=1.9.0
```

---

## 📚 Documentation et Tests

### 4.3 Mettre à Jour la Documentation

Ajouter dans le README.md :

```markdown
## Formats Supportés

### CSV
- Lecture avec validation
- Gestion des encodages
- Validation de structure

### Excel
- Support des feuilles multiples
- Lecture par feuille ou toutes les feuilles
- Gestion des formats .xlsx et .xls

### SQL
- Support de multiples bases de données
- Requêtes personnalisées
- Récupération de schémas
- Listing des tables

### GeoJSON
- Lecture de données géospatiales
- Validation des géométries
- Extraction des propriétés
- Conversion vers DataFrame
- Statistiques spatiales
```

### 4.4 Tests Complets

```python
# tests/test_extensions.py
import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

class TestExtensions:
    """Tests pour les extensions Excel, SQL et GeoJSON."""
    
    def test_excel_multiple_sheets(self, tmp_path):
        """Test de lecture Excel avec feuilles multiples."""
        # Créer un fichier Excel avec plusieurs feuilles
        df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df2 = pd.DataFrame({'X': [5, 6], 'Y': [7, 8]})
        
        excel_path = tmp_path / "multi_sheet.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
        
        extractor = ExcelExtractor()
        sheets = extractor.read_multiple_sheets(str(excel_path))
        
        assert len(sheets) == 2
        assert 'Sheet1' in sheets
        assert 'Sheet2' in sheets
    
    def test_sql_schema_retrieval(self):
        """Test de récupération de schéma SQL."""
        # Test avec SQLite en mémoire
        connection_string = "sqlite:///:memory:"
        engine = create_engine(connection_string)
        
        # Créer une table de test
        df_test = pd.DataFrame({
            'id': [1, 2],
            'name': ['Alice', 'Bob'],
            'value': [10.5, 20.3]
        })
        df_test.to_sql('test_table', engine, index=False)
        
        extractor = SQLExtractor(connection_string)
        schema = extractor.get_table_schema('test_table')
        
        assert schema['column_count'] == 3
        assert len(schema['columns']) == 3
    
    def test_geojson_spatial_analysis(self, tmp_path):
        """Test d'analyse spatiale GeoJSON."""
        # Créer des données géospatiales de test
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        gdf_test = gpd.GeoDataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        }, geometry=points, crs='EPSG:4326')
        
        geojson_path = tmp_path / "test.geojson"
        gdf_test.to_file(geojson_path, driver='GeoJSON')
        
        extractor = GeoJSONExtractor()
        gdf = extractor.read_geojson(str(geojson_path))
        
        # Test des statistiques spatiales
        stats = extractor.get_spatial_statistics(gdf)
        assert 'total_area' in stats
        assert 'geometry_types_count' in stats
        assert 'bounds' in stats
```

---

## 🎯 Résumé des Extensions

### ✅ Excel Support
- [x] Lecture de fichiers .xlsx et .xls
- [x] Support des feuilles multiples
- [x] Validation et gestion d'erreurs
- [x] Tests unitaires

### ✅ SQL Support
- [x] Connexion à multiples bases de données
- [x] Exécution de requêtes personnalisées
- [x] Récupération de schémas
- [x] Listing des tables
- [x] Tests avec SQLite

### ✅ GeoJSON Support
- [x] Lecture de données géospatiales
- [x] Validation des géométries
- [x] Extraction des propriétés
- [x] Statistiques spatiales
- [x] Conversion vers DataFrame

### 🔄 Prochaines Étapes

1. **Parallélisation** : Ajouter le support multi-threading pour les gros fichiers
2. **Streaming** : Implémenter le traitement par chunks pour la mémoire
3. **API REST** : Créer une interface web pour l'upload et le traitement
4. **Monitoring** : Ajouter des métriques de performance
5. **Scheduling** : Intégrer des tâches programmées

---

**Guide d'Extension ETL** - Prêt pour l'évolution du projet 🚀
