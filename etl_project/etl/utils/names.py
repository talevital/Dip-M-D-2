import os
import unicodedata
import re
import csv
from typing import Dict, Optional
from difflib import get_close_matches


def strip_accents(text: str) -> str:
    if text is None:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize('NFC', text)


def normalize_string(text: str) -> str:
    text = str(text or "").strip()
    text = strip_accents(text)
    # Replace non-letters by spaces
    text = re.sub(r"[^A-Za-z\s'-]", " ", text)
    # Collapse spaces
    text = re.sub(r"\s+", " ", text)
    # Uppercase
    return text.upper()


class NameStandardizer:
    def __init__(self, resource_csv_path: Optional[str] = None):
        self.mapping: Dict[str, str] = {}
        if resource_csv_path and os.path.exists(resource_csv_path):
            try:
                with open(resource_csv_path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        variant = normalize_string(row.get('variant', ''))
                        standard = normalize_string(row.get('standard', ''))
                        if variant and standard:
                            self.mapping[variant] = standard
            except Exception:
                # Fallback: keep empty mapping on read failure
                self.mapping = {}

    def standardize_token(self, token: str) -> str:
        norm = normalize_string(token)
        if not norm:
            return norm
        if norm in self.mapping:
            return self.mapping[norm]
        # Fuzzy match among known variants (simple)
        if self.mapping:
            match = get_close_matches(norm, self.mapping.keys(), n=1, cutoff=0.92)
            if match:
                return self.mapping[match[0]]
        return norm

    def standardize_full_name(self, value: str) -> str:
        value = normalize_string(value)
        if not value:
            return value
        # Split on spaces/hyphens/apostrophes while keeping separators normalized
        tokens = re.split(r"[\s\-']+", value)
        std_tokens = [self.standardize_token(t) for t in tokens if t]
        # Re-join with single space
        return " ".join(std_tokens)

















