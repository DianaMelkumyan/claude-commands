# Per-brand research sub-agent template

The `/market-research` orchestrator copies this file's body and substitutes
the placeholders below before invoking a `general-purpose` sub-agent per brand
in parallel.

**subagent_type**: general-purpose
**allowed_tools**: ["Write", "Read", "WebSearch", "WebFetch", "mcp__claude_ai_keystone__browser_navigate", "mcp__claude_ai_keystone__browser_screenshot", "mcp__claude_ai_keystone__browser_session_create", "mcp__claude_ai_keystone__browser_session_close"]

## Placeholders to substitute

- {{BRAND}} — brand name (e.g., "Chipotle")
- {{TOPIC}} — topic from research-brief.md
- {{VISUAL_RELEVANCE}} — high | medium | low
- {{SESSION_DIR}} — absolute path to .context/market-research/<run-id>/
- {{DIMENSIONS}} — newline-separated numbered list of dimensions verbatim from brief
- {{SCREENSHOT_TIER_BLOCK}} — substituted from one of three blocks (see below) based on {{VISUAL_RELEVANCE}}

## Prompt body (everything below this line is what the sub-agent receives)

You are researching ONE brand for a competitive teardown.

Brand: {{BRAND}}
Topic: {{TOPIC}}
Visual relevance: {{VISUAL_RELEVANCE}}
Session directory: {{SESSION_DIR}}

## Dimensions to evaluate (be narrow)

{{DIMENSIONS}}

For each dimension, find evidence of how this brand handles it. Use:
- Brand's own help center / FAQ / product docs
- App Store / Play Store listing description (for consumer apps)
- UX teardown blogs (Built for Mars, Growth.Design, UX Collective, Krazy Coupon Lady, Frugal Flyer, Coupon Cabin, Bustle, Elite Daily)
- Reddit threads in the brand's subreddit (signal for pain points only, not authoritative on flow)
- G2 / Capterra (for B2B brands)

## Screenshot strategy

{{SCREENSHOT_TIER_BLOCK}}

## Output: write findings-{{BRAND}}.md to {{SESSION_DIR}} following this schema EXACTLY

```markdown
# {{BRAND}}

**Status**: full | partial | failed
**Dimensions covered**: N/M
**Screenshots**: K
**Suggested pattern**: <one-phrase pattern label, e.g., wallet-claim-at-checkout, auto-add-item, drop-into-flow, picker, best-price-resolution, or "unclear">

## Dimension 1: <dimension name verbatim from brief>
- Finding: <1-2 sentences, no marketing fluff>
- Source: <url>

## Dimension 2: <dimension name verbatim from brief>
- Finding: <1-2 sentences>
- Source: <url>

[... one block per dimension. "Could not verify" entries written with reason ...]

## Screenshots
<only include this section if visual_relevance allows; otherwise omit entirely>

![<caption>](<url-or-relative-path>)
*<one-line description>*

## Sources
1. <url>
2. <url>
```

## Scope guardrails

- Do not evaluate dimensions outside the list above.
- If you cannot find credible evidence for a dimension, write "Could not verify" with one line on what you tried. Do not infer.
- Aim for ≤300 words total in findings file (excluding sources list and screenshots).
- Cite a URL for every specific claim.

## Retry logic

If web search returns nothing on first attempt, try one alternate phrasing (brand name + topic word + "review" / "UX" / "flow" / "how-to"). Stop after 2 attempts.

## Completion

Return JSON status:
{
  "brand": "{{BRAND}}",
  "dimensions_with_evidence": N,
  "dimensions_outcomes": {
    "<dimension-1-slug>": "evidence-found | could-not-verify",
    "<dimension-2-slug>": "evidence-found | could-not-verify"
  },
  "screenshots": { "tier_used": 1 | 2 | 3 | null, "count": K },
  "status": "full | partial | failed",
  "suggested_pattern": "<pattern label>",
  "notes": "<one line>"
}

---

## Screenshot tier blocks (orchestrator picks one)

### HIGH

Tier 1: For consumer apps, call WebFetch on
  https://itunes.apple.com/lookup?bundleId=<inferred-bundle-id>
  Returns JSON with `screenshotUrls` and `ipadScreenshotUrls`. These are stable CDN URLs.
  Bundle IDs you may need to infer: Starbucks=com.starbucks.mystarbucks, Chipotle=com.chipotle.ordering, McDonald's=com.mcdonalds.app, etc.

Tier 2: Search UX-teardown blogs for embedded screenshots. Query like:
  "site:builtformars.com {{BRAND}}" OR "site:bustle.com {{BRAND}} app" OR "{{BRAND}} app screenshot teardown".

Tier 3: If 1+2 yield nothing, call mcp__claude_ai_keystone__browser_session_create, then browser_navigate to the App Store / Play Store page, then browser_screenshot. Save the result to {{SESSION_DIR}}/screenshots/{{BRAND}}-<n>.png. Always browser_session_close after.

Target 1-2 screenshots per brand. Stop after 2.

### MEDIUM

Tier 1 only (App Store API). If nothing found, skip. No browser fallback.

### LOW

Skip screenshot pursuit entirely. Findings file omits the "## Screenshots" section.
