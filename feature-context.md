---
name: feature-context
description: Find PRD, product guide, and help articles for a Thanx feature by name. Searches Notion and Zendesk, confirms matches with the user, then fetches full content.
---

# Feature Context

Find the PRD, product guide, and help articles for a Thanx feature. Searches two Notion databases in parallel, confirms matches with the user, fetches full content, and returns structured results.

Designed to be invoked by other skills (slide-speaker-notes, slide-review, review-launchnotes, etc.) when they need product context. Can also be used standalone.

## Arguments

- `$ARGUMENTS` - A feature name or description. Examples:
  - "Bonus Points"
  - "Toast menu visibility"
  - "Universal Promo Codes"
  - "the new loyalty points multiplier feature"

## Notion Database IDs

- **PRD Database ("Projects"):** `6bac395d649c4fb98e7a31b56f7a38ae`
  - Name column: `Name` (title)
  - Key URL fields: `Product Guide (internal)`, `Help Article (External)`
- **Product Guide Database ("Product Guides (internal)"):** `da6b225f9fa9495b818ceca5fa7ce99f`
  - Name column: `Product Guide` (title)
  - Key URL fields: `Share External Article`

## Instructions

### Step 1: Search both Notion databases in parallel

Use `mcp__claude_ai_Notion__notion-search` to search both databases simultaneously. Run these two searches in parallel:

**Search 1 - PRDs:**
Search Notion for the feature name. Filter results to pages within the Projects database (database ID `6bac395d649c4fb98e7a31b56f7a38ae`). Look at titles matching the feature name keywords.

**Search 2 - Product Guides:**
Search Notion for the feature name. Filter results to pages within the Product Guides database (database ID `da6b225f9fa9495b818ceca5fa7ce99f`). Look at titles matching the feature name keywords.

For both searches, use the feature name as the query. If the feature name contains a category prefix (e.g., "Rewards: Bonus Points"), search with just the specific part ("Bonus Points") as well.

Collect up to 3 results from each database.

### Step 2: Handle no results

If one or both searches return no results:

- If zero PRD results: try a keyword-reduced search. Drop common words like "new", "feature", "update", "the", and retry with core nouns only.
- If still zero results after retry: report "PRD: None found" for that database.
- Apply the same retry logic to product guide results independently.
- If both databases return zero results even after retry, report that and stop.

### Step 3: Present matches and confirm

Present what was found in a clear format:

```
## Feature Context Results for "{feature name}"

### PRDs found:
1. {PRD title} - {Notion URL}
2. {PRD title} - {Notion URL}

### Product Guides found:
1. {Guide title} - {Notion URL}
2. {Guide title} - {Notion URL}

Which matches are correct? (e.g., "1 and 1", "PRD 2, Guide 1", or "all")
```

If exactly 1 match per database and the titles clearly match the feature name, still present them and ask for confirmation. Do not auto-select.

Wait for user confirmation before proceeding.

### Step 4: Fetch full content

After the user confirms which matches to use, fetch the confirmed pages in parallel using `mcp__claude_ai_Notion__notion-fetch`:

- Fetch the confirmed PRD page (full content)
- Fetch the confirmed Product Guide page (full content)

From the PRD page properties, also extract:
- `Product Guide (internal)` URL (may be empty)
- `Help Article (External)` URL (may be empty)

From the Product Guide page properties, also extract:
- `Share External Article` URL (may be empty)

### Step 5: Find help article

Check for help article URLs in this order:

1. PRD's `Help Article (External)` field
2. Product Guide's `Share External Article` field
3. Any Zendesk URLs found in the body content of either page

If a URL was found from steps 1-3, report it.

If no help article URL was found anywhere, fall back to searching Zendesk:
- Use `mcp__zendesk-knowledge-base__search_articles` with the feature name as the query
- If results are found, present the top 1-2 matches with titles and URLs
- If no results, report "Help Article: None found"

### Step 6: Return structured result

Present the final result:

```
## Feature Context: {feature name}

### PRD
- **Title:** {title}
- **Link:** {Notion URL}
- **Content:**
{full PRD content}

### Product Guide
- **Title:** {title}
- **Link:** {Notion URL}
- **Content:**
{full guide content}

### Help Article
- **Status:** Found (from PRD) | Found (from guide) | Found (Zendesk search) | None found
- **Title:** {title, if found}
- **Link:** {URL, if found}
```

If either PRD or Product Guide was not found, include the section with "None found" as the status. Always be explicit about what was and was not found.

## When Called by Other Skills

Other skills invoke this skill by saying: "Use `/feature-context {feature name}` to find the PRD, product guide, and help articles."

The calling skill should:
1. Extract the feature name from its own inputs (e.g., from slide content, LaunchNote title)
2. Invoke feature-context with that name
3. Use the returned content as source material for its own work

## Important

- Always search both databases in parallel for speed
- Never auto-select matches. Always confirm with the user.
- Fetch full content only after confirmation to avoid wasting API calls on wrong matches
- If a database returns no results, say so clearly rather than guessing
- The PRD database uses "Area: Feature" naming (e.g., "Rewards: Fixed price"). Try searching with and without the area prefix.
- The Product Guide database prefixes entries with "Product Guide:" (e.g., "Product Guide: Bonus Points"). The search should still work with just the feature name.
