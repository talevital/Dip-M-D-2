#!/usr/bin/env python3
"""
Script de démarrage unifié pour le projet ETL DIP
Usage: python start.py [api|etl|help]
"""

import sys
import os
import subprocess
import argparse

def start_api():
    """Démarre l'API FastAPI"""
    print("🚀 Démarrage de l'API ETL...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'API")
    except Exception as e:
        print(f"❌ Erreur API: {e}")

def start_etl():
    """Démarre le pipeline ETL"""
    print("🔄 Démarrage du Pipeline ETL...")
    try:
        from main import main
        main()
    except Exception as e:
        print(f"❌ Erreur ETL: {e}")

def show_help():
    """Affiche l'aide"""
    print("""
🔧 Script de démarrage ETL DIP
===============================

Usage: python start.py [commande]

Commandes disponibles:
  api     Démarre l'API FastAPI (http://localhost:8001)
  etl     Lance le pipeline ETL avec données d'exemple
  help    Affiche cette aide

Exemples:
  python start.py api    # Démarre l'API
  python start.py etl    # Lance le pipeline ETL
  python start.py        # Affiche l'aide

📚 Documentation API: http://127.0.0.1:8000/docs
🔄 Pipeline ETL: Traite les données d'exemple
    """)

def main():
    parser = argparse.ArgumentParser(description="Script de démarrage ETL DIP")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["api", "etl", "help"],
                       help="Commande à exécuter")
    
    args = parser.parse_args()
    
    if args.command == "api":
        start_api()
    elif args.command == "etl":
        start_etl()
    else:
        show_help()

if __name__ == "__main__":
    main()
