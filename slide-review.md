---
name: slide-review
description: Review slide deck content against a PRD and flag missing merchant value drivers, inaccuracies, or misleading claims. Read-only analysis, no modifications.
---

# Slide Review

Review a slide deck against a PRD. Flag missing merchant value drivers, inaccuracies, and weak framing. This is a read-only skill that never modifies the presentation.

## Arguments

- `$ARGUMENTS` - Flexible input. Can be any combination of:
  - A Notion PRD URL
  - A Google Slides presentation ID or URL, optionally with a specific slide range
  - Pasted text describing additional context or focus areas

Parse whatever is given. Both a PRD and a presentation are required. Ask for whichever is missing.

## Style Profile

- Path: `/Users/diana/conductor/workspaces/dAIna/claude-commands/slide-speaker-notes-style-profile.md`

## Instructions

### Step 0: Load style profile

Read the style profile at the path above. Use it to understand the voice, tone, and audience context for these slides. The audience is merchants. The style profile tells you what good slide content sounds like for this team.

If the file does not exist or is empty, proceed without it but note that style-level feedback will be limited.

### Step 1: Parse inputs

Identify what was provided in $ARGUMENTS:
- **Notion URL** -> fetch via `mcp__claude_ai_Notion__notion-fetch`
- **Google Slides URL or ID** -> extract presentation ID (from `docs.google.com/presentation/d/<ID>/...`) and optional slide range
- **Text** -> use as additional context or focus area

If the presentation is missing, ask for a Google Slides URL or ID.

If the PRD is missing but a presentation is available, extract the feature name from the slide content (deck title or most prominent feature reference) and invoke `/feature-context {feature name}` to find the PRD, product guide, and help articles. Use the returned PRD as the source of truth. Use the product guide and help article as additional cross-reference sources in Step 4. If feature-context finds no PRD, ask the user for a Notion URL or pasted PRD content.

### Step 2: Read the full presentation

Read the presentation via:
```bash
gws slides presentations get --params '{"presentationId": "<ID>"}'
```

From the response, extract for every slide:
- Slide number and layout
- All text content (titles, body text, bullet points)
- Speaker notes (at `slides[].slideProperties.notesPage.pageElements[].shape.text.textElements[].textRun.content`)

If `gws` returns a 401 auth error, tell the user to run `gws auth login` in their terminal and try again.

### Step 3: Fetch and parse the PRD

Fetch the PRD via `mcp__claude_ai_Notion__notion-fetch`. Extract:
- Core value propositions and merchant benefits
- Feature details, mechanics, and timelines
- Key integrations and technical specifics
- Caveats, limitations, and known constraints
- Target audience and use cases

### Step 4: Analyze and compare

For each slide, compare its content against the PRD. Evaluate:

1. **Missing value drivers**: Features or benefits in the PRD that merchants would care about but the deck does not cover. Prioritize by merchant impact, not completeness for its own sake.
2. **Inaccuracies**: Claims on slides that contradict the PRD (wrong timelines, incorrect mechanics, overstated capabilities).
3. **Misleading framing**: Statements that are technically true but could give merchants the wrong impression.
4. **Weak specificity**: Slides using vague language where the PRD has concrete details (names, numbers, integrations, timelines).
5. **Redundancy**: The same point made on multiple slides without adding new information.

### Step 5: Present the review

Organize findings by severity:

**Blocking Issues** (inaccuracies or misleading claims that must be fixed)
- List each with the slide number, the problem, and what the PRD actually says

**Missing Value Drivers** (important merchant benefits the deck skips)
- List each with the PRD section it comes from and a suggestion for where it could fit

**Improvement Suggestions** (framing, specificity, or flow)
- List each with the slide number and a concrete suggestion

Keep each item to 1-2 sentences. Do not rewrite the slides. The goal is a clear punch list, not a rewrite.

After the itemized review, provide a brief overall assessment: Is the deck ready for merchants? What are the top 2-3 things to fix first?

Then recommend next actions. If changes are needed, suggest the user invoke `/slide-generate-content` with the same PRD and presentation to apply fixes, so they can agree and proceed directly.

### Step 6: Dive deeper (on request)

If the user asks about a specific slide or topic, provide detailed analysis including:
- Exact PRD language that applies
- A suggested rewrite for that specific slide (only when asked)
- How the fix affects adjacent slides

## Important

- Never modify the presentation. This skill is read-only.
- Prioritize merchant impact over completeness. Not every PRD detail needs a slide.
- Flag contradictions clearly. Do not downplay inaccuracies.
- If the PRD itself is vague on a topic, say so rather than guessing.
- Do not pad the review. If the deck is solid, say so briefly.
