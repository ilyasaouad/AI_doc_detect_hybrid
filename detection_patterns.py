"""
detection_patterns.py
=====================
Patterns and phrases commonly associated with AI-generated text.
"""


class AIPatterns:
    """Collections of AI-typical linguistic patterns."""

    AI_PHRASE_PATTERNS = [
        r'\bin accordance with\b',
        r'\bin one embodiment\b',
        r'\bit should be noted that\b',
        r'\bit is worth noting\b',
        r'\bfurthermore\b',
        r'\bmoreover\b',
        r'\badditionally\b',
        r'\bin some implementations\b',
        r'\bas described herein\b',
        r'\bin various embodiments\b',
        r'\bthe present disclosure\b',
        r'\bby way of example\b',
        r'\bwithout limitation\b',
        r'\bone skilled in the art\b',
        r'\bit will be appreciated\b',
        r'\bit is contemplated\b',
        r'\bin certain aspects\b',
        r'\bas will be understood\b',
    ]

    TRANSITION_MARKERS = [
        'however', 'therefore', 'consequently', 'furthermore',
        'moreover', 'additionally', 'specifically', 'particularly',
        'notably', 'importantly', 'significantly', 'essentially',
        'fundamentally', 'accordingly', 'thus', 'hence'
    ]

    HEDGING_WORDS = [
        'may', 'might', 'could', 'can', 'possibly', 'potentially',
        'generally', 'typically', 'usually', 'often', 'sometimes',
        'substantially', 'approximately', 'relatively', 'somewhat'
    ]

    FILLER_PATTERNS = [
        r'\bin this regard\b',
        r'\bin this manner\b',
        r'\bin this context\b',
        r'\bto this end\b',
        r'\bwith respect to\b',
        r'\bwith regard to\b',
        r'\bin terms of\b',
        r'\bby virtue of\b',
    ]

    AI_STARTERS = ['the', 'in', 'a', 'this', 'these', 'an', 'according']
