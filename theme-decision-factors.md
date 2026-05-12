---
name: theme-decision-factors
description: Generate the Decision factors bullets for a Discovery Theme page in Notion by reading its linked PRDs and the Product Requests table. Drafts in chat for approval, then writes to the theme page. When the source has no extractable signal, goes loud and offers a Slack search fallback. Trigger when asked to generate or draft theme decision factors, or invoked as /theme-decision-factors with a theme URL or name.
---

# /theme-decision-factors

Generate the Decision factors bullet list for a Discovery Theme page: short, exec-readable bullets that capture why this theme is high priority right now. Designed to run on its own or in parallel with sibling section-skills under a future /theme orchestrator.

## Context

- Discovery Themes data source: `collection://348a84ed-4024-801f-a259-000bf6d220bd`
- Projects (PRDs) data source: `collection://0d7ef002-875f-453b-bb05-7789a3436086`
- Product Requests data source: `collection://2b8a84ed-4024-8169-aa72-000bce35362f`
- Relation: theme `⏩ Projects` ↔ project `Discovery Theme`
- Theme page template sections (current): `# Opportunity`, `# What we want customers to say` (with `### What they would say if we went further`), `# Decision factors`, `# Relevant projects`
- This skill writes ONLY to the body content under `# Decision factors`. Do not modify any other section.
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
- The current body content under `# Decision factors`

### Step 3: Section presence check

If the theme page has no `# Decision factors` heading at all, abort with a clear message: tell the user the page has no `# Decision factors` heading (h1), and suggest they add the line `# Decision factors` manually to the page before re-running. Do not create the heading.

### Step 4: Check for existing content

If the existing `# Decision factors` content has real (non-placeholder) bullets, show the current content to the user and ask whether to overwrite. Do not silently overwrite real PM-authored content.

### Step 5: Fetch all linked PRDs in parallel

One `mcp__claude_ai_Notion__notion-fetch` call per PRD URL, batched in a single message so the calls run concurrently. For each PRD, capture:

- Page title
- `Product team workflow` field value
- `Goal` field value
- `Features requested` relation value (list of Feature page URLs, may be empty)
- The body content - in particular Background, Problem, Goal, and any "Why now" / "Pressure" / "Competitive landscape" / "Customer asks" sections if present
- Any references to named competitors, named deals, named upstream initiatives, or merchant ARR rankings

If a relation field (`Features requested`, etc.) is not present at all in the `notion-fetch` output, treat it as empty - the tool omits empty relation properties from page output entirely. Do not interpret absence as a schema mismatch or abort.

### Step 6: Query the Product Requests table

The PRD-to-Product-Request linkage is mixed: some PRDs have a clean relation chain, others do not. Use the relation walk first, then fall back to text matching for any PRD that comes up empty.

**Quick check before walking.** If every PRD body is placeholder-only (Step 7 would exclude them all) and no PRD has a populated `Features requested` relation, skip the relation walk entirely and go straight to the text-match fallback. The relation walk has nothing to walk.

**Primary strategy (relation walk).** For each PRD with a populated `Features requested` relation, fetch each linked Feature page (data source `collection://2b8a84ed-4024-810e-88a9-000b4f891b3a`). On each Feature, capture:

- `Existing ARR (AIRTABLE)` (dollar number; aggregate ARR of all merchants linked to this Feature)
- `Request count (AIRTABLE)` (number of merchant requests)
- `Status (AIRTABLE)` (one of: Available, In Progress, Added to Roadmap, Blocked on partners, Won't do)
- `Requests (AIRTABLE)` (list of Product Request page URLs)
- `Merchant list (AIRTABLE)` (text list of merchant names)

Then fetch each Product Request URL from `Requests (AIRTABLE)` and capture: `Summary`, `Merchant Name (AIRTABLE)` (relation to merchant page; merchant pages do not carry a per-merchant ARR field, only `Location count`), `🔒 Created At (AIRTABLE)`, `Feature(s) status`.

Batch all Feature fetches in one message and all Product Request fetches in a second batched message.

**Fallback strategy (text match).** For any PRD with an empty `Features requested` relation, run `mcp__claude_ai_Notion__notion-search` against the Features data source `collection://2b8a84ed-4024-810e-88a9-000b4f891b3a` (pass it as the `data_source_url` parameter) using keyword fragments derived from the PRD title and the theme title. If the tool does not accept the data source scope or the results include hits from other data sources, filter results client-side to keep only those whose source / parent data source matches `collection://2b8a84ed-4024-810e-88a9-000b4f891b3a` and discard the rest - do not let global search results pollute the candidate set. Treat the top 1-3 surviving matches as candidate Features and walk the same Feature → Product Requests chain as above. Note the top 1-3 candidate matches and the rule used (e.g., "PRD title text-match against Features collection") in your working notes; surface them in the final-draft reasoning trail under an "Anchored on (Product Requests table)" line so the user can sanity-check the match.

**Surface the strongest available form of the ARR signal.** Prefer signals in this order, using whichever is reachable:

- **Cross-feature ARR ranking is reachable** via the existing "Demand by ARR" view of the Features database, sorted by `Existing ARR (AIRTABLE)` descending. Fetch this view by calling `mcp__claude_ai_Notion__notion-query-database-view` with `view_url` set to `https://www.notion.so/2b8a84ed4024818ba457f911a2cf0902?v=2b9a84ed-4024-8094-82d9-000cfba03b63` (the `view://2b9a84ed-4024-8094-82d9-000cfba03b63` URI corresponds to this `?v=` parameter; the `notion-fetch` tool does NOT support `view://` URIs, so always use `notion-query-database-view` for this step). The returned rows are already in the view's sort order; the first row is rank #1. Find the theme's Features in that list by matching either the page URL (`url` field on each row) or the page title (`Name` field) against the Features collected via the relation walk above; record each match's 1-based position. State the position as "#N by ARR on the Product Requests list" using the Feature's rank (e.g. "#2 by ARR on the Product Requests list"). Note: this view typically returns ~100 rows and the response often exceeds inline tool output limits, so the tool will save it to a file and return the path. Parse the file with python (e.g., `python3 -c "import json; data = json.load(open(path)); inner = json.loads(data[0]['text']); ..."`) to scan for theme-feature matches by name or URL.
- **Per-Feature aggregate ARR is reachable** as `Existing ARR (AIRTABLE)` on each Feature. State it with the named merchants from `Merchant list (AIRTABLE)` (e.g. "Requested by Acme, Beta, Gamma; $120K total ARR on the requesting list").
- **Per-merchant ARR is NOT directly reachable** from this graph - the merchants data source `collection://2b8a84ed-4024-81ba-a5ec-000b20876a72` does not carry an ARR field. Do not fabricate per-merchant ARR figures.
- **Only request count is reachable:** state the quantified aggregate (e.g. "Requested by 6 merchants on the Product Requests list" - using `Request count (AIRTABLE)`).
- **Neither ranking, ARR, nor count is reachable:** drop the request-table signal entirely. Record the gap in the reasoning trail.

### Step 7: Filter empty PRDs

Skip any PRD whose body is blank, contains only template placeholders, or contains "Replaced by Claude" without real content. Note them in the reasoning trail as excluded.

### Step 8: Extract candidate signals against the rubric

The rubric is "why now" signals. Two subtypes count:

**External pressure (dominant case):**
- Named competitor moves (shipped or announced, with a date when announced)
- Specific deal dependencies (named deal, named merchant, named ARR if available)
- Ranked customer asks (named ARR position) or quantified aggregate of named customers (breadth signal - see Step 10 tier 2; the latter is not a fallback when each contributing customer is named)
- Partner-driven pressure (named partner, named action)
- Regulatory or contractual obligations (named requirement)

**Internal timing pressure (load-bearing case only):**
- Capacity constraints (named team, named upstream initiative, named date)
- Upstream launch sequencing (named launch, named date, named dependency)
- Sequencing constraints that materially shape the timing decision

Internal momentum, strategic-fit narrative, and "we just shipped X so now Y" do NOT count. They are not why-now signals.

### Step 9: Apply the bar

A candidate becomes a bullet only if it carries:

- a named entity (specific competitor with a specific action, specific deal name, specific merchant or merchant tier with a specific ranking, specific upstream initiative), AND
- a specific fact about that entity.

If the underlying signal is real but the source only captures it in aggregate, allow the aggregate phrasing - but the aggregate must still be quantified. Never adjectival.

**Allowed:**
- "Olo shipped tap-to-identify in October."
- "Acme renewal blocks on POS-accurate matching."
- "#2 by ARR on the Product Requests list."
- "Requested by 3 of the top 10 merchants by ARR."
- "Two of the next four enterprise launches block on this; onboarding capacity already strained."

**Not allowed:**
- "Many merchants have asked." (adjectival aggregate)
- "Several competitors are catching up." (adjectival, no named action)
- "This is critical for the enterprise segment." (adjectival, no specific entity)
- "We just shipped GFD so this is the next logical step." (internal momentum, not a why-now signal)

### Step 10: Rank by force, cap at 5

Rank candidates by force tier, descending:

1. Named deal dependent on this (immediate revenue at risk)
2. Quantified aggregate of 4+ named customers/prospects converging on the same ask or pain within ~90 days (breadth-of-demand signal). Each contributing merchant must be named, and the count must be specific. This trumps single-instance signals because breadth is the strongest evidence that the theme is broadly load-bearing, not idiosyncratic. If only one or two merchants are named, this does not apply - drop to a lower tier.
3. Ranked ARR position with a number (top-10 by ARR, or named ranking on the Demand-by-ARR view)
4. Named competitor shipped
5. Named upstream launch / capacity constraint with a date
6. Named competitor announced with a date
7. Named partner / regulatory / contractual obligation
8. Adjectival aggregate (fallback only when no named specific exists - rarely passes the bar in Step 9)

Within a tier, pick the order that hits hardest for an exec scan and note the call in the reasoning trail. The reasoning trail names the assigned force tier per bullet so the ranking is auditable.

Cap at 5 bullets. No minimum, no padding. If only 2 strong signals exist, output 2. If 8 strong signals exist, keep the top 5 and list the dropped signals in the reasoning trail.

If zero candidates pass the bar, go to Step 11 (the empty/loud branch). Do not write to Notion in that branch until the user provides additional input.

### Step 11: Empty branch trigger

If zero candidates passed the bar in Steps 8-10, go loud. Use the format and behavior described in the "Empty/loud branch" section below. Do not draft, do not write to Notion, until the user provides additional input via that branch.

### Step 12: Draft and present

Apply the discipline rules below.

**Bullet discipline:**
- One line each. No bullet wraps.
- Short, focused on execs, polished. Each word earns its place.
- No padding, no hedging, no adjectival filler.

**Tone rules (must):**
- Use plain factual language. The bullet states a fact; it does not argue for prioritization.
- Use named entities and specific facts whenever the source supports them.
- When falling back to aggregate, the aggregate must be quantified.

**Tone rules (must not):**
- No internal Thanx capability names, code paths, or feature labels unless a feature name is load-bearing for understanding the fact.
- No adjectival hedging: "critical", "important", "significant", "key", "major", "robust", "comprehensive", "many", "several".
- No em dashes. Use regular dashes (-), commas, or rewrite the sentence.
- No fabrication. If a competitor name, deal name, ARR figure, or date is not in the source material, do not invent it.

Output in this format:

```
## Draft Decision factors for [Theme Name]

> - [bullet 1]
> - [bullet 2]
> - [bullet 3]
> - [bullet 4]
> - [bullet 5]

**Reasoning:**
- Force ranking applied: [bullet 1: tier-1 deal-dependent | bullet 2: tier-2 ARR-ranked | ...]
- Anchored on (PRDs): [PRD names -> which bullet(s) each grounded]
- Anchored on (Product Requests table): [feature row(s) -> which bullet(s) grounded, with merchant names + ARR if applicable]
- Aggregate fallbacks used: [bullets that fell back to aggregate phrasing + why no named specific was available]
- Excluded as too soft / adjectival / internal-without-timing-link: [signal + reason for each]
- Dropped below cap of 5: [signal + force tier, for any signals that were strong enough to canvass but bumped below 5]

Approve, edit, or scrap?
```

If the empty/loud branch fired (Step 11), the reasoning trail also includes `Anchored on (Slack)` or `Anchored on (user-provided)` rows depending on which fallback was used. See the "Empty/loud branch" section for the full variants.

### Step 13: On approval, write to Notion

Use `mcp__claude_ai_Notion__notion-update-page` with `update_content` and old_string/new_string replacement. Replace ONLY the body content under `# Decision factors`. Preserve the heading verbatim. Do not modify any other section. After writing, re-fetch the page to confirm the write succeeded. Reply with the link to the updated theme page.

### Step 14: On edit request, revise and re-present

Iterate on the bullets and re-present using the same draft format. Apply user-requested edits to phrasing and ranking. Iterate until approved or scrapped.

### Step 15: On scrap, exit without writing

No write. No log.

## Empty/loud branch

When Step 11 fires, present the following:

```
## No "why now" signals surfaced for [Theme Name]

I canvassed [N] linked PRD(s) and the Product Requests table. Nothing met the bar for a decision-factor bullet.

**PRDs with timing-adjacent language but no extractable specifics:**
- [PRD name]: [one-line note on what timing-adjacent language was present and why it did not qualify]
- [PRD name]: [...]

**Other PRDs canvassed:** [N] additional PRDs canvassed, no timing signal. [collapsed list of names]

**Product Requests table:** [one line - e.g. "0 requests linked to these features", or "12 requests but no merchant ARR ranking accessible from this view"]

**Two ways forward:**

1. **Paste anything you want me to use** - a deal name, a capacity constraint, a competitor move, a ranked ask, an upstream launch date. I will draft from what you provide.
2. **Search Slack** - I can search the priority channels for similar signal. Default search plan below; edit before I run it.

**Proposed Slack search plan:**
- Terms: "[theme name]", [linked PRD title 1], [linked PRD title 2], [any competitor names already mentioned in PRDs]
- Recency: last 180 days
- Channels (priority, in order): #loud-n-clear, #product, #industry-ammo, #sales, #sales-customersuccess, #customer-quotes, #product-data-team, #product-managers-team, #rnd-leadership, #customer-success
- Fallback: if priority channels yield nothing, expand to all accessible channels

Reply with (1) facts to use directly, (2) "search Slack" (with edits to the plan if any), or (3) "stop" to exit without writing.
```

**Per-PRD canvass note rule:** the per-PRD list is bounded. PRDs with any timing-adjacent language get a one-line note. PRDs with no timing-adjacent language at all are listed as a collapsed `[N other PRDs canvassed, no timing signal]` with names. This keeps the loud moment scannable even on themes with many PRDs.

### On "search Slack"

Apply user edits to the search plan (terms, recency, channels) if any, then run searches in parallel using `mcp__claude_ai_Slack__slack_search_public_and_private` across the priority channels first.

**Pilot pair first.** Run #loud-n-clear and #product before fanning out to the rest of the priority list. #loud-n-clear is gong-bot output and yields the highest-signal aggregate by far - each thread is pre-structured with named merchants, named speakers, direct quotes, and pain-point/feature-request tags, which maps cleanly onto the bar in Step 9. #product picks up named CEO directives, leadership escalations, and cross-team metrics threads. If the pilot pair returns enough material to draft from, present the findings and ask "keep looking in other channels, or draft from these?" before fanning out further. Only sweep the rest of the priority list when the pilot pair underdelivers.

This tool does not accept a list of channels as a native parameter. Channel scoping is applied via Slack search modifiers in the `query` string (e.g. `in:loud-n-clear`). One channel modifier per query is reliable, so run one search per priority channel in parallel rather than trying to OR channels together. If a query returns no results, fall through to running an unfiltered search and apply the priority-channel filter client-side, keeping only threads whose channel matches the priority list.

Recency: first, include `after:YYYY-MM-DD` (computed as today minus 180 days) in the query string; if that modifier is silently ignored by Slack, fall back to passing the same threshold as the `after` Unix timestamp parameter on the tool call; if that also fails, filter results client-side to threads created within the last 180 days.

Present priority-channel findings (or absence) and offer to expand:

- **Findings present:** "Found N candidate signals in priority channels. Keep looking in other channels for additional signal, or draft from these?"
- **No findings:** "No matching threads in priority channels. Expand to all accessible channels, or stop?"

On "draft from these": apply the bar in Step 9, draft candidate bullets from the priority-channel findings only, then present using the Step 12 format for the user's approve/edit/scrap decision before writing. Do not write to Notion without going through Step 12 first.

On "expand", run again across all accessible channels and present consolidated findings.

For each finding that meets the bar in Step 9, draft a candidate bullet. Slack threads are sources, not direct quotes - the bullet states the fact, the reasoning trail names the source thread with a link.

Present using the standard draft format from Step 12. The reasoning trail's "Anchored on" line gains: `Anchored on (Slack): [thread title → bullet, with link]`.

If Slack search across all channels yields nothing, say so plainly and exit without writing.

### On pasted facts

Treat the pasted facts as authoritative. Apply the bar in Step 9 to phrasing only - cut adjectival hedging, name the entity, quantify the aggregate. Do not second-guess the user's facts.

Draft and present using the standard Step 12 template. Reasoning trail's "Anchored on" line gains: `Anchored on (user-provided): [fact → bullet]`.

### On "stop"

Exit, no write, no log.

## Orchestrated mode

When the dispatch prompt from `/theme` includes the literal phrase `ORCHESTRATED MODE`, branch behavior as follows. Direct invocation is unchanged - the interactive empty/loud branch with user-approved Slack search remains the default.

**Required dispatch prompt fields the orchestrator provides:**

- `run_dir`: path to the per-run directory. The skill writes its run log to `<run_dir>/decision-factors.md`.
- `theme_id`: the resolved Notion page ID.

**Behavior changes vs default mode:**

1. Skip the "draft in chat for approval" step. No interactive presentation.
2. Run all default-mode steps (PRD fetch, canvass, Step 9 bar evaluation) **except** the chat-draft-and-approval step. The skill's drafting heuristics are unchanged; only the I/O boundary differs.
3. If at least one PRD-anchored bullet clears Step 9: status = `"ok"`, proceed to Step 5 below.
4. If no PRDs clear Step 9 (Step 11 trigger condition): **auto-execute the Slack fallback** instead of presenting the loud branch. See "Auto-Slack fallback" below.
5. Write the run log to `<run_dir>/decision-factors.md`.
6. If `status == "ok"`: write the bullets to the `# Decision factors` section of the Notion theme page. Then VERIFY the write: re-fetch the page and assert the new bullets appear under `# Decision factors`. The `notion-update-page` tool returns `{page_id: ...}` whether or not any `old_str` actually matched, so verification is the only way to detect a silent miss. If verification fails, retry the write once with a fresh fetch and recomputed `old_str`. If verification still fails, set `written_to_notion: false` and append the caveat `[WRITE_VERIFY_FAILED: notion-update-page returned success but new content not present after re-fetch]` to the existing caveats list. Do not silently report success without observed content.
7. If `status == "caveat"` or `status == "failed"`: do **not** write to Notion.
8. Do **not** append to `INDEX.md` - the orchestrator owns the index write for orchestrated runs.
9. Return the structured payload below.

### Auto-Slack fallback (orchestrated mode only)

When PRD canvass produces no qualifying signal:

1. **Auto-fire the pilot pair** (`#loud-n-clear` + `#product`). Same query construction as the default-mode plan: theme name + each linked PRD title, scoped via `in:<channel>` modifier, 180-day recency. Run queries in parallel via `mcp__claude_ai_Slack__slack_search_public_and_private`. Do **not** ask the user to approve the search plan.
2. Apply the Step 9 bar to pilot results.
3. **If pilot returns ≥ 3 qualifying signals**: incorporate into drafting, status = `"ok"`. Do not expand.
4. **If pilot returns < 3 qualifying signals**: auto-expand to the full priority channel list (`#industry-ammo`, `#sales`, `#sales-customersuccess`, `#customer-quotes`, `#product-data-team`, `#product-managers-team`, `#rnd-leadership`, `#customer-success`). Same query construction, same parallel execution, no user prompt.
5. Apply the Step 9 bar to the full sweep results.
6. **If full sweep returns ≥ 1 qualifying signal**: incorporate into drafting, status = `"ok"`.
7. **If full sweep returns 0 qualifying signals**: status = `"caveat"`, draft_text = "", emit caveat `[NO SIGNAL: PRDs and Slack both empty]`. Do **not** write to Notion.
8. **Borderline signals** (named entity but vague phrasing): include with `(vague, retained for color)` annotation. Status remains `"ok"`.

The auto-Slack fallback uses the same Step 9 bar, same priority channel list, same query construction as the default-mode interactive Slack flow. Only the user prompts (approve search plan, decide expand-or-draft) are removed.

**Return shape:**

```yaml
status: "ok" | "caveat" | "failed"
section: "decision-factors"
written_to_notion: <bool>
run_log_path: "<run_dir>/decision-factors.md"
one_line_summary: "<short summary, e.g. '4 bullets anchored on Slack pilot'>"
caveats: []  # ["[NO SIGNAL: PRDs and Slack both empty]"] when status == caveat; append "[WRITE_VERIFY_FAILED: ...]" if post-write verification fails after retry
```

**Run log shape (`<run_dir>/decision-factors.md`):**

```markdown
# theme-decision-factors run log

- **Theme:** <theme name>
- **Notion URL:** <theme page URL>
- **Run timestamp:** <ISO 8601>
- **Mode:** orchestrated

## Inputs

- PRDs canvassed (N total):
  - <PRD-ID> "<PRD title>" (<tier>): timing-signal-found: yes | no
  - ... (one bullet per PRD)
- Slack queries executed (only if PRD canvass produced no qualifying signal):
  - Pilot pair (#loud-n-clear + #product):
    - `<full query string>` → N results
    - ... (one per query)
  - Full sweep (only if pilot < 3 qualifying):
    - `<full query string>` → N results
    - ...

## Reasoning trail

- **Anchored on (PRDs):**
  - <PRD-ID> "<PRD title>" (<tier>) → bullet: <one-line restatement of the bullet anchored on this PRD>
  - ... (one bullet per anchored PRD)
- **Anchored on (Slack):**
  - <thread title> (<permalink>) → bullet: <one-line restatement of the bullet anchored on this thread>
  - ... (one bullet per anchored Slack thread)
- **Excluded (PRDs):** PRDs that were canvassed but did not contribute to a bullet.
  - <PRD-ID> "<PRD title>" (<tier>): <reason: too speculative, off-theme, no quantified evidence, etc.>
  - ... (one bullet per excluded PRD; omit this section if no PRDs were canvassed-but-rejected)
- **Excluded (Slack):** Slack threads canvassed but did not contribute to a bullet.
  - <thread title> (<permalink>): <reason>
  - ... (omit this section if Slack was not searched or all results were used)
- **Step 9 bar applied:** <one-liner restating the bar that decisions were judged against>

## Final draft

<verbatim bullets written to Notion, or empty if status != ok>

## Caveats

<list of caveats; empty if none. e.g. "[NO SIGNAL: PRDs and Slack both empty]" when status == caveat>

## Wrote to

<Notion section anchor link, or "not written, status: <status> - <reason>">
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

This skill is designed to run in parallel with sibling section-skills (`theme-opportunity`, `theme-customer-voice`) under a future /theme orchestrator. To support that:

- Single theme per invocation, identified by argument.
- No dependency on prior conversation turns.
- Writes only to the `# Decision factors` section, never other sections.
- The approved bullet list plus reasoning trail is self-contained output the orchestrator can capture and log.
- The empty/loud branch is interactive - it requires user input before writing. An orchestrator must either (a) surface the loud prompt to the user mid-orchestration, or (b) accept that this skill may exit without writing while siblings complete. The skill itself does not block siblings - it just fails to write its section.
- No calibration log written by this skill in V1.
