import argparse
from pathlib import Path

from ba_copilot.llm import ask_ollama


PROMPTS = {
    "summarize": """
Summarise these notes into:
- Executive Summary
- Key Decisions
- Action Items
- Risks
- Open Questions
- Suggested Next Steps
""",
    "requirements": """
Extract requirements from these notes.

Return a Markdown table with:
ID | Requirement | Type | Priority | Rationale | Open Question
""",
    "stories": """
Convert these notes into user stories.

Format:
As a [user], I want [capability], so that [benefit].

Include Given / When / Then acceptance criteria.
""",
    "raid": """
Create a RAID log.

Return a Markdown table with:
Type | Description | Impact | Owner | Mitigation

Types:
- Risk
- Assumption
- Issue
- Dependency
""",
}


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=[
            "healthcheck",
            "summarize",
            "requirements",
            "stories",
            "raid",
        ],
    )

    parser.add_argument("file", nargs="?")
    parser.add_argument("--output", "-o")
    parser.add_argument("--model", default="llama3.2:3b")

    args = parser.parse_args()

    if args.mode == "healthcheck":
        result = ask_ollama(
            "Reply with only: Ollama connection OK",
            model=args.model,
        )
        print(result)
        return

    if not args.file:
        raise SystemExit("Please provide an input file.")

    input_path = Path(args.file)

    if not input_path.exists():
        raise SystemExit(f"File not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")

    prompt = f"""
{PROMPTS[args.mode]}

Input notes:
{text}
"""

    result = ask_ollama(prompt, model=args.model)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"Output saved to: {output_path}")
    else:
        print(result)


if __name__ == "__main__":
    main()
