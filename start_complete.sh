#!/bin/bash

# Script de démarrage complet pour le projet DIP avec fonctionnalités avancées
# Intégration complète du projet Asam237/dataviz

echo "🚀 Démarrage du projet DIP avec fonctionnalités avancées intégrées"
echo "=================================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "dip-frontend" ] || [ ! -d "etl_project" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis la racine du projet DIP"
    echo "   Structure attendue:"
    echo "   Dip-M-D-2/"
    echo "   ├── dip-frontend/"
    echo "   └── etl_project/"
    exit 1
fi

# Fonction pour vérifier si un port est utilisé
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port utilisé
    else
        return 1  # Port libre
    fi
}

# Fonction pour tuer un processus sur un port
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔄 Arrêt du processus sur le port $port (PID: $pid)"
        kill -9 $pid
        sleep 2
    fi
}

echo "🔍 Vérification des ports..."

# Vérifier et libérer les ports si nécessaire
if check_port 3000; then
    echo "⚠️  Le port 3000 est utilisé. Arrêt du processus..."
    kill_port 3000
fi

if check_port 8000; then
    echo "⚠️  Le port 8000 est utilisé. Arrêt du processus..."
    kill_port 8000
fi

echo "✅ Ports libérés"

# Démarrer le backend ETL
echo ""
echo "🔧 Démarrage du backend ETL (port 8000)..."
cd etl_project

# Vérifier les dépendances Python
echo "📦 Vérification des dépendances Python..."
python3 -c "import pandas, numpy, plotly, matplotlib, seaborn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Installation des dépendances Python manquantes..."
    pip3 install pandas numpy plotly matplotlib seaborn fastapi uvicorn --break-system-packages
fi

# Démarrer l'API
echo "🚀 Démarrage de l'API FastAPI..."
python3 start.py api &
BACKEND_PID=$!

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
sleep 5

# Vérifier que l'API répond
for i in {1..10}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
        echo "✅ API démarrée avec succès"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ L'API n'a pas démarré correctement"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    echo "   Tentative $i/10..."
    sleep 2
done

# Retourner à la racine
cd ..

# Démarrer le frontend
echo ""
echo "🎨 Démarrage du frontend Next.js (port 3000)..."
cd dip-frontend

# Vérifier les dépendances Node.js
echo "📦 Vérification des dépendances Node.js..."
if [ ! -d "node_modules" ]; then
    echo "⚠️  Installation des dépendances Node.js..."
    npm install
fi

# Vérifier les dépendances spécifiques aux fonctionnalités avancées
echo "🔍 Vérification des dépendances avancées..."
npm list @radix-ui/react-accordion > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  Installation des dépendances Radix UI..."
    npm install @radix-ui/react-accordion @radix-ui/react-alert-dialog @radix-ui/react-aspect-ratio @radix-ui/react-avatar @radix-ui/react-checkbox @radix-ui/react-collapsible @radix-ui/react-context-menu @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-hover-card @radix-ui/react-label @radix-ui/react-menubar @radix-ui/react-navigation-menu @radix-ui/react-popover @radix-ui/react-progress @radix-ui/react-radio-group @radix-ui/react-scroll-area @radix-ui/react-select @radix-ui/react-separator @radix-ui/react-slider @radix-ui/react-slot @radix-ui/react-switch @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-toggle @radix-ui/react-toggle-group @radix-ui/react-tooltip class-variance-authority clsx cmdk date-fns embla-carousel-react file-saver html-to-image html2canvas input-otp jspdf papaparse react-day-picker react-dropzone react-hook-form react-resizable-panels sonner tailwind-merge tailwindcss-animate vaul xlsx zod @hookform/resolvers
fi

# Démarrer le serveur de développement
echo "🚀 Démarrage du serveur de développement Next.js..."
npm run dev &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
echo "⏳ Attente du démarrage du frontend..."
sleep 10

# Vérifier que le frontend répond
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend démarré avec succès"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Le frontend n'a pas démarré correctement"
        kill $FRONTEND_PID 2>/dev/null
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    echo "   Tentative $i/10..."
    sleep 3
done

# Retourner à la racine
cd ..

echo ""
echo "🎉 Démarrage complet réussi !"
echo "=================================================================="
echo ""
echo "🌐 Applications disponibles:"
echo "   📊 Frontend DIP:     http://localhost:3000"
echo "   📈 Page Dataviz:     http://localhost:3000/dataviz"
echo "   🔧 API Backend:      http://127.0.0.1:8000"
echo "   📚 Documentation:    http://127.0.0.1:8000/docs"
echo ""
echo "🚀 Fonctionnalités avancées intégrées:"
echo "   ✅ Import intelligent avec détection d'inconsistances"
echo "   ✅ Analytics avancées avec corrélations et prédictions"
echo "   ✅ Graphiques interactifs de tous types"
echo "   ✅ Dashboard complet avec métriques"
echo "   ✅ Export haute résolution des visualisations"
echo "   ✅ Recommandations intelligentes de graphiques"
echo ""
echo "🧪 Pour tester l'intégration:"
echo "   python3 test_integration.py"
echo ""
echo "🛑 Pour arrêter les services:"
echo "   Appuyez sur Ctrl+C ou exécutez: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services arrêtés"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT SIGTERM

# Attendre indéfiniment
echo "⏳ Services en cours d'exécution... (Ctrl+C pour arrêter)"
wait

