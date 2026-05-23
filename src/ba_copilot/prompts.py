def build_workflow_prompt(
    persona_text: str,
    prompt_text: str,
    workspace_context: str,
    notes_text: str,
) -> str:
    return f"""
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


def build_review_prompt(
    reviewer_text: str,
    workspace_context: str,
    document_text: str,
) -> str:
    return f"""
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


def build_revise_prompt(
    reviser_text: str,
    workspace_context: str,
    original_text: str,
    review_text: str,
) -> str:
    return f"""
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
