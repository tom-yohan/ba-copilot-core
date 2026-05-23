import argparse
import shutil
from pathlib import Path

from ba_copilot.llm import ask_ollama
from ba_copilot.prompts import (
    build_review_prompt,
    build_revise_prompt,
    build_workflow_prompt,
)
from ba_copilot.prompts import (
    build_review_prompt,
    build_revise_prompt,
    build_workflow_prompt,
)


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
MAX_WORKSPACE_CONTEXT_CHARS = 12000


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
    raise SystemExit(f"Could not find '{name}' in {directory}\n\nAvailable options:\n{available_text}")


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


def resolve_output_path(output: str | None, workspace_path: Path | None, default_name: str | None = None) -> Path | None:
    if not output:
        if workspace_path and default_name:
            return workspace_path / "outputs" / f"{default_name}.md"
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


def load_workspace_context(workspace_path: Path | None) -> str:
    if not workspace_path:
        return ""

    context_sections = []

    for folder_name in ["knowledge", "decisions"]:
        folder = workspace_path / folder_name
        if not folder.exists():
            continue

        for file_path in sorted(folder.glob("*.md")):
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            context_sections.append(f"## {folder_name}/{file_path.name}\n\n{content}")

    combined_context = "\n\n---\n\n".join(context_sections)

    if len(combined_context) > MAX_WORKSPACE_CONTEXT_CHARS:
        combined_context = combined_context[:MAX_WORKSPACE_CONTEXT_CHARS]
        combined_context += "\n\n[Workspace context truncated due to size limit.]"

    return combined_context


def write_or_print_output(result: str, output_path: Path | None) -> None:
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")
        print(f"Output saved to: {output_path}")
    else:
        print(result)


def run_healthcheck(model: str) -> None:
    result = ask_ollama("Reply with only: Ollama connection OK", model=model)
    print(result)


def run_legacy_mode(mode: str, input_file: str, output: str | None, model: str) -> None:
    notes = read_text_file(Path(input_file))

    prompt = f"""
{LEGACY_PROMPTS[mode]}

Input notes:
{notes}
"""

    result = ask_ollama(prompt, model=model)
    write_or_print_output(result, Path(output) if output else None)


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
    workspace_context = load_workspace_context(workspace_path)

    selected_model = model or persona

    combined_prompt = f"""
You must follow the persona and workflow instructions below.

# Persona

{persona_text}

# Workflow Prompt

{prompt_text}

# Workspace Context

{workspace_context or "No additional workspace context provided."}

# Input Notes

{notes_text}

# Instruction

Use the persona as your role and perspective.
Use the workflow prompt as the task definition and output structure.
Analyse only the provided notes.
Do not invent unsupported facts.
"""

    result = ask_ollama(combined_prompt, model=selected_model)
    write_or_print_output(result, output_path)


def run_review(
    reviewer: str,
    input_file: str,
    output: str | None,
    model: str | None,
    workspace: str | None,
) -> None:
    workspace_path = resolve_workspace(workspace)

    reviewer_path = resolve_named_file(PERSONAS_DIR, reviewer)
    input_path = resolve_input_path(input_file, workspace_path)
    output_path = resolve_output_path(output, workspace_path, "review")

    reviewer_text = read_text_file(reviewer_path)
    document_text = read_text_file(input_path)
    workspace_context = load_workspace_context(workspace_path)

    selected_model = model or reviewer

    combined_prompt = f"""
You must review the document below from the perspective of the reviewer persona.

# Reviewer Persona

{reviewer_text}

# Workspace Context

{workspace_context or "No additional workspace context provided."}

# Document To Review

{document_text}

# Review Instructions

Review the document. Do not rewrite it fully.

Produce:
1. Overall Assessment
2. Strengths
3. Weaknesses
4. Missing Risks or Assumptions
5. Gaps or Ambiguities
6. Recommended Improvements
7. Specific Suggested Edits

Rules:
- Be constructive and specific.
- Do not invent unsupported facts.
- Clearly label assumptions.
- Focus on improving quality, clarity, usefulness, and risk awareness.
"""

    result = ask_ollama(combined_prompt, model=selected_model)
    write_or_print_output(result, output_path)

def run_revise(
    reviser: str,
    original_file: str,
    review_file: str,
    output: str | None,
    model: str | None,
    workspace: str | None,
) -> None:
    workspace_path = resolve_workspace(workspace)

    reviser_path = resolve_named_file(PERSONAS_DIR, reviser)

    original_path = resolve_input_path(
        original_file,
        workspace_path,
    )

    review_path = resolve_input_path(
        review_file,
        workspace_path,
    )

    output_path = resolve_output_path(
        output,
        workspace_path,
        "revised",
    )

    reviser_text = read_text_file(reviser_path)
    original_text = read_text_file(original_path)
    review_text = read_text_file(review_path)

    workspace_context = load_workspace_context(
        workspace_path,
    )

    selected_model = model or reviser

    combined_prompt = f"""
You must revise the original document using the review feedback and the reviser persona.

# Reviser Persona

{reviser_text}

# Workspace Context

{workspace_context or "No additional workspace context provided."}

# Original Document

{original_text}

# Review Feedback

{review_text}

# Revision Instructions

Produce a revised version of the original document.

Rules:
- Preserve useful content from the original.
- Apply the review feedback where it improves quality.
- Do not invent unsupported facts.
- Clearly label assumptions.
- Improve structure, clarity, specificity, and actionability.
- Output only the revised document.
"""

    result = ask_ollama(
        combined_prompt,
        model=selected_model,
    )

    write_or_print_output(
        result,
        output_path,
    )

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

    workspaces = [p for p in sorted(WORKSPACES_DIR.iterdir()) if p.is_dir() and p.name != "_template"]
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
        for subdir in ["notes", "outputs", "knowledge", "decisions", "prompts"]:
            (workspace_path / subdir).mkdir(parents=True, exist_ok=True)

        (workspace_path / "README.md").write_text(
            f"# {name}\n\nProject workspace.\n",
            encoding="utf-8",
        )

    print(f"Workspace created: {workspace_path}")
