import argparse
from pathlib import Path
import shutil

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
WORKSPACES_DIR = PROJECT_ROOT / "workspaces"
WORKSPACE_TEMPLATE_DIR = WORKSPACES_DIR / "_template"


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
    available_text = "\n".join(f"- {item}" for item in available) or "No files found."

    raise SystemExit(
        f"Could not find '{name}' in {directory}\n\nAvailable options:\n{available_text}"
    )


def resolve_workspace(workspace: str | None) -> Path | None:
    if not workspace:
        return None

    workspace_path = WORKSPACES_DIR / workspace

    if not workspace_path.exists():
        raise SystemExit(
            f"Workspace not found: {workspace_path}\n"
            f"Create it with: PYTHONPATH=src python -m ba_copilot.main workspace create {workspace}"
        )

    return workspace_path


def resolve_input_path(input_file: str, workspace_path: Path | None) -> Path:
    input_path = Path(input_file)

    if input_path.exists():
        return input_path

    if workspace_path:
        workspace_candidate = workspace_path / input_file
        if workspace_candidate.exists():
            return workspace_candidate

        notes_candidate = workspace_path / "notes" / input_file
        if notes_candidate.exists():
            return notes_candidate

    return input_path


def resolve_output_path(
    output: str | None,
    workspace_path: Path | None,
    prompt_name: str | None = None,
) -> Path | None:
    if not output:
        if workspace_path and prompt_name:
            return workspace_path / "outputs" / f"{prompt_name}.md"
        return None

    output_path = Path(output)

    if output_path.is_absolute():
        return output_path

    if workspace_path:
        return workspace_path / output_path

    return output_path


def resolve_prompt_path(prompt_name: str, workspace_path: Path | None) -> Path:
    if workspace_path:
        workspace_prompts_dir = workspace_path / "prompts"

        direct = workspace_prompts_dir / prompt_name
        if direct.exists():
            return direct

        with_md = workspace_prompts_dir / f"{prompt_name}.md"
        if with_md.exists():
            return with_md

    return resolve_named_file(PROMPTS_DIR, prompt_name)


def write_or_print_output(result: str, output_path: Path | None) -> None:
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"Output saved to: {output_path}")
    else:
        print(result)


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

    write_or_print_output(
        result,
        Path(output) if output else None,
    )


def run_workflow(
    persona: str,
    prompt_name: str,
    input_file: str,
    output: str | None,
    model: str | None,
    workspace: str | None,
) -> None:
    workspace_path = resolve_workspace(workspace)

    persona_path = resolve_named_file(PERSONAS_DIR, persona)
    prompt_path = resolve_prompt_path(prompt_name, workspace_path)
    input_path = resolve_input_path(input_file, workspace_path)
    output_path = resolve_output_path(output, workspace_path, prompt_name)

    persona_text = read_text_file(persona_path)
    prompt_text = read_text_file(prompt_path)
    notes_text = read_text_file(input_path)

    selected_model = model or persona

    combined_prompt = f"""
You must follow the persona and workflow instructions below.

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

    result = ask_ollama(
        combined_prompt,
        model=selected_model,
    )

    write_or_print_output(result, output_path)


def list_assets() -> None:
    print("\nPersonas:")
    for path in sorted(PERSONAS_DIR.glob("*.md")):
        print(f"- {path.stem}")

    print("\nPrompts:")
    for path in sorted(PROMPTS_DIR.glob("*.md")):
        print(f"- {path.stem}")

    print("\nWorkspaces:")

    if not WORKSPACES_DIR.exists():
        print("- No workspaces directory found.")
        return

    workspaces = [
        p for p in sorted(WORKSPACES_DIR.iterdir())
        if p.is_dir() and p.name != "_template"
    ]

    if not workspaces:
        print("- No project workspaces found.")
    else:
        for path in workspaces:
            print(f"- {path.name}")


def create_workspace(name: str) -> None:
    workspace_path = WORKSPACES_DIR / name

    if workspace_path.exists():
        raise SystemExit(f"Workspace already exists: {workspace_path}")

    if WORKSPACE_TEMPLATE_DIR.exists():
        shutil.copytree(WORKSPACE_TEMPLATE_DIR, workspace_path)
    else:
        for subdir in [
            "notes",
            "outputs",
            "knowledge",
            "decisions",
            "prompts",
        ]:
            (workspace_path / subdir).mkdir(
                parents=True,
                exist_ok=True,
            )

        (workspace_path / "README.md").write_text(
            f"# {name}\n\nProject workspace.\n",
            encoding="utf-8",
        )

    print(f"Workspace created: {workspace_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local business analysis copilot"
    )

    subparsers = parser.add_subparsers(dest="command")

    healthcheck_parser = subparsers.add_parser(
        "healthcheck",
        help="Check Ollama connectivity",
    )

    healthcheck_parser.add_argument(
        "--model",
        default="llama3.2:3b",
    )

    subparsers.add_parser(
        "list",
        help="List personas, prompts, and workspaces",
    )

    workspace_parser = subparsers.add_parser(
        "workspace",
        help="Manage workspaces",
    )

    workspace_subparsers = workspace_parser.add_subparsers(
        dest="workspace_command"
    )

    workspace_create_parser = workspace_subparsers.add_parser(
        "create",
        help="Create workspace",
    )

    workspace_create_parser.add_argument("name")

    run_parser = subparsers.add_parser(
        "run",
        help="Run persona + prompt workflow",
    )

    run_parser.add_argument(
        "--workspace",
        help="Workspace name under workspaces/",
    )

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
        default=None,
        help="Optional model override.",
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
        return

    if args.command == "list":
        list_assets()
        return

    if args.command == "workspace":
        if args.workspace_command == "create":
            create_workspace(args.name)
            return

        workspace_parser.print_help()
        return

    if args.command == "run":
        run_workflow(
            persona=args.persona,
            prompt_name=args.prompt,
            input_file=args.input,
            output=args.output,
            model=args.model,
            workspace=args.workspace,
        )
        return

    if args.command in LEGACY_PROMPTS:
        run_legacy_mode(
            mode=args.command,
            input_file=args.file,
            output=args.output,
            model=args.model,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
