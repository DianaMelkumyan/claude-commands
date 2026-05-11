---
name: revelio
description: Route a task through the recommended sequence of gstack + superpowers skills, skipping ones that aren't relevant. Use when you want a guided, opinionated workflow from idea to ship without having to remember which skill goes where.
---

# Revelio

Reveal which skills apply to the current task and walk through them in order. Skip the ones that don't fit. Stop and ask before any irreversible step.

## Arguments

- `$ARGUMENTS` — one-line task description. If empty, ask the user what they want to do before classifying.

## Step 1: Classify the task

Pick exactly one class. If unsure, ask the user. Do not guess silently.

| Class | Signals |
|---|---|
| `new-project` | "starting from scratch", no repo yet, greenfield, kickoff |
| `new-feature` | existing repo, net-new functionality, design + implementation needed |
| `bug` | error report, regression, "it was working", stack trace, failing test |
| `ui-polish` | "doesn't look right", visual QA, design review, spacing/hierarchy |
| `refactor` | restructure existing code, no behavior change intended |
| `one-off` | tiny change, doc fix, single-line edit, config tweak |
| `ship-only` | work is done, just need to PR/merge |

State the chosen class to the user with one sentence of reasoning, then continue.

## Step 2: Build the route

Look up the class in the matrix below. Output the full sequence as a numbered checklist, with `[SKIP: <reason>]` printed inline for any stage the class doesn't need. This makes the routing visible before any work starts.

### Matrix

Legend: `sp:` = superpowers, `gs:` = gstack, `da:` = dAIna-local.

| Stage | new-project | new-feature | bug | ui-polish | refactor | one-off | ship-only |
|---|---|---|---|---|---|---|---|
| Discovery | `gs:kickoff` | SKIP | SKIP | SKIP | SKIP | SKIP | SKIP |
| Ideation | `gs:office-hours` | `sp:brainstorming` | SKIP | `sp:brainstorming` | `sp:brainstorming` if scope unclear else SKIP | SKIP | SKIP |
| Plan | `sp:writing-plans` | `sp:writing-plans` | SKIP (diagnose first) | `sp:writing-plans` if multi-step else SKIP | `sp:writing-plans` | SKIP | SKIP |
| Strategic review | `gs:plan-ceo-review` (offer) | offer if scope is large | SKIP | SKIP | SKIP | SKIP | SKIP |
| Plan review | `gs:plan-eng-review` | offer | SKIP | `gs:plan-design-review` | offer | SKIP | SKIP |
| Diagnose | SKIP | SKIP | `sp:systematic-debugging` then escalate to `da:investigate` then `da:debug` | SKIP | SKIP | SKIP | SKIP |
| Implement | `sp:subagent-driven-development` | `sp:subagent-driven-development` | `da:fixit` if quick + background-able, else direct edit | direct edit | `sp:subagent-driven-development` | direct edit | SKIP |
| TDD | `sp:test-driven-development` | `sp:test-driven-development` | reproduce-then-fix (no formal TDD) | SKIP (visual) | `sp:test-driven-development` | SKIP | SKIP |
| QA | `gs:qa` | `gs:qa` or direct verify | verify fix lands + re-run failing test | `gs:design-review` | run tests | SKIP | SKIP |
| Self-review | `sp:requesting-code-review` | `sp:requesting-code-review` | SKIP if trivial | SKIP | `sp:requesting-code-review` | SKIP | SKIP |
| Verify-before-done | `sp:verification-before-completion` | ALWAYS | ALWAYS | ALWAYS | ALWAYS | if claiming done | ALWAYS |
| Ship | `gs:ship` | `da:pr` or `gs:ship` | `da:pr` | `da:pr` | `da:pr` | `da:save-w-specs` | `da:pr` |

### Print format

```
Task: <one-line restatement>
Class: <class> — <why>

Route:
1. <stage> → <skill or SKIP>
2. ...
```

Use a checkbox per stage so progress is visible.

## Step 3: Walk the route

For each step in order:

1. If `SKIP`, print `[SKIP: <reason>]` and move on.
2. If a skill: announce `→ invoking <skill> to <purpose>`, then call it via the Skill tool.
3. After the skill returns, mark the checkbox, then **pause and ask** before proceeding to the next step *if* the step had an irreversible side effect (commit, push, PR, file write outside the workspace, external message). Reversible local steps (planning, drafting) flow through without asking.

If the user types `skip` between steps, mark the current step `[SKIP: user]` and move on. If they type `stop`, halt and print the remaining route so they can resume.

## Step 4: Wrap up

After the last step:

- Print the final route with all marks.
- If anything was deferred (e.g., "shipped without QA"), call it out explicitly with the risk.
- Save nothing to memory — revelio is a per-task router, not a long-lived state.

## When NOT to use revelio

- The user already named a specific skill (`/ship`, `/brainstorming`, etc.) — just invoke that one.
- The task is mid-flight and the user just wants help with one step.
- The user is in pure exploration / Q&A mode, not building anything.

## Notes

- This skill is a router, not a re-implementation. It calls other skills via the Skill tool — it never inlines their logic.
- Routing follows the `Skill Routing` section in `~/.claude/CLAUDE.md`. If that section changes, update this matrix.
- Skills in the `Ignored gstack skills` list of CLAUDE.md must not be invoked from here even if the matrix could fit them.
