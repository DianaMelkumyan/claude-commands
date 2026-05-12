# Synthesis sub-agent template

The `/market-research` orchestrator copies this body and substitutes placeholders before invoking a single `general-purpose` sub-agent for synthesis.

**subagent_type**: general-purpose
**allowed_tools**: ["Write", "Read", "Glob"]

## Placeholders to substitute

- {{SESSION_DIR}} — absolute path to .context/market-research/<run-id>/
- {{TOPIC}} — topic from research-brief.md
- {{BRIEF_PATH}} — absolute path to {{SESSION_DIR}}/research-brief.md
- {{PRD_INPUT}} — "true" if input was a PRD URL, "false" otherwise

## Prompt body

You are assembling a final competitive-landscape markdown document for: {{TOPIC}}

Do NOT do any new web research. Pure assembly from existing files.

## Inputs

- Read the brief: {{BRIEF_PATH}}
- Glob for all per-brand findings: {{SESSION_DIR}}/findings-*.md
- Each findings file follows a fixed schema (Status, Dimensions covered, Suggested pattern, per-dimension blocks, Screenshots section, Sources).

## Output

Write {{SESSION_DIR}}/market-landscape.md following this structure:

```markdown
# Market landscape: {{TOPIC}}

<one-paragraph scope statement summarizing the brief's topic interpretation and dimensions>

## Summary table

A Markdown table with rows = brands (in order from brief), columns = dimensions (in order from brief), cells = 1-2 phrase summary pulled from each brand's findings.
- Brands with status=partial get a `~` prefix on the brand name.
- Cells where the brand could not be verified on that dimension get `✗`.

## Screenshots

Only include this section if visual_relevance in the brief is `high` or `medium` AND at least one brand has screenshots.

For each brand with screenshots, write:
### <Brand>
![<caption>](<url or path verbatim from findings file>)
*<one-line description from findings>*

## Cross-brand patterns

Group brands by their `Suggested pattern` field. A pattern requires ≥2 brands to become a section. Patterns with only one brand go into a final "One-off observations" appendix.

For each multi-brand pattern, write:
### Pattern A: <descriptive name>
**Brands**: <comma-separated list>
**How it works**: <2-3 sentences synthesizing the brand findings>
**Pros**: <bullet list, 2-4 items>
**Cons**: <bullet list, 2-4 items>

## Anti-patterns
<top-level callout of any anti-patterns or hidden-eligibility traps flagged in findings>

## Recommendations for Thanx

{{IF PRD_INPUT IS true}}
For each in-scope behavior from the PRD's Scope of Work (extract from the brief's dimension list), recommend a pattern and cite 1-2 brands as evidence.

### Scenario 1: <in-scope behavior verbatim>
**Recommendation**: Pattern X. **Why**: <2-3 sentence rationale citing brand evidence>.

{{ELSE}}
Omit this section.
{{END IF}}

## Sources
Deduplicated URL list across all per-brand findings. Number them 1..N.
```

## Style guidance

- No marketing fluff. Direct, comparable language.
- Brand names in **bold** when first introduced in a section.
- Source citations always linked inline where claimed.
- Keep total length under ~2000 words (excluding the summary table).
