from typing import List, Dict, Tuple
import re

def _normalize(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z\s'-]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s

def cluster_by_threshold(values: List[str], threshold: float = 0.85) -> List[List[str]]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception:
        # If sklearn not available, return trivial clusters
        return [[v] for v in values]

    # Keep a mapping to reconstruct original tokens but ignore empties
    unique_vals = []
    seen = set()
    for v in values:
        if v in seen:
            continue
        seen.add(v)
        if _normalize(v):
            unique_vals.append(v)

    if len(unique_vals) == 0:
        return []

    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4), preprocessor=_normalize)
    try:
        X = vec.fit_transform(unique_vals)
    except ValueError:
        # empty vocabulary or all stop words
        return [[v] for v in unique_vals]
    sim = cosine_similarity(X)

    # Build clusters via simple union-find / BFS on similarity graph
    n = len(unique_vals)
    visited = [False]*n
    clusters: List[List[str]] = []
    for i in range(n):
        if visited[i]:
            continue
        stack = [i]
        visited[i] = True
        comp_idx = [i]
        while stack:
            u = stack.pop()
            for v in range(n):
                if not visited[v] and sim[u, v] >= threshold:
                    visited[v] = True
                    stack.append(v)
                    comp_idx.append(v)
        clusters.append([unique_vals[k] for k in comp_idx])
    return clusters


