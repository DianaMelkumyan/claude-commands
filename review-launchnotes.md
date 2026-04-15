---
name: review-launchnotes
description: Review a LaunchNotes announcement for accuracy, missing value, and positioning.
---

# Review LaunchNote

Review a LaunchNotes announcement draft for a merchant-facing audience. Cross-reference against internal docs (Product Guide, PRD, Tech spike) and external docs (Zendesk help articles). Leave inline Notion comments tagging me with findings.

## Arguments

- `$ARGUMENTS` - A Notion URL to the launch note page to review.

## Context

- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`
- LaunchNotes DB: `https://www.notion.so/thanxwiki/30ca84ed4024803caf34c2739b77ad1a?v=30ca84ed4024803a948b000c7e10aa7e`
- Personas file: `/Users/diana/dAIna/thanx-context/thanx-personas-and-context.md`

## Instructions

### Step 0: Load context

Read the personas file above. These personas define the audience for every review. Keep them in mind throughout.

### Step 1: Gather sources

Fetch the launch note page from Notion (the $ARGUMENTS URL). From the page properties, collect:
- The **Draft** section (this is what you're reviewing)
- Linked **Product Guide** pages (from the "Product Guides (internal)" property)
- Linked **Help Articles** (from the "Help Article (if any)" property) - fetch these via Zendesk search
- Any linked **PRD** or **Tech spike** pages

If any of the above links are missing (no linked Product Guide, no PRD, or no Help Article), extract the feature name from the launch note title and invoke `/feature-context {feature name}` to find the missing sources. Use whatever feature-context returns to fill in the gaps. If the launch note already has all sources linked, skip feature-context.

Launch agents in parallel to fetch all linked sources (both from page properties and from feature-context). Priority order for cross-referencing accuracy: Product Guide > PRD > Tech spike > Zendesk help articles.

### Step 2: Review the Draft

Evaluate the launch note content against all sources. The review target is the main announcement body - if there is a "Draft" heading, review the content under it. Review for these 4 dimensions:

#### 1. Accuracy
- Compare every claim in the draft against the Product Guide and other sources.
- Flag incorrect URLs, wrong feature descriptions, misattributed behaviors.
- Flag claims that are technically true but misleading for a non-technical merchant audience.
- Check that dashboard links, feature names, and flows match what's documented.

#### 2. Missing value
- **Do a structural comparison first.** List every major section/topic in the Product Guide and Zendesk article. For each, check whether the draft covers it. Flag entire missing topics - these are usually the biggest gaps.
- Pay special attention to: transition/migration guidance, edge cases, common use cases, and "what to do if you use X" scenarios (e.g., hidden menus, special configurations). These are high-value for merchants and easy to omit.
- Identify important benefits or use cases documented in the sources that the draft omits.
- Focus on value a merchant would care about - not technical details.
- Check if the draft explains the "so what" for every feature described.
- Look for missing caveats that could cause merchant confusion (e.g., forward-only applicability, per-merchant scoping, irreversible changes).

#### 3. Positioning
- Is the framing merchant-value-first or feature-first? It should be value-first.
- Does the tone match the communication style guide in the personas doc? (Plain language, concrete, no superlatives, revenue/time/risk framing)
- Does it lead with fear/legal risk when it could lead with trust/protection/simplicity?
- Would "The Stretched Marketing Director" persona understand this in 2 minutes between meetings?
- Would "The Skeptical Executive" find this credible without feeling sold to?

#### 4. Clarity
- Read each paragraph as a merchant seeing it for the first time. Flag sentences that are ambiguous, confusing, or could be misread.
- Flag missing words that change meaning (e.g., "an item" when it should be "an item/modifier").
- Flag inconsistent formatting patterns (e.g., some FAQs use "Q:/A:" prefix while others use bold-question-only style).
- Do NOT flag cosmetic formatting issues (bold spacing, trailing spaces, HTML vs markdown). Only flag formatting that breaks readability or renders incorrectly.

### Step 3: Check existing discussions

Fetch the page with `include_discussions: true`. Read all existing comment threads. Do NOT duplicate feedback that's already been raised. If you agree with an existing comment, you may reply to that thread with a "+1" and additional context.

### Step 4: Post inline comments

For each finding, post an **inline comment** on the relevant text in the draft using `selection_with_ellipsis`. Tag me in every comment.

Comment format:
- Prefix with a tag: `[INCORRECT]`, `[ACCURACY]`, `[MISSING]`, `[POSITIONING]`, or `[CLARITY]`
- Be specific: quote what's wrong and suggest the fix
- Keep it concise - the reviewer (me) will decide what to action

**Important:**
- Every comment must be placed on the specific text it's about. E.g., if a URL is wrong, comment on that URL. If a paragraph's framing is off, comment on that paragraph. Never post comments on section headings or the page itself.
- Do NOT post page-level comments or summary comments on Notion. Summaries go in the conversation only.
- If the selection text appears in both the detailed section and the draft, use a longer/more specific snippet that uniquely matches the draft. If a comment still fails with "Multiple occurrences found", prepend or append surrounding words to disambiguate. Never silently drop a comment - retry with a more specific selector.

### Step 5: Summary

After posting all comments, output a summary to me in the conversation (not on Notion) with:
- The launch note title and Notion URL (linked)
- Total issues found by category
- The single most important fix

### Step 6: Check for more

Query the LaunchNotes database for other items where PM/Reviewer is me and Status is "Ready for Review". If any exist, list them and ask: "Want me to review the next one?"
