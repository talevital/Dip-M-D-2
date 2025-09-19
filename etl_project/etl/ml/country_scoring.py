#!/usr/bin/env python
# coding: utf-8

import os
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class CountryScoringEngine:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "Scripts_python", "Modele1_IT", "DATA_uemoa-pp0.xlsx")
        
    def charger_donnees(self) -> pd.DataFrame:
        """Charge l'Excel local en utilisant un chemin relatif au fichier courant."""
        try:
            df = pd.read_excel(self.data_path, sheet_name='DB_Modele')
            
            # Nettoyage standard des pays
            df = df.copy()
            df["PAYS"] = (
                df["PAYS"].astype(str)
                .str.strip()
                .str.title()
                .replace({
                    "Benin": "Bénin",
                    "benin": "Bénin",
                    "Côte D'Ivoire": "Côte d'Ivoire",
                    "Guinée - Bissau": "Guinée-Bissau",
                })
            )
            
            # Forcer numérique sur toutes les colonnes indicateurs (hors PAYS/ANNEE)
            num_cols = [c for c in df.columns if c not in ["PAYS", "ANNEE"]]
            df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")
            df[num_cols] = df.groupby("PAYS")[num_cols].transform(lambda col: col.fillna(col.mean()))
            
            return df
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données: {e}")
            raise

    def calculer_scores(self, df_source: pd.DataFrame, annee: Optional[int] = None, 
                       poids: Optional[Dict[str, float]] = None, 
                       pays: Optional[List[str]] = None) -> pd.DataFrame:
        """Calcule le DataFrame final des scores et notations.
        - annee: None pour toute la période (2010-2024) sinon une année précise
        - poids: dict avec clés des 4 dimensions en pourcentage ou None pour auto
        - pays: liste des pays à filtrer ou None pour tous
        """
        df = df_source.copy()

        # Filtre période
        if annee is not None:
            df = df[df["ANNEE"] == annee]
        else:
            df = df[(df["ANNEE"] >= 2010) & (df["ANNEE"] <= 2024)]

        DIMENSIONS = {
            "Macroéconomie": [c for c in df.columns if c.startswith("P1_")],
            "Système financier": [c for c in df.columns if c.startswith("P2_")],
            "Inclusion financière et numérique": [c for c in df.columns if c.startswith("P3_")],
            "Démographie et développement": [c for c in df.columns if c.startswith("P4_")],
        }

        ID_COLS = ["PAYS", "ANNEE"]
        df_Macro = df[ID_COLS + DIMENSIONS["Macroéconomie"]]
        df_Fin = df[ID_COLS + DIMENSIONS["Système financier"]]
        df_Incl = df[ID_COLS + DIMENSIONS["Inclusion financière et numérique"]]
        df_Demo = df[ID_COLS + DIMENSIONS["Démographie et développement"]]

        # MinMax scaling par dimension
        def scale_part(df_part):
            cols_num = [c for c in df_part.columns if c not in ID_COLS]
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled = pd.DataFrame(scaler.fit_transform(df_part[cols_num]), columns=cols_num)
            return scaled

        macro_scaled = scale_part(df_Macro)
        fin_scaled = scale_part(df_Fin)
        incl_scaled = scale_part(df_Incl)
        demo_scaled = scale_part(df_Demo)

        # PCA par dimension puis moyenne des PCs retenues pour 80% de variance
        def pca_reduce(df_scaled):
            pca = PCA()
            X = pca.fit_transform(df_scaled)
            explained = np.cumsum(pca.explained_variance_ratio_)
            n_components = int(np.argmax(explained >= 0.80) + 1)
            pca_final = PCA(n_components=n_components)
            X_final = pca_final.fit_transform(df_scaled)
            X_df = pd.DataFrame(X_final, columns=[f"PC{i+1}" for i in range(n_components)])
            score = X_df.mean(axis=1)
            return score

        s_macro = pca_reduce(macro_scaled)
        s_fin = pca_reduce(fin_scaled)
        s_incl = pca_reduce(incl_scaled)
        s_demo = pca_reduce(demo_scaled)

        # Fusion des scores
        df_resultat = pd.concat([
            df_Macro[ID_COLS].reset_index(drop=True),
            s_macro.rename("Macroéconomie"),
            s_fin.rename("Système financier"),
            s_incl.rename("Inclusion financière et numérique"),
            s_demo.rename("Démographie et développement"),
        ], axis=1)

        df_long = pd.melt(
            df_resultat,
            id_vars=ID_COLS,
            value_vars=[
                "Macroéconomie",
                "Système financier",
                "Inclusion financière et numérique",
                "Démographie et développement",
            ],
            var_name="Dimension",
            value_name="PC_Score",
        )

        # Poids
        if poids is None:
            unique_dims = df_long["Dimension"].unique()
            auto = 100 / len(unique_dims)
            poids_map = {d: auto for d in unique_dims}
        else:
            poids_map = poids

        df_long["Pondération"] = df_long["Dimension"].map(poids_map)
        df_long["Score_dimension"] = df_long["PC_Score"] * (df_long["Pondération"] / 100)

        # Normalisation et agrégation
        min_s, max_s = df_long['Score_dimension'].min(), df_long['Score_dimension'].max()
        if max_s - min_s == 0:
            df_long['score_normalise'] = 0
        else:
            df_long['score_normalise'] = ((df_long['Score_dimension'] - min_s) / (max_s - min_s)) * 100

        df_final = df_long.groupby(ID_COLS)["score_normalise"].sum().reset_index()
        df_final["Score_Global"] = df_final["score_normalise"] / 4

        # Notation
        def attribuer_notation(score):
            if 75 <= score <= 100:
                return "AAA", "Excellente qualité, risque minimal"
            elif 50 <= score < 75:
                return "AA-", "Haute qualité, risque faible"
            elif 25 <= score < 50:
                return "B+", "Hautement spéculatif, risque élevé"
            elif 0 <= score < 25:
                return "D", "Défaut avéré"
            else:
                return None, "Score invalide"

        df_final[["Notation", "Signification"]] = df_final['Score_Global'].apply(
            lambda x: pd.Series(attribuer_notation(x))
        )

        # Appliquer le filtre pays uniquement après le calcul global (pour conserver une normalisation cohérente)
        if pays is not None:
            if isinstance(pays, str):
                df_final = df_final[df_final["PAYS"] == pays]
            else:
                df_final = df_final[df_final["PAYS"].isin(pays)]

        return df_final

    def get_available_years(self) -> List[int]:
        """Retourne la liste des années disponibles"""
        df = self.charger_donnees()
        return sorted(df["ANNEE"].unique().tolist())

    def get_available_countries(self) -> List[str]:
        """Retourne la liste des pays disponibles"""
        df = self.charger_donnees()
        return sorted(df["PAYS"].unique().tolist())

    def calculate_scoring(self, year: Optional[int] = None, 
                         weights: Optional[Dict[str, float]] = None,
                         countries: Optional[List[str]] = None) -> Dict[str, Any]:
        """Point d'entrée principal pour le calcul de scoring"""
        try:
            df_full = self.charger_donnees()
            df_resultats = self.calculer_scores(df_full, annee=year, poids=weights, pays=countries)
            
            # Conversion en format JSON-friendly
            results = []
            for _, row in df_resultats.iterrows():
                results.append({
                    "pays": row["PAYS"],
                    "annee": int(row["ANNEE"]),
                    "score_global": float(row["Score_Global"]),
                    "notation": row["Notation"],
                    "signification": row["Signification"]
                })
            
            return {
                "success": True,
                "data": results,
                "summary": {
                    "total_countries": len(df_resultats["PAYS"].unique()),
                    "total_records": len(df_resultats),
                    "year_range": f"{year}" if year else "2010-2024",
                    "average_score": float(df_resultats["Score_Global"].mean()),
                    "best_score": float(df_resultats["Score_Global"].max()),
                    "worst_score": float(df_resultats["Score_Global"].min())
                },
                "config": {
                    "year": year,
                    "weights": weights,
                    "countries": countries
                },
                "processed_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul de scoring: {e}")
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
