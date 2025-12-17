"""
Streamlit app for AI document detection.
Users can upload PDF, DOCX, or TXT and view a report + download JSON.
"""

import io
from pathlib import Path
from typing import Optional

import streamlit as st

from detector import PatentAIDetector
from report_generator import generate_report, as_json
from core.hybrid_analyzer import HybridAnalyzer


def extract_text_from_upload(uploaded_file) -> str:
    """Extract raw text from an uploaded file based on its extension/MIME."""
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()
    data = uploaded_file.read()

    if name.endswith(".txt"):
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return data.decode("latin-1", errors="replace")

    if name.endswith(".pdf"):
        try:
            import pdfplumber  # type: ignore
        except Exception as e:
            st.error("pdfplumber is required for PDF extraction. Please install dependencies.")
            return ""
        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
        return "\n\n".join(text_parts)

    if name.endswith(".docx"):
        try:
            import docx  # python-docx
        except Exception as e:
            st.error("python-docx is required for DOCX extraction. Please install dependencies.")
            return ""
        text = []
        doc = docx.Document(io.BytesIO(data))
        for p in doc.paragraphs:
            if p.text:
                text.append(p.text)
        return "\n".join(text)

    st.warning("Unsupported file type. Please upload .pdf, .docx, or .txt")
    return ""


def main():
    st.set_page_config(page_title="AI Document Detector", layout="wide")
    st.title("AI Document Detection (MVP)")
    st.write("Upload a PDF, DOCX, or TXT file to analyze.")

    with st.sidebar:
        st.header("Input")
        input_mode = st.radio("Source", ["Upload file", "Paste text / Sample"], index=0)
        uploaded = None
        pasted_text = None
        if input_mode == "Upload file":
            uploaded = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
        else:
            sample = (
                "FIG. 1 illustrates a housing 10 coupled to a hinge 12 via pin 14. "
                "As shown in FIG. 2, the actuator 16a is connected to bracket 18 through slot 20. "
                "In FIG. 3, element 22 engages aperture 24b in the cover 26."
            )
            pasted_text = st.text_area("Paste text (or edit sample)", value=sample, height=180)
            if st.button("Use sample text"):
                st.session_state["pasted_text"] = sample
            if "pasted_text" in st.session_state and not pasted_text:
                pasted_text = st.session_state["pasted_text"]

        st.divider()
        st.header("Classification")
        mode = st.radio("Mode", ["Heuristic", "Heuristic + AI"], index=0, help="Heuristic-only or Hybrid with LLM")
        threshold = st.slider(
            "AI decision threshold", min_value=0.3, max_value=0.9, value=0.6, step=0.01,
            help="Classify as AI when confidence >= threshold",
        )

        # Presets and custom weights
        st.header("Weights")
        preset = st.selectbox("Preset", ["Balanced (default)", "Conservative", "Aggressive"], index=0)
        use_custom = st.checkbox("Customize weights", value=False)

        st.header("LLM (Hybrid)")
        model_name = st.text_input("Model name (Ollama)", value="llama3.2", help="Requires model pulled in Ollama")

        # Base weights by preset
        if preset == "Balanced (default)":
            base_weights = {
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
        elif preset == "Conservative":
            base_weights = {
                "ai_patterns": 0.22,
                "transitions": 0.10,
                "hedging": 0.10,
                "repetition": 0.12,
                "vocab_diversity": 0.13,
                "sentence_structure": 0.13,
                "uniformity": 0.07,
                "burstiness": 0.08,
                "drawing_descriptions": 0.05,
            }
        else:  # Aggressive
            base_weights = {
                "ai_patterns": 0.30,
                "transitions": 0.16,
                "hedging": 0.16,
                "repetition": 0.10,
                "vocab_diversity": 0.09,
                "sentence_structure": 0.07,
                "uniformity": 0.05,
                "burstiness": 0.04,
                "drawing_descriptions": 0.03,
            }

        weights = dict(base_weights)
        if use_custom:
            st.caption("Adjust feature weights; they will be normalized to sum to 1.0")
            for k in weights.keys():
                weights[k] = st.slider(f"{k}", min_value=0.0, max_value=0.5, value=float(weights[k]), step=0.01)
            # Normalize
            s = sum(weights.values()) or 1.0
            for k in weights:
                weights[k] = weights[k] / s

        run_btn = st.button("Analyze")

    if run_btn and input_mode == "Upload file" and uploaded is None:
        st.warning("Please upload a file first.")
        return

    should_run = run_btn or st.session_state.get("auto_run", False)
    if (uploaded is not None or (pasted_text and pasted_text.strip())) and should_run:
        st.session_state["auto_run"] = True
        with st.spinner("Extracting text and analyzing..."):
            if input_mode == "Upload file":
                text = extract_text_from_upload(uploaded)
            else:
                text = pasted_text or ""

            if not text.strip():
                st.error("No text provided or extracted.")
                return
            if mode == "Heuristic + AI":
                analyzer = HybridAnalyzer(decision_threshold=threshold, feature_weights=weights, model_name=model_name)
                result = analyzer.analyze(text)
            else:
                detector = PatentAIDetector(decision_threshold=threshold, feature_weights=weights)
                result = detector.analyze_text(text)

        col1, col2 = st.columns([3, 2])
        with col1:
            st.subheader("Report")
            st.text(generate_report(result))
        with col2:
            st.subheader("Summary")
            st.metric("Likely AI-generated", str(result.is_likely_ai_generated))
            st.metric("Confidence", f"{result.confidence_score:.2f}")
            st.metric("Risk level", result.risk_level)

            # LLM rationale details in Hybrid mode (Heuristic + AI)
            if mode == "Heuristic + AI":
                llm_score = result.feature_scores.get("llm_ai_assessment")
                if llm_score is not None:
                    st.subheader("LLM Assessment")
                    st.progress(min(1.0, max(0.0, float(llm_score))))
                    st.caption(result.detailed_analysis.get("llm_rationale", ""))
                    red_flags = result.detailed_analysis.get("llm_red_flags", "")
                    if red_flags:
                        st.caption(f"Red flags: {red_flags}")

            # Drawing description consistency quick view (if present)
            dd_score = result.feature_scores.get("drawing_descriptions")
            if dd_score is not None:
                st.subheader("Drawing Description Consistency")
                st.progress(min(1.0, max(0.0, dd_score)))
                st.caption(result.detailed_analysis.get("drawing_descriptions", ""))

            st.subheader("Download JSON")
            st.download_button(
                label="Download Result JSON",
                file_name=f"ai_detection_result.json",
                mime="application/json",
                data=as_json(result).encode("utf-8"),
            )

        with st.expander("Feature Scores", expanded=False):
            for k, v in sorted(result.feature_scores.items()):
                st.write(f"{k}: {v:.2f}")

        with st.expander("Details", expanded=False):
            for k, v in sorted(result.detailed_analysis.items()):
                st.write(f"- {k}: {v}")

        with st.expander("Recommendations", expanded=False):
            for rec in result.recommendations:
                st.write(f"- {rec}")


if __name__ == "__main__":
    main()
