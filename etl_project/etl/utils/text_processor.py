"""
Module de traitement avancé de données textuelles
Extraction de features, nettoyage avancé, traitement des champs à choix multiples
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from typing import List, Dict, Optional, Tuple, Union
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from fuzzywuzzy import fuzz
import textdistance
from loguru import logger

# Télécharger les ressources NLTK nécessaires
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class TextProcessor:
    """
    Classe pour le traitement avancé de données textuelles
    """
    
    def __init__(self, language: str = 'french'):
        """
        Initialise le processeur de texte
        
        Args:
            language: Langue pour les stop words ('french', 'english')
        """
        self.language = language
        self.stop_words = set(stopwords.words(language)) if language in ['french', 'english'] else set()
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()
        
        # Patterns regex pour différents types de données
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+33|0)[1-9](\d{8})',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            'number': r'\b\d+(?:\.\d+)?\b',
            'currency': r'\b\d+(?:\.\d+)?\s*(?:€|EUR|USD|\$)\b'
        }
    
    def clean_text(self, text: str, remove_accents: bool = True, 
                   remove_special_chars: bool = True, normalize_whitespace: bool = True) -> str:
        """
        Nettoie un texte en appliquant diverses normalisations
        
        Args:
            text: Texte à nettoyer
            remove_accents: Supprimer les accents
            remove_special_chars: Supprimer les caractères spéciaux
            normalize_whitespace: Normaliser les espaces
            
        Returns:
            Texte nettoyé
        """
        if pd.isna(text) or text == '':
            return ''
        
        text = str(text)
        
        # Conversion en minuscules
        text = text.lower()
        
        # Suppression des accents
        if remove_accents:
            text = unicodedata.normalize('NFD', text)
            text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Suppression des caractères spéciaux
        if remove_special_chars:
            text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalisation des espaces
        if normalize_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_text_features(self, text: str) -> Dict[str, Union[int, float, str]]:
        """
        Extrait des features textuelles d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire de features
        """
        if pd.isna(text) or text == '':
            return {
                'length': 0,
                'word_count': 0,
                'sentence_count': 0,
                'avg_word_length': 0.0,
                'unique_words_ratio': 0.0,
                'has_numbers': False,
                'has_emails': False,
                'has_urls': False,
                'has_phone': False,
                'has_currency': False
            }
        
        text = str(text)
        cleaned_text = self.clean_text(text, remove_special_chars=False)
        
        # Features de base
        length = len(text)
        words = word_tokenize(cleaned_text)
        word_count = len(words)
        sentences = sent_tokenize(text)
        sentence_count = len(sentences)
        
        # Features calculées
        avg_word_length = np.mean([len(word) for word in words]) if words else 0.0
        unique_words_ratio = len(set(words)) / word_count if word_count > 0 else 0.0
        
        # Features de contenu
        has_numbers = bool(re.search(self.patterns['number'], text))
        has_emails = bool(re.search(self.patterns['email'], text))
        has_urls = bool(re.search(self.patterns['url'], text))
        has_phone = bool(re.search(self.patterns['phone'], text))
        has_currency = bool(re.search(self.patterns['currency'], text))
        
        return {
            'length': length,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_word_length': avg_word_length,
            'unique_words_ratio': unique_words_ratio,
            'has_numbers': has_numbers,
            'has_emails': has_emails,
            'has_urls': has_urls,
            'has_phone': has_phone,
            'has_currency': has_currency
        }
    
    def tokenize_and_clean(self, text: str, remove_stop_words: bool = True, 
                          lemmatize: bool = True, stem: bool = False) -> List[str]:
        """
        Tokenise et nettoie un texte
        
        Args:
            text: Texte à traiter
            remove_stop_words: Supprimer les stop words
            lemmatize: Appliquer la lemmatisation
            stem: Appliquer le stemming
            
        Returns:
            Liste de tokens nettoyés
        """
        if pd.isna(text) or text == '':
            return []
        
        text = str(text)
        cleaned_text = self.clean_text(text)
        
        # Tokenisation
        tokens = word_tokenize(cleaned_text)
        
        # Suppression des stop words
        if remove_stop_words:
            tokens = [token for token in tokens if token.lower() not in self.stop_words]
        
        # Lemmatisation
        if lemmatize:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Stemming
        if stem:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        # Suppression des tokens vides
        tokens = [token for token in tokens if len(token) > 1]
        
        return tokens
    
    def extract_keywords(self, texts: List[str], max_keywords: int = 10, 
                        min_df: float = 0.1, max_df: float = 0.9) -> List[str]:
        """
        Extrait les mots-clés les plus importants d'une liste de textes
        
        Args:
            texts: Liste de textes
            max_keywords: Nombre maximum de mots-clés à extraire
            min_df: Fréquence minimale des documents
            max_df: Fréquence maximale des documents
            
        Returns:
            Liste des mots-clés
        """
        if not texts:
            return []
        
        # Vectorisation TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=max_keywords * 2,
            min_df=min_df,
            max_df=max_df,
            stop_words=list(self.stop_words) if self.language in ['french', 'english'] else None
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculer les scores moyens
            scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Trier par score et retourner les meilleurs
            keyword_indices = np.argsort(scores)[::-1][:max_keywords]
            keywords = [feature_names[i] for i in keyword_indices]
            
            return keywords
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des mots-clés: {e}")
            return []
    
    def detect_topics(self, texts: List[str], n_topics: int = 5, 
                     method: str = 'lda') -> Tuple[List[str], np.ndarray]:
        """
        Détecte les topics dans une liste de textes
        
        Args:
            texts: Liste de textes
            n_topics: Nombre de topics à détecter
            method: Méthode de détection ('lda' ou 'nmf')
            
        Returns:
            Tuple (topics, document_topic_matrix)
        """
        if not texts:
            return [], np.array([])
        
        # Vectorisation
        vectorizer = CountVectorizer(
            max_features=1000,
            min_df=2,
            max_df=0.95,
            stop_words=list(self.stop_words) if self.language in ['french', 'english'] else None
        )
        
        try:
            doc_term_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Détection de topics
            if method == 'lda':
                model = LatentDirichletAllocation(
                    n_components=n_topics,
                    random_state=42,
                    max_iter=10
                )
            else:  # nmf
                model = NMF(
                    n_components=n_topics,
                    random_state=42,
                    max_iter=200
                )
            
            doc_topic_matrix = model.fit_transform(doc_term_matrix)
            
            # Extraction des mots-clés par topic
            topics = []
            for topic_idx, topic in enumerate(model.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics.append(f"Topic {topic_idx + 1}: {', '.join(top_words[:5])}")
            
            return topics, doc_topic_matrix
            
        except Exception as e:
            logger.warning(f"Erreur lors de la détection de topics: {e}")
            return [], np.array([])
    
    def cluster_similar_texts(self, texts: List[str], similarity_threshold: float = 0.8,
                            method: str = 'tfidf') -> List[List[int]]:
        """
        Regroupe les textes similaires en clusters
        
        Args:
            texts: Liste de textes
            similarity_threshold: Seuil de similarité
            method: Méthode de clustering ('tfidf', 'fuzzy')
            
        Returns:
            Liste des clusters (indices des textes)
        """
        if not texts or len(texts) < 2:
            return [[0]] if texts else []
        
        if method == 'tfidf':
            return self._cluster_tfidf(texts, similarity_threshold)
        else:  # fuzzy
            return self._cluster_fuzzy(texts, similarity_threshold)
    
    def _cluster_tfidf(self, texts: List[str], threshold: float) -> List[List[int]]:
        """Clustering basé sur TF-IDF et similarité cosinus"""
        try:
            # Vectorisation TF-IDF
            vectorizer = TfidfVectorizer(
                max_features=1000,
                min_df=1,
                max_df=0.95
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Calcul de la similarité cosinus
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Clustering DBSCAN
            eps = 1 - threshold  # Convertir le seuil en eps pour DBSCAN
            dbscan = DBSCAN(eps=eps, min_samples=1, metric='precomputed')
            
            # Convertir la matrice de similarité en matrice de distance
            distance_matrix = 1 - similarity_matrix
            clusters = dbscan.fit_predict(distance_matrix)
            
            # Regrouper les indices par cluster
            cluster_groups = {}
            for idx, cluster_id in enumerate(clusters):
                if cluster_id not in cluster_groups:
                    cluster_groups[cluster_id] = []
                cluster_groups[cluster_id].append(idx)
            
            return list(cluster_groups.values())
            
        except Exception as e:
            logger.warning(f"Erreur lors du clustering TF-IDF: {e}")
            return [[i] for i in range(len(texts))]
    
    def _cluster_fuzzy(self, texts: List[str], threshold: float) -> List[List[int]]:
        """Clustering basé sur FuzzyWuzzy"""
        try:
            n = len(texts)
            clusters = []
            used = set()
            
            for i in range(n):
                if i in used:
                    continue
                
                cluster = [i]
                used.add(i)
                
                for j in range(i + 1, n):
                    if j in used:
                        continue
                    
                    # Calculer la similarité
                    similarity = fuzz.token_sort_ratio(texts[i], texts[j]) / 100.0
                    
                    if similarity >= threshold:
                        cluster.append(j)
                        used.add(j)
                
                clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            logger.warning(f"Erreur lors du clustering fuzzy: {e}")
            return [[i] for i in range(len(texts))]
    
    def process_multiple_choice_field(self, text: str, 
                                    possible_values: List[str],
                                    similarity_threshold: float = 0.8) -> Tuple[str, float]:
        """
        Traite un champ à choix multiples en trouvant la meilleure correspondance
        
        Args:
            text: Texte à traiter
            possible_values: Liste des valeurs possibles
            similarity_threshold: Seuil de similarité minimum
            
        Returns:
            Tuple (valeur_correspondante, score_similarité)
        """
        if pd.isna(text) or text == '' or not possible_values:
            return '', 0.0
        
        text = str(text).strip()
        
        # Nettoyer le texte
        cleaned_text = self.clean_text(text)
        
        best_match = ''
        best_score = 0.0
        
        for value in possible_values:
            cleaned_value = self.clean_text(value)
            
            # Calculer différents scores de similarité
            exact_match = fuzz.ratio(cleaned_text, cleaned_value) / 100.0
            token_sort = fuzz.token_sort_ratio(cleaned_text, cleaned_value) / 100.0
            token_set = fuzz.token_set_ratio(cleaned_text, cleaned_value) / 100.0
            
            # Score moyen
            score = (exact_match + token_sort + token_set) / 3.0
            
            if score > best_score:
                best_score = score
                best_match = value
        
        # Retourner la correspondance seulement si elle dépasse le seuil
        if best_score >= similarity_threshold:
            return best_match, best_score
        else:
            return '', 0.0
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait des entités nommées basiques (emails, téléphones, URLs, etc.)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire des entités trouvées
        """
        if pd.isna(text) or text == '':
            return {}
        
        text = str(text)
        entities = {}
        
        # Recherche des patterns
        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def calculate_text_similarity(self, text1: str, text2: str, 
                                method: str = 'fuzzy') -> float:
        """
        Calcule la similarité entre deux textes
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            method: Méthode de calcul ('fuzzy', 'cosine', 'jaccard')
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if pd.isna(text1) or pd.isna(text2):
            return 0.0
        
        text1, text2 = str(text1), str(text2)
        
        if method == 'fuzzy':
            # Utiliser FuzzyWuzzy
            ratio = fuzz.ratio(text1, text2) / 100.0
            token_sort = fuzz.token_sort_ratio(text1, text2) / 100.0
            token_set = fuzz.token_set_ratio(text1, text2) / 100.0
            return (ratio + token_sort + token_set) / 3.0
        
        elif method == 'cosine':
            # Utiliser TF-IDF et similarité cosinus
            try:
                vectorizer = TfidfVectorizer()
                tfidf_matrix = vectorizer.fit_transform([text1, text2])
                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                return float(similarity)
            except:
                return 0.0
        
        elif method == 'jaccard':
            # Utiliser l'index de Jaccard
            try:
                words1 = set(self.tokenize_and_clean(text1))
                words2 = set(self.tokenize_and_clean(text2))
                
                if not words1 and not words2:
                    return 1.0
                elif not words1 or not words2:
                    return 0.0
                
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                return intersection / union
            except:
                return 0.0
        
        else:
            return 0.0


class MultiChoiceProcessor:
    """
    Processeur spécialisé pour les champs à choix multiples
    """
    
    def __init__(self, text_processor: TextProcessor):
        self.text_processor = text_processor
    
    def standardize_multiple_choice(self, df: pd.DataFrame, column: str,
                                   possible_values: List[str],
                                   similarity_threshold: float = 0.8,
                                   create_mapping: bool = True) -> pd.DataFrame:
        """
        Standardise une colonne à choix multiples
        
        Args:
            df: DataFrame contenant les données
            column: Nom de la colonne à standardiser
            possible_values: Liste des valeurs possibles
            similarity_threshold: Seuil de similarité minimum
            create_mapping: Créer une colonne de mapping
            
        Returns:
            DataFrame avec la colonne standardisée
        """
        df = df.copy()
        
        # Colonne standardisée
        standardized_col = f"{column}_standardized"
        mapping_col = f"{column}_mapping"
        
        # Traiter chaque valeur
        standardized_values = []
        mapping_values = []
        
        for value in df[column]:
            standardized, score = self.text_processor.process_multiple_choice_field(
                value, possible_values, similarity_threshold
            )
            standardized_values.append(standardized)
            mapping_values.append(f"{value} -> {standardized} ({score:.2f})" if standardized else f"{value} -> Non reconnu")
        
        df[standardized_col] = standardized_values
        
        if create_mapping:
            df[mapping_col] = mapping_values
        
        return df
    
    def detect_multiple_choice_patterns(self, df: pd.DataFrame, column: str,
                                     min_frequency: int = 2) -> List[str]:
        """
        Détecte automatiquement les patterns dans une colonne à choix multiples
        
        Args:
            df: DataFrame contenant les données
            column: Nom de la colonne à analyser
            min_frequency: Fréquence minimale pour considérer un pattern
            
        Returns:
            Liste des patterns détectés
        """
        if column not in df.columns:
            return []
        
        # Compter les occurrences
        value_counts = df[column].value_counts()
        
        # Filtrer par fréquence minimale
        frequent_values = value_counts[value_counts >= min_frequency].index.tolist()
        
        # Nettoyer et normaliser les valeurs
        cleaned_values = []
        for value in frequent_values:
            if pd.notna(value):
                cleaned = self.text_processor.clean_text(str(value))
                if cleaned and len(cleaned) > 1:
                    cleaned_values.append(cleaned)
        
        # Regrouper les valeurs similaires
        clusters = self.text_processor.cluster_similar_texts(
            cleaned_values, similarity_threshold=0.8, method='fuzzy'
        )
        
        # Extraire les représentants de chaque cluster
        patterns = []
        for cluster in clusters:
            if cluster:
                # Prendre la valeur la plus fréquente du cluster
                cluster_values = [frequent_values[i] for i in cluster]
                representative = max(cluster_values, key=lambda x: value_counts[x])
                patterns.append(representative)
        
        return patterns


def apply_text_processing(df: pd.DataFrame, text_columns: List[str],
                         text_processor: Optional[TextProcessor] = None,
                         extract_features: bool = True,
                         extract_keywords: bool = False,
                         detect_topics: bool = False) -> pd.DataFrame:
    """
    Applique le traitement textuel à un DataFrame
    
    Args:
        df: DataFrame à traiter
        text_columns: Colonnes textuelles à traiter
        text_processor: Instance de TextProcessor (créée automatiquement si None)
        extract_features: Extraire les features textuelles
        extract_keywords: Extraire les mots-clés
        detect_topics: Détecter les topics
        
    Returns:
        DataFrame enrichi avec les features textuelles
    """
    if text_processor is None:
        text_processor = TextProcessor()
    
    df = df.copy()
    
    for column in text_columns:
        if column not in df.columns:
            continue
        
        logger.info(f"Traitement de la colonne textuelle: {column}")
        
        # Extraction de features textuelles
        if extract_features:
            features_df = pd.DataFrame([
                text_processor.extract_text_features(text)
                for text in df[column]
            ])
            
            # Ajouter les features au DataFrame
            for feature in features_df.columns:
                df[f"{column}_{feature}"] = features_df[feature]
        
        # Extraction de mots-clés
        if extract_keywords and len(df) > 1:
            texts = df[column].dropna().astype(str).tolist()
            if texts:
                keywords = text_processor.extract_keywords(texts)
                logger.info(f"Mots-clés extraits pour {column}: {keywords[:5]}")
        
        # Détection de topics
        if detect_topics and len(df) > 5:
            texts = df[column].dropna().astype(str).tolist()
            if texts:
                topics, doc_topic_matrix = text_processor.detect_topics(texts)
                logger.info(f"Topics détectés pour {column}: {topics[:3]}")
                
                # Ajouter les scores de topics au DataFrame
                if len(doc_topic_matrix) > 0:
                    for i in range(min(doc_topic_matrix.shape[1], 3)):
                        df[f"{column}_topic_{i+1}"] = doc_topic_matrix[:, i]
    
    return df
