"""
AI-powered analyzer using a local LLM (Ollama).
Produces a DetectionResult compatible with the existing system.
"""

import json
from typing import Dict
from data_models import DetectionResult
from config.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from config.settings import (
    MAX_INPUT_CHARS,
    MAX_TOKENS,
    TEMPERATURE,
)
from core.llm_client import OllamaClient


class AIAnalyzer:
    def __init__(self, model_name: str | None = None):
        self.client = OllamaClient(model_name)

    def _parse_json_safe(self, raw: str) -> dict:
        """Try strict JSON, then fallback to extracting the largest JSON object."""
        try:
            return json.loads(raw)
        except Exception:
            pass
        # Fallback: find the outermost JSON object via regex and attempt to load
        import re
        candidates = re.findall(r"\{[\s\S]*\}", raw)
        for chunk in reversed(candidates):  # try the last one first
            try:
                return json.loads(chunk)
            except Exception:
                continue
        return {}

    def analyze(self, text: str) -> DetectionResult:
        try:
            truncated = text[:MAX_INPUT_CHARS]

            prompt = SYSTEM_PROMPT + "\n" + USER_PROMPT_TEMPLATE.format(text=truncated)
            raw = self.client.generate(
                prompt=prompt,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )

            parsed = self._parse_json_safe(raw)

            ai_score = float(parsed.get("ai_likelihood", 0.0)) if parsed else 0.0
            rationale = parsed.get("rationale", "") if parsed else ""
            red_flags = parsed.get("red_flags", []) if parsed else []
            confidence_notes = parsed.get("confidence_notes", "") if parsed else ""

            risk = self._risk_from_score(ai_score)

            return DetectionResult(
                is_likely_ai_generated=ai_score >= 0.6,
                confidence_score=round(ai_score, 2),
                risk_level=risk,
                feature_scores={"llm_ai_assessment": ai_score},
                detailed_analysis={
                    "llm_rationale": rationale,
                    "llm_red_flags": ", ".join(red_flags) if isinstance(red_flags, list) else str(red_flags),
                    "llm_confidence_notes": confidence_notes,
                },
                recommendations=self._recommendations(ai_score),
            )

        except Exception as e:
            return DetectionResult(
                is_likely_ai_generated=False,
                confidence_score=0.0,
                risk_level="ERROR",
                feature_scores={},
                detailed_analysis={"error": str(e)},
                recommendations=["LLM analysis failed – fallback recommended"],
            )

    def _risk_from_score(self, score: float) -> str:
        if score >= 0.75:
            return "HIGH"
        elif score >= 0.6:
            return "MEDIUM"
        elif score >= 0.4:
            return "LOW"
        return "MINIMAL"

    def _recommendations(self, score: float):
        if score >= 0.6:
            return [
                "LLM indicates likely AI-generated text",
                "Recommend manual review, especially drawings section",
            ]
        return ["No strong AI signal from LLM"]
