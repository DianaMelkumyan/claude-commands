---
name: review-all-launchnotes
description: Review all LaunchNotes assigned to me in parallel. Lists items ready for review, then spins up agents to review each one simultaneously.
---

# Review All Launch Notes

List all LaunchNotes assigned to me with "Ready for Review" status, then launch parallel agents to review every one of them at once.

## Context

- LaunchNotes DB: `https://www.notion.so/thanxwiki/30ca84ed4024803caf34c2739b77ad1a?v=30ca84ed4024803a948b000c7e10aa7e`
- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`
- Personas file: `/Users/diana/dAIna/thanx-context/thanx-personas-and-context.md`

## Instructions

### Step 1: Fetch the list

Query the LaunchNotes Announcements Tracker Notion database. Filter for items where:
- **PM/Reviewer** includes me (user ID above)
- **Status** is "Ready for Review"

If no items found, say: "No launch notes are ready for review right now." and stop.

Display a table with: Feature name, Status, Publish Date, and Notion URL.

### Step 2: Confirm

Tell the user how many launch notes were found and say:

> I'll spin up [N] agents to review these in parallel. Each agent will cross-reference against Product Guides, PRDs, and Zendesk articles, then post inline Notion comments tagging you.
>
> Ready? (y to review all, or pick specific numbers)

If the user picks specific numbers, only review those. If they confirm, review all.

### Step 3: Launch parallel review agents

For each launch note to review, launch an Agent (subagent_type: general-purpose) in the background with the following prompt. Replace `{{NOTION_URL}}` and `{{FEATURE_NAME}}` for each item:

```
You are reviewing a LaunchNotes announcement draft. Follow these instructions exactly.

## Target
- Launch note: "{{FEATURE_NAME}}"
- Notion URL: {{NOTION_URL}}
- My Notion user ID: 713e97f8-e2f5-4bba-9d96-bd0ccb7b6133
- Personas file: /Users/diana/dAIna/thanx-context/thanx-personas-and-context.md

## Step 0: Load context
Read the personas file. These personas define the audience for every review.

## Step 1: Gather sources
Fetch the launch note page from Notion. From the page properties, collect:
- The Draft section (this is what you're reviewing)
- Linked Product Guide pages (from "Product Guides (internal)" property)
- Linked Help Articles (from "Help Article (if any)" property) - fetch via Zendesk search
- Any linked PRD or Tech spike pages

If any of the above links are missing (no linked Product Guide, no PRD, or no Help Article), extract the feature name from the launch note title and invoke `/feature-context {feature name}` to find the missing sources. Use whatever feature-context returns to fill in the gaps. If the launch note already has all sources linked, skip feature-context.

Launch parallel fetches for all linked sources (both from page properties and from feature-context). Priority for cross-referencing: Product Guide > PRD > Tech spike > Zendesk.

## Step 2: Review the Draft
Evaluate the draft against all sources. Review for 4 dimensions:

### 1. Accuracy
- Compare every claim against Product Guide and other sources.
- Flag incorrect URLs, wrong feature descriptions, misattributed behaviors.
- Flag claims technically true but misleading for non-technical merchants.
- Check dashboard links, feature names, and flows match documentation.

### 2. Missing value
- Do a structural comparison first. List every major section/topic in the Product Guide and Zendesk article. For each, check if the draft covers it. Flag entire missing topics.
- Pay attention to: transition/migration guidance, edge cases, common use cases, "what to do if you use X" scenarios.
- Identify important benefits or use cases the draft omits.
- Check if the draft explains the "so what" for every feature.
- Look for missing caveats that could cause merchant confusion.

### 3. Positioning
- Is the framing merchant-value-first or feature-first? Should be value-first.
- Does the tone match the communication style guide in the personas doc?
- Does it lead with fear/legal risk when it could lead with trust/protection/simplicity?
- Would "The Stretched Marketing Director" understand this in 2 minutes?
- Would "The Skeptical Executive" find this credible without feeling sold to?

### 4. Clarity
- Read each paragraph as a merchant seeing it for the first time. Flag ambiguous or confusing sentences.
- Flag missing words that change meaning.
- Flag inconsistent formatting patterns that break readability.
- Do NOT flag cosmetic formatting issues.

## Step 3: Check existing discussions
Fetch the page with include_discussions: true. Read all comment threads. Do NOT duplicate feedback already raised. You may "+1" existing comments with additional context.

## Step 4: Post inline comments
For each finding, post an inline comment on the relevant text using selection_with_ellipsis. Tag me (user ID above) in every comment.

Comment format:
- Prefix with: [INCORRECT], [ACCURACY], [MISSING], [POSITIONING], or [CLARITY]
- Be specific: quote what's wrong and suggest the fix
- Keep it concise

Important:
- Every comment must be on the specific text it's about. Never post on headings or the page itself.
- Do NOT post page-level or summary comments on Notion. Summaries go in the conversation only.
- If selection text appears multiple times, use a longer snippet to disambiguate. Never silently drop a comment - retry with a more specific selector.

## Step 5: Return summary
Return a summary with:
- The launch note title and Notion URL
- Total issues found by category (Accuracy, Missing, Positioning, Clarity)
- The single most important fix
```

Launch ALL agents in a single message so they run concurrently. Use `run_in_background: true` for each.

### Step 4: Collect and summarize

As each agent completes, collect its summary. Once all agents are done, present a combined report:

1. **Overview table** - one row per launch note: Feature name, Notion URL, total issues, most critical fix
2. **Per-note summaries** - the full summary from each agent
3. **Cross-cutting patterns** - if the same type of issue appears across multiple notes, call it out (e.g., "3 of 5 notes lead with features instead of merchant value")

End with: "All reviews posted as inline Notion comments. Check each page for details."
