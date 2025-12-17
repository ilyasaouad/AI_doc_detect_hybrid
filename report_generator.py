"""
report_generator.py
===================
Generates human-readable and JSON reports.
"""

import json
from typing import Dict

from data_models import DetectionResult


def generate_report(result: DetectionResult) -> str:
    lines = []
    lines.append("AI Document Detection Report")
    lines.append("-" * 32)
    lines.append(f"Likely AI-generated: {result.is_likely_ai_generated}")
    lines.append(f"Confidence score: {result.confidence_score:.2f}")
    lines.append(f"Risk level: {result.risk_level}")
    lines.append("")
    lines.append("Feature Scores:")
    for k, v in sorted(result.feature_scores.items()):
        lines.append(f"  - {k}: {v:.2f}")
    lines.append("")
    lines.append("Details:")
    for k, v in sorted(result.detailed_analysis.items()):
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("Recommendations:")
    for rec in result.recommendations:
        lines.append(f"  - {rec}")
    return "\n".join(lines)


def generate_summary(result: DetectionResult) -> str:
    return f"AI-likely={result.is_likely_ai_generated}, conf={result.confidence_score:.2f}, risk={result.risk_level}"


def as_json(result: DetectionResult) -> str:
    payload: Dict[str, object] = {
        "is_likely_ai_generated": result.is_likely_ai_generated,
        "confidence_score": result.confidence_score,
        "risk_level": result.risk_level,
        "feature_scores": result.feature_scores,
        "detailed_analysis": result.detailed_analysis,
        "recommendations": result.recommendations,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
