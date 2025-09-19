#!/bin/bash

echo "🚀 Démarrage du serveur FastAPI unifié DIP..."

# Aller dans le répertoire du projet ETL
cd /Users/angevitaloura/Documents/GitHub/Dip-M-D-2/etl_project

# Activer l'environnement virtuel
source venv/bin/activate

echo "📡 Serveur unifié démarré sur http://localhost:8000"
echo "🔐 Authentification + ETL intégrés"
echo ""
echo "🔗 Accès :"
echo "   • API : http://localhost:8000"
echo "   • Docs : http://localhost:8000/docs"
echo "   • Login : http://localhost:8000/auth/login"
echo "   • Fichiers : http://localhost:8000/files"
echo ""
echo "🔑 Connexion :"
echo "   • Email : admin@dip.com"
echo "   • Mot de passe : admin123"
echo ""
echo "Pour arrêter : Ctrl+C"

# Démarrer le serveur unifié
python -m uvicorn api.main_integrated:app --host 0.0.0.0 --port 8000 --reload
