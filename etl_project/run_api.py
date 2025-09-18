#!/usr/bin/env python3
"""
Test simple de l'API ETL
"""

import uvicorn
from api.main import app

if __name__ == "__main__":
    print("🚀 Démarrage de l'API ETL DIP...")
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    print("🔄 Appuyez sur Ctrl+C pour arrêter")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'API")
    except Exception as e:
        print(f"❌ Erreur: {e}")
