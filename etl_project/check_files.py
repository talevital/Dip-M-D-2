#!/usr/bin/env python3
"""
Script pour vérifier les fichiers dans la base de données
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.db import get_database_url, get_session
from api.models import UploadedFile, UploadedRow

def check_database():
    """Vérifier l'état de la base de données"""
    print("🔍 Vérification de la base de données...")
    
    # Vérifier si la base de données existe
    db_url = get_database_url()
    print(f"📁 Base de données: {db_url}")
    
    if "sqlite" in db_url:
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.exists(db_path):
            print(f"❌ Base de données non trouvée: {db_path}")
            return False
        else:
            print(f"✅ Base de données trouvée: {db_path}")
    
    # Vérifier les tables
    try:
        with get_session() as session:
            # Vérifier la table uploaded_files
            result = session.execute(text("SELECT COUNT(*) FROM uploaded_files"))
            file_count = result.scalar()
            print(f"📊 Nombre de fichiers: {file_count}")
            
            if file_count > 0:
                # Afficher les fichiers
                files = session.query(UploadedFile).all()
                print("\n📋 Fichiers trouvés:")
                for f in files:
                    print(f"  • ID: {f.id}")
                    print(f"    Nom: {f.original_name}")
                    print(f"    Chemin: {f.stored_path}")
                    print(f"    Taille: {f.size_bytes} bytes")
                    print(f"    Lignes: {f.row_count}")
                    print(f"    Colonnes: {f.col_count}")
                    print(f"    Créé: {f.created_at}")
                    print(f"    Uploadé par: {f.uploaded_by}")
                    print(f"    Fichier existe: {os.path.exists(f.stored_path)}")
                    print()
            
            # Vérifier la table uploaded_rows
            result = session.execute(text("SELECT COUNT(*) FROM uploaded_rows"))
            row_count = result.scalar()
            print(f"📊 Nombre de lignes stockées: {row_count}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    
    return True

def check_uploads_directory():
    """Vérifier le dossier uploads"""
    print("\n🔍 Vérification du dossier uploads...")
    
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        print(f"❌ Dossier uploads non trouvé: {upload_dir}")
        return False
    
    files = os.listdir(upload_dir)
    print(f"📁 Dossier uploads: {upload_dir}")
    print(f"📊 Nombre de fichiers: {len(files)}")
    
    if files:
        print("📋 Fichiers trouvés:")
        for f in files:
            file_path = os.path.join(upload_dir, f)
            size = os.path.getsize(file_path)
            print(f"  • {f} ({size} bytes)")
    
    return True

def main():
    """Fonction principale"""
    print("🚀 Vérification de l'état des fichiers")
    print("=" * 50)
    
    # Vérifier la base de données
    db_ok = check_database()
    
    # Vérifier le dossier uploads
    uploads_ok = check_uploads_directory()
    
    print("\n" + "=" * 50)
    if db_ok and uploads_ok:
        print("✅ Vérification terminée avec succès")
    else:
        print("⚠️  Problèmes détectés")
    
    return db_ok and uploads_ok

if __name__ == "__main__":
    main()
