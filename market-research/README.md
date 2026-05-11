# /market-research

Standalone competitive-teardown skill. See full design at:
https://github.com/thanx-ai/honolulu-v3/blob/main/docs/superpowers/specs/2026-05-11-market-research-skill-design.md

## Structure

- `../market-research.md` - slash command body (orchestrator)
- `knowledge/modules.json` - bundled Modules DB snapshot
- `knowledge/visual-relevance-keywords.md` - keyword lists for visual_relevance inference
- `knowledge/brief-template.md` - research-brief.md skeleton
- `agents/brand-research.md` - per-brand sub-agent prompt template
- `agents/synthesis.md` - synthesis sub-agent prompt template
- `scripts/refresh-modules.py` - refreshes knowledge/modules.json from Notion

## Related commands

- `../market-research:set-parent.md` - saves the fallback Notion parent URL
- `../market-research:refresh-modules.md` - triggers a Modules DB snapshot refresh
