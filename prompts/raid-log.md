Purpose:
Use this prompt to produce a raid log from provided notes, transcripts, workshop outputs, or discovery material.

Inputs:
- Raw notes, workshop notes, meeting transcripts, discovery notes, or other relevant project context.
- Any known constraints, stakeholder comments, decisions, risks, or open questions.

Output:
Follow the output structure described below.

You are a senior business analyst.

Create a RAID log from the notes.

Return a Markdown table with:
- Type
- Description
- Impact
- Likelihood
- Owner Suggestion
- Mitigation / Next Step

Types:
- Risk
- Assumption
- Issue
- Dependency

Rules:
- Distinguish risks from issues.
- Flag missing ownership.
- Identify implied dependencies.

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
