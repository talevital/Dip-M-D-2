#!/usr/bin/env python3
"""
Test du module de traitement textuel
"""

import pandas as pd
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.utils.text_processor import TextProcessor, MultiChoiceProcessor, apply_text_processing

def test_text_processor():
    """Test des fonctionnalités de base du TextProcessor"""
    print("=== Test TextProcessor ===")
    
    # Créer des données de test
    data = {
        'nom': ['Jean Dupont', 'Marie Martin', 'Pierre Durand', 'Sophie Bernard'],
        'email': ['jean.dupont@email.com', 'marie.martin@test.fr', 'pierre.durand@work.com', 'sophie.bernard@mail.org'],
        'description': [
            'Développeur senior avec 10 ans d\'expérience en Python et JavaScript',
            'Data scientist spécialisée en machine learning et analyse de données',
            'Chef de projet agile avec expertise en gestion d\'équipe',
            'UX/UI designer créative avec portfolio impressionnant'
        ],
        'pays': ['France', 'france', 'FRANCE', 'Allemagne']
    }
    
    df = pd.DataFrame(data)
    print(f"DataFrame original: {df.shape}")
    print(df.head())
    
    # Initialiser le processeur
    processor = TextProcessor(language='french')
    
    # Test de nettoyage de texte
    print("\n--- Test nettoyage ---")
    cleaned = processor.clean_text("Éléphant & éléphant, c'est l'été!")
    print(f"Texte original: Éléphant & éléphant, c'est l'été!")
    print(f"Texte nettoyé: {cleaned}")
    
    # Test d'extraction de features
    print("\n--- Test extraction features ---")
    features = processor.extract_text_features("Bonjour! Mon email est test@example.com et mon téléphone 0123456789")
    print("Features extraites:")
    for key, value in features.items():
        print(f"  {key}: {value}")
    
    # Test d'extraction de mots-clés
    print("\n--- Test extraction mots-clés ---")
    texts = df['description'].tolist()
    keywords = processor.extract_keywords(texts, max_keywords=5)
    print(f"Mots-clés extraits: {keywords}")
    
    # Test de détection de topics
    print("\n--- Test détection topics ---")
    topics, _ = processor.detect_topics(texts, n_topics=3)
    print("Topics détectés:")
    for topic in topics:
        print(f"  {topic}")
    
    # Test de clustering
    print("\n--- Test clustering ---")
    clusters = processor.cluster_similar_texts(df['pays'].tolist(), similarity_threshold=0.8)
    print(f"Clusters détectés: {clusters}")
    
    # Test de similarité
    print("\n--- Test similarité ---")
    similarity = processor.calculate_text_similarity("Jean Dupont", "Jean Dupont", method='fuzzy')
    print(f"Similarité 'Jean Dupont' vs 'Jean Dupont': {similarity}")
    
    return True

def test_multiple_choice():
    """Test du MultiChoiceProcessor"""
    print("\n=== Test MultiChoiceProcessor ===")
    
    # Données de test
    data = {
        'statut': ['actif', 'Actif', 'ACTIF', 'inactif', 'Inactif', 'suspendu', 'Suspendu'],
        'pays': ['France', 'france', 'FRANCE', 'Allemagne', 'allemagne', 'Espagne', 'espagne']
    }
    
    df = pd.DataFrame(data)
    processor = TextProcessor()
    multi_processor = MultiChoiceProcessor(processor)
    
    # Test de standardisation
    possible_values = ['actif', 'inactif', 'suspendu']
    df_std = multi_processor.standardize_multiple_choice(
        df, 'statut', possible_values, similarity_threshold=0.8
    )
    
    print("Standardisation des choix multiples:")
    print(df_std[['statut', 'statut_standardized', 'statut_mapping']].head())
    
    # Test de détection de patterns
    patterns = multi_processor.detect_multiple_choice_patterns(df, 'pays', min_frequency=1)
    print(f"Patterns détectés: {patterns}")
    
    return True

def test_apply_text_processing():
    """Test de la fonction apply_text_processing"""
    print("\n=== Test apply_text_processing ===")
    
    # Données de test
    data = {
        'nom': ['Jean Dupont', 'Marie Martin', 'Pierre Durand'],
        'description': [
            'Développeur senior avec 10 ans d\'expérience',
            'Data scientist spécialisée en ML',
            'Chef de projet agile'
        ]
    }
    
    df = pd.DataFrame(data)
    print(f"DataFrame original: {df.shape}")
    
    # Appliquer le traitement textuel
    df_processed = apply_text_processing(
        df, 
        text_columns=['nom', 'description'],
        extract_features=True,
        extract_keywords=True,
        detect_topics=True
    )
    
    print(f"DataFrame traité: {df_processed.shape}")
    print("Nouvelles colonnes:")
    for col in df_processed.columns:
        if col not in df.columns:
            print(f"  {col}")
    
    return True

if __name__ == "__main__":
    try:
        test_text_processor()
        test_multiple_choice()
        test_apply_text_processing()
        print("\n✅ Tous les tests sont passés avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
