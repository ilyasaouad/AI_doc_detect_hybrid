"""
text_utils.py
=============
Utility text processing functions used by analyzers.
"""

import math
import re
from typing import List, Tuple


def extract_words_only(text: str) -> List[str]:
    """
    Return a list of lowercase word tokens (letters/numbers) with punctuation removed.
    """
    if not text:
        return []
    # Normalize dashes
    normalized = text.replace("\u2013", "-").replace("\u2014", "-")
    # Replace non-word chars (keep dash and apostrophe inside words)
    normalized = re.sub(r"[^\w\-']+", " ", normalized)
    # Split and lowercase
    tokens = [t.lower().strip("-'") for t in normalized.split() if t.strip("-'")]
    return tokens


def split_into_sentences(text: str) -> List[str]:
    """
    Very lightweight sentence splitter (period/question/semicolon/exclamation based).
    """
    if not text:
        return []
    # Protect common abbreviations to avoid over-splitting
    protected = re.sub(r"\b(e\.g|i\.e|etc)\.", lambda m: m.group(0).replace(".", "<DOT>"), text, flags=re.I)
    parts = re.split(r"(?<=[\.\?\!;])\s+", protected)
    sentences = [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]
    return sentences


def calculate_word_count(text: str) -> int:
    return len(extract_words_only(text))


def calculate_density_per_1000_words(count: int, total_words: int) -> float:
    if total_words <= 0:
        return 0.0
    return (count / max(total_words, 1)) * 1000.0


def calculate_coefficient_of_variation(values: List[float]) -> float:
    if not values:
        return 0.0
    n = len(values)
    if n <= 1:
        return 0.0
    mean = sum(values) / n
    if mean == 0:
        return 0.0
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    std = var ** 0.5
    return std / mean


def _type_token_ratio(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def calculate_moving_average_ttr(tokens: List[str], window: int = 100) -> float:
    """
    Compute the average type-token ratio over sliding windows.
    """
    if not tokens:
        return 0.0
    if window <= 0:
        window = 50
    if len(tokens) <= window:
        return _type_token_ratio(tokens)
    ratios = []
    step = max(1, window // 2)
    for i in range(0, len(tokens) - window + 1, step):
        chunk = tokens[i:i + window]
        ratios.append(_type_token_ratio(chunk))
    return sum(ratios) / len(ratios) if ratios else 0.0


def create_ngrams(tokens: List[str], n: int = 2) -> List[Tuple[str, ...]]:
    if n <= 1 or not tokens:
        return []
    return [tuple(tokens[i:i + n]) for i in range(0, len(tokens) - n + 1)]
