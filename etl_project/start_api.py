#!/usr/bin/env python3
"""
Script de démarrage simple pour l'API ETL
Usage: python start_api.py
"""

import uvicorn
import os
import sys

def main():
    """Démarre l'API FastAPI ETL"""
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists("api/main.py"):
        print("❌ Erreur: Ce script doit être exécuté depuis le répertoire etl_project/")
        print("   Structure attendue: etl_project/api/main.py")
        sys.exit(1)
    
    print("🚀 Démarrage de l'API ETL DIP...")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔄 Mode: Reload activé")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_dirs=["api", "etl", "utils"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'API ETL")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
