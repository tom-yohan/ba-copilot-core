import argparse

from ba_copilot.core import (
    LEGACY_PROMPTS,
    create_workspace,
    list_assets,
    run_healthcheck,
    run_legacy_mode,
    run_review,
    run_revise,
    run_workflow,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local business analysis copilot")
    subparsers = parser.add_subparsers(dest="command")

    healthcheck_parser = subparsers.add_parser("healthcheck", help="Check Ollama connectivity")
    healthcheck_parser.add_argument("--model", default="llama3.2:3b")

    subparsers.add_parser("list", help="List personas, prompts, and workspaces")

    workspace_parser = subparsers.add_parser("workspace", help="Manage workspaces")
    workspace_subparsers = workspace_parser.add_subparsers(dest="workspace_command")
    workspace_create_parser = workspace_subparsers.add_parser("create", help="Create workspace")
    workspace_create_parser.add_argument("name")

    run_parser = subparsers.add_parser("run", help="Run persona + prompt workflow")
    run_parser.add_argument("--workspace", help="Workspace name under workspaces/")
    run_parser.add_argument("--persona", required=True)
    run_parser.add_argument("--prompt", required=True)
    run_parser.add_argument("--input", required=True)
    run_parser.add_argument("--output", "-o")
    run_parser.add_argument("--model", default=None, help="Optional model override.")

    review_parser = subparsers.add_parser("review", help="Review an existing output using a reviewer persona")
    review_parser.add_argument("--workspace", help="Workspace name under workspaces/")
    review_parser.add_argument("--reviewer", required=True)
    review_parser.add_argument("--input", required=True)
    review_parser.add_argument("--output", "-o")
    review_parser.add_argument("--model", default=None, help="Optional model override.")

    revise_parser = subparsers.add_parser("revise", help="Revise an output using review feedback")
    revise_parser.add_argument("--workspace", help="Workspace name under workspaces/")
    revise_parser.add_argument("--reviser", required=True)
    revise_parser.add_argument("--original", required=True)
    revise_parser.add_argument("--review", required=True)
    revise_parser.add_argument("--output", "-o")
    revise_parser.add_argument("--model", default=None, help="Optional model override.")

    for legacy_mode in LEGACY_PROMPTS:
        legacy_parser = subparsers.add_parser(legacy_mode)
        legacy_parser.add_argument("file")
        legacy_parser.add_argument("--output", "-o")
        legacy_parser.add_argument("--model", default="llama3.2:3b")

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
        run_workflow(args.persona, args.prompt, args.input, args.output, args.model, args.workspace)
        return

    if args.command == "review":
        run_review(args.reviewer, args.input, args.output, args.model, args.workspace)
        return

    if args.command == "revise":
        run_revise(args.reviser, args.original, args.review, args.output, args.model, args.workspace)
        return

    if args.command in LEGACY_PROMPTS:
        run_legacy_mode(args.command, args.file, args.output, args.model)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
