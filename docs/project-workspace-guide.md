# Project Workspace Guide

Use separate workspaces for different projects or clients.

Recommended structure:

    workspaces/
    └── project-name/
        ├── notes/
        ├── outputs/
        ├── knowledge/
        ├── prompts/
        └── decisions/

Do not commit confidential or client-owned material unless explicitly approved.

Recommended workflow:

1. Create a workspace.
2. Add sanitised notes.
3. Run prompts through Open WebUI or CLI tooling.
4. Save reviewed outputs.
5. Move reusable patterns back into the core repo.
