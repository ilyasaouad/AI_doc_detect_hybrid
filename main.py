"""
main.py
=======
CLI entry for AI document detection (PDF minimal support).
"""

import argparse
import sys
from pathlib import Path

from detector import PatentAIDetector
from report_generator import generate_report, generate_summary, as_json


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="AI Document Detection")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--pdf", type=str, help="Path to PDF file to analyze")
    g.add_argument("--text", type=str, help="Plain text to analyze")
    p.add_argument("--threshold", type=float, default=0.6, help="Decision threshold for AI classification (default 0.6)")
    p.add_argument("--json-out", type=str, help="Optional path to write JSON output")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    detector = PatentAIDetector(decision_threshold=args.threshold)

    try:
        if args.pdf:
            result = detector.analyze_pdf(args.pdf)
        else:
            result = detector.analyze_text(args.text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    # Console report
    print(generate_report(result))

    # JSON output if requested
    if args.json_out:
        out_path = Path(args.json_out)
        try:
            out_path.write_text(as_json(result), encoding="utf-8")
            print(f"\nWrote JSON to: {out_path}")
        except Exception as e:
            print(f"Failed to write JSON: {e}", file=sys.stderr)
            return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
