# /research - Product Feature Research

Generate a structured research dossier for a product feature or topic area. Answers: "How does Thanx work today on this subject, and how does it fail customer needs and expectations?"

## Usage

```
/research <topic>
```

Example: `/research order status tracking`

## Process

### Step 1: Setup Session
1. Check if `research-sessions/<topic-slug>/` already exists — if so, note existing files (dossier.md, findings.md, etc.) so agents can build on prior research rather than starting from scratch
2. Create session directory if it doesn't exist: `research-sessions/<topic-slug>/`
3. Create `findings.md` in the session directory
4. Note the start time

### Step 2: Launch Parallel Research Agents

Launch ALL of these agents simultaneously using the Agent tool:

1. **Notion Product Guides** (`research-notion-guides`)
   - Search for product guides explaining current functionality related to the topic
   - Use `mcp__claude_ai_Notion__notion-search` with query about current product behavior

2. **Feature Requests** (`research-feature-requests`)
   - Search Notion for customer feature requests related to the topic
   - Look in the Features database for relevant requests with merchant advocacy data

3. **Adjacent PRDs** (`research-adjacent-prds`)
   - Search Notion for existing PRDs that touch this area
   - Check both high conviction and backlog PRDs
   - Note their status, scope, and any overlap

4. **Product Q&A** (`research-product-qa`)
   - Search Notion for product Q&A content, internal questions, and answers
   - Look for recurring questions that indicate gaps

5. **GitHub/Keystone** (`research-github-keystone`)
   - Search GitHub repos for technical implementation details
   - Look at relevant models, APIs, and data flows
   - Check Keystone for available context

6. **Jira** (`research-jira`)
   - Search Jira for related tickets, bugs, and planned work
   - Look for patterns in support tickets

7. **Data** (`research-data`)
   - Search for DBT models, data tables, and analytics related to the topic
   - Identify what data exists and what's missing
   - Note: may depend on GitHub agent findings for model names

### Step 3: Synthesize Findings

Once all agents report back, synthesize into a dossier with these sections:

```markdown
# Research Dossier: [Topic]
Date: [date]
Researcher: [Ask the user their name, or infer from conversation context]

## Current State
How Thanx works today on this subject. Include links to product guides and relevant code.

## Customer Pain Points
How it fails customer needs and expectations. Include feature request data (merchant count, ARR).

## Data Landscape
What data exists, what's tracked, what's missing. Include DBT model names and data sources.

## Adjacent Work
Related PRDs (with status), in-progress projects, and historical context.

## Technical Implementation
How it's built today. Key repos, models, APIs.

## Technical Debt & Related Bugs
Existing bugs, known quality issues, and tech debt that would affect or be affected by this initiative. Organize by subsystem (e.g., deep linking, location, app architecture, data quality).

Each subsystem table MUST include a "Jira" column:
- **Logged bugs**: Include the Jira ticket key (e.g., BUGS-3955, PLAT-3321)
- **Unlogged issues**: Mark as "Unlogged" with the source system where the issue was discovered in parentheses (e.g., "Unlogged (Notion: Smart Links guide)", "Unlogged (GitHub: thanx-breact)", "Unlogged (Snowflake: stg_nucleus tables)")

Table format per subsystem:
| Issue | Jira | Status | Filed | Impact |
|-------|------|--------|-------|--------|
| Description of bug/debt | BUGS-1234 or Unlogged (Source: detail) | Open/In Review/Done [date]/Resolved [date] | YYYY-MM-DD | What it affects |

**Bug date conventions:**
- Always include a "Filed" column with the date the ticket was created
- For resolved/done tickets, append the resolution date in brackets after the status (e.g., "Done [Mar 3]", "Resolved [Feb 19]")
- Fetch dates from Jira API when available

**Non-redundancy rule:** If bugs are already shown in investigation-specific sections (e.g., "Magic Link Login", "Campaign Delays"), do NOT repeat them in the Tech Debt section. The Tech Debt section should only contain systemic/cross-cutting issues not covered in other sections. Add a note: "> Bug tables for each area are in their respective investigation sections above."

To populate this: after all agents report back, search Jira (via JQL) for tickets matching each identified tech debt item. Cross-reference agent findings with Jira results to determine logged vs. unlogged status.

## Open Questions
Things that need further investigation — especially around data (how much does this happen? are people using it now?).

## Recommended Next Steps
What should happen next based on findings.
```

### Step 4: Publish

1. Save dossier to `research-sessions/<topic-slug>/dossier.md`

2. **Present findings and ask about publishing:**
   Present the key findings to the researcher as a summary, then ask:
   "Would you like me to publish this? Options:
   - **Notion + Slack** — publish to the Research Dossier database and post a summary to #product-managers-team
   - **Notion only** — publish to the Research Dossier database, no Slack post
   - **Skip** — keep it local only (saved in `research-sessions/`)"

   If the researcher chooses to skip, jump to Step 5.

3. **If publishing to Notion** (researcher chose Notion + Slack or Notion only):

   Ask about open questions: "Are there any open questions you want to highlight? These will be added to the dossier's Open Questions section. (Type 'none' to skip)"

   If the researcher provides questions:
   - Append them to the `## Open Questions` section of the dossier
   - Re-save `dossier.md` with the updated content

   Before writing content, fetch the Notion markdown spec via `ReadMcpResourceTool` with server `claude.ai Notion` and uri `notion://docs/enhanced-markdown-spec`. Tables must use `<table>` XML syntax, not markdown pipe tables.

   **Always create a NEW page in the database** using `mcp__claude_ai_Notion__notion-create-pages`:
   ```javascript
   {
     "parent": { "data_source_id": "2b3a9bbb-75ac-4cab-a9ce-c73d2a17d669" },
     "pages": [
       {
         "properties": {
           "Topic": "<research topic>",
           "date:Date:start": "<YYYY-MM-DD>",
           "Researcher": "<current-user-id>"
         },
         "content": "<full dossier in Notion-flavored markdown — use <table> XML syntax for tables, not pipe tables>"
       }
     ]
   }
   ```

   **Important:** The `data_source_id` is a plain UUID, not prefixed with `collection://`. The `Researcher` property is a plain string (user UUID), not an array.

   To get the current user ID:
   - Use `mcp__claude_ai_Notion__notion-get-users` with `query` matching the researcher's name
   - Look up the researcher dynamically — do NOT hardcode a user ID
   - Known IDs for reference (verify at runtime):
     - Erin Eastick: `2ced872b-594c-8139-a02f-00021e86d8ca`
     - Aaron Newton: look up via `notion-get-users` with query "Aaron"
     - Diana Dilanyan: look up via `notion-get-users` with query "Diana"

   **IMPORTANT — Do NOT search for and update an existing page.** Even when re-running research on an existing topic, always use `notion-create-pages` with the `data_source_id` parent above. This guarantees the page lands in the Research Dossier database, not in a private or orphaned location. If an older version of the dossier exists elsewhere, it can be archived manually.

   The response will include the new page URL — store this for the Slack post.

4. **If posting to Slack** (researcher chose Notion + Slack):
   Use the Slack post message tool to send to `#product-managers-team` (channel ID `C0AA8ANGBDM` — see operational-context.md):
   ```
   :microscope: New research dossier: *<Topic>*
   <one-sentence summary of key findings>
   <Notion URL>
   [If open questions exist: "Open questions needing input: <questions>"]
   Generated by my research agents
   ```

5. Output the Notion URL (if published) for reference

### Step 5: Improve
Remind the user they can run `/improve` to capture learnings from this session.

## Notes
- Each agent should return structured findings with source links
- The Data agent may need to wait for GitHub agent results to know what models to look for
- Commit session output to git after each research session
- **Notion table format:** Notion does not support markdown pipe tables. Use `<table header-row="true">` with plain `<tr>`/`<td>` — do NOT use `<thead>` or `<tbody>` (silently ignored, causes rows to collapse). Fetch the spec from `ReadMcpResourceTool` (server: `claude.ai Notion`, uri: `notion://docs/enhanced-markdown-spec`) before creating pages.

### MCP Tools in Subagents
Notion and Jira MCP tools are **consistently denied** in subagents. Plan for this:
1. Launch all agents in parallel as normal — the GitHub/Keystone agent (which uses `gh` via Bash) reliably works
2. When agents report MCP denials, run the critical Notion and Jira searches from the main session:
   - **Notion:** Run 3-5 `notion-search` queries covering product guides, feature requests, PRDs, and Q&A for the topic
   - **Jira:** Run 2-3 JQL queries covering bugs, stories, and recent completions
3. Merge main-session Notion/Jira results with whatever agents did find (existing session files, GitHub results) during synthesis
