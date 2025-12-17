"""
data_models.py
==============
Data structures used throughout the patent detector.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DetectionResult:
    """
    Stores the complete result of a patent analysis.
    """

    is_likely_ai_generated: bool
    confidence_score: float
    risk_level: str

    feature_scores: Dict[str, float]
    detailed_analysis: Dict[str, str]
    recommendations: List[str]
