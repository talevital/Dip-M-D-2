#!/usr/bin/env python3
"""
Script de test pour diagnostiquer les problèmes de l'API ETL
"""

import sys
import os

def test_imports():
    """Teste les imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        import pandas as pd
        print("✅ pandas importé")
    except ImportError as e:
        print(f"❌ Erreur pandas: {e}")
        return False
    
    try:
        import fastapi
        print("✅ fastapi importé")
    except ImportError as e:
        print(f"❌ Erreur fastapi: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn importé")
    except ImportError as e:
        print(f"❌ Erreur uvicorn: {e}")
        return False
    
    try:
        from api.main import app
        print("✅ API FastAPI importée")
    except ImportError as e:
        print(f"❌ Erreur import API: {e}")
        return False
    
    return True

def test_database():
    """Teste la connexion à la base de données"""
    print("\n🔍 Test de la base de données...")
    
    try:
        from api.db import get_engine
        engine = get_engine()
        print("✅ Connexion DB réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
        return False

def test_etl_modules():
    """Teste les modules ETL"""
    print("\n🔍 Test des modules ETL...")
    
    try:
        from etl.extract.csv_extractor import CSVExtractor
        print("✅ CSVExtractor importé")
    except ImportError as e:
        print(f"❌ Erreur CSVExtractor: {e}")
        return False
    
    try:
        from etl.transform.clean_data import DataCleaner
        print("✅ DataCleaner importé")
    except ImportError as e:
        print(f"❌ Erreur DataCleaner: {e}")
        return False
    
    try:
        from utils.helpers import DataProfiler
        print("✅ DataProfiler importé")
    except ImportError as e:
        print(f"❌ Erreur DataProfiler: {e}")
        return False
    
    return True

def main():
    print("🧪 Diagnostic de l'API ETL DIP")
    print("=" * 40)
    
    # Test des imports
    imports_ok = test_imports()
    
    # Test de la base de données
    db_ok = test_database()
    
    # Test des modules ETL
    etl_ok = test_etl_modules()
    
    print("\n📊 Résumé des tests:")
    print(f"Imports: {'✅ OK' if imports_ok else '❌ ÉCHEC'}")
    print(f"Base de données: {'✅ OK' if db_ok else '❌ ÉCHEC'}")
    print(f"Modules ETL: {'✅ OK' if etl_ok else '❌ ÉCHEC'}")
    
    if imports_ok and db_ok and etl_ok:
        print("\n🎉 Tous les tests sont passés! L'API devrait fonctionner.")
        print("💡 Essayez: python start.py api")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return imports_ok and db_ok and etl_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
