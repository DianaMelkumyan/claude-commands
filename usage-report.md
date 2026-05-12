---
name: usage-report
description: Analyze Claude Code usage analytics - skill invocations, permission interruptions, and optimization recommendations. Use periodically to tune your workflow.
---

## Context

- Skill usage log: !{cat /Users/diana/conductor/workspaces/dAIna/analytics/skill-usage.jsonl 2>/dev/null | tail -500}
- Skill usage count: !{wc -l /Users/diana/conductor/workspaces/dAIna/analytics/skill-usage.jsonl 2>/dev/null | awk '{print $1}'}
- Permission requests log: !{cat /Users/diana/conductor/workspaces/dAIna/analytics/permission-requests.jsonl 2>/dev/null | tail -500}
- Permission requests count: !{wc -l /Users/diana/conductor/workspaces/dAIna/analytics/permission-requests.jsonl 2>/dev/null | awk '{print $1}'}

## Instructions

Analyze Claude Code usage data and recommend workflow optimizations. Produce a single report with three sections.

### Section 1: Skill Usage

If skill data exists (5+ entries):

1. **Frequency table** - skill name, total invocations, sorted descending
2. **Recency** - last used date for each skill
3. **Trend** - active / declining / abandoned (used early but stopped)

Present as a markdown table. Only flag skills as pruning candidates if they were invoked once AND last used more than 30 days ago. Single-use skills within the last 30 days are legitimate one-offs.

If fewer than 5 entries, say "Not enough skill data yet (N entries). Check back after a week of use."

### Section 2: Permission Interruptions

If permission data exists (5+ entries):

1. **Top interrupted tools** - tool name, count, sorted descending
2. **Patterns** - are the same tools repeatedly asking? Group by tool name.
3. **Actionable recommendations** - for each frequently interrupted tool, suggest one of:
   - Add to `permissions.allow` in settings.json (if safe and repetitive)
   - Add a glob-scoped allow rule (e.g., `Bash(git push:*)`)
   - Keep as-is (if the interruption is genuinely useful as a safety check)

Be conservative: only recommend allowing tools where the interruption pattern shows routine, safe operations. Never recommend allowing destructive commands.

If fewer than 5 entries, say "Not enough permission data yet (N entries). Check back after a week of use."

### Section 3: Quick Wins

Based on both datasets, list 1-3 concrete actions the user could take right now to reduce friction, with the exact settings.json change needed. Format as copy-pasteable JSON snippets.

### Tone

Keep it short. Tables over paragraphs. No filler.
