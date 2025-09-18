#!/usr/bin/env python3
"""
Script de démarrage pour le pipeline ETL principal
Usage: python start_etl.py
"""

import sys
import os
from main import main

def start_etl_pipeline():
    """Démarre le pipeline ETL principal avec données d'exemple"""
    
    print("🔄 Démarrage du Pipeline ETL DIP...")
    print("📊 Traitement des données d'exemple")
    print("=" * 50)
    
    try:
        # Exécuter le pipeline principal
        main()
        
        print("\n✅ Pipeline ETL terminé avec succès!")
        print("📁 Fichiers générés:")
        print("   - sample_data_original.csv")
        print("   - sample_data_transformed.csv") 
        print("   - data_profile_final.json")
        print("   - profile_comparison.json")
        print("   - etl_pipeline.log")
        
    except Exception as e:
        print(f"❌ Erreur dans le pipeline ETL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_etl_pipeline()
