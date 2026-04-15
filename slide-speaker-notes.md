---
name: slide-speaker-notes
description: Generate webinar speaker notes in the user's voice from a PRD, screenshot, or slide content. Reads a persistent style profile automatically.
---

# Slide Speaker Notes

Generate speaker notes for webinar slides in my voice. Uses a persistent style profile so you never need example decks.

## Arguments

- `$ARGUMENTS` - Flexible input. Can be any combination of:
  - A Notion PRD URL
  - A Google Slides presentation ID or URL, optionally with a slide number
  - A screenshot file path
  - Pasted text describing the slide content
  - `update-profile` to enter profile update mode

Parse whatever is given. Ask for anything else you need.

## Style Profile

- Path: `/Users/diana/conductor/workspaces/dAIna/claude-commands/slide-speaker-notes-style-profile.md`

## Instructions

### Step 0: Load style profile

Read the style profile at the path above. This is the source of truth for voice, tone, structure, and length. Do not ask for example decks.

If the file does not exist or is empty, tell the user and stop.

If `$ARGUMENTS` is `update-profile`, skip to the Profile Update Mode section below.

### Step 1: Parse inputs

Identify what was provided in $ARGUMENTS:
- **Notion URL** -> fetch via `mcp__claude_ai_Notion__notion-fetch`
- **Google Slides URL or ID** -> extract presentation ID (from `docs.google.com/presentation/d/<ID>/...`) and optional slide number
- **Screenshot path** -> read the image file
- **Text** -> use as-is for slide content context

If only a PRD was given with no slide context, ask the user to describe the slide content, provide a presentation ID, or share a screenshot. The skill can work from just a PRD, but slide context improves accuracy.

### Step 1.5: Gather feature context (if no PRD provided)

If no Notion PRD URL was provided in $ARGUMENTS, but slide content or a screenshot is available:

1. Extract the feature name from the slide content (use the slide title or the most prominent feature reference)
2. Invoke `/feature-context {feature name}` to find the PRD, product guide, and help articles
3. Use the returned PRD content as the source of truth for accuracy
4. Use the product guide and help article links as supplementary references

If a PRD URL was already provided, skip this step. The user's explicit URL takes priority.

### Step 2: Read target presentation (if provided)

If a presentation ID was given, read it via:
```bash
gws slides presentations get --params '{"presentationId": "<ID>"}'
```

From the response, extract for the target slide(s):
- All text content (titles, body, bullet points)
- Any existing speaker notes (at `slides[].slideProperties.notesPage.pageElements[].shape.text.textElements[].textRun.content`)
- Adjacent slides for transition context

If `gws` returns a 401 auth error, tell the user to run `gws auth login` in their terminal and try again.

### Step 3: Generate speaker notes

Write speaker notes for the target slide following the style profile exactly. Key rules:
1. Match the voice, tone, and structure from the profile
2. The slide content is the primary anchor. The notes should explain and expand on what's on the slide. Use the PRD to verify accuracy and add depth, not as the starting outline.
3. Be accurate to the PRD - no claims that contradict the source
4. Flow naturally from previous slide notes (if available)
5. Keep to 4-6 short paragraphs, 100-200 words. Only exceed when the topic genuinely demands it, which is rare.

Present the draft notes clearly so they can be read as they would be spoken.

### Step 4: Content review recommendation

After presenting the notes, if you noticed any mismatches between the slide content and the PRD (missing points, misleading claims, outdated framing), briefly mention it and suggest running `/slide-review` to analyze and update the slide content. Keep it to one sentence, e.g.: "The slide doesn't mention X from the PRD - you might want to run `/slide-review` to check the slide content."

If the slide content looks aligned with the PRD, skip this step.

### Step 5: Apply (on user approval)

Once approved, write **only the speaker notes** to the slide. Never modify slide content.

Find the notes text box object ID from the slide's `slideProperties.notesPage.pageElements` - the shape with `placeholder.type: "BODY"`.

If existing notes need replacing, delete first then insert:
```bash
gws slides presentations batchUpdate --params '{"presentationId": "<ID>"}' --json '{
  "requests": [
    {
      "deleteText": {
        "objectId": "<notesPageObjectId>",
        "textRange": {"type": "ALL"}
      }
    },
    {
      "insertText": {
        "objectId": "<notesPageObjectId>",
        "text": "<approved speaker notes>",
        "insertionIndex": 0
      }
    }
  ]
}'
```

If notes are empty, just insert:
```bash
gws slides presentations batchUpdate --params '{"presentationId": "<ID>"}' --json '{
  "requests": [{
    "insertText": {
      "objectId": "<notesPageObjectId>",
      "text": "<approved speaker notes>",
      "insertionIndex": 0
    }
  }]
}'
```

Confirm by re-reading the slide.

### Step 6: Continue

After writing one slide, ask: "Next slide?" If yes, loop back to Step 3 with the next slide's content.

## Profile Update Mode

When invoked with `update-profile` or when the user gives feedback that sounds like a lasting preference:

1. Read the current style profile
2. Identify what new preference the feedback implies
3. Propose a specific edit (show the before/after for the relevant section)
4. Apply only after user approval

During normal use, if corrections suggest a pattern (not a one-off), offer: "This seems like a general preference. Want me to update the style profile?"

## Important

- Never write to the presentation without explicit user approval
- Never modify slide content, only speaker notes
- The style match is the top priority - sound like the user, not like an AI
- If the PRD contradicts the slide content, flag it but do not silently fix it in the notes
