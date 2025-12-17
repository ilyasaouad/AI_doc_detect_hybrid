# AI Document Detection (MVP)

Minimal heuristic-based detector to estimate whether a document is AI-generated. Supports plain text and PDFs (via pdfplumber).

## Requirements

- Python 3.11+ (recommended)
- pdfplumber (for PDF extraction)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

Analyze a PDF and print a console report:

```bash
python main.py --pdf "path/to/doc.pdf"
```

Analyze a text string:

```bash
python main.py --text "This is an example patent description..."
```

Save JSON output alongside console report:

```bash
python main.py --pdf "path/to/doc.pdf" --json-out result.json
```

### Streamlit UI (Upload PDF/DOCX/TXT)

Run the app:

```bash
streamlit run app_streamlit.py
```

Then open the provided local URL. Upload a PDF, DOCX, or TXT file to see the analysis and download JSON.

In the sidebar, adjust the AI decision threshold to control when the app flags text as AI-generated.
## Output

The console report includes:
- Likely AI-generated (bool)
- Confidence score (0–1)
- Risk level (minimal/low/medium/high)
- Feature scores
- Detailed explanations
- Recommendations

The optional JSON includes all the above in machine-readable form.

## Notes
- This is a minimal heuristic MVP; it doesn’t use ML models. It relies on linguistic/structural signals.
- PDF extraction quality varies by document; some PDFs may not extract clean text.

## Development

Project layout:
- `main.py` – CLI entry point
- `detector.py` – Orchestrates analyzers and aggregates scores
- `analyzers.py` – Heuristic feature analyzers (incl. drawing description consistency)
- `text_utils.py` – Tokenization and text statistics
- `report_generator.py` – Console and JSON report rendering
- `data_models.py` – Data classes (e.g., DetectionResult)

Run help:

```bash
python main.py -h
```
# AI_doc_detect_hybrid
