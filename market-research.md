# /market-research

Standalone competitive-teardown skill. Takes a PRD URL, feature request URL, or
plain topic string, runs a parallel multi-brand external research pass, and
publishes results as a page in the [Market research database](https://www.notion.so/35da84ed40248070aedee942503090ca)
plus a durable local markdown file. When invoked on a PRD URL, the PRD's
`# Additional Resources` section gets a link to the new database entry — the
research becomes a relevant reference without being embedded as a subpage of
the PRD itself.

**Reference files** (loaded by this command at run time, paths relative to this file):
- `market-research/knowledge/modules.json` — Technical Partner Strategy snapshot
- `market-research/knowledge/visual-relevance-keywords.md`
- `market-research/knowledge/brief-template.md`
- `market-research/agents/brand-research.md`
- `market-research/agents/synthesis.md`

## Constants

```
MARKET_RESEARCH_DB_DATA_SOURCE_ID = "35da84ed-4024-8023-9f06-000be3f49b54"
MARKET_RESEARCH_DB_URL            = "https://www.notion.so/35da84ed40248070aedee942503090ca"
MODULES_SOURCE_URL                = "https://www.notion.so/8662d31182004bc5a3f2b547f9ba6dd7"
```

## Usage

```
/market-research <PRD url | feature request url | title string> [--brands "X, Y, Z"]
```

## Workflow overview

3 phases plus an inline user checkpoint:

0. **MCP health check (~5s, cached)**: verify Notion connected; warn if not.
1. **Scoping (~30s–2min)**: parse input, run /prd internal scoping agents (Branch B only), match category from bundled modules.json, extract dimensions, write research-brief.md.
2. **[Checkpoint]**: user reviews/edits the brief, types `go`.
3. **Research (~45–90s, parallel fan-out)**: launch 1 sub-agent per brand using `general-purpose` subagent type with explicit allowed_tools. Each writes findings-<brand>.md.
4. **Synthesis + publish (~30s)**: one synthesis sub-agent merges findings into competitive-teardown.md, then orchestrator creates a page in the Market research database and (when applicable) links it from the input PRD's Additional Resources.

Total wall-clock target: 2-4 minutes.

---

# MCP Health Check (runs automatically before Phase 0)

Verify Notion MCP is connected before starting. Cached to avoid repeated verification.

## Cache logic

1. **Cache file**: `~/.claude/market-research/.mcp-health-cache.json` with `last_check` timestamp.
2. **If `last_check` is less than 1 hour old**: skip the check.
3. **If missing or stale**: run the health check below.

## Health check

Test Notion (required): call `mcp__claude_ai_Notion__notion-search` with `query: "test", page_size: 1`. Success → connected. Error → disconnected.

Write `last_check` + result to the cache file.

**If Notion disconnected → STOP and emit:**

```
❌ Notion MCP not connected

/market-research requires Notion write access to publish results.

Fix:
1. Check that the Claude AI Notion connector is enabled in settings.
2. Restart this Conductor workspace if needed.
3. Re-run /market-research.
```

Exit immediately.

---

# Phase 0: Argument parsing

Parse the command argument:

- **If the argument is a Notion URL** (matches `https://www.notion.so/...` or `https://notion.so/...`): record `input.source = "notion-url"`, `input.value = <url>`, extract the page ID.
- **If the argument is any other string**: record `input.source = "string"`, `input.value = <string>`.
- **`--brands "X, Y, Z"`**: split on commas, trim whitespace, record as `user_seed_brands`.

Generate a `run_id` using a timestamp-based ID like `2026-05-11-1430` plus a short hash.

Create session directory: `<workspace>/.context/market-research/<run-id>/`
Write `input.txt` to the session dir containing the verbatim command argument(s).

---

# Phase 1: Scoping

## Branch detection

If `input.source == "notion-url"`:
  Fetch the page: `mcp__claude_ai_Notion__notion-fetch id: <url>`.
  Inspect the content for:
    - presence of `# Scope of Work` with non-empty bullets
    - presence of `# The problem` with non-empty text
  
  **Branch A** if both Scope of Work and The problem are populated.
  **Branch B** if the page exists but at least one of those is empty/thin.

If `input.source == "string"`:
  **Branch C** (title-only). Skip the Notion fetch.

Record `branch` in run-log payload.

## Branch B scoping pass

Launch these two agents IN PARALLEL (single Task tool message with both calls), copying their prompts from the existing /prd skill:

- `prd-research-features` from `prd/.claude/agents/prd-research-features.md`
- `prd-research-slack` from `prd/.claude/agents/prd-research-slack.md`

For each, override the output path to write to BOTH:
1. `<session-dir>/scoping-features.md` (or scoping-slack.md)
2. `prd/prd-sessions/<page-id>/research-features.md` (or research-slack.md) — so the PRD's session dir is also populated for future /prd invocations.

Wait for both to complete. The findings inform dimension extraction below.

## Branch C scoping

No scoping pass. Parse the title string for:
- **Subject**: the noun phrase (e.g., "segments" in "Exportable segments")
- **Verb**: the verb or action ("Exportable" → "export")

These two values seed dimension inference.

## Visual relevance inference

Read `market-research/knowledge/visual-relevance-keywords.md`.

Concatenate (lowercased) the topic, the PRD scope text (if Branch A), and the PRD problem text (if Branch A).
Search for substring matches against the High, Medium, and Low keyword lists.

- If any High keyword matches → `visual_relevance = "high"`.
- Else if any Medium keyword matches → `visual_relevance = "medium"`.
- Else if any Low keyword matches → `visual_relevance = "low"`.
- Else → default to `"medium"`.

## Category match

Read `market-research/knowledge/modules.json`. For each module in `modules[]`:
- Concatenate `module + features + category` (lowercased).
- Compute a relevance score against the topic using keyword overlap.

Pick the top 1-2 modules whose categories the topic touches. Record the matched categories in the brief. If no module scores above 0 → `category_match = "implied"` or `"no-match"` with explicit reasoning recorded.

## Brand list assembly

```
proposed_brands = []

# 1. Modules DB seed (highest priority — partner names from snapshot)
for category in matched_categories:
    for module in modules.json where category in module.category:
        for partner in split(module.example_partners, ","):
            if partner not in ("", "None") and "‣" not in partner:
                add(partner, provenance="modules-db")

# 2. User --brands seed
for brand in user_seed_brands:
    add(brand, provenance="user-seed")

# 3. Learned-from-history (skill-suggested)
read ~/.claude/market-research/run-log.jsonl
for past run in matched category:
    if past run had brands not in modules.json AND those brands had status="full" in >70% of their prior appearances (≥5 prior runs in category required):
        add(brand, provenance="learned-from-history", note="strong signal in N prior runs")

# Deduplicate, cap at 15
```

For brands with ≥3 prior data points on the dimensions we're proposing now, add a "Strong on: <dim> (X/N)" or "Thin on: <dim> (X/N)" note to the brand's row. (Per spec Section 5 — Calibration 4.)

Note: If the matched categories have empty/marker-only example_partners in modules.json (e.g., "‣" placeholders that represent unresolved relations), the brand list will rely more heavily on the user's `--brands` seed. Surface this in the brief if proposed brand count is <3.

## Dimension extraction

**Branch A**:
- Read PRD's `# Scope of Work` section.
- Each bullet under `In scope` becomes a dimension candidate.
- Normalize to "comparable behaviors" — strip Thanx-specific implementation details.
- Cap at 6.

**Branch B**:
- Read `scoping-features.md` and `scoping-slack.md` outputs.
- Identify the top-cited friction points or unmet needs.
- Map each to a comparable behavior (e.g., "customers can't find which item qualifies" → dimension: "qualifying item disclosure").
- Cap at 6.

**Branch C**:
- From subject + verb, infer 4-6 dimensions in the verb's behavior space:
  - "Export" → formats, destinations, sync cadence, transformations
  - "Configure" → entry points, default values, validation, undo/redo
  - "Visualize" → chart types, drill-down depth, filter affordances, sharing/embedding

Then, if run-log has ≥5 prior runs with overlapping subject keywords, surface dimensions PMs accepted without edit in those prior runs as proposed candidates.

## Write the brief

Read `market-research/knowledge/brief-template.md`. Substitute placeholders with the values computed above. Write to `<session-dir>/research-brief.md`.

For Branch C, include the title-only warning banner at the top:
```
⚠ Title-only input. Dimensions inferred from "<title>" alone.
   Run on a PRD or feature request page for higher-quality dimensions.
```

---

# Checkpoint: User reviews the brief

Print a tight summary to the user:

```
✏️  Research brief ready: <session-dir>/research-brief.md

Category: <matched-categories> (<confidence>)
Visual relevance: <visual_relevance>
Brands (<N>): <comma-separated list of final brands>
Dimensions (<M>): <pipe-separated dimension names>

Type 'go' to run research, 'edit' to open the brief in $EDITOR, or paste 
corrections and I'll re-render the brief.
```

Then WAIT for user input. Handle three response patterns:

1. **`go` or empty input**: proceed to Phase 2.
2. **`edit`**: open the brief in `$EDITOR` (fallback: nano). Re-render the summary after the editor closes. Wait again.
3. **Inline corrections** (anything else): treat as PM feedback. Re-run dimension/brand assembly with the corrections applied (e.g., "drop Domino's, add Dutch Bros, change dimension 5 to 'reward stacking with promos'"). Re-render the brief on disk. Print the updated summary. Wait again.

Brief.md edit cycles: unlimited. No artificial cap.

---

# Phase 2: Research fan-out

Read the final brand list and dimensions from `<session-dir>/research-brief.md`.
Read `market-research/agents/brand-research.md`.

For each brand:
1. Pick the correct screenshot tier block (HIGH / MEDIUM / LOW) based on `visual_relevance`.
2. Substitute placeholders: `{{BRAND}}`, `{{TOPIC}}`, `{{VISUAL_RELEVANCE}}`, `{{SESSION_DIR}}`, `{{DIMENSIONS}}` (the numbered dimension list), `{{SCREENSHOT_TIER_BLOCK}}`.

Dispatch all per-brand agents in ONE Task tool message (parallel execution):

```
for brand in brands:
    Task(
        subagent_type="general-purpose",
        description=f"Research {brand}",
        allowed_tools=["Write", "Read", "WebSearch", "WebFetch",
                       "mcp__claude_ai_keystone__browser_navigate",
                       "mcp__claude_ai_keystone__browser_screenshot",
                       "mcp__claude_ai_keystone__browser_session_create",
                       "mcp__claude_ai_keystone__browser_session_close"],
        prompt=substituted_prompt,
    )
```

Cap 10 concurrent in the first batch. If brand_count > 10, after batch 1 completes, dispatch batch 2 with remaining brands. Single-message dispatch per batch.

Wait for all sub-agents to complete. Read their returned JSON status and consolidate.

## Failure handling

For each brand:
- **status: "failed"**: append to retry queue.
- **status: "partial"**: include in synthesis but mark with `~` prefix in the brand list.
- **status: "full"**: include without modification.

After the first batch returns, dispatch ONE retry batch for all failed brands. Second-failure brands are dropped from synthesis with a footnote in the final report.

If the entire first batch fails (likely a network outage or rate limit):
- Print a clear error to the user.
- Do NOT auto-retry.
- Preserve session state so the user can re-invoke on the same session ID later.

---

# Phase 3: Synthesis + Publish

## 3a. Run synthesis sub-agent

Read `market-research/agents/synthesis.md`. Substitute placeholders:
- `{{SESSION_DIR}}` — current run's session dir
- `{{TOPIC}}` — from brief
- `{{BRIEF_PATH}}` — `<session-dir>/research-brief.md`
- `{{PRD_INPUT}}` — "true" if input was a Notion URL, else "false"

Dispatch ONE general-purpose sub-agent with `allowed_tools: ["Write", "Read", "Glob"]`.

When the sub-agent returns, verify `<session-dir>/competitive-teardown.md` exists and is non-empty.

## 3b. Create the Notion page in the Market research database

Read `<session-dir>/competitive-teardown.md`.

Transform pipe tables to Notion `<table>` XML (Notion's enhanced-markdown spec requires this for rendering).

For each `![](screenshots/<brand>-<n>.png)` reference in the markdown:
1. Run the upload helper:
   ```bash
   bash ~/.claude/skills/upload-notion-image/upload.sh \
        <session-dir>/screenshots/<brand>-<n>.png \
        <new_page_id_once_created> \
        "<caption from markdown>"
   ```
   The helper returns a `file_upload_id` on stdout.
2. Replace the `![](path)` reference in the markdown body with `<image file_upload_id="..."/>` (Notion-native).

(Image uploads happen AFTER page creation since the helper needs the page ID. Strategy: create the page first with markdown image references pointing to placeholder URLs or omit those blocks initially; then upload images; then update the page content to swap in the file_upload_id references. Simpler alternative: create the page with text-only content first, then call the upload helper for each image which attaches as child blocks on the new page.)

Create the page:

```
mcp__claude_ai_Notion__notion-create-pages
  parent: {type: "data_source_id", data_source_id: "35da84ed-4024-8023-9f06-000be3f49b54"}
  pages: [{
    properties: {"Name": "Competitive landscape: <topic>"},
    icon: "🔭",
    content: <transformed markdown>
  }]
```

Capture the returned page URL.

## 3c. Update PRD's Additional Resources (PRD input only)

If `input.source == "notion-url"`:

Re-fetch the PRD page to find a unique anchor in the Additional Resources section (the section often already has bullets; appending requires matching the last bullet or the section heading uniquely).

Then update:

```
mcp__claude_ai_Notion__notion-update-page
  page_id: <PRD page id>
  command: "update_content"
  content_updates: [{
    old_str: "<unique anchor in Additional Resources>",
    new_str: "<unique anchor>\n- Competitive landscape: <mention-page url=\"<new page url>\">Competitive landscape: <topic></mention-page>"
  }]
```

If the update_content call fails to find a match (Additional Resources section missing or no unique anchor available), log the failure but do NOT block — the database page is still created and the markdown still exists locally. Surface the failure in the final report.

## 3d. Append run log entries

Write two entries:
1. `<session-dir>/run-log.jsonl` (session-local)
2. `~/.claude/market-research/run-log.jsonl` (global, append-only)

Entry schema (single JSONL line):

```json
{
  "run_id": "...",
  "timestamp": "<iso>",
  "input": {"source": "notion-url | string", "value": "..."},
  "user_seed_brands": [...],
  "branch": "A | B | title-only",
  "matched_categories": [...],
  "category_match_confidence": "direct | implied | no-match",
  "brand_list": {"proposed": [...], "user_edited": true|false, "final": [...]},
  "dimensions": {"proposed": [...], "user_edited": true|false, "final": [...]},
  "visual_relevance": "high | medium | low",
  "phase_2_outcomes": {
    "<brand>": {
      "status": "full | partial | failed",
      "dimensions": {"<dim-slug>": "evidence-found | could-not-verify", "...": "..."}
    }
  },
  "screenshot_outcomes": {"<brand>": {"tier_used": "1|2|3|null", "count": "N"}},
  "synthesis_patterns_emerged": [],
  "output": {"markdown_path": "...", "notion_page_url": "...", "prd_link_appended": true|false}
}
```

Mirror to `~/.claude/market-research/run-log.jsonl` (create parent dir if needed).

## 3e. Final report

Print to the user:

```
✓ Market research complete

Topic: <topic>
Brands researched: <N> (<full> full, <partial> partial: <list>, <failed> failed: <list>)
Dimensions: <M>
Patterns identified: <P> distinct + <A> anti-pattern(s)

Outputs:
  Markdown:  <session-dir>/competitive-teardown.md
  Notion:    <page url>
             (in Market research database)

<if input was a PRD URL:>
PRD link: <appended | failed to append - section anchor not found>

If this is research for a future PRD:
  Run /prd and paste the Notion page URL into the Phase 0 initial-context prompt.
  /prd's Phase 1 notion-research agent will surface the teardown findings during
  research, but won't bake the recommendations into the PRD body — keeping it as
  a reference, not a directive.

Run logged for future calibration.
```

---

# Error handling summary

- **Notion MCP disconnected**: STOP at health check. Print fix instructions.
- **Branch B scoping agents fail**: continue with whatever partial output exists; surface in brief.
- **Whole research batch fails**: pause, surface error, do not auto-retry. Preserve session.
- **Individual brand fails twice**: drop from synthesis with footnote.
- **Synthesis sub-agent fails**: re-dispatch ONCE; if still fails, write a fallback synthesis that's just the summary table + a note that pattern clustering couldn't complete.
- **Notion publish fails**: retry create-page ONCE; if second failure, surface error and point user at the local markdown. Session retains a `pending-publish` flag.
- **PRD Additional Resources update fails**: log it, continue. The page is still in the DB.
