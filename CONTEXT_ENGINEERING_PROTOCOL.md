# AI Document Detection – Context Engineering Protocol and Documentation

Version: 0.1

## 1) Overview
This document defines the context engineering protocol, operating modes, and documentation for the AI Document Detection MVP. The goal is to make behavior predictable, configurable, and auditable across CLI and Streamlit UI, while preparing for future LLM-assisted features.

- Core engine: Heuristic analyzers + weighted aggregation (no ML dependencies)
- Inputs: PDF/DOCX/TXT (via Streamlit) and PDF/text via CLI
- Outputs: Human-readable report + JSON (CLI and Streamlit)
- Tunables: Feature weights, decision threshold, targeted rules (e.g., hedging+transitions bump)

## 2) System Components
- `text_utils.py`: Tokenization, sentence splitting, statistics (density, CV, TTR)
- `analyzers.py`: Heuristic features
  - AI phrase patterns, transitions, hedging, repetition, vocabulary diversity, sentence structure, uniformity, paragraph burstiness
- `detector.py`: PatentAIDetector orchestrates analyzers and aggregates scores with weights, threshold, and optional rule-based bumps
- `report_generator.py`: Human report and JSON serialization
- `main.py`: CLI interface (supports `--pdf`, `--text`, `--threshold`, optional `--json-out`)
- `app_streamlit.py`: Streamlit UI (file upload, threshold slider, report + JSON download)

## 3) Heuristics and Scoring
- Each analyzer returns `(score ∈ [0,1], explanation)`
- Weighted aggregation with adjusted LLM-oriented weights:
  - ai_patterns: 0.25
  - transitions: 0.12
  - hedging: 0.12
  - repetition: 0.11
  - vocab_diversity: 0.11
  - sentence_structure: 0.09
  - uniformity: 0.05
  - burstiness: 0.05
  - drawing_descriptions: 0.10
- Rule-based bump:
  - if transitions > 0.9 and hedging > 0.9: confidence += 0.10 (capped at 1.0)
- Decision threshold (default 0.60) determines AI classification.

## 4) Context Engineering Protocol
The app is heuristic-driven, but we treat configuration and usage as a context protocol to ensure consistent outcomes.

### 4.1 Goals
- Consistency across documents and operators
- Tunable sensitivity by scenario (conservative vs. aggressive detection)
- Transparent, explainable outputs suitable for audit/review

### 4.2 Personas
- Reviewer (default): Wants balanced detection, clear explanations, and simple controls (threshold)
- Investigator (aggressive): Willing to lower threshold and up-weight AI-like markers to flag candidates for review
- Compliance (conservative): Wants low false positives, prefers higher threshold and reduced weight on noisy features

### 4.3 Configuration Context Schema
- Decision threshold: float in [0.3, 0.9] (UI), default 0.6 (CLI/UI)
- Feature weights: dictionary[str → float] summing ≈ 1.0
- Rules: list of conditional adjustments (e.g., bump on extreme combos)

Recommended presets:
- Conservative: threshold=0.70; lower hedging/transitions to 0.10 each; increase sentence_structure to 0.14
- Balanced (default): threshold=0.60; weights as defined above
- Aggressive: threshold=0.45; increase ai_patterns/transitions/hedging (e.g., 0.32/0.16/0.16); reduce repetition/diversity

### 4.4 Input Preparation
- PDF: extracted using pdfplumber; results depend on PDF text structure
- DOCX: extracted using python-docx paragraphs
- TXT: read as UTF-8 (fallback latin-1)
- Recommendation: remove headers/footers/boilerplate if they dominate style

### 4.5 Output Interpretation
- Confidence score ∈ [0,1]
- Risk buckets (derived from confidence, for guidance only):
  - minimal (< 0.4), low (0.4–<0.6), medium (0.6–<0.75), high (≥ 0.75)
- Feature scores: 0..1 per analyzer; see explanations for reasons
- Recommendations: Rule-of-thumb edits and next steps

### 4.6 Change Management and Traceability
- Record the configuration used (threshold, weights, rules) together with the JSON output for auditability
- When tuning, capture before/after results and rationale

## 5) Usage

### 5.1 CLI
- Analyze PDF with default threshold:
  ```bash
  python main.py --pdf "path/to/file.pdf"
  ```
- Analyze text with custom threshold:
  ```bash
  python main.py --text "Some text..." --threshold 0.45
  ```
- Save JSON output:
  ```bash
  python main.py --pdf "path/to/file.pdf" --json-out result.json
  ```

### 5.2 Streamlit UI
- Run:
  ```bash
  streamlit run app_streamlit.py
  ```
- Upload PDF/DOCX/TXT, adjust the threshold slider, click Analyze
- Download JSON via the provided button

## 6) Configuration Recipes
- Flip borderline to AI (for evaluation only):
  - Lower threshold to 0.45
  - Optionally raise ai_patterns/transitions/hedging weights further
  - Add single-signal bump if desired, e.g., `if hedging > 0.9: confidence += 0.08`
- Conservative review:
  - Threshold ≥ 0.70; reduce hedging/transitions to 0.10; raise sentence_structure

## 7) Quality Assurance
- Test set: Collect a small corpus of known-human and known-LLM texts
- Metrics:
  - Balanced accuracy at threshold τ ∈ {0.45, 0.60, 0.70}
  - False positive rate (important for conservative mode)
  - Stability: small edits to text should not swing the label dramatically
- Regression checks:
  - Locked sample outputs for a few docs to detect unintended changes after refactors

## 8) Governance, Ethics, and Privacy
- This tool is heuristic and not a definitive classifier; always pair with human judgment
- Avoid punitive use; treat as triage/assistive signal
- Respect document confidentiality: files are processed locally; avoid uploading to third-party services
- Log only necessary metadata (if logging is enabled in the host environment)

## 9) Troubleshooting
- Streamlit missing static files (index.html): reinstall Streamlit without cache (see README troubleshooting), pin to `streamlit==1.32.2`
- PDF text extraction poor: try different extractor or preprocess with OCR where applicable
- Non-UTF-8 TXT: loader falls back to latin-1; consider re-encoding file

## 10) Future Extensions
- Interactive per-feature weight sliders in UI and saved profiles
- Model-assisted detectors (hybrid with heuristic baseline)
- Section-aware analysis (claims vs. abstract vs. description)
- Language detection and multilingual patterns

---
For questions or change requests, capture:
- Document type and sample (if sharable)
- Current configuration (threshold, weights, rules)
- Observed output and desired behavior
- Proposed adjustment and rationale
