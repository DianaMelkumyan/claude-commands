---
name: slide-generate-content
description: Generate slide content (titles, body text, bullet points) for a presentation based on a PRD. Can write content to Google Slides after approval.
---

# Slide Content Generator

Generate slide content (titles, body text, bullet points) from a PRD. Can optionally write content to an existing Google Slides presentation.

## Arguments

- `$ARGUMENTS` - Flexible input. Can be any combination of:
  - A Notion PRD URL
  - A Google Slides presentation ID or URL (to use as a target or structural reference)
  - A slide count or structure outline
  - Pasted text describing the target audience or focus areas
  - `update-profile` to enter profile update mode

Parse whatever is given. A PRD is required. Ask for it if not provided.

## Style Profile

- Path: `/Users/diana/conductor/workspaces/dAIna/claude-commands/slide-speaker-notes-style-profile.md`

## Instructions

### Step 0: Load style profile

Read the style profile at the path above. While this profile was written for speaker notes, its voice and tone guidelines, Do and Do Not rules, and audience context apply equally to slide content. Adapt the rules for slide format (bullets and short phrases rather than flowing paragraphs).

If the file does not exist or is empty, tell the user and proceed with sensible defaults, but note that style-level consistency may be limited.

If `$ARGUMENTS` is `update-profile`, skip to the Profile Update Mode section below.

### Step 1: Parse inputs

Identify what was provided in $ARGUMENTS:
- **Notion URL** -> fetch via `mcp__claude_ai_Notion__notion-fetch`
- **Google Slides URL or ID** -> extract presentation ID (from `docs.google.com/presentation/d/<ID>/...`)
- **Text** -> use as structural guidance, audience notes, or focus area

A PRD (Notion URL or pasted content) is required. If not provided, try to identify the feature name from the other inputs (presentation title, pasted text, audience notes) and invoke `/feature-context {feature name}` to find the PRD, product guide, and help articles. If feature-context finds a PRD, use it. If no feature name can be identified and no PRD was provided, ask the user for it.

If a presentation ID is given, determine whether the user wants to:
- **Populate an existing deck** (slides already exist, fill in or replace content)
- **Use it as a structural reference** (mimic the layout for new content)

Ask if ambiguous.

### Step 2: Read existing presentation (if provided)

If a presentation ID was given, read it via:
```bash
gws slides presentations get --params '{"presentationId": "<ID>"}'
```

From the response, extract for each slide:
- Slide object ID
- Layout and placeholder structure
- All text content in each placeholder (titles, subtitles, body text)
- Placeholder object IDs (at `slides[].pageElements[].objectId` where the element has `placeholder.type` of "TITLE", "SUBTITLE", "BODY", or "CENTERED_TITLE")
- Existing content that should be preserved vs. replaced

If `gws` returns a 401 auth error, tell the user to run `gws auth login` in their terminal and try again.

### Step 3: Fetch and parse the PRD

Fetch the PRD via `mcp__claude_ai_Notion__notion-fetch`. Extract:
- Core value propositions and merchant benefits
- Feature details, mechanics, and timelines
- Key integrations and technical specifics
- Caveats, limitations, and known constraints
- Target audience and use cases

### Step 4: Plan the slide structure

Before generating content, present a slide outline:
- Slide number and proposed title
- Key points each slide will cover
- Which PRD sections map to which slides
- Any PRD content that does not fit the deck scope (acknowledge and skip)

If an existing presentation was read, map the outline to the existing slide structure. Flag slides that need new content vs. slides whose content looks complete.

Wait for user approval of the outline before generating full content.

### Step 5: Generate slide content

For each slide in the approved outline, generate:
- **Title**: Short, specific, merchant-focused. No generic titles like "Key Features" when a specific benefit can lead.
- **Body text / bullet points**: Concise, concrete, specific. Follow the style profile rules:
  - Use real names (Toast, NCR, Olo, Valutec) not "supported POS systems"
  - Use specific numbers and timelines, not "coming soon" or "many"
  - Avoid AI-polished language: no "revolutionize", "seamlessly", "empower", "game-changer", "cutting-edge"
  - Avoid em dashes
  - Do not repeat the same concept across slides
  - Each bullet should add new information, not rephrase the previous one

Present all generated content slide-by-slide so it can be reviewed before writing.

### Step 6: Duplicate before editing (existing slides only)

When updating slides in an existing presentation, duplicate each target slide before modifying it. This preserves comments, revision history, and other metadata on the original.

To duplicate a slide:
```bash
gws slides presentations batchUpdate --params '{"presentationId": "<ID>"}' --json '{
  "requests": [{
    "duplicateObject": {
      "objectId": "<slideObjectId>"
    }
  }]
}'
```

The response returns the new slide's object ID in `replies[].duplicateObject.objectId`. Use this ID for all subsequent content writes.

After duplicating, note the mapping of original slide ID to duplicate slide ID so the user knows which slides are the updated copies.

### Step 7: Apply (on user approval)

Once approved, write content to the presentation. For each slide with content changes:

**To replace text in an existing placeholder** (delete existing text, then insert new):
```bash
gws slides presentations batchUpdate --params '{"presentationId": "<ID>"}' --json '{
  "requests": [
    {
      "deleteText": {
        "objectId": "<placeholderObjectId>",
        "textRange": {"type": "ALL"}
      }
    },
    {
      "insertText": {
        "objectId": "<placeholderObjectId>",
        "text": "<new slide content>",
        "insertionIndex": 0
      }
    }
  ]
}'
```

**To insert text into an empty placeholder**:
```bash
gws slides presentations batchUpdate --params '{"presentationId": "<ID>"}' --json '{
  "requests": [{
    "insertText": {
      "objectId": "<placeholderObjectId>",
      "text": "<new slide content>",
      "insertionIndex": 0
    }
  }]
}'
```

Batch all updates for a single slide into one batchUpdate call. Process one slide at a time so failures are isolated.

After writing each slide, re-read it to confirm the content was applied correctly.

### Step 8: Continue

After completing all slides, summarize what was written. Include the mapping of original to duplicate slides so the user can review the copies alongside the originals, then delete the originals once satisfied.

Ask if any slides need revision.

## Profile Update Mode

When invoked with `update-profile` or when the user gives feedback that sounds like a lasting preference:

1. Read the current style profile
2. Identify what new preference the feedback implies
3. Propose a specific edit (show the before/after for the relevant section)
4. Apply only after user approval

During normal use, if corrections suggest a pattern (not a one-off), offer: "This seems like a general preference. Want me to update the style profile?"

## Important

- Never write to the presentation without explicit user approval
- Always present content for review before writing
- Always duplicate existing slides before modifying them. Never edit originals in place.
- Be accurate to the PRD. Do not invent features or timelines that are not in the source.
- If the PRD is vague on a detail, say so in the review rather than filling in a guess
- Slide content should be scannable. Short phrases and bullets, not paragraphs.
- The style profile rules about specificity and avoiding marketing language are critical for slide content
- If any placeholder object IDs cannot be found in the presentation data, tell the user which slides could not be updated and why
