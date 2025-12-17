# AI_doc_detect_hybrid

Hybrid AI + heuristic detector built on top of AI_doc_detect.

## Features
- Traditional heuristic detector (no external models)
- Optional Hybrid mode: combines heuristic score with a local LLM (Ollama)
- Streamlit UI: upload PDF/DOCX/TXT or paste text; adjust threshold and weights; Mode toggle (Heuristic / Heuristic + AI); select Ollama model

## Requirements
- Python 3.9+
- Optional for Hybrid mode: Ollama running locally with a model (default `llama3.2`)

```bash
pip install -r requirements.txt
```

## Environment
Create a `.env` file (optional) to override defaults:

```
# Ollama
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.2
OLLAMA_TIMEOUT=120
OLLAMA_MAX_RETRIES=3

# Hybrid weighting
TRADITIONAL_WEIGHT=0.4
AI_WEIGHT=0.6

# Logging
LOG_LEVEL=INFO
```

## Running (CLI - Hybrid)
You can quickly test the hybrid analyzer without Ollama; it will gracefully fall back to the traditional result if LLM analysis fails.

```bash
python main_hybrid.py < sample.txt
```

## Running (Streamlit UI)
Use the existing Streamlit app located here. It now supports a Mode toggle (Heuristic / Heuristic + AI) and paste sample text.

```bash
streamlit run app_streamlit.py
```

In the sidebar:
- Choose source: Upload file or Paste text / Sample
- Choose mode: Heuristic or Heuristic + AI
- Adjust decision threshold and (optionally) weights

## Notes
- If Ollama is not running or the model is missing, Hybrid mode will fall back to the traditional detector result.
- PDF text extraction quality varies by document.
