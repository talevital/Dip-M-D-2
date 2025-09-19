"""
Script de démarrage unifié pour l'API DIP
Démarre l'API ETL avec authentification intégrée
"""

import uvicorn
from api.main_unified import app

if __name__ == "__main__":
    print("🚀 Démarrage de l'API DIP unifiée (ETL + Authentification)")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔐 Authentification: http://localhost:8000/auth/login")
    print("=" * 60)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        log_level="info",
        reload=True
    )


