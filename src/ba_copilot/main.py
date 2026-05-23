import argparse
from pathlib import Path

from ba_copilot.llm import ask_ollama


LEGACY_PROMPTS = {
    "summarize": "Summarise these notes into Executive Summary, Decisions, Actions, Risks, Open Questions, and Next Steps.",
    "requirements": "Extract a Markdown requirements table with ID, Requirement, Type, Priority, Rationale, and Open Question.",
    "stories": "Convert these notes into user stories with Given/When/Then acceptance criteria.",
    "raid": "Create a RAID log table with Type, Description, Impact, Owner, and Mitigation.",
}


PROJECT_ROOT = Path.cwd()
PERSONAS_DIR = PROJECT_ROOT / "personas"
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    return path.read_text(encoding="utf-8")


def resolve_named_file(directory: Path, name: str) -> Path:
    direct = directory / name
    if direct.exists():
        return direct

    with_md = directory / f"{name}.md"
    if with_md.exists():
        return with_md

    available = sorted(p.stem for p in directory.glob("*.md"))

    raise SystemExit(
        f"Could not find '{name}' in {directory}\n\nAvailable:\n- "
        + "\n- ".join(available)
    )


def run_healthcheck(model: str) -> None:
    result = ask_ollama(
        "Reply with only: Ollama connection OK",
        model=model,
    )
    print(result)


def run_legacy_mode(
    mode: str,
    input_file: str,
    output: str | None,
    model: str,
) -> None:
    notes = read_text_file(Path(input_file))

    prompt = f"""
{LEGACY_PROMPTS[mode]}

Input notes:
{notes}
"""

    result = ask_ollama(prompt, model=model)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        print(f"Output saved to: {output}")
    else:
        print(result)


def run_workflow(
    persona: str,
    prompt_name: str,
    input_file: str,
    output: str | None,
    model: str,
) -> None:
    persona_text = read_text_file(
        resolve_named_file(PERSONAS_DIR, persona)
    )

    prompt_text = read_text_file(
        resolve_named_file(PROMPTS_DIR, prompt_name)
    )

    notes_text = read_text_file(Path(input_file))

    combined_prompt = f"""
# Persona

{persona_text}

# Workflow Prompt

{prompt_text}

# Input Notes

{notes_text}

# Instruction

Use the persona as your role and perspective.
Use the workflow prompt as the task definition and output structure.
Analyse only the provided notes.
Do not invent unsupported facts.
"""

    result = ask_ollama(combined_prompt, model=model)

    if output:
        Path(output).write_text(result, encoding="utf-8")
        print(f"Output saved to: {output}")
    else:
        print(result)


def list_assets() -> None:
    print("\nPersonas:")
    for path in sorted(PERSONAS_DIR.glob("*.md")):
        print(f"- {path.stem}")

    print("\nPrompts:")
    for path in sorted(PROMPTS_DIR.glob("*.md")):
        print(f"- {path.stem}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local business analysis copilot"
    )

    subparsers = parser.add_subparsers(dest="command")

    healthcheck_parser = subparsers.add_parser("healthcheck")
    healthcheck_parser.add_argument(
        "--model",
        default="llama3.2:3b",
    )

    subparsers.add_parser("list")

    run_parser = subparsers.add_parser("run")

    run_parser.add_argument(
        "--persona",
        required=True,
    )

    run_parser.add_argument(
        "--prompt",
        required=True,
    )

    run_parser.add_argument(
        "--input",
        required=True,
    )

    run_parser.add_argument(
        "--output",
        "-o",
    )

    run_parser.add_argument(
        "--model",
        default="llama3.2:3b",
    )

    for legacy_mode in LEGACY_PROMPTS:
        legacy_parser = subparsers.add_parser(legacy_mode)

        legacy_parser.add_argument("file")

        legacy_parser.add_argument(
            "--output",
            "-o",
        )

        legacy_parser.add_argument(
            "--model",
            default="llama3.2:3b",
        )

    args = parser.parse_args()

    if args.command == "healthcheck":
        run_healthcheck(args.model)

    elif args.command == "list":
        list_assets()

    elif args.command == "run":
        run_workflow(
            persona=args.persona,
            prompt_name=args.prompt,
            input_file=args.input,
            output=args.output,
            model=args.model,
        )

    elif args.command in LEGACY_PROMPTS:
        run_legacy_mode(
            mode=args.command,
            input_file=args.file,
            output=args.output,
            model=args.model,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
