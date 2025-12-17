"""
Demo entry point for hybrid AI + heuristic detection.
"""

from core.hybrid_analyzer import HybridAnalyzer
from report_generator import generate_report


def main():
    analyzer = HybridAnalyzer()

    print("Enter patent text (Ctrl+D to finish):")
    text = ""
    try:
        while True:
            text += input() + "\n"
    except EOFError:
        pass

    result = analyzer.analyze(text)
    print(generate_report(result))


if __name__ == "__main__":
    main()
