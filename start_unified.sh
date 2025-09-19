#!/bin/bash

echo "🚀 Démarrage de la plateforme DIP unifiée..."

# Aller dans le répertoire du projet ETL
cd /Users/angevitaloura/Documents/GitHub/Dip-M-D-2/etl_project

# Activer l'environnement virtuel
source venv/bin/activate

echo "📡 Démarrage du serveur FastAPI unifié (authentification + ETL)..."
# Démarrer le serveur FastAPI unifié sur le port 8000
python -m uvicorn api.main_integrated:app --host 0.0.0.0 --port 8000 --reload &

# Attendre que le serveur démarre
sleep 3

echo "🌐 Démarrage du frontend Next.js..."
# Aller dans le répertoire frontend
cd /Users/angevitaloura/Documents/GitHub/Dip-M-D-2/dip-frontend

# Démarrer le frontend Next.js
npm run dev &

echo "✅ Plateforme DIP démarrée !"
echo ""
echo "🔗 Accès aux services :"
echo "   • Frontend : http://localhost:3000"
echo "   • API FastAPI : http://localhost:8000"
echo "   • Documentation API : http://localhost:8000/docs"
echo ""
echo "🔐 Connexion :"
echo "   • Email : admin@dip.com"
echo "   • Mot de passe : admin123"
echo ""
echo "📁 Accès aux fichiers ETL :"
echo "   • Page des fichiers : http://localhost:3000/etl/files"
echo "   • Upload de fichiers : http://localhost:3000/etl/upload"
echo ""
echo "Pour arrêter les serveurs, appuyez sur Ctrl+C"

# Attendre que l'utilisateur arrête les serveurs
wait
