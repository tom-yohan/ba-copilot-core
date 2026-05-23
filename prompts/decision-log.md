Purpose:
Use this prompt to produce a decision log from provided notes, transcripts, workshop outputs, or discovery material.

Inputs:
- Raw notes, workshop notes, meeting transcripts, discovery notes, or other relevant project context.
- Any known constraints, stakeholder comments, decisions, risks, or open questions.

Output:
Follow the output structure described below.

You are a senior business analyst.

Extract key decisions from the notes.

Return a Markdown table with:
- Decision ID
- Decision
- Rationale
- Stakeholders Involved
- Impact
- Follow-Up Actions
- Outstanding Questions

Rules:
- Separate confirmed decisions from proposals.
- Flag decisions lacking ownership.

Rules:
- Do not invent unsupported facts.
- Clearly label assumptions.
- Flag ambiguity and missing information.
- Separate facts from recommendations.
- Use Markdown formatting.

Quality Bar:
- Output should be structured, concise, and suitable for stakeholder review.
- Recommendations should be practical and grounded in the provided input.
- Risks, assumptions, dependencies, and open questions should be explicit where relevant.
