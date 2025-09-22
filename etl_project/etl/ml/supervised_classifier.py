"""
Module de scoring des pays basé sur l'analyse PCA multi-dimensionnelle
Adapté du script Jupyter Scripts_python/Modele1_IT/Script python_IT.ipynb
"""

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json
logger = logging.getLogger(__name__)

class CountryScoringEngine:
    """
    Moteur de scoring des pays basé sur l'analyse PCA multi-dimensionnelle
    """
    
    def __init__(self):
        self.dimensions = {
            "Macroéconomie": ["P1_"],
            "Système financier": ["P2_"],
            "Inclusion financière et numérique": ["P3_"],
            "Démographie et développement": ["P4_"]
        }
        
        self.scaler = StandardScaler()
        self.pca = PCA()
        self.scoring_results = {}
        
    def load_data(self, data_source: str) -> pd.DataFrame:
        """
        Charge les données depuis une source (Excel, CSV, ou base de données)
        """
        try:
            if data_source.endswith('.xlsx'):
                df = pd.read_excel(data_source, sheet_name='DB_Modele')
            elif data_source.endswith('.csv'):
                df = pd.read_csv(data_source)
            else:
                # Pour l'instant, utiliser des données de test
                df = self._generate_test_data()
            
            # Nettoyage des données
            df = self._clean_data(df)
            return df
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            return self._generate_test_data()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie et standardise les données
        """
        df = df.copy()
        
        # Standardisation des noms de pays
        df["PAYS"] = (
            df["PAYS"]
            .str.strip()
            .str.title()
            .replace({
                "Benin": "Bénin",
                "benin": "Bénin",
                "Côte D'Ivoire": "Côte d'Ivoire",
                "Guinée - Bissau": "Guinée-Bissau"
            })
        )
        
        # Identifier les colonnes numériques
        num_cols = [col for col in df.columns if col not in ["PAYS", "ANNEE"]]
        
        # Conversion en numérique
        df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
        
        # Remplacer les NaN par la moyenne du pays
        df[num_cols] = df.groupby("PAYS")[num_cols].transform(
            lambda col: col.fillna(col.mean()).infer_objects(copy=False)
        )
        
        return df
    
    def _generate_test_data(self) -> pd.DataFrame:
        """
        Génère des données de test pour les pays UEMOA
        """
        countries = ["Bénin", "Burkina Faso", "Côte d'Ivoire", "Guinée-Bissau", 
                    "Mali", "Niger", "Sénégal", "Togo"]
        
        data = []
        for country in countries:
            for year in range(2010, 2025):
                row = {
                    "PAYS": country,
                    "ANNEE": year,
                    # Variables macroéconomiques (P1_)
                    "P1_CIFSPB": np.random.normal(50, 10),
                    "P1_CIFSP": np.random.normal(45, 8),
                    "P1_PH": np.random.normal(60, 12),
                    "P1_PUDC": np.random.normal(40, 15),
                    "P1_TIM": np.random.normal(55, 10),
                    "P1_RFPSPNB": np.random.normal(35, 8),
                    "P1_TCP": np.random.normal(50, 12),
                    
                    # Variables système financier (P2_)
                    "P2_NFB": np.random.normal(30, 8),
                    "P2_NSB": np.random.normal(25, 6),
                    "P2_NEF": np.random.normal(20, 5),
                    "P2_NSEF": np.random.normal(15, 4),
                    "P2_NB": np.random.normal(35, 10),
                    "P2_EB": np.random.normal(40, 12),
                    "P2_EF": np.random.normal(30, 8),
                    "P2_ECB": np.random.normal(25, 6),
                    "P2_ETC": np.random.normal(20, 5),
                    "P2_EEF": np.random.normal(15, 4),
                    
                    # Variables inclusion financière (P3_)
                    "P3_TB": np.random.normal(45, 10),
                    "P3_NTCMEO": np.random.normal(30, 8),
                    "P3_NCMEA": np.random.normal(25, 6),
                    "P3_NTPS": np.random.normal(35, 10),
                    "P3_NCIET": np.random.normal(20, 5),
                    "P3_NTT": np.random.normal(40, 12),
                    "P3_VMJ": np.random.normal(50, 15),
                    "P3_VATTC": np.random.normal(45, 10),
                    "P3_VAMT": np.random.normal(30, 8),
                    "P3_VAMJ": np.random.normal(25, 6),
                    "P3_NTPP": np.random.normal(35, 10),
                    "P3_VATPP": np.random.normal(40, 12),
                    "P3_VP": np.random.normal(50, 15),
                    "P3_VAP": np.random.normal(45, 10),
                    
                    # Variables démographie (P4_)
                    "P4_SP": np.random.normal(60, 15),
                    "P4_P": np.random.normal(55, 12)
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def calculate_dimension_scores(self, df: pd.DataFrame, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcule les scores par dimension pour une année donnée ou toute la période
        """
        # Filtrer par année si spécifiée
        if year:
            df_filtered = df[df["ANNEE"] == year].copy()
        else:
            df_filtered = df[(df["ANNEE"] >= 2010) & (df["ANNEE"] <= 2024)].copy()
        
        results = {}
        
        for dimension_name, prefixes in self.dimensions.items():
            # Identifier les colonnes de cette dimension
            dimension_cols = []
            for prefix in prefixes:
                dimension_cols.extend([col for col in df_filtered.columns if col.startswith(prefix)])
            
            if not dimension_cols:
                continue
            
            # Extraire les données de la dimension
            dimension_data = df_filtered[dimension_cols].values
            
            # Standardisation
            dimension_data_scaled = self.scaler.fit_transform(dimension_data)
            
            # Analyse PCA
            pca_result = self.pca.fit_transform(dimension_data_scaled)
            
            # Calcul des coefficients PCA
            pca_coefficients = self.pca.components_[0]  # Première composante principale
            
            # Calcul des scores par critère
            scores_by_criteria = []
            for i, col in enumerate(dimension_cols):
                if i < len(pca_coefficients):
                    score = dimension_data_scaled[:, i] * pca_coefficients[i]
                    scores_by_criteria.append({
                        'criteria': col,
                        'coefficient': pca_coefficients[i],
                        'scores': score.tolist()
                    })
            
            # Score global de la dimension
            dimension_scores = np.sum([item['scores'] for item in scores_by_criteria], axis=0)
            
            # Normalisation des scores (0-100)
            min_score = np.min(dimension_scores)
            max_score = np.max(dimension_scores)
            normalized_scores = ((dimension_scores - min_score) / (max_score - min_score)) * 100
            
            results[dimension_name] = {
                'scores': normalized_scores.tolist(),
                'criteria_details': scores_by_criteria,
                'pca_explained_variance': self.pca.explained_variance_ratio_[0],
                'countries': df_filtered['PAYS'].tolist(),
                'years': df_filtered['ANNEE'].tolist() if year is None else [year] * len(df_filtered)
            }
        
        return results
    
    def calculate_global_scores(self, df: pd.DataFrame, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcule les scores globaux par pays
        """
        dimension_scores = self.calculate_dimension_scores(df, year)
        
        # Extraire les pays uniques
        if year:
            countries = df[df["ANNEE"] == year]['PAYS'].unique()
        else:
            countries = df[(df["ANNEE"] >= 2010) & (df["ANNEE"] <= 2024)]['PAYS'].unique()
        
        global_results = {}
        
        for country in countries:
            country_scores = []
            dimension_details = {}
            
            for dimension_name, dimension_data in dimension_scores.items():
                # Trouver l'index du pays dans les résultats
                country_index = dimension_data['countries'].index(country) if country in dimension_data['countries'] else None
                
                if country_index is not None:
                    score = dimension_data['scores'][country_index]
                    country_scores.append(score)
                    dimension_details[dimension_name] = {
                        'score': float(score),
                        'notation': self._get_notation(score),
                        'signification': self._get_signification(score)
                    }
            
            # Score global (moyenne des dimensions)
            global_score = np.mean(country_scores) if country_scores else 0
            
            global_results[country] = {
                'global_score': float(global_score),
                'global_notation': self._get_notation(global_score),
                'global_signification': self._get_signification(global_score),
                'dimensions': dimension_details,
                'year': year if year else '2010-2024'
            }
        
        return global_results
    
    def _get_notation(self, score: float) -> str:
        """
        Attribue une notation basée sur le score
        """
        if 75 <= score <= 100:
            return "A"
        elif 50 <= score < 75:
            return "B"
        elif 25 <= score < 50:
            return "C"
        elif 0 <= score < 25:
            return "D"
        else:
            return "E"
    
    def _get_signification(self, score: float) -> str:
        """
        Attribue une signification basée sur le score
        """
        if 75 <= score <= 100:
            return "Excellent"
        elif 50 <= score < 75:
            return "Bon"
        elif 25 <= score < 50:
            return "Moyen"
        elif 0 <= score < 25:
            return "Faible"
        else:
            return "Très Faible"
    
    def get_country_evolution(self, df: pd.DataFrame, country: str) -> Dict[str, Any]:
        """
        Calcule l'évolution des scores d'un pays sur la période
        """
        country_data = df[df["PAYS"] == country].copy()
        
        if country_data.empty:
            return {}
        
        evolution = []
        
        for year in sorted(country_data["ANNEE"].unique()):
            year_scores = self.calculate_global_scores(df, year)
            
            if country in year_scores:
                evolution.append({
                    'year': int(year),
                    'global_score': year_scores[country]['global_score'],
                    'global_notation': year_scores[country]['global_notation'],
                    'dimensions': year_scores[country]['dimensions']
                })
        
        return {
            'country': country,
            'evolution': evolution,
            'period': f"{min(evolution, key=lambda x: x['year'])['year']}-{max(evolution, key=lambda x: x['year'])['year']}" if evolution else "N/A"
        }
    
    def process_country_scoring(self, data_source: str, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Fonction principale pour traiter le scoring des pays
        """
        try:
            # Charger les données
            df = self.load_data(data_source)
            
            # Calculer les scores globaux
            global_scores = self.calculate_global_scores(df, year)
            
            # Calculer l'évolution pour chaque pays
            evolution_data = {}
            for country in global_scores.keys():
                evolution_data[country] = self.get_country_evolution(df, country)
            
            return {
                'success': True,
                'data_source': data_source,
                'year': year,
                'processed_at': datetime.now().isoformat(),
                'global_scores': global_scores,
                'evolution_data': evolution_data,
                'summary': {
                    'total_countries': len(global_scores),
                    'average_score': np.mean([score['global_score'] for score in global_scores.values()]),
                    'best_country': max(global_scores.items(), key=lambda x: x[1]['global_score'])[0],
                    'worst_country': min(global_scores.items(), key=lambda x: x[1]['global_score'])[0]
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du scoring: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }


def process_file_scoring(file_path: str, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Fonction principale pour traiter un fichier de données et calculer les scores
    """
    engine = CountryScoringEngine()
    return engine.process_country_scoring(file_path, year)

@login_required
def get_country_scores(file_path: str, country_code: str, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Récupère les scores d'un pays spécifique
    """
    engine = CountryScoringEngine()
    result = engine.process_country_scoring(file_path, year)
    
    if not result['success']:
        return result
    
    # Mapper les codes pays aux noms
    country_mapping = {
        'BJ': 'Bénin',
        'BF': 'Burkina Faso', 
        'CI': 'Côte d\'Ivoire',
        'GW': 'Guinée-Bissau',
        'ML': 'Mali',
        'NE': 'Niger',
        'SN': 'Sénégal',
        'TG': 'Togo'
    }
    
    country_name = country_mapping.get(country_code)
    if not country_name:
        return {
            'success': False,
            'error': f'Pays non trouvé: {country_code}'
        }
    
    if country_name in result['global_scores']:
        return {
            'success': True,
            'country': country_name,
            'country_code': country_code,
            'year': year,
            'data': result['global_scores'][country_name],
            'evolution': result['evolution_data'][country_name]
        }
    else:
        return {
            'success': False,
            'error': f'Données non disponibles pour {country_name}'
        }

if __name__ == "__main__":
    # Test du module
    engine = CountryScoringEngine()
    result = engine.process_country_scoring("test_data", year=2023)
    print(json.dumps(result, indent=2, ensure_ascii=False))
