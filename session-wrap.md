---
name: session-wrap
description: End-of-session routine that runs handoff, improve, then commits and pushes all changes to GitHub.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, Agent
---

# Session Wrap

One-command end-of-session routine. Updates project documentation, runs the improvement workflow, then commits and pushes everything to GitHub.

## Arguments

- `$ARGUMENTS` - Optional notes about the session (e.g., "focused on auth refactor")

## Context

- Current repo: !`git rev-parse --show-toplevel 2>/dev/null | head -1`
- Current branch: !`git branch --show-current 2>/dev/null | head -1`
- Remote: !`git remote get-url origin 2>/dev/null | head -1`
- Uncommitted changes: !`git status --short 2>/dev/null | head -20`
- Recent commits: !`git log --oneline -5 2>/dev/null | head -5`

## Instructions

### Step 1: Run /handoff

If the session involved work on a specific project (code changes, deployments, pipeline work):
1. Run the `/handoff` skill to generate or update the project's HANDOFF.md
2. It will combine the conversation context, git history, and codebase state to update the doc
3. If nothing meaningful changed, it will skip silently

If the session was general with no code changes, skip this step.

### Step 2: Run /improve

Run the `/improve` skill to:
- Analyze skills used in the session for improvement opportunities
- Check for new skill opportunities
- Identify and fix codebase gaps
- Capture knowledge into the project's `context/knowledge/` directory (if one exists)

Report what `/improve` found and apply approved changes.

### Step 3: Commit and push to GitHub

After all updates are applied:

1. **Check for changes** — run `git status`. If there are no uncommitted changes, skip to Step 4.

2. **Stage changes** — add all modified and new files that were created or updated during this session (skill improvements, HANDOFF.md, knowledge files, codebase fixes). Be selective — do not stage files unrelated to this session's work.

3. **Create a commit** with a clear message summarizing what the session accomplished. Follow the repo's existing commit message style if one is apparent from recent history. Include a brief note about what was improved (e.g., "Update HANDOFF.md, improve /review skill, fix missing error handling in auth module").

4. **Push to the current branch** on the remote. If the branch has no upstream, set one with `git push -u origin <branch>`.

5. If the push fails (e.g., remote has new commits), report the error and let the user decide how to resolve it. Do not force-push.

### Step 4: Confirm Completion

Report a brief summary:
```
Session wrap complete:
- /handoff: [updated/skipped/no project]
- /improve: [X improvements applied, Y new skills proposed]
- git: [committed and pushed / nothing to commit / push failed]
```
