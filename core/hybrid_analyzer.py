"""
Hybrid analyzer combining traditional heuristics with AI-powered analysis.
"""

from detector import PatentAIDetector
from core.ai_analyzer import AIAnalyzer
from config.settings import HYBRID_WEIGHTS
from data_models import DetectionResult


class HybridAnalyzer:
    def __init__(self, model_name: str | None = None, decision_threshold: float = 0.6, feature_weights: dict | None = None):
        # Allow passing the same tunables as the UI
        self.traditional = PatentAIDetector(decision_threshold=decision_threshold, feature_weights=feature_weights)
        self.ai = AIAnalyzer(model_name)

    def analyze(self, text: str) -> DetectionResult:
        trad_result = self.traditional.analyze_text(text)
        ai_result = self.ai.analyze(text)

        if ai_result.risk_level == "ERROR":
            return trad_result

        combined_score = (
            trad_result.confidence_score * HYBRID_WEIGHTS["traditional"]
            + ai_result.confidence_score * HYBRID_WEIGHTS["ai"]
        )

        risk, verdict = self._verdict(combined_score)

        merged_features = dict(trad_result.feature_scores)
        merged_features.update(ai_result.feature_scores)

        merged_details = dict(trad_result.detailed_analysis)
        merged_details.update(ai_result.detailed_analysis)

        return DetectionResult(
            is_likely_ai_generated=verdict,
            confidence_score=round(combined_score, 2),
            risk_level=risk,
            feature_scores=merged_features,
            detailed_analysis=merged_details,
            recommendations=self._merge_recommendations(
                trad_result, ai_result, combined_score
            ),
        )

    def _verdict(self, score: float):
        if score >= 0.75:
            return "HIGH", True
        elif score >= 0.6:
            return "MEDIUM", True
        elif score >= 0.4:
            return "LOW", False
        return "MINIMAL", False

    def _merge_recommendations(self, trad, ai, score):
        recs = []
        recs.extend(trad.recommendations)
        recs.extend(ai.recommendations)

        if score >= 0.6:
            recs.append("Hybrid system flags this document for review")

        return list(dict.fromkeys(recs))
