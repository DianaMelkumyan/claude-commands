# /market-research

Standalone market-research skill. Studies how leaders in a space (partners, competitors, and exemplars) handle a given product behavior. See full design at:
https://github.com/thanx-ai/honolulu-v3/blob/main/docs/superpowers/specs/2026-05-11-market-research-skill-design.md

## Structure

- `../market-research.md` - slash command body (orchestrator)
- `knowledge/modules.json` - bundled Modules DB snapshot
- `knowledge/brand-references.json` - curated brand list per category with iOS bundle IDs / docs URLs
- `knowledge/visual-relevance-keywords.md` - keyword lists for visual_relevance inference
- `knowledge/brief-template.md` - research-brief.md skeleton
- `agents/brand-research.md` - per-brand sub-agent prompt template
- `agents/synthesis.md` - synthesis sub-agent prompt template
- `scripts/refresh-modules.py` - refreshes knowledge/modules.json from Notion

## Related commands

- `../market-research:refresh-modules.md` - triggers a Modules DB snapshot refresh
