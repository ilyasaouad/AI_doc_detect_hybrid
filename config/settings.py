"""
Global configuration for AI-powered detection.
All values can be overridden via environment variables.
"""

import os
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# ===============================
# Ollama connection
# ===============================
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))

# ===============================
# Model selection
# ===============================
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2")

# ===============================
# Hybrid weights
# ===============================
HYBRID_WEIGHTS = {
    "traditional": float(os.getenv("TRADITIONAL_WEIGHT", "0.4")),
    "ai": float(os.getenv("AI_WEIGHT", "0.6")),
}

# ===============================
# LLM analysis limits
# ===============================
MAX_INPUT_CHARS = 6000        # truncate very long documents
MAX_TOKENS = 512              # response size
TEMPERATURE = 0.0             # deterministic output

# ===============================
# Logging
# ===============================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
