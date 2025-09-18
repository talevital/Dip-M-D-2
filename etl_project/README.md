# Projet ETL Python - Documentation Complète

## 📋 Table des Matières

1. [Installation](#installation)
2. [Structure du Projet](#structure-du-projet)
3. [Utilisation](#utilisation)
4. [Modules et Fonctionnalités](#modules-et-fonctionnalités)
5. [Exemples d'Utilisation](#exemples-dutilisation)
6. [Tests](#tests)
7. [Extension du Projet](#extension-du-projet)
8. [Dépannage](#dépannage)

## 🚀 Installation

### Prérequis

- Python 3.8+
- PostgreSQL (optionnel pour le chargement)
- pip

### Installation des Dépendances

```bash
# Cloner ou télécharger le projet
cd etl_project

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration de la Base de Données (Optionnel)

Pour utiliser le chargement PostgreSQL, configurez la variable d'environnement :

```bash
# Linux/Mac
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"

# Windows
set DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

## 📁 Structure du Projet

```
etl_project/
│
├─ etl/                          # Modules ETL principaux
│   ├─ extract/                  # Extraction de données
│   │   └─ csv_extractor.py      # Extracteur CSV avec validation
│   │
│   ├─ transform/                # Transformation de données
│   │   ├─ clean_data.py         # Nettoyage (valeurs manquantes, doublons, etc.)
│   │   ├─ normalize_data.py     # Normalisation et standardisation
│   │   └─ enrich_data.py        # Enrichissement et création de features
│   │
│   └─ load/                     # Chargement de données
│       └─ load_postgres.py      # Chargement PostgreSQL avec SQLAlchemy
│
├─ utils/                        # Utilitaires
│   └─ helpers.py               # Profilage et validation des données
│
├─ tests/                        # Tests unitaires
│   └─ test_etl.py              # Tests du pipeline ETL
│
├─ main.py                       # Point d'entrée principal
├─ requirements.txt              # Dépendances Python
└─ README.md                     # Cette documentation
```

## 🎯 Utilisation

### Démarrage Rapide

```bash
# Option 1: Script unifié (recommandé)
python start.py api    # Démarre l'API FastAPI
python start.py etl    # Lance le pipeline ETL

# Option 2: Scripts individuels
python start_api.py    # Démarre l'API FastAPI
python start_etl.py    # Lance le pipeline ETL

# Option 3: Commandes directes
python main.py         # Pipeline ETL avec données d'exemple
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000  # API FastAPI
```

### 🚀 Démarrage de l'API

```bash
# Depuis le répertoire etl_project/
python start.py api

# L'API sera disponible sur:
# - http://localhost:8000
# - Documentation: http://localhost:8000/docs
# - Interface interactive: http://localhost:8000/redoc
```

### Utilisation Programmée

```python
from etl.extract.csv_extractor import CSVExtractor
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from etl.load.load_postgres import PostgreSQLLoader
from utils.helpers import DataProfiler

# 1. Extraction
extractor = CSVExtractor()
df = extractor.read_csv('your_data.csv')

# 2. Nettoyage
cleaner = DataCleaner()
df_clean = cleaner.clean_data(df)

# 3. Normalisation
normalizer = DataNormalizer()
df_normalized = normalizer.normalize_data(df_clean)

# 4. Enrichissement
enricher = DataEnricher()
df_enriched = enricher.enrich_data(df_normalized)

# 5. Chargement (si PostgreSQL configuré)
if os.getenv('DATABASE_URL'):
    loader = PostgreSQLLoader(os.getenv('DATABASE_URL'))
    loader.load_data(df_enriched, 'table_name')
```

## 🔧 Modules et Fonctionnalités

### 📥 Extraction (`etl/extract/`)

#### CSVExtractor
- **Lecture de fichiers CSV** avec gestion d'erreurs
- **Validation des données** (structure, contenu)
- **Logging détaillé** des opérations
- **Gestion des encodages** et formats

```python
extractor = CSVExtractor()
df = extractor.read_csv('data.csv', encoding='utf-8')
validation = extractor.validate_csv(df)
```

### 🔄 Transformation (`etl/transform/`)

#### DataCleaner (`clean_data.py`)
- **Gestion des valeurs manquantes** : imputation, suppression, interpolation
- **Suppression des doublons** avec options configurables
- **Traitement des valeurs aberrantes** : winsorisation, IQR, z-score
- **Correction des incohérences** : standardisation des chaînes

```python
cleaner = DataCleaner()
df_clean = cleaner.clean_data(
    df,
    missing_strategy='fill',      # 'drop', 'fill', 'interpolate', 'group_fill'
    remove_duplicates=True,
    handle_outliers=True,
    fix_inconsistencies=True
)
```

#### DataNormalizer (`normalize_data.py`)
- **Normalisation numérique** : StandardScaler, MinMaxScaler, RobustScaler
- **Standardisation catégorielle** : label encoding, one-hot encoding, frequency encoding
- **Normalisation des dates** : extraction de composants temporels
- **Transformations personnalisées** : log, Box-Cox

```python
normalizer = DataNormalizer()
df_normalized = normalizer.normalize_data(
    df,
    numerical_method='standard',   # 'standard', 'minmax', 'robust', 'log', 'boxcox'
    categorical_method='label',    # 'label', 'onehot', 'frequency'
    normalize_dates=True
)
```

#### DataEnricher (`enrich_data.py`)
- **Colonnes conditionnelles** : calculs basés sur des fonctions
- **Features agrégées** : groupements et agrégations
- **Features temporelles** : extraction de composants de dates
- **Features d'interaction** : opérations entre colonnes
- **Binning** : discrétisation de variables continues

```python
enricher = DataEnricher()

# Colonnes conditionnelles
conditions = {
    'pib_par_habitant': lambda df: df['pib'] / df['population'],
    'balance_commerciale': lambda df: df['export'] - df['import']
}

# Agrégations
aggregations = {
    'group_by': 'pays',
    'aggregations': {'pib': ['mean', 'sum'], 'population': ['mean']},
    'prefix': 'agg'
}

df_enriched = enricher.enrich_data(
    df,
    conditional_columns=conditions,
    aggregations=aggregations
)
```

### 📤 Chargement (`etl/load/`)

#### PostgreSQLLoader (`load_postgres.py`)
- **Connexion PostgreSQL** avec SQLAlchemy
- **Création automatique de tables** basée sur le DataFrame
- **Chargement optimisé** par chunks
- **Gestion des types de données** automatique
- **Exécution de requêtes SQL** personnalisées

```python
loader = PostgreSQLLoader('postgresql://user:pass@localhost/db')
success = loader.load_data(df, 'table_name', if_exists='replace')
```

### 🛠️ Utilitaires (`utils/`)

#### DataProfiler (`helpers.py`)
- **Profilage complet** des données
- **Métriques de qualité** : complétude, cohérence, validité
- **Analyse mémoire** et performance
- **Sauvegarde/chargement** de profils JSON
- **Comparaison de profils** pour détecter les changements

```python
profiler = DataProfiler()
profile = profiler.profile_dataframe(df, detailed=True)
profiler.save_profile(profile, 'profile.json')
```

## 📊 Exemples d'Utilisation

### Exemple 1 : Pipeline Complet pour Données Économiques

```python
import pandas as pd
from etl.extract.csv_extractor import CSVExtractor
from etl.transform.clean_data import DataCleaner
from etl.transform.normalize_data import DataNormalizer
from etl.transform.enrich_data import DataEnricher
from utils.helpers import DataProfiler

# 1. Extraction
extractor = CSVExtractor()
df = extractor.read_csv('economic_data.csv')

# 2. Profilage initial
profiler = DataProfiler()
profile_initial = profiler.profile_dataframe(df)

# 3. Nettoyage
cleaner = DataCleaner()
df_clean = cleaner.clean_data(
    df,
    missing_strategy='group_fill',
    group_by='pays',
    handle_outliers='winsorize'
)

# 4. Normalisation
normalizer = DataNormalizer()
df_normalized = normalizer.normalize_data(
    df_clean,
    numerical_method='robust',
    categorical_method='onehot'
)

# 5. Enrichissement
enricher = DataEnricher()

# Création de features économiques
conditions = {
    'pib_par_habitant': lambda df: df['pib_millions'] / df['population_millions'],
    'balance_commerciale': lambda df: df['export_millions'] - df['import_millions'],
    'taux_ouverture': lambda df: (df['export_millions'] + df['import_millions']) / df['pib_millions'] * 100,
    'pays_riche': lambda df: df['pib_millions'] > df['pib_millions'].quantile(0.75)
}

# Agrégations par pays
aggregations = {
    'group_by': 'pays',
    'aggregations': {
        'pib_millions': ['mean', 'sum', 'std'],
        'population_millions': ['mean', 'sum'],
        'inflation_taux': ['mean', 'std']
    },
    'prefix': 'agg'
}

df_enriched = enricher.enrich_data(
    df_normalized,
    conditional_columns=conditions,
    aggregations=aggregations
)

# 6. Profilage final
profile_final = profiler.profile_dataframe(df_enriched)
comparison = profiler.compare_profiles(profile_initial, profile_final)

print(f"Données enrichies: {len(df_enriched)} lignes, {len(df_enriched.columns)} colonnes")
print(f"Changements détectés: {comparison['changes_detected']}")
```

### Exemple 2 : Traitement de Données Temporelles

```python
# Données avec colonnes de dates
df = pd.DataFrame({
    'date': pd.date_range('2023-01-01', periods=100, freq='D'),
    'valeur': np.random.normal(100, 20, 100),
    'categorie': np.random.choice(['A', 'B', 'C'], 100)
})

# Enrichissement avec features temporelles
enricher = DataEnricher()
time_features = {
    'date_column': 'date',
    'features': ['year', 'month', 'quarter', 'day_of_week', 'is_weekend']
}

df_enriched = enricher.enrich_data(df, time_features=time_features)

# Agrégations temporelles
aggregations = {
    'group_by': ['year', 'month'],
    'aggregations': {'valeur': ['mean', 'sum', 'count']},
    'prefix': 'monthly'
}

df_final = enricher.enrich_data(df_enriched, aggregations=aggregations)
```

## 🧪 Tests

### Exécution des Tests

```bash
# Installer pytest si pas déjà fait
pip install pytest

# Exécuter tous les tests
pytest tests/

# Exécuter un test spécifique
pytest tests/test_etl.py::TestETLPipeline::test_csv_extractor

# Exécuter avec couverture
pytest --cov=etl tests/
```

### Tests Disponibles

- **test_csv_extractor** : Test de l'extracteur CSV
- **test_data_cleaner** : Test du nettoyeur de données
- **test_data_normalizer** : Test du normaliseur
- **test_data_enricher** : Test de l'enrichisseur
- **test_data_profiler** : Test du profileur
- **test_end_to_end_pipeline** : Test du pipeline complet

## 🔧 Extension du Projet

### Ajout d'un Nouveau Format d'Extraction

1. **Créer un nouveau fichier** dans `etl/extract/` :

```python
# etl/extract/excel_extractor.py
import pandas as pd
from loguru import logger

class ExcelExtractor:
    def __init__(self):
        self.logger = logger
    
    def read_excel(self, file_path: str, **kwargs) -> pd.DataFrame:
        try:
            self.logger.info(f"Lecture du fichier Excel: {file_path}")
            df = pd.read_excel(file_path, **kwargs)
            self.logger.info(f"Fichier Excel lu: {len(df)} lignes")
            return df
        except Exception as e:
            self.logger.error(f"Erreur lecture Excel: {e}")
            raise
```

2. **Ajouter les tests** dans `tests/test_etl.py` :

```python
def test_excel_extractor(self, tmp_path):
    # Test du nouvel extracteur
    pass
```

### Ajout d'une Nouvelle Méthode de Transformation

1. **Étendre la classe existante** ou créer une nouvelle :

```python
# Dans etl/transform/clean_data.py
def handle_text_normalization(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Normalise le texte (majuscules, accents, etc.)"""
    df_clean = df.copy()
    for col in columns:
        if col in df.columns:
            df_clean[col] = df_clean[col].str.lower().str.strip()
    return df_clean
```

2. **Mettre à jour la documentation** et les tests.

### Ajout d'une Nouvelle Base de Données

1. **Créer un nouveau chargeur** dans `etl/load/` :

```python
# etl/load/load_mysql.py
from sqlalchemy import create_engine

class MySQLoader:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
    
    def load_data(self, df: pd.DataFrame, table_name: str) -> bool:
        # Implémentation spécifique à MySQL
        pass
```

## 🔍 Dépannage

### Problèmes Courants

#### Erreur de Connexion PostgreSQL
```
Error: connection to server at "localhost" failed
```
**Solution** : Vérifier que PostgreSQL est démarré et que les paramètres de connexion sont corrects.

#### Erreur de Mémoire
```
MemoryError: Unable to allocate array
```
**Solution** : Utiliser le chargement par chunks ou réduire la taille des données.

#### Erreur de Type de Données
```
TypeError: Cannot convert string to float
```
**Solution** : Vérifier les types de données dans le CSV et ajuster la stratégie de nettoyage.

### Logs et Debugging

Le projet utilise `loguru` pour le logging. Les logs sont sauvegardés dans `etl_pipeline.log`.

```python
from loguru import logger

# Activer le debug
logger.add("debug.log", level="DEBUG")

# Logs personnalisés
logger.info("Début du traitement")
logger.warning("Valeurs manquantes détectées")
logger.error("Erreur critique")
```

### Performance

#### Optimisations Recommandées

1. **Chargement par chunks** pour les gros fichiers
2. **Types de données optimisés** (int32 au lieu de int64)
3. **Parallélisation** pour les transformations lourdes
4. **Indexation** des bases de données

#### Monitoring

```python
import time
from utils.helpers import DataProfiler

start_time = time.time()

# Votre pipeline ETL
df_processed = process_data(df)

end_time = time.time()
print(f"Temps de traitement: {end_time - start_time:.2f} secondes")

# Profilage mémoire
profiler = DataProfiler()
profile = profiler.profile_dataframe(df_processed)
print(f"Utilisation mémoire: {profile['memory_usage']['total_memory_mb']:.2f} MB")
```

## 📚 Ressources Additionnelles

### Documentation des Bibliothèques

- [Pandas](https://pandas.pydata.org/docs/) - Manipulation de données
- [SQLAlchemy](https://docs.sqlalchemy.org/) - ORM et connexions DB
- [Scikit-learn](https://scikit-learn.org/stable/) - Normalisation et preprocessing
- [Loguru](https://loguru.readthedocs.io/) - Logging avancé

### Bonnes Pratiques ETL

1. **Validation des données** à chaque étape
2. **Logging détaillé** pour le debugging
3. **Gestion d'erreurs** robuste
4. **Tests unitaires** complets
5. **Documentation** des transformations
6. **Monitoring** des performances

---

**Projet ETL Python** - Développé pour l'analyse économique et la visualisation de données 🚀
