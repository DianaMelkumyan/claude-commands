---
name: theme-opportunity
description: Generate the Opportunity paragraph for a Discovery Theme page in Notion by reading its linked PRDs. Drafts in chat for approval, then writes to the theme page. Trigger when asked to generate or draft a theme opportunity, or invoked as /theme-opportunity with a theme URL or name.
---

# /theme-opportunity

Generate the Opportunity paragraph (1-2 sentences) for a Discovery Theme page. Designed to be runnable on its own, or in parallel with sibling section-skills under a future /theme orchestrator.

## Context

- Discovery Themes data source: `collection://348a84ed-4024-801f-a259-000bf6d220bd`
- Projects (PRDs) data source: `collection://0d7ef002-875f-453b-bb05-7789a3436086`
- Relation: theme `⏩ Projects` ↔ project `Discovery Theme`
- Theme page template sections (current): `# Opportunity`, `# What we want customers to say` (with `### What they would say if we went further`), `# Decision factors` (optional), `# Relevant projects`
- This skill writes ONLY to the `# Opportunity` section. Do not modify any other section.
- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`

## Picker heuristic

The skill produces one of two output lengths. The picker decides between them by evaluating three signals against the Strong-evidence PRDs and the cross-cutting story.

### Length variants

- **Short form:** 1-2 sentences. Hard cap at 2.
- **Long form:** exactly 2 short paragraphs. Hard cap at 2. Same beats as the short form (problem, who feels it most acutely, consequence). Not a structural split. Just more room to carry concrete grounding for multiple platforms, segments, or stakeholder groups, and to distinguish failure modes without compressing them. Same exec audience. Every word earns its place. Business outcomes only - no implementation language.

### Signals

**Signal A - Multiple concrete grounding points.** The problem has multiple specific platforms, segments, or partner ecosystems that all need to be named for an exec to understand who feels it. Compressing to one would misrepresent the scope.

**Signal B - Two distinct consequence modes both load-bearing.** The problem produces materially different consequences in different contexts (e.g. damage at live merchants AND blocking in active sales conversations), and collapsing them into one sentence loses a real branch of the story.

**Signal C - Structurally compound "who feels it."** The affected population is multiple structurally distinct stakeholder groups (e.g. brands already deployed + brands evaluating + a partner-side stakeholder), not a single segment with adjectives.

### Decision rules

| Source state | Decision |
|---|---|
| Fewer than 2 Strong-evidence PRDs with real content | Existing abort flow (Step 7) |
| Zero signals present | **Short, single-form** |
| Two or more signals present | **Long, single-form** |
| Exactly one signal present | **Dual-form** (recommend long; alternate short) |

The picker is evaluated explicitly. The reasoning trail names which signals were judged present and which were judged absent.

## Input

Argument is a Discovery Theme URL or name (e.g. "In-store loyalty foundations").

If no argument is provided, ask the user which theme to draft for, then proceed.

## Instructions

### Step 1: Resolve the theme

- If the input is a Notion URL, extract the page ID.
- If the input is a name, search the Discovery Themes data source and confirm the match with the user before proceeding. If multiple matches exist, list them and ask the user to pick.

### Step 2: Fetch the theme page

Use `mcp__claude_ai_Notion__notion-fetch`. Capture:

- Theme title
- `Pillar`, `Status`, `Signal Clarity` properties
- The list of URLs in the `⏩ Projects` relation
- The current body content under `# Opportunity`

### Step 3: Check for existing content

If the existing Opportunity section already has real content (anything other than the default gray placeholder text "1-2 sentences: what is the problem/opportunity, and who feels it most acutely?"), show the current content to the user and ask whether to overwrite. Do not silently overwrite real PM-authored content.

### Step 4: Fetch all linked PRDs in parallel

One `mcp__claude_ai_Notion__notion-fetch` call per PRD URL, batched in a single message so the calls run concurrently. For each PRD, capture:

- Page title
- `Product team workflow` field value
- `Goal` field value
- The body content (Background, Problem, Goal/Outcome sections in particular)

### Step 5: Categorize PRDs by Product team workflow

This drives weighting:

- **Strong evidence**: primary source. The Opportunity must be grounded in these.
- **Moderate evidence**: secondary source. Use to enrich, not anchor.
- **Early evidence**: context only. Do not let these define the narrative.
- **Archived**: ignore entirely.

### Step 6: Filter empty PRDs (with recovery)

Before skipping a PRD as empty, attempt recovery from adjacent sources:

1. **Child pages of the PRD.** Brainstorm/dirty-notes pages and "Draft PRD for [feature]" sub-pages often hold the real draft when the canonical PRD is a "Replaced by Claude" placeholder.
2. **Pages cross-linked under "Additional Resources" / "Related PRDs"** in sibling PRDs that did have real content.
3. **Pillar-level strategy docs** when the theme's Pillar property points to one (e.g. for ThanxAI pillar themes: "Thanx AI Product Plan", "AI H1 2026", "Thanx AI External Positioning").

Only skip the PRD if no substantive context is recoverable. When recovery succeeds, treat the recovered content as if it were the PRD body, and note the recovery source in the reasoning trail (e.g. "Advisor PRD body empty; recovered from child page 'Draft PRD for Advisor'").

If the user explicitly directs inclusion of an item whose source PRD is empty or thin, honor the direction - they often have context the skill cannot see (recent conversations, adjacent themes). Note the override in the reasoning trail rather than re-arguing source coverage.

### Step 6.5: Cross-theme PRD check

For each PRD that survives Step 6, check its `Discovery Theme` relation. If it lists more than one theme:

1. Fetch the sibling theme's `# Opportunity` section (one parallel call per sibling).
2. Note the angle already taken there - the current theme should frame the shared PRD complementarily, not duplicate.
3. Carry the sibling-theme angles into the reasoning trail so the picker and drafter can see the boundary.

Example: the Ordering experience builder PRD is linked to both "ThanxAI for marketing" and "CMS: Web customization". The CMS theme owns the brand-continuity / custom-domain / Blaze story. The ThanxAI theme should stay in the AI-driven creative-canvas lane (vibe-code your own ordering on Thanx APIs), not restate the brand-continuity case.

### Step 7: Abort condition

If fewer than 2 PRDs remain after filtering (Strong + Moderate evidence with real content), tell the user the source material is thin and ask whether to proceed anyway, expand the workflow tiers considered, or stop.

### Step 8: Identify the cross-cutting story and evaluate picker signals

Read the Strong-evidence PRDs (and Moderate-evidence PRDs as enrichment) and answer three questions:

1. What single problem do they collectively address?
2. Who feels that problem most acutely (which merchant segment, partner ecosystem, customer type)?
3. What is the consequence if the problem persists? When applicable, distinguish two failure modes: damage where the related capability is already deployed, vs. blocking where it is being evaluated.

Then evaluate the three signals defined in the "Picker heuristic" section:

- **Signal A** (multiple concrete grounding points): present / absent
- **Signal B** (two distinct consequence modes both load-bearing): present / absent
- **Signal C** (structurally compound "who feels it"): present / absent

Apply the decision rules to determine: short single-form, long single-form, or dual-form. Carry the picker decision and the per-signal judgments forward to Step 9.

### Step 8.5: Framing mode (ambition-led vs gap-fix)

Determine the framing mode before drafting. Two modes:

**Ambition-led** - the theme is a forward-looking, net-new capability that puts Thanx ahead. The Opportunity is the new experience the merchant unlocks; evidence is demand + competitive lead. Avoid "today X is broken / slow / blocking" language - the experience is new, not a fix.

**Gap-fix** - the theme closes a parity gap, fixes a broken flow, or removes operational drag. The Opportunity is what breaks for the merchant today; evidence is incidence + cost.

Decision rules (in order):

| Source state | Mode |
|---|---|
| Theme `Pillar` is `ThanxAI` or another forward-looking pillar | Ambition-led (default) |
| Strong-evidence PRDs are net-new capabilities with no existing-flow predecessor | Ambition-led |
| Strong-evidence PRDs are explicit fixes to existing flows or parity catch-ups | Gap-fix |
| Mixed or ambiguous | Gap-fix (safer default; flag in reasoning trail) |

The user can override with a one-word direction ("ambition" / "gap-fix") in their request. Honor it.

Mode shapes Step 9:

- **Ambition-led, long form:** Paragraph 1 = the new experience (what the merchant or operator gets). Paragraph 2 = why this puts Thanx ahead (named demand signal + competitive lead). Do NOT close on cost or consequence.
- **Gap-fix, long form:** Paragraph 1 = what breaks today, who feels it. Paragraph 2 = where the cost lands. (Current default behavior, unchanged.)
- **Short form:** Same mode applies, compressed.

### Step 9: Draft

Apply the tone rules in all cases. Before drafting, internalize the lead heuristic:

**Lead with the outcome, not the missing capabilities.** The headline beat is what breaks for the customer or the merchant, not a list of features Thanx doesn't have. Surface deficiencies as evidence of the outcome (in service of a failure mode), not as the outcome itself. If a draft reads as "Thanx web ordering lacks X, Y, Z," restructure so X/Y/Z appear as supporting evidence under a unifying experiential claim.

- **Short single-form:** draft the 1-2 sentence version only.
- **Long single-form:** draft the 2-paragraph version only. The third sentence of paragraph 1 is a flexible slot - by default it names *who feels it most acutely* (stakeholder enumeration), but it can also carry a pillar tie-in (frame the gap against the theme's strategic pillar), a moment-of-truth framing (anchor on the consumer interaction where the gap lands), or a market-floor framing (name the parity expectation). If the user pushes back on the stakeholder list, offer 2-3 alternatives by *meaning* rather than reworking the same beat. Concrete grounding can move to paragraph 2 in those cases.
- **Dual-form:** draft both versions. Both must be drafted with equal care. Do not lazy-draft the alternate. The recommended form (long) and the alternate (short) must each independently meet the tone rules. If you cannot honestly produce both at quality, the picker should have been single-form - revisit Step 8.

### Step 10: Present the draft for approval

For **single-form** (short or long), output:

```
## Draft Opportunity for [Theme Name]

> [paragraph(s)]

**Reasoning:**
- Cross-cutting story: [one line]
- Length chosen: [short | long]. [one-line why, naming signals present and absent]
- Anchored on (Strong evidence): [PRD names]
- Enriched by (Moderate evidence): [PRD names, or "none"]
- Excluded as too speculative or empty: [PRD names + reason]
- Concrete grounding chosen: [e.g. "Square and Qu" - and why]

Approve, edit, or scrap?
```

For **dual-form**, output:

```
## Draft Opportunity for [Theme Name]

**Recommended: long form**

> [recommended draft - 2 paragraphs]

**Alternate: short form**

> [alternate draft - 1-2 sentences]

**Reasoning:**
- Cross-cutting story: [one line]
- Length recommendation: long. [one-line why]
- Why it was close: [name the specific signal that triggered dual generation - one of: multiple-grounding-points, two-consequence-modes, compound-who-feels-it]
- Anchored on (Strong evidence): [PRD names]
- Enriched by (Moderate evidence): [PRD names, or "none"]
- Excluded as too speculative or empty: [PRD names + reason]
- Concrete grounding chosen: [...]

Approve recommended, use alternate, edit either, or scrap?
```

### Step 11: On approval, write to Notion and append to calibration log

Use `mcp__claude_ai_Notion__notion-update-page` with old_string/new_string replacement. Replace the existing Opportunity section content with the approved paragraph(s). Do not modify any other section. After writing, re-fetch the page to confirm the write succeeded.

Then append one JSONL row to `theme/.claude/skills/theme-opportunity/calibration.log` (create the file if it does not exist). One line per run, valid JSON object, no trailing comma:

```json
{
  "date": "YYYY-MM-DD",
  "theme": {"id": "<page-id>", "name": "<theme name>"},
  "cross_cutting_story": "<one-line synthesis from Step 8>",
  "prds": {
    "anchored": [{"id": "<page-id>", "title": "<prd title>"}],
    "enriched": [{"id": "<page-id>", "title": "<prd title>"}],
    "excluded": [{"id": "<page-id>", "title": "<prd title>", "reason": "<one-line why>"}]
  },
  "signals": {
    "a_multiple_grounding_points": {"present": true, "reason": "<one-line why>"},
    "b_two_consequence_modes": {"present": false, "reason": "<one-line why>"},
    "c_compound_who_feels_it": {"present": true, "reason": "<one-line why>"}
  },
  "skill": {
    "mode": "single|dual",
    "recommended": "short|long",
    "reason": "<one-line why this form>"
  },
  "user": {
    "picked": "short|long",
    "edited": false,
    "edit_summary": "<what changed, only if edited; otherwise omit>",
    "reason": "<optional, only if user volunteered; otherwise omit>"
  },
  "agreement": true
}
```

Field rules:

- `date`: today's date in `YYYY-MM-DD`.
- `theme.id`: the Notion page ID. `theme.name`: the theme title.
- `cross_cutting_story`: the one-line synthesis produced in Step 8.
- `prds.anchored` / `prds.enriched`: PRDs used to ground the draft (high and moderate conviction respectively). Each entry includes Notion page ID and title for stability across renames.
- `prds.excluded`: PRDs filtered out per Step 6 or judged too speculative. Each entry includes a one-line reason.
- `signals`: capture all three signals explicitly as `{present, reason}`. Do not collapse to a single `trigger` label - the per-signal booleans and reasons are what enable later analysis of which signals are over/under-firing.
- `skill.mode`: `single` if the skill drafted one form; `dual` if it drafted both.
- `skill.recommended`: the form the picker chose (or recommended in dual mode).
- `skill.reason`: one-line why the picker landed on this form, derived from the signal booleans.
- `user.picked`: which form the reviewer actually approved. Equals `skill.recommended` for single-form. May differ in dual-form when the reviewer picks the alternate.
- `user.edited`: `true` if the reviewer requested any edits before approval, otherwise `false`.
- `user.edit_summary`: present only when `edited=true`. One line capturing what the reviewer changed (e.g. "swapped 'critical' for 'load-bearing'", "tightened second paragraph", "removed Square reference"). Pure binary `edited=yes|no` loses the signal we need.
- `user.reason`: present only when the user volunteered a reason in their approval/override message. Do not prompt for it.
- `agreement`: `true` when `user.picked == skill.recommended` and `user.edited == false`. Otherwise `false`.

Append using the Bash tool with a redirected echo (single line, no pretty-printing), or the equivalent file-append primitive. If the parent directory does not exist, `mkdir -p` first. The skill must not read the log during normal operation.

Reply with the link to the updated theme page.

Scrapped drafts do not produce log entries.

### Step 12: On edit request, revise and re-present

For **single-form**: iterate on the draft and re-present using the same single-form output template.

For **dual-form**: ask the reviewer which version to edit (recommended, alternate, or both). Iterate on the requested version(s) and re-present using the dual-form output template, preserving the unedited version.

Iterate until approved, swapped to the alternate, or scrapped. Edits made before approval set `user.edited=true` in the calibration log row written by Step 11, and the reviewer's changes are summarized in one line in `user.edit_summary` (e.g. "swapped 'critical' for 'load-bearing'", "tightened second paragraph"). Capture this from the diff between the last drafted version and the approved version - do not prompt the user for it.

## Tone rules

These apply across both length variants. The audience and discipline do not change between short and long.

The Opportunity MUST:

- Stay within the chosen length cap. Short = 1-2 sentences. Long = exactly 2 short paragraphs.
- Name the problem AND who feels it most acutely.
- Name the consequence (what breaks because of the problem).
- Use concrete grounding (specific platforms, partner ecosystems, merchant segments) when source material supports it. Generic phrasing like "many merchants" is a smell.
- Distinguish failure modes when applicable: damage where the capability is deployed vs. blocking where it is being evaluated.

The Opportunity MUST NOT:

- Include statistics, dollar amounts, or merchant counts. Those belong in signal/decision-factors sections, not here.
- Include direct customer quotes. Same reason.
- Use adjectival hedging. Avoid words like "critical", "urgent", "important", "significant", "key", "major". They are low-information and exec readers discount them.
- Use em dashes. Use regular dashes (-), commas, or rewrite the sentence.
- Read as a Solution. The Opportunity is the problem statement, not the proposed approach.
- Fabricate merchant names, ARR figures, or quotes that are not present in the source PRDs.
- Be longer than the chosen length cap. The long form is not license to explain or hedge - it is room to carry concrete grounding the short form would have to drop.
- Be longer than what an exec can absorb in one breath while scanning. For the long form, that means each paragraph reads as one breath.
- In ambition-led mode, frame the experience as a new possibility, not as a fix to a broken flow. Phrases like "wait on a developer", "file a ticket", "manual today", "blocked by", or "force handholding" tag the framing as gap-fix; rewrite as the unlocked experience.

## Orchestrated mode

When the dispatch prompt from `/theme` includes the literal phrase `ORCHESTRATED MODE`, branch behavior as follows. Direct invocation (without that phrase) is unchanged.

**Required dispatch prompt fields the orchestrator provides:**

- `run_dir`: absolute or repo-relative path to the per-run directory (e.g. `.context/theme-runs/in-store-loyalty-foundations-20260506-141422/`). The skill writes its run log to `<run_dir>/opportunity.md`.
- `theme_id`: the resolved Notion page ID (so the skill skips its own resolution step).

**Behavior changes:**

1. Skip the "draft in chat for approval" step. No interactive presentation, no waiting for user input.
2. Run all default-mode steps (PRD fetch, canvass, length-picker, drafting) **except** the chat-draft-and-approval step. The skill's drafting heuristics are unchanged; only the I/O boundary differs.
3. Determine status:
   - `"ok"`: a draft was produced and would normally be written to Notion.
   - `"failed"`: an error prevented drafting (no PRDs, all archived, upstream Notion failure, etc.).
4. Write the run log to `<run_dir>/opportunity.md` (see "Run log shape" below).
5. If `status == "ok"`: write the draft to the `# Opportunity` section of the Notion theme page (same write logic as default mode, just without the chat approval step). Then VERIFY the write: re-fetch the page and assert the new paragraph text appears under `# Opportunity`. The `notion-update-page` tool returns `{page_id: ...}` whether or not any `old_str` actually matched, so verification is the only way to detect a silent miss. If verification fails, retry the write once with a fresh fetch and recomputed `old_str`. If verification still fails, set `written_to_notion: false` and add the caveat `[WRITE_VERIFY_FAILED: notion-update-page returned success but new content not present after re-fetch]`. Do not silently report success without observed content.
6. If `status == "failed"`: do **not** write to Notion.
7. Do **not** append to `INDEX.md` - the orchestrator owns the index write for orchestrated runs.
8. Return the structured payload below to the orchestrator.

**Return shape:**

```yaml
status: "ok" | "failed"
section: "opportunity"
written_to_notion: <bool>
run_log_path: "<run_dir>/opportunity.md"
one_line_summary: "<short human-readable summary>"
caveats: []  # populated with ["[WRITE_VERIFY_FAILED: ...]"] if post-write verification fails after retry
```

**Run log shape (`<run_dir>/opportunity.md`):**

```markdown
# theme-opportunity run log

- **Theme:** <theme name>
- **Notion URL:** <theme page URL>
- **Run timestamp:** <ISO 8601>
- **Mode:** orchestrated

## Inputs

- PRDs canvassed (N total): list of {ID, title, Product team workflow tier}

## Reasoning trail

- **Anchored on:**
  - <PRD-ID> "<PRD title>" (<tier>): <one-line rationale for how this PRD informed the draft>
  - ... (one bullet per anchored PRD)
- **Excluded:** PRDs that were canvassed but did not contribute to the draft. List with the bar that excluded each one.
  - <PRD-ID> "<PRD title>" (<tier>): <reason: too speculative, no quantified evidence, etc.>
  - ... (one bullet per excluded PRD; omit this section if no PRDs were canvassed-but-rejected)
- **Length pick:** <short | long>, <one-line rationale>
- **Cross-cutting outcome:** <one-liner unifying narrative>

## Final draft

<verbatim text written to Notion, or empty if status == failed>

## Caveats

(none for opportunity)

## Wrote to

<Notion section anchor link, or "not written, status: failed - <reason>">
```

## Direct-invoke INDEX.md append

When invoked **directly** (not from `/theme` orchestrator), after writing the run log:

1. Compute INDEX path: `<repo_root>/.context/theme-runs/INDEX.md`.
2. If the file does not exist, create it with the header (see `theme/.claude/commands/theme.md` "INDEX.md format and append rules").
3. Append a single row covering this section's run:
   - `Theme`: `<theme_name>`
   - `URL`: `<theme_url>`
   - `Run dir`: `<theme-slug>-<timestamp>` (relative)
   - `Timestamp`: ISO 8601 UTC
   - `Sections`: `<section-short-name>:<status>` (e.g. `opp:ok`, `voice:failed`, `factors:caveat`)
   - `Last tweaked`: `-`

Section short-names: `opp` (opportunity), `voice` (customer-voice), `factors` (decision-factors).

When invoked from the orchestrator (orchestrated mode), do **not** append - the orchestrator owns the row write.

## Notes for parallel orchestration

This skill is designed to run in parallel with sibling section-skills under a future /theme orchestrator. To support that:

- Single theme per invocation, identified by argument.
- No dependency on prior conversation turns.
- Writes only to the Opportunity section, never other sections.
- The approved paragraph plus reasoning trail is self-contained output the orchestrator can capture and log.
