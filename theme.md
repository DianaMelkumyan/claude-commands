---
description: Orchestrate the three section workflows (Opportunity, Customer voice, Decision factors) for a Discovery Theme page in Notion. Front-loads PRD-count gate and optional populate, then runs sections in parallel with auto-write to Notion. Run logs persist to .context/theme-runs/ for follow-up tweaks.
---

# /theme

Coordinate the three section-drafting skills against a Discovery Theme page in Notion: resolve the theme, optionally run `theme-populate-prds`, then dispatch `theme-opportunity`, `theme-customer-voice`, and `theme-decision-factors` in parallel under orchestrated mode. Each sub-agent drafts and (if status is `ok`) writes its section to Notion. Reasoning trails persist to per-run MD files in `.context/theme-runs/<theme-slug>-<timestamp>/` so future Claude sessions can answer follow-up tweaks without re-fetching.

## Input

Argument is a Discovery Theme URL or name (e.g. "In-store loyalty foundations").

If no argument is provided, ask which theme to fill out, then proceed.

## Phase 1: Front-loaded (interactive)

### Step 1: Resolve the theme

If the input is a Notion URL, extract the page ID. Otherwise, look up the name against the Discovery Themes data source (`collection://348a84ed-4024-801f-a259-000bf6d220bd`). If ambiguous (multiple matches), ask which one. Capture:

- `theme_id`: Notion page ID
- `theme_name`: human-readable name
- `theme_url`: Notion page URL
- `theme_slug`: lowercased theme name with non-alphanumerics replaced by hyphens (e.g. "In-store loyalty foundations" → "in-store-loyalty-foundations")

### Step 2: Count linked PRDs

Fetch the theme page and count its `⏩ Projects` relation entries. **Raw count** - do not filter by `Product team workflow` status. Archived PRDs count toward the 5.

### Step 3: Compute run directory

Compute the run directory path:

```
<repo_root>/.context/theme-runs/<theme_slug>-<YYYYMMDD-HHMMSS-UTC>/
```

Create the directory. The orchestrator and all sub-agents write to this same directory.

### Step 4: PRD-count gate

If count < 5, ask the user:

> This theme has N linked PRDs. Want to run `/theme-populate-prds` first to find more before drafting?

- If yes: invoke the `theme-populate-prds` skill via the Skill tool. It runs its own interactive recommend-and-approve flow. Pass through the `run_dir` (computed in Step 3) so populate writes its log to the same run directory. After populate returns, proceed automatically to Phase 2 regardless of the new PRD count.
- If no: proceed to Phase 2.

If count ≥ 5, skip the gate and proceed.

## Phase 2: Parallel drafting + write + log (non-interactive)

### Step 5: Dispatch three sub-agents in parallel

Use the Agent tool to spawn three sub-agents in a single message (parallel execution). Each gets a dispatch prompt that:

- Names the skill to invoke (`theme-opportunity`, `theme-customer-voice`, or `theme-decision-factors`).
- Provides `theme_id`, `theme_name`, `theme_url`, `run_dir`.
- Includes the literal phrase `ORCHESTRATED MODE`.
- Explicitly instructs: do not present a draft in chat, do not ask the user any questions, write the run log to `<run_dir>/<section>.md`, conditionally write to Notion based on status, return the structured payload `{status, section, written_to_notion, run_log_path, one_line_summary, caveats}`.

**Dispatch prompt template (per sub-agent):**

```
Invoke the <skill-name> skill in ORCHESTRATED MODE.

Theme: <theme_name>
Theme ID: <theme_id>
Theme URL: <theme_url>
Run dir: <run_dir>

ORCHESTRATED MODE instructions:
- Do not present a draft in chat. Do not ask the user any questions.
- Run your full drafting logic.
- Write your run log to <run_dir>/<section>.md (see your skill's "Run log shape").
- If status == "ok": write your section to the Notion theme page, then re-fetch and verify the new content is observed before reporting written_to_notion=true. If verification fails, retry the write once; if still failing, return written_to_notion=false with a [WRITE_VERIFY_FAILED] caveat.
- If status != "ok": do not write to Notion.
- Do not append to INDEX.md (orchestrator handles).
- Return the structured payload: {status, section, written_to_notion, run_log_path, one_line_summary, caveats}.
```

Sub-agents do not interact with the user during this phase.

### Step 6: Collect returns

Wait for all three sub-agents to return their structured payloads. Collect them in a fixed order (opportunity, customer-voice, decision-factors).

If a sub-agent fails to return a structured payload (raw error, timeout, malformed response), treat its result as `{status: "failed", section: <expected>, written_to_notion: false, run_log_path: null, one_line_summary: "Sub-agent did not return structured payload", caveats: ["dispatch failure"]}`.

## Phase 3: Finalize

### Step 7: Write orchestrator index file

Write `<run_dir>/orchestrator.md`:

```markdown
# /theme run log (orchestrator index)

- **Theme:** <theme_name>
- **Notion URL:** <theme_url>
- **Run timestamp:** <ISO 8601>
- **Populate:** ran / skipped / declined
- **PRD count:** <pre-run> → <post-run> (if populate ran; else just current count)

## Sections

| Section | Status | Wrote to Notion | Summary | Run log |
|---|---|---|---|---|
| Opportunity | <status> | <yes/no> | <one_line_summary> | opportunity.md |
| Customer voice | <status> | <yes/no> | <one_line_summary> | customer-voice.md |
| Decision factors | <status> | <yes/no> | <one_line_summary> | decision-factors.md |

## Caveats

<concatenate any caveats from sub-agent payloads, by section. Empty if none.>

## Theme page

<Notion URL>
```

### Step 8: Append to `.context/theme-runs/INDEX.md`

Append a single row covering this run. See the "INDEX.md format and append rules" section below for the index format and append behavior (create file with header if it doesn't exist).

### Step 9: Return summary to chat

Reply with:

- The Notion theme page link (always).
- A per-section line: `Opportunity: ok / wrote to Notion`, `Customer voice: caveat / not written - <one_line_summary>`, etc.
- The run directory path.

End the run. Do not ask the user any further questions - they review on Notion.

## Failure modes

- **All three sub-agents fail:** still write the orchestrator index file documenting failure, but write nothing to Notion. Surface all three failures in chat.
- **Theme resolution fails:** stay in resolution loop until valid theme provided or user aborts. Do not create a run dir.
- **Populate fails or is cancelled:** continue to Phase 2 with the existing PRD set. Populate's run log captures whatever happened.
- **`.context/` directory not writable:** report the path and the OS error to the user, abort. Do not write to Notion if logs cannot be persisted (consistency: every Notion write should have a corresponding log).

## Tweak loop

After the run, if the user comes back in any future Claude session against the same local repo checkout and asks "tweak X for theme Y" or "where did this come from?":

1. Read `.context/theme-runs/INDEX.md` to find the latest run for theme Y.
2. Read the relevant per-section log from that run dir.
3. Apply the requested tweak using cached context (sources, exclusions, queries) without re-fetching upstream PRDs unless the tweak requires fresh data.
4. **Re-fetch the Notion theme page immediately before each `update_content` write.** The PM may have hand-edited the page in Notion between session-start and now (typos fixed, smart-quote chars introduced, sections rewritten). `update_content` requires `old_str` to match the *current* page byte-for-byte; cached fetches from earlier in the session will fail validation against concurrent edits. Match `old_str` against the just-fetched content, not against what the run log said the page used to contain. Preserve any concurrent PM edits that don't conflict with the tweak.
5. Write the revised content to Notion.
6. Optionally append a `tweak-<timestamp>.md` to the run dir documenting what changed and why. Update the `Last tweaked` cell in INDEX.md.

This loop is informal - no separate skill, just Claude reading the file and doing what's asked.

## INDEX.md format and append rules

`.context/theme-runs/INDEX.md` is the cross-run discovery file. A future Claude session reads it first to find the right run dir for a tweak request.

**File header (created on first run if not present):**

```markdown
# Theme runs index

Append-only log of `/theme` and direct-invoke section runs. Read this file first when answering "tweak X for theme Y" requests in a future session.

| Theme | URL | Run dir | Timestamp | Sections | Last tweaked |
|---|---|---|---|---|---|
```

**Append rules:**

- **`/theme` orchestrator runs:** append one row after Phase 3 Step 7 (orchestrator.md written). The `Sections` cell lists all three sections with status (e.g. `opp:ok, voice:ok, factors:caveat`).
- **Direct-invoke section runs (`/theme-opportunity` etc. without orchestrator):** the section skill appends one row after writing its run log. The `Sections` cell lists only that one section (e.g. `factors:ok`).
- **Direct-invoke `/theme-populate-prds`:** appends a row with `Sections` = `populate:done` (or `populate:declined` if user declined).
- **Tweak operations:** locate the matching row by theme URL + run dir, update only the `Last tweaked` cell with the current ISO 8601 timestamp.

**Concurrency:** the orchestrator writes its row only after all sub-agents finish (single writer). Direct-invoke runs are single-agent. Two simultaneous direct invocations against the same INDEX.md are theoretically possible but unlikely - the file is append-only and the worst case is interleaved rows, which is recoverable. No locking needed for V1.

**Row content:**

- `Theme`: human-readable theme name.
- `URL`: Notion theme page URL (this is the canonical identifier for tweak lookups).
- `Run dir`: relative path from `.context/theme-runs/` to the run directory (e.g. `in-store-loyalty-foundations-20260506-141422`).
- `Timestamp`: ISO 8601 UTC of the run start.
- `Sections`: comma-separated `<short-name>:<status>` pairs.
- `Last tweaked`: ISO 8601 UTC of the most recent tweak operation, or `-` if never tweaked.
