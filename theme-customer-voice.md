---
name: theme-customer-voice
description: Generate the customer-voice quotes (primary line and stretch line) for a Discovery Theme page in Notion. Splits the work by Product team workflow tier - Strong-evidence PRDs anchor the first quote, Strong + Moderate evidence anchor the second. Drafts in chat for approval, then writes to the theme page. Trigger when asked to generate or draft theme customer voice, or invoked as /theme-customer-voice with a theme URL or name.
---

# /theme-customer-voice

Generate the merchant-voice quotes for a Discovery Theme page: a primary line ("What we want customers to say") and a stretch line ("What they would say if we went further"). Designed to run on its own or in parallel with sibling section-skills under a future /theme orchestrator.

## Context

- Discovery Themes data source: `collection://348a84ed-4024-801f-a259-000bf6d220bd`
- Projects (PRDs) data source: `collection://0d7ef002-875f-453b-bb05-7789a3436086`
- Relation: theme `⏩ Projects` ↔ project `Discovery Theme`
- PRD priority field: `Product team workflow`. Values: `Strong evidence`, `Moderate evidence`, `Early evidence`, plus archived/other.
- Theme page template sections (current): `# Opportunity`, `# What we want customers to say` (with `### What they would say if we went further`), `# Decision factors` (optional), `# Relevant projects`
- This skill writes ONLY to the `# What we want customers to say` section AND its `### What they would say if we went further` subsection. Do not modify any other section.
- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`

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
- The current body content under `# What we want customers to say` and `### What they would say if we went further`

### Step 3: Check for existing content

If the existing content already has real merchant-voice quotes (anything other than the default gray placeholder text), show the current content to the user and ask whether to overwrite. Do not silently overwrite real PM-authored content.

### Step 4: Fetch all linked PRDs in parallel

One `mcp__claude_ai_Notion__notion-fetch` call per PRD URL, batched in a single message so the calls run concurrently. For each PRD, capture:

- Page title
- `Product team workflow` field value
- `Goal` field value
- The body content (Background, Problem, Goal, What success looks like sections in particular)
- Any "What we want customers to say" or "What customer joy looks like" content if present in the PRD

### Step 5: Categorize PRDs by Product team workflow

This drives the two-tier split:

- **Strong evidence**: anchors the first quote. The "What we want customers to say" line must be grounded in these.
- **Moderate evidence**: enriches the second quote. The "What they would say if we went further" line layers Moderate-evidence outcomes on top of Strong-evidence outcomes.
- **Early evidence**: ignore unless the user explicitly asks to include them. They are too speculative to define merchant joy.
- **Archived / blank / "Replaced by Claude" placeholder PRDs**: ignore entirely. Note them in the reasoning trail as excluded.

### Step 6: Handle thin or empty PRDs by tier

**Strong evidence — never skip, even if empty.** A Strong-evidence tag is a PM's assertion that this PRD is load-bearing for the theme. If the body is blank, contains only template placeholders, or says "Replaced by Claude", do best-effort interpretation: combine the PRD title, the theme name and pillar, and what the other Strong-evidence PRDs are doing to infer this PRD's intent. Surface that interpretation in the reasoning trail so the user can correct it.

- **Direct mode:** if the title is ambiguous or the inferred intent feels speculative, ASK the user for one paragraph of context before drafting. Do not silently invent an outcome for a Strong PRD.
- **Orchestrated mode:** do best-effort silently (no questions). Note any speculation explicitly in the reasoning trail / run log.

**Moderate evidence — title-as-weak-signal.** If a Moderate-evidence PRD body is empty but the title clearly signals intent (e.g. "Custom app icons"), use the title as a weak signal and note it. If the title is too generic or the intent unclear, skip and note as excluded.

**Early evidence — ignore** unless the user explicitly asks to include them.

**Archived — ignore entirely.**

**Narrative coherence exception.** If a tagged Strong-evidence PRD (real-content or title-only) does not share the cross-cutting outcome that the other Strong-evidence PRDs jointly express (i.e. its merchant payoff is structurally unrelated to the theme's narrative), exclude it from the anchor. Note the mismatch in the reasoning trail and recommend the user consider re-tagging the PRD off this theme. This is narrative coherence, not reclassification - the PRD's tier stays Strong evidence; it's just not load-bearing for THIS theme's merchant voice.

### Step 7: Thin-source handling

**7a. Thin Strong-evidence source.** If fewer than 2 Strong-evidence PRDs are tagged to the theme, proceed anyway with a best-effort primary line and call out the thin source explicitly in the reasoning trail. If the source is too thin to ground anything, say so in the draft and stop without writing to Notion.

**7b. No Moderate-evidence source.** If zero Moderate-evidence PRDs remain after filtering, DO NOT draft a stretch line. Leave the `### What they would say if we went further` heading empty when writing to Notion. Do NOT extrapolate a stretch line from:
- Out-of-Scope or "future direction" sections inside Strong-evidence PRDs
- Vision quotes from leadership embedded in Strong-evidence PRDs
- "Candidate themes" or "what V2 might be" lists in placeholder/bandwidth PRDs
- The empty placeholder PRD's title alone

These are deferred scope, not committed Moderate-evidence work, and stretch lines drawn from them are hallucinations dressed as enrichment.

In both 7a and 7b, do not ask the user whether to expand tiers or reclassify; the workflow tier on each PRD is the source of truth.

### Step 8: Identify the cross-cutting outcome

Read the Strong-evidence PRDs and answer:

1. What single experience do they collectively deliver to the merchant's guests AND the merchant's operations?
2. What is the merchant's *felt* emotional payoff if all Strong-evidence PRDs ship - the joy, pride, relief, or trust that returns? Land on one emotional arc, not a list of resolved problems. ("My loyalty program finally feels like the gift I built it to be" beats "I'm not fielding tickets, customers redeem reliably, my regulars come back" - the first is felt, the second is operational.)
3. **Roll the Strong-evidence outcomes into a single beat, do not enumerate one clause per PRD.** Three Strong PRDs do not equal three comma-joined clauses. Find the unifying frame and let one beat carry all three. ("The right reward reaches them at the right moment no matter where or when they're ordering" carries timing + timezone + in-cart UX in a single felt beat. "Time-based rewards work, customers in every timezone get the right hour, and they can figure out how to apply it" is the failure mode - three feature-shaped clauses dressed as one quote.)

Then read the Moderate-evidence PRDs and answer:

1. Does Moderate evidence *extend* the Strong-evidence theme (more accuracy, more coverage) or does it *pivot the frame* (from accuracy to frictionlessness, from completeness to intelligence)?
2. If it pivots, name the new frame. The stretch line should reflect the new emotional payoff, not just "Strong evidence, but more."
3. If a single Moderate-evidence PRD is the dominant capability shift (e.g. tap-to-identify, AI personalization), let it anchor the stretch line as the headliner; supporting Moderate-evidence PRDs become enrichment.

### Step 8.5: Frame-fit check

Before drafting, walk every Strong-evidence PRD title against the chosen frame. For each PRD ask: does its intent (from the body if present, from title-plus-context otherwise) belong inside the frame I picked?

- **All fit:** proceed to draft.
- **One or more don't fit:** either widen the frame to include them, or apply the narrative coherence exception in Step 6 and exclude that PRD from the anchor (with rationale in the reasoning trail).
- **Title-only PRD's intent is unclear after the check:** in direct mode, ask the user for context before drafting. In orchestrated mode, do best-effort and note in the reasoning trail.

This is the moment to catch the "placeholder PRD whose title carries a pillar absent from the other PRDs" failure mode - the frame should expand to include it, not silently drop it.

### Step 9: Draft both quotes

Apply the heuristics under "What makes a quote land" and the tone rules below. If Step 7b applies (no Moderate-evidence PRDs), draft only the primary line and skip the stretch line entirely.

### Step 10: Present for approval

Output in this format (full version, when both lines exist):

```
## Draft customer voice for [Theme Name]

> ## What we want customers to say
> *(Strong evidence only)*
>
> > "[1-3 sentence merchant quote]"
>
> ## What they would say if we went further
> *(Strong + Moderate evidence)*
>
> > "[1-3 sentence merchant quote]"

**Reasoning:**
- Strong-evidence cross-cutting outcome: [one line]
- Stretch frame: [extends Strong-evidence / pivots to X]
- Anchored on (Strong evidence): [PRD names]
- Stretch enrichment (Moderate evidence): [PRD names + role each plays - headliner vs. supporting]
- Excluded as too speculative or empty: [PRD names + reason]

**Questions to sharpen this:**
- [Surface 1-3 judgment calls about the *quote itself* the user should weigh in on - e.g. voice (merchant vs. guest), whether stretch should extend or pivot the frame, which of two phrasings lands harder. Do NOT ask about PRD categorization, inclusion, or whether the source material is correct - those are taken as given.]

Approve, edit, or scrap?
```

When Step 7b applies (no Moderate-evidence PRDs), use the primary-only variant:

```
## Draft customer voice for [Theme Name]

> ## What we want customers to say
> *(Strong evidence only)*
>
> > "[1-3 sentence merchant quote]"
>
> ## What they would say if we went further
> *(no Moderate-evidence PRDs - leaving empty per Step 7b)*

**Reasoning:**
- Strong-evidence cross-cutting outcome: [one line]
- Anchored on (Strong evidence): [PRD names]
- No Moderate-evidence source: stretch line intentionally omitted (no Moderate-evidence PRDs tagged to this theme)
- Excluded as too speculative or empty: [PRD names + reason]

**Questions to sharpen this:** [1-3 quote-craft questions]

Approve, edit, or scrap?
```

### Step 11: On approval, write run log and Notion update

**First, write the run log** to `.context/theme-runs/<theme-slug>-<timestamp>/customer-voice.md` per the "Run log" section below. Then append to `INDEX.md` per the "INDEX.md append" section.

**Then write to Notion.** Use `mcp__claude_ai_Notion__notion-update-page` with `update_content` and old_str/new_str replacement.

**Default case (both lines drafted):** Replace BOTH:
- The blockquote line(s) under `# What we want customers to say`
- The blockquote line(s) under `### What they would say if we went further`

**No-stretch case (Step 7b applied):** Write only the primary blockquote under `# What we want customers to say` and leave `### What they would say if we went further` with no blockquote underneath.

Preserve the headings themselves verbatim. Do not modify any other section.

**Verify the write.** Re-fetch the page and assert the new blockquote text appears under both headings (or only under the primary heading in the no-stretch case). The `notion-update-page` tool returns `{page_id: ...}` whether or not any `old_str` actually matched, AND can return success even when the underlying call timed out or failed silently. Verification is the only way to detect either failure mode. If verification fails, retry the write once with a fresh fetch and recomputed `old_str`. If verification still fails, tell the user explicitly: `WRITE FAILED: notion-update-page returned success but new content not present after re-fetch`. Do not silently report success without observed content.

Reply with the link to the updated theme page once verification passes.

### Step 12: On edit request, revise and re-present

Iterate until approved or scrapped.

## What makes a quote land

Five moves separate a quote that reads like a feature recap from one that reads like a merchant talking to a peer. Reach for these.

### 1. End on identity, not relief

The strongest closer doesn't say "the pain is gone" - it says "I am someone different now." Compare:

- Relief: "I'm not afraid to touch my home page anymore."
- Identity: "It finally feels like a marketing channel I run, not one that runs me."

The identity flip is the felt payoff. Pride, ownership, control. Relief is table stakes; identity is the win. If the closer reads like a defensive posture (no longer afraid, no longer broken, no longer fighting), rewrite it as an offensive one (I run, I lead, I plan, I am the kind of operator who).

### 2. Every clause is observable from the merchant's chair

Each clause should describe something the merchant *watches happen* or *does themselves*. Test: can the merchant point at it from their seat? Compare:

- Feature-shaped: "Scheduled publishing for home page versions."
- Observable: "Switches over on the day I planned."

If the clause names a feature ("preview mode", "segmentation", "version control"), rewrite until it names what the merchant sees become true ("I see every version before they do", "each kind of guest gets their own page", "I can roll it back").

### 3. Strip Thanx vocabulary

Merchants don't say "preview" or "MECE" or "version" or "scheduling." They say "I see it before they do" / "the home page I built for Tuesday goes live on Tuesday" / "each kind of guest gets a different page." If a Thanx-internal noun survives the draft, the line is half-finished - keep rewriting. Feature names are allowed only when the merchant's mental model genuinely needs them (rare).

### 4. Action verbs in the body, identity verb in the closer

Body sentences use *do/watch* verbs (shows, switches, see, runs, opts, redeems). The closer uses an *am/feel* verb (it feels like / I run / I'm the kind of operator who / it just works). The shift from *doing* to *being* is what makes the closer land harder than the body.

### 5. One frame, then check each PRD against it

Pick the unifying frame first - what single identity or experience are all the Strong-evidence PRDs serving? Then check each PRD's outcome belongs *inside* that frame. Without a frame you get three comma-joined feature mentions; with it the three capabilities become evidence for one identity.

For example, "marketing channel I run" is a frame. Inside it, "different home page per guest" + "switches on the day I planned" + "I see every version first" all serve the *I run this* identity. Outside it, the same three read as a checklist.

If a Strong-evidence PRD's outcome doesn't fit your frame, you have two choices: pick a wider frame, or apply the narrative coherence exception in Step 6 and exclude the PRD.

### Putting it together

A line that nails all five reads like one beat with a felt payoff:

> "My app shows a different home page to each kind of guest, switches over on the day I planned, and I see every version before they do. It finally feels like a marketing channel I run, not one that runs me."

- Frame: *marketing channel I run* (move 5)
- Body verbs: shows, switches, see (move 4)
- Each clause observable: different home page, switches, I see (move 2)
- Zero Thanx nouns: no "MECE", "scheduling", "preview" (move 3)
- Closer: identity flip, "I run, not one that runs me" (move 1)

## Tone rules

Both quotes MUST:

- Be in **merchant voice** ("My guests...", "I see...", "My loyalty program..."). The speaker is the restaurant operator, not the consumer.
- Focus on **outcomes**, not features. "My guests opt in for themselves" beats "We support GFD enrollment." "Numbers match my POS to the cent" beats "We removed fuzzy matching."
- **Land a felt emotional payoff**, not just a non-broken operational state. "I'm not fielding tickets" describes the absence of pain. "My loyalty program finally feels like the gift I built it to be" lands a felt emotional arc. The line should read like joy, pride, relief, or trust, not like an operations dashboard going green.
- Be 1-3 sentences. Hard cap at 3.
- Roll multiple PRD outcomes into a **single unified beat**, not one comma-joined clause per PRD. Anchoring on N PRDs does not mean naming N outcomes. Find the frame all the PRDs collectively deliver and let one beat carry it.
- Pass the **"would a merchant actually say this to a peer" test.** Read the line aloud. Would a real operator say it that way in a hallway conversation, or does it scan as a constructed list joined by commas? If it reads as a written summary, rewrite it as something a person would say.
- Use the merchant's own colloquial language ("just works", "to the cent", "runs on its own").

Both quotes MUST NOT:

- Reference internal Thanx capability names, code paths, or feature labels (no "fuzzy matching", "check-in", "GFD", "Apple VAS"). The line should describe the outcome of the pain disappearing - what becomes true for the merchant, what worry stops, what work is no longer needed. A feature name can appear if it's load-bearing for expressing that outcome (stripping it would lose the merchant's mental model of what's happening, or erase which downstream tool now works). What's not okay: enumerating features and calling the list an outcome - "we now support X, Y, and Z reward types" is feature inventory dressed as merchant joy. What is okay: naming what becomes true when those features exist - confidence, fit, peace of mind - with a feature noun only when the outcome can't be expressed without it.
- Include statistics, dollar amounts, ARR figures, or merchant counts.
- Use adjectival hedging. Avoid "critical", "important", "significant", "key", "major", "robust", "comprehensive". They are low-information.
- Use em dashes (—). Use regular dashes (-), commas, or rewrite the sentence.
- Be longer than what a merchant would actually say in conversation.
- Fabricate quotes from real merchants. The output is a *target* merchant voice, not an attributed quote.
- Read as the same idea twice. The primary line and stretch line must express different emotional payoffs - if they're paraphrases of each other, the stretch isn't really a stretch.

The primary line specifically:

- Captures what shipping ALL Strong-evidence PRDs delivers, not the loudest one.
- Lands the merchant's felt emotional payoff (joy, pride, relief, trust returning) - not just the worry stopping.
- Carries every Strong-evidence outcome inside a single rolled-up beat. Do not name each PRD's contribution separately.

The stretch line specifically:

- Captures what shipping Strong + Moderate evidence delivers - the *next-level* experience beyond the Strong-evidence baseline.
- If Moderate evidence pivots the frame, lean into the new frame (don't just say "Strong evidence, but more accurate").
- Names the resolved pain explicitly alongside the new payoff. "I do X myself in minutes, instead of waiting hours for someone at Thanx" lands harder than "I do X myself in minutes" because the contrast makes the win concrete.
- **Stays as terse as primary.** Moderate-evidence anchoring means the stretch can be *informed* by those PRDs, not that it must enumerate them. Cap at 1-3 short sentences with a single emotional payoff. ("Anytime I have a new reward idea, I just configure it. I don't have to wait for IT to provide the IDs to me." beats a 3-clause configuration tour comma-joined to enumerate every Moderate PRD.)
- Should feel aspirational without sounding like marketing copy.

## Run log

Every run (direct or orchestrated) writes a per-skill run log so future tweaks ("redo voice without that bullet") can recover sources, exclusions, and reasoning without re-canvassing the PRDs.

**Path:** `.context/theme-runs/<theme-slug>-<timestamp>/customer-voice.md`

- `<theme-slug>`: lowercased theme title with non-alphanumerics replaced by `-`.
- `<timestamp>`: UTC, format `YYYYMMDD-HHMMSS` (matches existing dirs in `.context/theme-runs/`).
- In orchestrated mode, the orchestrator passes `run_dir` and the skill writes to `<run_dir>/customer-voice.md`. The orchestrator picks the dir name; the skill does not compute it.
- In direct mode, the skill computes the dir name itself.

**Shape:**

```markdown
# theme-customer-voice run log

- **Theme:** <theme name>
- **Notion URL:** <theme page URL>
- **Run timestamp:** <ISO 8601>
- **Mode:** direct | orchestrated

## Inputs

- PRDs canvassed split by tier:
  - Strong-evidence (N): list of {ID, title, body-status: real-content | empty-with-load-bearing-title | empty-narrative-mismatch}
  - Moderate-evidence (N): list of {ID, title, body-status}
  - Early-evidence (N): list of {ID, title}
  - Archived (N): list of {ID, title}

## Reasoning trail

- **Frame:** <one-line frame the primary anchors on>
- **Frame-fit check (Step 8.5):** for each Strong PRD, fits / widened-frame / excluded-via-narrative-coherence
- **Primary line anchored on:**
  - <PRD-ID> "<PRD title>" (Strong): <one-line rationale>
  - ... (one bullet per anchored PRD)
- **Stretch line anchored on:**
  - <PRD-ID> "<PRD title>" (Strong | Moderate): <one-line rationale>
  - ... (one bullet per anchored PRD)
- **Excluded:** PRDs that were canvassed but did not contribute to either quote.
  - <PRD-ID> "<PRD title>" (<tier>): <reason>
  - ... (omit if none)
- **Cross-cutting outcome:** <one-liner unifying narrative>

## Final draft

**Primary:** <verbatim primary line written to Notion, or empty if failed>

**Stretch:** <verbatim stretch line written to Notion, or empty if failed>

## Caveats

(none unless post-write verification fails - then `[WRITE_VERIFY_FAILED]`, or speculative interpretation of empty Strong PRDs - then `[SPECULATIVE_INTERPRETATION: <PRD-id>]`)

## Wrote to

<Notion section anchor links, or "not written, status: failed - <reason>">
```

## INDEX.md append

When invoked **directly** (not from `/theme` orchestrator), after writing the run log:

1. Compute INDEX path: `<repo_root>/.context/theme-runs/INDEX.md`.
2. If the file does not exist, create it with the header (see `theme/.claude/commands/theme.md` "INDEX.md format and append rules").
3. Append a single row:
   - `Theme`: `<theme_name>`
   - `URL`: `<theme_url>`
   - `Run dir`: `<theme-slug>-<timestamp>` (relative)
   - `Timestamp`: ISO 8601 UTC
   - `Sections`: `voice:<status>` (e.g. `voice:ok`, `voice:failed`, `voice:caveat`)
   - `Last tweaked`: `-`

When invoked from the orchestrator (orchestrated mode), do **not** append - the orchestrator owns the row write.

## Orchestrated mode

When the dispatch prompt from `/theme` includes the literal phrase `ORCHESTRATED MODE`, branch behavior as follows. Direct invocation is unchanged.

**Required dispatch prompt fields the orchestrator provides:**

- `run_dir`: path to the per-run directory. The skill writes its run log to `<run_dir>/customer-voice.md`.
- `theme_id`: the resolved Notion page ID.

**Behavior changes:**

1. Skip the "draft in chat for approval" step. No interactive presentation.
2. Run all default-mode steps (PRD fetch, tier-split canvass, primary + stretch drafting) **except** the chat-draft-and-approval step. The skill's drafting heuristics are unchanged; only the I/O boundary differs.
3. Determine status:
   - `"ok"`: both lines produced and would normally be written.
   - `"failed"`: no Strong-evidence PRDs, no draftable quotes, upstream failure, etc.
4. Write the run log to `<run_dir>/customer-voice.md` per the shared "Run log" section above.
5. If `status == "ok"`: write to `# What we want customers to say` (primary) and `### What they would say if we went further` (stretch) sections of the Notion theme page, then verify per Step 11's verification block. On verification failure after one retry, set `written_to_notion: false` and add the caveat `[WRITE_VERIFY_FAILED: notion-update-page returned success but new content not present after re-fetch]`. Do not silently report success without observed content.
6. If `status == "failed"`: do **not** write to Notion.
7. Do **not** append to `INDEX.md` - the orchestrator owns the index write for orchestrated runs.
8. Return the structured payload below.

**Return shape:**

```yaml
status: "ok" | "failed"
section: "customer-voice"
written_to_notion: <bool>
run_log_path: "<run_dir>/customer-voice.md"
one_line_summary: "<short summary>"
caveats: []  # populated with ["[WRITE_VERIFY_FAILED: ...]"] if post-write verification fails after retry
```

**Run log:** see the shared "Run log" section above for path and shape.

## Notes for parallel orchestration

This skill is designed to run in parallel with sibling section-skills under a future /theme orchestrator. To support that:

- Single theme per invocation, identified by argument.
- No dependency on prior conversation turns.
- Writes only to the customer voice sections, never other sections.
- The approved quotes plus reasoning trail are self-contained output the orchestrator can capture and log.
