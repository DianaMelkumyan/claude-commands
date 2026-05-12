---
name: theme-populate-prds
description: Find PRDs from the Projects database that match a Discovery Theme's scope, recommend per-PRD actions (add / move / share / leave), and update the theme's `⏩ Projects` relation after PM approval. Trigger when asked to find or populate PRDs for a theme, or invoked as /theme-populate-prds with a theme URL or name.
---

# /theme-populate-prds

Populate the `⏩ Projects` relation on a Discovery Theme page. Inverse of `/theme-opportunity` and `/theme-customer-voice`: those operate on themes that already have PRDs linked. This skill is the upstream step that gets PRDs onto themes in the first place.

## Context

- Discovery Themes data source: `collection://348a84ed-4024-801f-a259-000bf6d220bd`
- Projects (PRDs) database: `6bac395d-649c-4fb9-8e7a-31b56f7a38ae`. Reference view (for humans): `https://www.notion.so/thanxwiki/6bac395d649c4fb98e7a31b56f7a38ae?v=357a84ed4024808a84d3000cd300494d`. The view excludes PRDs past discovery and removed PRDs - the skill replicates these filters in code (see Step 5).
- View filters as of 2026-05-07 (the skill replicates these via the Keystone API; if the view filters change in Notion, update the skill):
  - `Status` is not in: `(0) Done`, `(1) Rolling Out`, `(1.5) Coming soon`, `(2) In Progress`, `(2.5) Technical discovery`, `(3) Planned`
  - `Discovery` is not in: `Removed (completed before/no longer relevant)`, `Removed (updated)`, `Removed (dropped)`
- Projects DB property types (verified 2026-05-07): `Status` is type `select`, `Discovery` is type `status`. They are not symmetric. Using the wrong filter operator returns `database property select does not match filter status`.
- Theme ↔ PRD relation: theme `⏩ Projects` ↔ PRD `Discovery Theme`. Multi-select on both sides. A PRD belonging to more than one theme is treated as an exception, not a default.
- Sibling section-skills: `/theme-opportunity`, `/theme-customer-voice`. This skill is designed to run on its own or under a future `/theme` orchestrator.
- My Notion user ID: `713e97f8-e2f5-4bba-9d96-bd0ccb7b6133`

## Input

Argument is a Discovery Theme URL or name (e.g. "Loyalty transitions").

If no argument is provided, ask the user which theme to populate, then proceed.

## Instructions

### Step 1: Resolve the theme

- If the input is a Notion URL, extract the page ID.
- If the input is a name, search the Discovery Themes data source and confirm the match with the user before proceeding. If multiple matches exist, list them and ask the user to pick.

### Step 2: Fetch the theme page

Use `mcp__claude_ai_Notion__notion-fetch`. Capture:

- Theme title
- `Status`, `Signal Clarity` properties
- The list of URLs already in the `⏩ Projects` relation (so they can be marked "already linked, untouched" later)
- Any body content (Opportunity, notes) - usually empty for a new theme, but if present it informs interpretation generation

Show the user what was pulled from the page before proceeding to Step 3, so they can see whether interpretation is grounded in name only or in name + page content.

### Step 3: Generate scope interpretations

From the theme name and any captured page content, produce 3-6 plausible scope interpretations of what the theme could cover. Present as a numbered list. If the theme name is unambiguous, a single interpretation is acceptable. If it remains ambiguous after reading the page, ask the user for clarification before generating.

Example for "Loyalty transitions":

```
1. Transition between loyalty providers (vendor switching)
2. Transition between earning mechanisms (visit-based to spend-based)
3. Cross-brand transitions (multi-brand / multi-merchant)
4. Internal operations transitions
5. External-facing customer transitions
```

### Step 4: User refines scope

User picks which interpretations apply (e.g. "1, 2, and 4"). Skill records the picked subset. If the user says none of the interpretations match, ask for their own description before continuing.

### Step 5: Fetch the candidate universe

Query the Projects database via `mcp__claude_ai_keystone__notion_query_database` with the database ID and the filter object below. Iterate `start_cursor` until `has_more: false` to enumerate the full universe - the database has more than 100 rows and the claude.ai Notion `notion-query-database-view` tool does not expose a pagination cursor, so it cannot be used for this step. **No body reads at this step.**

Why Keystone rather than the claude.ai Notion MCP:
- claude.ai Notion's `notion-query-database-view` returns at most 100 rows with `has_more: true` and no cursor. There is no native escape hatch.
- Keystone's `notion_query_database` is read-only (fine for Step 5) and supports `start_cursor` pagination + a `filter` object.
- Writes in Step 11 still use the claude.ai Notion MCP. Keystone is read-only and per global instructions claude.ai Notion is preferred for writes.

Filter object (replicates the human-facing view filter):

```json
{
  "and": [
    {"property": "Status", "select": {"does_not_equal": "(0) Done"}},
    {"property": "Status", "select": {"does_not_equal": "(1) Rolling Out"}},
    {"property": "Status", "select": {"does_not_equal": "(1.5) Coming soon"}},
    {"property": "Status", "select": {"does_not_equal": "(2) In Progress"}},
    {"property": "Status", "select": {"does_not_equal": "(2.5) Technical discovery"}},
    {"property": "Status", "select": {"does_not_equal": "(3) Planned"}},
    {"property": "Discovery", "status": {"does_not_equal": "Removed (completed before/no longer relevant)"}},
    {"property": "Discovery", "status": {"does_not_equal": "Removed (updated)"}},
    {"property": "Discovery", "status": {"does_not_equal": "Removed (dropped)"}}
  ]
}
```

Note the operator types: `Status` uses `select`, `Discovery` uses `status`. See "Context" above. If a query call returns `database property X does not match filter Y`, `Could not find property`, or `Invalid value`, call `mcp__claude_ai_keystone__notion_get_database` against the Projects database to inspect the current `Status` and `Discovery` property types and option names, surface the mismatch to the user, and update this skill before continuing. Do not silently drop the offending filter.

**Pagination via dumped-file extraction.** Each Projects DB row from Keystone is ~6 KB (full property objects with all option metadata). Even `page_size: 10` exceeds the tool output budget for this DB, so Keystone always dumps the response to a file under `tool-results/` and returns an error of the form `Output has been saved to <path>`. Use this path - never try to read the dumped file's JSON directly into context.

Per-page procedure:

1. Call `notion_query_database` with `database_id`, the filter object above, and `page_size: 100`. (`start_cursor` is omitted on the first call; on subsequent calls, pass the previous page's `next_cursor`.)
2. Capture the dumped file path from the tool's error message (the path after `Output has been saved to`).
3. Run the extractor below via Bash, passing the dump path. The extractor's stdout is a compact JSON object `{rows: [...], has_more: bool, next_cursor: str|null}` that fits in context. Parse it.
4. Append the page's `rows` to the running candidate-universe list.
5. If `has_more: true`, repeat from step 1 with `start_cursor: <next_cursor>`. Stop when `has_more: false`.

Extractor (run via Bash on each dumped file - do not inline the raw JSON):

```bash
python3 - "$DUMP_PATH" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
inner = json.loads(data[0]["text"])
def title(p):
    arr = (p.get("Name") or {}).get("title", [])
    return "".join(t.get("plain_text", "") for t in arr)
def status_or_select(p, key):
    v = p.get(key)
    if not v: return None
    if v.get("type") == "status": return (v.get("status") or {}).get("name")
    if v.get("type") == "select": return (v.get("select") or {}).get("name")
    return None
def relation_ids(p, key):
    v = p.get(key) or {}
    return [r["id"] for r in v.get("relation", [])]
out = []
for r in inner["rows"]:
    p = r["properties"]
    out.append({
        "id": r["id"],
        "title": title(p),
        "discovery": status_or_select(p, "Discovery"),
        "product_team_workflow": status_or_select(p, "Product team workflow"),
        "discovery_theme_ids": relation_ids(p, "Discovery Theme"),
    })
print(json.dumps({"rows": out, "has_more": inner["has_more"], "next_cursor": inner.get("next_cursor")}))
PY
```

The extractor emits exactly the fields Step 6 onward needs: `id`, `title`, `discovery`, `product_team_workflow`, `discovery_theme_ids`. **Do not `cat` the dumped file into context** - only the extractor's compact stdout is loaded.

If a future Keystone call ever returns the response inline (narrower filter that fits under the budget), the same row shape applies - parse the inline JSON identically.

**Important caveat: `discovery_theme_ids` from Keystone is unreliable.** As of 2026-05-07, Keystone's `notion_query_database` returns `"relation": []` for `Discovery Theme` on rows that demonstrably have the relation populated (verified via `notion-fetch`). Treat the value extracted in Step 5 as a soft hint only. The authoritative source for each candidate's current themes is the `Discovery Theme` field in the Step 7 `notion-fetch` body read - capture it there and use it (not the Step 5 value) to drive the `add` / `move` / `share` / `leave` decision in Step 9.

Validation gates (fail loudly with a clear message if any trip):

- Query returned 0 rows across all pages: stop, tell the user the query returned no candidates.
- Required properties missing from row shape (Title, `Discovery Theme`): stop, name the missing properties.
- Pagination did not terminate within 20 pages: stop, surface the page count - the database is unexpectedly large.
- Tool output contains neither inline rows nor a dump-file path: stop, surface the raw error - Keystone's response format may have changed.

### Step 6: Two-pass narrowing

- **Pass A (Notion search):** for each picked interpretation, derive 1-3 keyword phrases from the interpretation text. Run `mcp__claude_ai_Notion__notion-search` for each phrase. Collect hits, intersected with the candidate universe from Step 5 (so off-view results are dropped).
- **Pass B (title sweep over the universe):** scan all candidate-universe rows' titles for relevance to the picked interpretations. Cheap (no body reads). Catches PRDs whose phrasing doesn't match Notion search keywords but whose title is on-topic.
- Merge Pass A and Pass B into a deduped candidate set.

### Step 7: Body reads on the merged set

Fetch full bodies in parallel (one `mcp__claude_ai_Notion__notion-fetch` per PRD, batched in a single message). Capture Background, Problem, Success / Outcome sections.

Also capture the `Discovery Theme` value from each fetched body's `<properties>` block. `notion-fetch` returns this as a list of theme page URLs. This is the authoritative `currently_on` value used by Step 9 (action recommendation) and Step 12 (calibration log) - it overrides whatever Step 5 reported. See "Important caveat" in Step 5.

### Step 8: Score and bucket

For each candidate, judge match strength against the picked interpretations using title + body. Assign one of three confidence buckets:

- **High** - the PRD's primary problem is one of the picked interpretations. Strong fit, no stretch needed.
- **Medium** - touches a picked interpretation but has a different primary frame, or matches one interpretation strongly while orthogonal to others.
- **Low** - tangential or speculative match. Surfaced for awareness, not strongly recommended.

Capture a one-line `confidence_reason` per PRD. If you cannot score a PRD because the body is too thin or ambiguous, ask the user for context rather than guessing silently.

### Step 9: Recommend per-PRD action

For each candidate, recommend one action based on its current `Discovery Theme` value:

- **Orphan PRD** (no current theme): recommend `add`.
- **Already-themed PRD**: recommend one of `move` / `share` / `leave` based on contextual judgment of the new theme title vs. the current theme(s) and the PRD's content. `share` is the exception, not the default. Capture a one-line `action_reason` per PRD.

### Step 10: Present picks for bulk approval

Numbered list, sorted within each confidence bucket:

```
Recommended PRDs for "<theme name>":

High confidence:
  1. <PRD title>            [orphan]                   → add
     why: <one-line reasoning>
  2. <PRD title>            [on: <other theme>]        → move
     why: <one-line reasoning>
  3. <PRD title>            [on: <theme A>, <theme B>] → share
     why: <one-line reasoning>

Medium confidence:
  4. <PRD title>            [orphan]                   → add
     why: <one-line reasoning>
  5. <PRD title>            [on: <other theme>]        → leave
     why: <one-line reasoning>

Low confidence:
  6. <PRD title>            [orphan]                   → add
     why: <one-line reasoning>

Already linked to "<theme name>" (untouched, for context):
  - <PRD title>
  - <PRD title>

Anything I missed? Approve all, or override (e.g. "skip 6, move 5, rest as-is").
```

User responds with one terse instruction. Apply the overrides, restate the final write plan once, and write only after the user confirms.

If the user mentions a PRD the skill missed (e.g. "you missed 'Loyalty receipt scan'"), resolve the title to a page in the Projects database, apply the user's chosen action for it, and log it as a `confidence: missed` row.

### Step 11: Write to Notion

For each PRD in the approved set, update its `Discovery Theme` relation via `mcp__claude_ai_Notion__notion-update-page`:

- `add` - append the new theme to the PRD's `Discovery Theme`. Used for orphans.
- `move` - replace ALL existing `Discovery Theme` values with the new theme. If the PRD was on multiple themes, all are removed. To preserve an existing theme alongside the new one, the user should pick `share` instead.
- `share` - append the new theme alongside the PRD's existing `Discovery Theme` values (the multi-theme exception).
- `leave` and `skip` - no write.

After writes complete, re-fetch the theme page to confirm the `⏩ Projects` relation reflects the changes. Reply with the link to the updated theme page and a short summary of what changed.

If a write fails for a specific PRD, surface the failure in the output and do not append a calibration log line for that PRD.

### Step 12: Append calibration log

Append one JSONL line per PRD (recommended or missed) to `theme/.claude/skills/theme-populate-prds/calibration.log` (create the file if it does not exist). Use the Bash tool with a redirected echo, or the equivalent file-append primitive. **The skill must not read the log during normal operation.**

Row shape:

```json
{
  "date": "YYYY-MM-DD",
  "theme": {"id": "<page-id>", "name": "<theme name>"},
  "interpretations_offered": ["<scope a>", "<scope b>", "<scope c>"],
  "interpretations_picked": ["<scope a>", "<scope c>"],
  "prd": {"id": "<page-id>", "title": "<prd title>"},
  "currently_on": [{"id": "<theme-id>", "name": "<theme name>"}],
  "skill": {
    "confidence": "high|med|low|missed",
    "confidence_reason": "<one-line>",
    "action": "add|move|share|leave|none",
    "action_reason": "<one-line>"
  },
  "user": {
    "action": "add|move|share|leave|skip",
    "reason": "<optional, only if user volunteered in their override message>"
  },
  "agreement": true
}
```

Field rules:

- `agreement = (skill.action == user.action)`. Always `false` for `confidence: missed` (where `skill.action: "none"`).
- `confidence: "missed"` is the row shape for PRDs the user added at approval time that the skill did not recommend.
- `user.reason` is only populated if the user volunteered a reason in their override message. Do not prompt for it.
- `currently_on` is the PRD's `Discovery Theme` value at the START of the run (before any writes). Empty array for orphans.

## Validation gates (summary)

- Step 1: theme not found or ambiguous - ask the user to disambiguate.
- Step 5: query returned 0 rows across all pages - stop, surface the empty result.
- Step 5: filter property/value mismatch (schema drift) - stop, inspect the current schema via `notion_get_database`, surface to user.
- Step 5: query rows missing required properties (Title, Discovery Theme) - stop, name the missing properties.
- Step 5: pagination didn't terminate within 20 pages - stop, surface the page count.
- Step 7: PRD body fetch fails for one row - log the failure, exclude from scoring, continue with the rest.
- Step 11: write fails for one PRD - tell the user which PRDs failed; do not append calibration log lines for failed writes.

## Tone / discipline rules

- Reasoning lines (`confidence_reason`, `action_reason`) are one line each. They are tuning signal, not exec prose.
- Never fabricate PRDs. Every recommendation is a real Notion page from the candidate universe.
- Never silently mutate. Every write happens after explicit user approval. The user's bulk-approval instruction is the consent gate; the skill restates the final write plan once before writing.
- Action recommendations are contextual judgments, not hardcoded defaults. The skill explains its reasoning for each.
- If the skill needs additional context to disambiguate the theme or score a specific PRD, ask the user. Do not lean on properties outside the design and do not guess silently.
- Never use em dashes. Use regular dashes (-), commas, or rewrite the sentence.

## Run log emission

When invoked from the `/theme` orchestrator, the dispatch prompt provides a `run_dir` path. Write a run log to `<run_dir>/populate.md` after the relation update completes (or after the user declines/cancels).

When invoked directly (no `run_dir` provided), generate a one-section run dir at `.context/theme-runs/<theme-slug>-<timestamp>/` and write `populate.md` there. Theme-slug is the lowercased theme name with non-alphanumerics replaced by hyphens (e.g. "In-store loyalty foundations" -> "in-store-loyalty-foundations"). Timestamp is `YYYYMMDD-HHMMSS` UTC.

**Behavior is unchanged otherwise** - populate continues to recommend, ask for PM approval, and update relations interactively in both orchestrated and direct modes.

**Run log shape (`<run_dir>/populate.md`):**

```markdown
# theme-populate-prds run log

- **Theme:** <theme name>
- **Notion URL:** <theme page URL>
- **Run timestamp:** <ISO 8601>
- **Mode:** orchestrated | direct

## Inputs

- Initial linked PRD count: <N>
- Search criteria used: <theme name terms, scope keywords, exclusions>
- Candidate pool size: <N candidates from Projects database>

## Recommendations

| PRD | Action recommended | Action taken | Rationale |
|---|---|---|---|
| <PRD title> | add / move / share / leave | accepted / declined | <one-liner> |
| ... | ... | ... | ... |

## Final state

- Linked PRDs after run: <N>
- PRDs added: <list>
- PRDs declined: <list>

## Wrote to

- Theme `⏩ Projects` relation updated, or "no relation update (user declined all recommendations)"
```

If invoked from the orchestrator: do **not** append to `INDEX.md` (orchestrator owns the index write).

If invoked directly: append a single-section row to `.context/theme-runs/INDEX.md` (see `theme/.claude/commands/theme.md` "INDEX.md format and append rules" for the format).

## Direct-invoke INDEX.md append

When invoked **directly** (not from `/theme` orchestrator), after writing the run log:

1. Compute INDEX path: `<repo_root>/.context/theme-runs/INDEX.md`.
2. If the file does not exist, create it with the header (see `theme/.claude/commands/theme.md` "INDEX.md format and append rules").
3. Append a single row covering this populate run:
   - `Theme`: `<theme_name>`
   - `URL`: `<theme_url>`
   - `Run dir`: `<theme-slug>-<timestamp>` (relative)
   - `Timestamp`: ISO 8601 UTC
   - `Sections`: `populate:done` (if relation was updated) or `populate:declined` (if user declined all recommendations)
   - `Last tweaked`: `-`

When invoked from the orchestrator (orchestrated mode), do **not** append - the orchestrator owns the row write.

## Notes for parallel orchestration

This skill is designed to run on its own or in parallel with sibling section-skills under a future `/theme` orchestrator. To support that:

- Single theme per invocation, identified by argument.
- No dependency on prior conversation turns.
- Writes only to PRDs' `Discovery Theme` relation (and reciprocally the theme's `⏩ Projects`). Does not modify any other theme section.
- Approved picks plus reasoning trail are self-contained output the orchestrator can capture and log.
