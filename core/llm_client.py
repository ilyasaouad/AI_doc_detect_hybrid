"""
Minimal Ollama API client.
No external SDK required.
"""

import time
import requests
from config.settings import (
    OLLAMA_HOST,
    OLLAMA_TIMEOUT,
    OLLAMA_MAX_RETRIES,
    DEFAULT_MODEL,
)

class OllamaClient:
    def __init__(self, model_name: str | None = None):
        self.model = model_name or DEFAULT_MODEL
        self.endpoint = f"{OLLAMA_HOST}/api/generate"

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        last_error = None
        for _ in range(OLLAMA_MAX_RETRIES):
            try:
                response = requests.post(
                    self.endpoint,
                    json=payload,
                    timeout=OLLAMA_TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                last_error = e
                time.sleep(1)

        raise RuntimeError(f"Ollama request failed: {last_error}")
