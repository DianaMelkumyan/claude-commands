# /market-research

Standalone market-research skill. Takes a PRD URL, feature request URL, or
plain topic string, runs a parallel multi-brand external research pass to learn
how leaders in the space (partners, competitors, and exemplars alike) handle the
behavior, and publishes results as a page in the [Market research database](https://www.notion.so/35da84ed40248070aedee942503090ca)
plus a durable local markdown file. When invoked on a PRD URL, the PRD's
`# Additional Resources` section gets a link to the new database entry — the
research becomes a relevant reference without being embedded as a subpage of
the PRD itself.

**Reference files** (loaded by this command at run time, paths relative to this file):
- `market-research/knowledge/modules.json` — Technical Partner Strategy snapshot (authoritative module/category map)
- `market-research/knowledge/brand-references.json` — curated brand list per category with iOS bundle IDs (consumer) or product-docs URLs (B2B)
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
/market-research <PRD url | feature request url | title string> [--brands "X, Y, Z"] [--output-dir <path>]
```

When `--output-dir <path>` is set, the skill writes a structured `result.json` to that directory at the end of the run (in addition to all existing artifacts). The result.json is the machine-readable contract consumed by orchestrators like `/accio`. When unset, only the existing session-dir artifacts are produced.

`--output-dir` is purely additive. It does NOT change any other behavior — in particular, **Notion publish (Phase 3b), run-log entries (Phase 3d), local markdown (3a), and PRD-Resources linking (3c, when input is a Notion URL) all run identically regardless of whether `--output-dir` is set.** There is no "machine mode" that skips publishing. Publishing IS the canonical artifact.

## Workflow overview

3 phases, no manual checkpoint — the brief summary prints before research kicks off; user can Ctrl+C if it looks wrong:

0. **MCP health check (~5s, cached)**: verify Notion connected; warn if not.
1. **Scoping (~30s–2min)**: parse input, run /prd internal scoping agents (Branch B only), match category from bundled modules.json, extract dimensions, write research-brief.md. Print summary.
2. **Research (~45–90s, parallel fan-out)**: launch 1 sub-agent per brand using `general-purpose` subagent type with explicit allowed_tools. Each writes findings-<brand>.md.
3. **Synthesis + publish (~30s)**: one synthesis sub-agent merges findings into market-landscape.md, then orchestrator creates a page in the Market research database and (when applicable) links it from the input PRD's Additional Resources.

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
- **`--output-dir <path>`**: record as `result_output_dir`. Will be used in Phase 3 to write `result.json`. Expand `~` to `$HOME` and make absolute.

**Capture `started_at` as an ISO 8601 UTC timestamp NOW** (e.g., `2026-05-11T14:30:00Z`). Initialize empty `decisions = []` and `signals = []` lists in memory — they accumulate throughout the run.

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

**Record a decision and signal for the branch choice:**
```
decisions.append({
  "type": "branch",
  "chose": "Branch A | B | C",
  "why": "<short reason — e.g., 'rich PRD with populated Scope and Problem' | 'PRD exists but Scope is thin' | 'title-only input, no PRD URL'>"
})
```
If Branch C: `signals.append("branch_c_title_only")`.
If Branch B: `signals.append("branch_b_partial_prd")`.

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

**Record category-match decision:**
```
decisions.append({
  "type": "category_match",
  "chose": "<matched-categories joined with ' + '>",
  "why": "<short reason: 'direct keyword overlap on X, Y' | 'implied from <signal>' | 'no direct match — chose <fallback> based on <reason>'>",
  "alternatives_considered": [<other categories that scored above 0 but weren't picked, if any>]
})
```
If confidence is "implied": `signals.append("category_match_implied")`.
If confidence is "no-match": `signals.append("category_match_none")`.

## Brand list assembly

```
proposed_brands = []

# 1. brand-references.json — curated per-category list (PRIMARY source)
# The matched_categories may include sub-categories under Operations 
# (e.g., "Operations - Feedback"). Match exact keys in brand-references.json.
read knowledge/brand-references.json
for category_key in matched_categories:
    for brand in brand_references.categories[category_key].consumer_brands:
        add(brand.name, provenance="brand-references", 
            bundle_id=brand.bundle_id, brand_type="consumer-app", note=brand.note)
    for brand in brand_references.categories[category_key].b2b_brands:
        add(brand.name, provenance="brand-references", 
            docs_url=brand.docs_url, brand_type="b2b", note=brand.note)

# 2. Modules DB seed (SECONDARY — only when brand-references has nothing for the category,
#    or to supplement partner names that aren't already covered)
for category in matched_categories:
    for module in modules.json where category in module.category:
        for partner in split(module.example_partners, ","):
            if partner not in ("", "None") and "‣" not in partner and partner not in proposed_brands:
                add(partner, provenance="modules-db")

# 3. User --brands seed
for brand in user_seed_brands:
    add(brand, provenance="user-seed")

# 4. Learned-from-history (skill-suggested)
read ~/.claude/market-research/run-log.jsonl
for past run in matched category:
    if past run had brands not in brand-references.json AND those brands had status="full" 
       in >70% of their prior appearances (≥5 prior runs in category required):
        add(brand, provenance="learned-from-history", note="strong signal in N prior runs")

# Deduplicate by name (case-insensitive), cap at 15
```

For brands with ≥3 prior data points on the dimensions we're proposing now, add a "Strong on: <dim> (X/N)" or "Thin on: <dim> (X/N)" note to the brand's row. (Per spec Section 5 — Calibration 4.)

Each entry in the brand list carries a **reference**: either `bundle_id` (consumer apps, used by per-brand agent for iTunes Search API tier 1) or `docs_url` (B2B brands, used as the per-brand agent's starting point for product-docs research). When both are null, the agent falls back to free-form web search at runtime.

**Record brand-list-scoping decision (always):**
```
decisions.append({
  "type": "brand_list",
  "chose": "<N> brands: <comma-separated names>",
  "why": "<short reason — e.g., 'modules-db seed (12) + user --brands (1) + learned-from-history (2), deduped, capped at 15'>"
})
```
If final brand count < 3: `signals.append("sparse_brand_list")`.

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

# Brief summary (no checkpoint — proceeds automatically)

After writing research-brief.md to disk, print a tight summary to the user and proceed immediately to Phase 2. No wait for input. The user can Ctrl+C if anything looks wrong before research kicks off (Phase 2 token-heavy work happens AFTER the summary prints).

```
Research brief written: <session-dir>/research-brief.md

Category: <matched-categories> (<confidence>)
Visual relevance: <visual_relevance>
Brands (<N>): <comma-separated list of final brands>
Dimensions (<M>): <pipe-separated dimension names>

Starting parallel research...
```

To rerun with different brands or dimensions, re-invoke `/market-research` with `--brands "..."` overrides, or edit research-brief.md in the session dir and re-invoke on the same session (resume-mode behavior; not a v1 hard requirement but the session dir is preserved either way).

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
- **status: "partial"**: include in synthesis but mark with `~` prefix in the brand list. `signals.append(f"brand_{slug(brand)}_partial")`.
- **status: "full"**: include without modification.

After the first batch returns, dispatch ONE retry batch for all failed brands. Second-failure brands are dropped from synthesis with a footnote in the final report. For each dropped brand: `signals.append(f"brand_{slug(brand)}_unreachable")`.

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

When the sub-agent returns, verify `<session-dir>/market-landscape.md` exists and is non-empty.

## 3b. Create the Notion page in the Market research database

**This step ALWAYS runs.** Publishing to the Market research database is the canonical artifact of /market-research — it is not gated by `--output-dir`, "machine mode", orchestrator invocation, or any other flag. The Notion page is the durable, shareable output; the result.json (3e) and local markdown (3a) are additive complements, not replacements. Skipping this step breaks /prd Phase 1 (notion-search) and /accio chain consumers that resolve the page by URL.

Do NOT introduce a `notion_publish_skipped_machine_mode` signal or any equivalent skip gate. If publish fails, surface the failure per the error-handling rules below — do not pre-emptively skip.

Read `<session-dir>/market-landscape.md`.

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
    properties: {"Name": "Market landscape: <topic>"},
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
    new_str: "<unique anchor>\n- Market landscape: <mention-page url=\"<new page url>\">Market landscape: <topic></mention-page>"
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

## 3e. (Optional) Write result.json for orchestrator consumption

This step runs ONLY when `result_output_dir` was provided via `--output-dir`. Skip entirely otherwise.

**Capture `completed_at` as an ISO 8601 UTC timestamp NOW.**

**Determine overall status:**
- `status = "ok"` if synthesis succeeded and ≥80% of brands returned `full`.
- `status = "warn"` if any of: synthesis_partial signal set, any brand_unreachable signal, any brand_partial signal, sparse_brand_list signal, category_match_implied or category_match_none signal, or notion publish degraded but markdown produced.
- `status = "error"` if synthesis failed entirely OR notion publish failed AND no usable markdown exists.

**Compute `confidence` (float 0-1):**
Start at 1.0. Subtract:
- Branch C: -0.25
- Branch B: -0.10
- Category match "implied": -0.10
- Category match "no-match": -0.20
- Each failed brand: -0.05 (cap total brand-failure deduction at -0.30)
- Each partial brand: -0.02 (cap total at -0.10)
- `synthesis_partial` signal: -0.15
- `sparse_brand_list` signal: -0.10

Clamp to [0, 1]. Round to 2 decimal places.

**Add synthesis-weighting decision if synthesis grouped brands into patterns:**
```
decisions.append({
  "type": "synthesis_weighting",
  "chose": "<N> distinct patterns + <M> one-off observations + <K> anti-patterns",
  "why": "<one-line rationale — e.g., 'majority pattern (Pattern A: wallet-claim) appeared in 7/12 brands; anti-pattern surfaced in 3 brands'>"
})
```
If synthesis returned partial output (could not fully cluster), `signals.append("synthesis_partial")`.

**Build the result.json payload:**

```json
{
  "stage": "market_research",
  "status": "<computed status>",
  "signals": <the accumulated signals list, deduplicated>,
  "started_at": "<captured at Phase 0>",
  "completed_at": "<captured above>",
  "artifacts": [
    {"path": "<session-dir>/market-landscape.md", "kind": "markdown"},
    {"path": "<session-dir>/research-brief.md", "kind": "markdown"},
    {"path": "<session-dir>/run-log.jsonl", "kind": "json"}
    // Add findings-<brand>.md files (kind: "markdown")
    // Add scoping-features.md / scoping-slack.md if Branch B (kind: "markdown")
    // Add screenshots/* if any (kind: "screenshot")
  ],
  "decisions": <the accumulated decisions list>,
  "confidence": <computed confidence>,
  "notion_page_url": "<the published page url from Phase 3b — always set on successful publish; null ONLY if the Notion create-pages call failed after retry. Never null due to mode/--output-dir; 3b is unconditional>",
  "branch": "<A | B | C>"
}
```

**Validate before writing:**

```bash
# Write to a temp file first
TMP_RESULT=$(mktemp)
echo '<the json payload>' > "$TMP_RESULT"

# Validate
python3 /Users/diana/conductor/workspaces/dAIna/claude-commands/market-research/scripts/validate-result.py "$TMP_RESULT"
```

If the validator exits non-zero: **FAIL LOUD**. Print the validator's stderr output to the user, do NOT write the file to `result_output_dir`, and exit with an error. This protects orchestrators downstream from receiving malformed contracts.

If valid: move the temp file to `<result_output_dir>/result.json`. Create parent directory if needed.

## 3f. Final report

Print to the user:

```
✓ Market research complete

Topic: <topic>
Brands researched: <N> (<full> full, <partial> partial: <list>, <failed> failed: <list>)
Dimensions: <M>
Patterns identified: <P> distinct + <A> anti-pattern(s)

Outputs:
  Markdown:  <session-dir>/market-landscape.md
  Notion:    <page url>
             (in Market research database)
<if --output-dir was set:>
  Result:    <result_output_dir>/result.json (schema: market_research, status: <status>, confidence: <conf>)

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
