"""
detector.py
===========
Main orchestrator for AI patent detection.
"""

from typing import Dict, List, Tuple

from data_models import DetectionResult
from analyzers import (
    analyze_uniformity,
    analyze_ai_patterns,
    analyze_sentence_structure,
    analyze_vocabulary_diversity,
    analyze_repetition,
    analyze_transitions,
    analyze_hedging,
    analyze_burstiness,
    analyze_drawing_descriptions,
)


FeatureFunc = callable


class PatentAIDetector:
    """
    Minimal heuristic detector that aggregates multiple feature scores into an overall
    confidence with simple weights.
    """

    def __init__(self, decision_threshold: float = 0.6, feature_weights: Dict[str, float] | None = None) -> None:
        # Decision threshold for classifying as AI-generated
        self.decision_threshold = float(decision_threshold)
        # Default weights (sum ≈ 1.0) to emphasize LLM-like signals
        default_weights: Dict[str, float] = {
            "ai_patterns": 0.25,
            "transitions": 0.12,
            "hedging": 0.12,
            "repetition": 0.11,
            "vocab_diversity": 0.11,
            "sentence_structure": 0.09,
            "uniformity": 0.05,
            "burstiness": 0.05,
            "drawing_descriptions": 0.10,
        }
        self.feature_weights: Dict[str, float] = feature_weights or default_weights

    def analyze_text(self, text: str) -> DetectionResult:
        features: Dict[str, float] = {}
        details: Dict[str, str] = {}

        def run(name: str, fn) -> None:
            score, expl = fn(text)
            features[name] = float(max(0.0, min(1.0, score)))
            details[name] = expl

        run("ai_patterns", analyze_ai_patterns)
        run("transitions", analyze_transitions)
        run("hedging", analyze_hedging)
        run("repetition", analyze_repetition)
        run("vocab_diversity", analyze_vocabulary_diversity)
        run("sentence_structure", analyze_sentence_structure)
        run("uniformity", analyze_uniformity)
        run("burstiness", analyze_burstiness)
        run("drawing_descriptions", analyze_drawing_descriptions)

        # Weighted sum
        confidence = 0.0
        for k, w in self.feature_weights.items():
            confidence += features.get(k, 0.0) * w

        # Option 3: penalize/boost when both transitions and hedging are very high
        if features.get("transitions", 0.0) > 0.9 and features.get("hedging", 0.0) > 0.9:
            confidence += 0.10

        confidence = max(0.0, min(1.0, confidence))

        risk = self._risk_from_confidence(confidence)
        recs = self._recommendations(confidence)

        return DetectionResult(
            is_likely_ai_generated=confidence >= self.decision_threshold,
            confidence_score=confidence,
            risk_level=risk,
            feature_scores=features,
            detailed_analysis=details,
            recommendations=recs,
        )

    def analyze_pdf(self, pdf_path: str) -> DetectionResult:
        text = self._extract_text_from_pdf(pdf_path)
        return self.analyze_text(text)

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            import pdfplumber  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "pdfplumber not available. Install with `pip install pdfplumber` or provide plain text."
            ) from e
        text_parts: List[str] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n\n".join(text_parts)

    @staticmethod
    def _risk_from_confidence(conf: float) -> str:
        if conf >= 0.75:
            return "high"
        if conf >= 0.6:
            return "medium"
        if conf >= 0.4:
            return "low"
        return "minimal"

    @staticmethod
    def _recommendations(conf: float) -> List[str]:
        if conf >= 0.75:
            return [
                "Perform manual review and cross-check with known prior art phrasing.",
                "Request author revision to reduce formulaic language and hedging.",
            ]
        if conf >= 0.6:
            return [
                "Spot-check sections with repetitive starters and transitions.",
                "Encourage domain-specific terminology and concrete examples.",
            ]
        if conf >= 0.4:
            return [
                "Consider minor edits to improve sentence variety and reduce filler.",
            ]
        return ["No immediate action needed; monitor writing style across documents."]
