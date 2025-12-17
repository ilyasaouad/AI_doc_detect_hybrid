"""
analyzers.py
============
Individual AI-detection analysis functions.
"""

import re
from collections import Counter
from typing import Tuple, Dict

from detection_patterns import AIPatterns
from text_utils import (
    split_into_sentences,
    calculate_word_count,
    calculate_density_per_1000_words,
    calculate_coefficient_of_variation,
    calculate_moving_average_ttr,
    extract_words_only,
    create_ngrams,
)

# All analyzer functions return (score, explanation)
# where score is 0..1 and higher means more likely AI for that feature.


def analyze_ai_patterns(text: str) -> Tuple[float, str]:
    if not text:
        return 0.0, "No text provided."
    total = 0
    matches = 0
    for pat in AIPatterns.AI_PHRASE_PATTERNS + AIPatterns.FILLER_PATTERNS:
        total += 1
        if re.search(pat, text, flags=re.I):
            matches += 1
    score = min(1.0, matches / max(total, 1))
    return score, f"Matched {matches}/{total} AI-typical phrases."


def analyze_transitions(text: str) -> Tuple[float, str]:
    if not text:
        return 0.0, "No text provided."
    tokens = extract_words_only(text)
    total_words = len(tokens)
    count = sum(1 for t in tokens if t in set(AIPatterns.TRANSITION_MARKERS))
    density = calculate_density_per_1000_words(count, total_words)
    # Heuristic: >20 per 1000 words is suspicious
    score = max(0.0, min(1.0, density / 20.0))
    return score, f"Transition density {density:.1f}/1000 words (count={count})."


def analyze_hedging(text: str) -> Tuple[float, str]:
    if not text:
        return 0.0, "No text provided."
    tokens = extract_words_only(text)
    total_words = len(tokens)
    count = sum(1 for t in tokens if t in set(AIPatterns.HEDGING_WORDS))
    density = calculate_density_per_1000_words(count, total_words)
    # Heuristic: >15 per 1000 words is suspicious
    score = max(0.0, min(1.0, density / 15.0))
    return score, f"Hedging density {density:.1f}/1000 words (count={count})."


def analyze_repetition(text: str) -> Tuple[float, str]:
    if not text:
        return 0.0, "No text provided."
    tokens = extract_words_only(text)
    if not tokens:
        return 0.0, "No tokens."
    counts = Counter(tokens)
    most_common = counts.most_common(5)
    # Repetition score based on proportion of top words
    top_total = sum(c for _, c in most_common)
    score = min(1.0, top_total / max(len(tokens), 1) * 2)  # amplify a bit
    details = ", ".join(f"{w}:{c}" for w, c in most_common)
    return score, f"Top-5 words cover {top_total}/{len(tokens)} tokens. [{details}]"


def analyze_vocabulary_diversity(text: str) -> Tuple[float, str]:
    tokens = extract_words_only(text)
    ttr = calculate_moving_average_ttr(tokens, window=100)
    # Lower diversity (low TTR) tends to be more AI-like; invert
    ai_score = max(0.0, min(1.0, 1.0 - ttr))
    return ai_score, f"Moving average TTR ~ {ttr:.2f}."


def analyze_sentence_structure(text: str) -> Tuple[float, str]:
    sentences = split_into_sentences(text)
    lengths = [calculate_word_count(s) for s in sentences]
    cv = calculate_coefficient_of_variation(lengths)
    # Very low variance across sentence lengths can be AI-like
    # Heuristic: cv < 0.35 => higher AI score
    if cv <= 0:
        score = 0.0
    else:
        score = max(0.0, min(1.0, (0.35 - min(cv, 0.35)) / 0.35))
    return score, f"Sentence length CV={cv:.2f} over {len(sentences)} sentences."


def analyze_uniformity(text: str) -> Tuple[float, str]:
    """Basic stylistic uniformity via start words of sentences."""
    sentences = split_into_sentences(text)
    starts = []
    for s in sentences:
        tokens = extract_words_only(s)
        if tokens:
            starts.append(tokens[0])
    if not starts:
        return 0.0, "No sentences."
    counts = Counter(starts)
    # If a few starters dominate, consider it more uniform -> more AI-like
    top = counts.most_common(1)[0][1]
    score = min(1.0, top / max(len(starts), 1))
    return score, f"Most frequent sentence starter occurs {top}/{len(starts)} sentences."


def analyze_burstiness(text: str) -> Tuple[float, str]:
    """Simple burstiness: variance of paragraph lengths (words). Lower = more AI-like."""
    if not text:
        return 0.0, "No text provided."
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    lengths = [calculate_word_count(p) for p in paragraphs]
    cv = calculate_coefficient_of_variation(lengths)
    # Low burstiness (low cv) -> higher AI score
    score = max(0.0, min(1.0, (0.3 - min(cv, 0.3)) / 0.3)) if lengths else 0.0
    return score, f"Paragraph length CV={cv:.2f} over {len(lengths)} paragraphs."


def analyze_drawing_descriptions(text: str) -> Tuple[float, str]:
    """
    Detect anomalies in patent drawing descriptions (FIG./Figure/Fig.) that are characteristic
    of AI-generated text:
      - Missing or sparse numeric references in figure sentences
      - High proportion of single-use reference numbers (lack of consistent reuse)
      - Low presence of spatial/relational connectors in figure sentences

    Returns:
      (ai_score, explanation) where ai_score in [0,1] and higher = more AI-like.
    """
    import re
    from collections import Counter

    if not text or not text.strip():
        return 0.0, "No text provided."

    # Split lightweightly by sentence boundaries
    sentence_split = re.split(r"(?<=[\.?\!;])\s+", text.strip())
    sentences = [s for s in sentence_split if s.strip()]
    if not sentences:
        return 0.0, "No sentences found."

    # Identify sentences that reference figures (FIG., Fig., Figure)
    fig_pattern = re.compile(r"\b(fig(?:\.|ure)?\s*\d+)\b", flags=re.I)
    figure_sents = [s for s in sentences if fig_pattern.search(s)]
    fs = len(figure_sents)
    if fs == 0:
        return 0.0, "No figure description sentences detected."

    # Numeric reference pattern: e.g., 12, 12a, 14b (common in drawings)
    ref_pattern = re.compile(r"\b(\d{1,4}[a-z]?)\b", flags=re.I)

    # Spatial/relational connectors typical in drawing descriptions
    connectors = [
        "connected to", "connected with", "coupled to", "coupled with",
        "adjacent to", "via", "through", "hinge", "slot", "aperture",
        "channel", "passage", "mounted to", "secured to", "mated with",
        "attached to", "in communication with", "in fluid communication",
        "interface", "joined to", "pivotally", "slidably", "rotatably",
    ]
    conn_patterns = [re.compile(r"\b" + re.escape(c) + r"\b", flags=re.I) for c in connectors]

    # Extract references and connector hits from figure sentences
    all_refs = []
    connector_hits = 0
    for s in figure_sents:
        refs = ref_pattern.findall(s)
        filtered = [r.lower() for r in refs]
        all_refs.extend(filtered)
        if any(cp.search(s) for cp in conn_patterns):
            connector_hits += 1

    ref_count = len(all_refs)
    unique_refs = len(set(all_refs))
    counts = Counter(all_refs)
    singletons = sum(1 for r, c in counts.items() if c == 1)
    singleton_rate = (singletons / unique_refs) if unique_refs > 0 else 1.0

    refs_per_fig_sentence = ref_count / fs if fs else 0.0
    connectors_per_fig_sentence = connector_hits / fs if fs else 0.0

    # Heuristic scoring (higher = more AI-like)
    if refs_per_fig_sentence >= 2.0:
        score_ref_density = 0.0
    else:
        score_ref_density = max(0.0, min(1.0, (2.0 - refs_per_fig_sentence) / 2.0))

    score_singleton = max(0.0, min(1.0, singleton_rate))

    score_connectors = max(0.0, min(1.0, 1.0 - min(1.0, connectors_per_fig_sentence)))

    if ref_count == 0:
        combined = 0.9
        explanation = (
            f"No numeric references found in {fs} figure sentence(s); this is atypical for patent drawings."
        )
        return combined, explanation

    combined = (
        0.45 * score_singleton
        + 0.35 * score_ref_density
        + 0.20 * score_connectors
    )
    combined = max(0.0, min(1.0, combined))

    details = (
        f"Figure sentences: {fs}, total refs: {ref_count}, unique refs: {unique_refs}; "
        f"singleton refs: {singletons} ({singleton_rate:.2f}); "
        f"refs/fig-sent: {refs_per_fig_sentence:.2f}; "
        f"connector density: {connectors_per_fig_sentence:.2f}/sentence."
    )
    return combined, details
