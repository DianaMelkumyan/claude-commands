# Per-brand research sub-agent template

The `/market-research` orchestrator copies this file's body and substitutes
the placeholders below before invoking a `general-purpose` sub-agent per brand
in parallel.

**subagent_type**: general-purpose
**allowed_tools**: ["Write", "Read", "WebSearch", "WebFetch"]

## Placeholders to substitute

- {{BRAND}} — brand name (e.g., "Chipotle")
- {{TOPIC}} — topic from research-brief.md
- {{VISUAL_RELEVANCE}} — high | medium | low
- {{SESSION_DIR}} — absolute path to .context/market-research/<run-id>/
- {{DIMENSIONS}} — newline-separated numbered list of dimensions verbatim from brief
- {{BRAND_TYPE}} — consumer-app | b2b | unknown (from brand-references.json)
- {{BUNDLE_ID}} — iOS App Store bundle ID for consumer-app brands (may be `null`)
- {{DOCS_URL}} — product documentation URL for b2b brands (may be `null`)
- {{BRAND_NOTE}} — optional context note from brand-references.json (may be empty string)
- {{SCREENSHOT_TIER_BLOCK}} — substituted based on {{VISUAL_RELEVANCE}} + {{BRAND_TYPE}} (see blocks below)

## Prompt body (everything below this line is what the sub-agent receives)

You are researching ONE brand for a market-landscape teardown. The brand may be a competitor, a partner, or an aspirational exemplar — what matters is learning how they handle the behavior the topic describes.

Brand: {{BRAND}}
Brand type: {{BRAND_TYPE}}
{{BRAND_NOTE_LINE_IF_NONEMPTY}}
Topic: {{TOPIC}}
Visual relevance: {{VISUAL_RELEVANCE}}
Session directory: {{SESSION_DIR}}

## Dimensions to evaluate (be narrow)

{{DIMENSIONS}}

For each dimension, find evidence of how this brand handles it.

For **consumer-app** brands, prioritize:
- Brand's own help center / FAQ
- App Store / Play Store listing description
- UX teardown blogs (Built for Mars, Growth.Design, UX Collective, Krazy Coupon Lady, Frugal Flyer, Coupon Cabin, Bustle, Elite Daily)
- Reddit threads in the brand's subreddit (signal for pain points only, not authoritative on flow)

For **b2b** brands, prioritize:
- Brand's product documentation (the starting URL is provided in {{DOCS_URL}} when known)
- G2 / Capterra UI reviews
- Vendor's own product-tour or feature pages
- Independent reviews (UX Collective, B2B SaaS comparisons)

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

![<caption>](<url>)
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
  "screenshots": { "tier_used": 1 | 2 | null, "count": K },
  "status": "full | partial | failed",
  "suggested_pattern": "<pattern label>",
  "notes": "<one line>"
}

---

## Screenshot tier blocks (orchestrator picks based on {{VISUAL_RELEVANCE}} + {{BRAND_TYPE}})

### HIGH + consumer-app

Tier 1 (preferred): If {{BUNDLE_ID}} is not null, fetch:
  https://itunes.apple.com/lookup?bundleId={{BUNDLE_ID}}&country=us
  Parse the JSON `results[0]`. Extract `screenshotUrls` (iPhone, 5+ URLs) and `ipadScreenshotUrls`.
  Use the first 1-2 iPhone screenshot URLs directly as `![caption](url)` references in your Screenshots section. These are stable Apple CDN URLs.

If {{BUNDLE_ID}} is null, do an iTunes Search API lookup by name first:
  https://itunes.apple.com/search?term={{BRAND}}&entity=software&country=us&limit=3
  Pick the result whose `sellerName` or `artistName` matches {{BRAND}}. Use its `screenshotUrls`.

Tier 2 (fallback if Tier 1 yields no usable URLs): Search UX-teardown blogs for embedded screenshots. Use these targeted queries (one at a time):
  - site:builtformars.com {{BRAND}}
  - site:bustle.com {{BRAND}} app
  - site:frugalflyer.ca {{BRAND}}
  - site:thekrazycouponlady.com {{BRAND}}
  - {{BRAND}} app screenshot teardown

When you find a blog post that embeds screenshots, WebFetch the post and look for `<img>` tags whose `src` is a CDN URL (typically `*.cloudfront.net/`, `*.imgix.net/`, `*.cdn.shopify.com/`, etc.). Pick the largest-looking image (highest dimensions in the URL or filename).

Target 1-2 screenshots per brand. Stop after 2 are sourced.

### HIGH + b2b

Tier 1: WebFetch {{DOCS_URL}} (if not null). Look for `<img>` tags showing product UI — typical pattern is a docs page with annotated UI screenshots. Use those URLs directly.

If {{DOCS_URL}} is null, search:
  - site:g2.com {{BRAND}} screenshots
  - site:capterra.com {{BRAND}}
  - {{BRAND}} product tour

Target 1-2 screenshots. Stop after 2.

### MEDIUM + consumer-app

Tier 1 only (iTunes API). If {{BUNDLE_ID}} is null, do the name search once. Skip if nothing found. No blog-search fallback.

### MEDIUM + b2b

Tier 1 only (WebFetch {{DOCS_URL}}). Skip if nothing found.

### LOW (any brand type)

Skip screenshot pursuit entirely. Findings file omits the "## Screenshots" section.
