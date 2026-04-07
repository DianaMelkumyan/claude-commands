---
name: deduplicate
description: Audit a document for redundant content across sections. Identifies duplicated information, recommends which section should own each fact, and produces a concrete edit plan to shorten the document without losing information. Use when a help article, guide, or long-form doc feels repetitive.
---

# /deduplicate - Document Deduplication Audit

Audit a document for redundant content. For each piece of information, keep it only once in the most relevant section. Produce a concrete plan to shorten the document without losing useful info.

## Arguments

- First argument: URL or file path of the document to audit. If a Zendesk URL, fetch the article using mcp__zendesk-knowledge-base__get_article. If a Notion URL, fetch using mcp__claude_ai_Notion__notion-fetch. If a file path, read directly.

## Instructions

### Step 1: Fetch the Document

Fetch the document content based on the argument type (Zendesk URL, Notion URL, or file path). If no argument is provided, ask the user which document to audit.

### Step 2: Build an Information Inventory

Go through the document section by section. For each distinct piece of information (a fact, instruction, detail, or concept), record:
- What the information is (short label)
- Every section where it appears (by heading name)
- Which section is the most natural home for it

Be thorough. Check for:
- Exact duplicates (same sentence or near-identical phrasing in multiple places)
- Semantic duplicates (same fact expressed differently)
- FAQ answers that restate body content
- Overview/intro bullets that are expanded later in dedicated sections
- Important Notes that repeat content from earlier sections
- Examples that re-explain concepts already covered

### Step 3: Identify Section Overlap

Look for sections that could be merged or removed entirely:
- Sections where more than 70% of content is covered elsewhere
- Sections that serve the same purpose under different headings
- Short sections (under 2 sentences of unique content) that could fold into a neighboring section

### Step 4: Present the Audit

Present findings in this format:

**Duplicated Information** (table)

| Info | Appears In | Keep In | Remove From |
|------|-----------|---------|-------------|

**Section-Level Recommendations**

For each section, one of:
- KEEP - has mostly unique content
- MERGE INTO [section] - fold unique bits into another section, delete this one
- REMOVE - fully redundant, no unique content
- TRIM - keep section but remove specific duplicated items

**FAQ Deduplication**

List each FAQ question and whether the answer adds value beyond the article body. Mark as KEEP (new info), TRIM (shorten, partially redundant), or REMOVE (fully answered in body).

**Estimated Reduction**

Estimate how much shorter the document would be after all changes, in approximate word count and percentage.

### Step 5: Wait for Approval

Present the full audit and wait for the user to approve, modify, or selectively apply recommendations. Do NOT make any changes until the user confirms.

If the user approves all or specific recommendations, apply the changes to the document. For Zendesk articles, use mcp__zendesk-knowledge-base__update_article. For Notion pages, use mcp__claude_ai_Notion__notion-update-page. For files, edit directly.

## Key Principles

- Every fact should live in exactly one section - the most relevant one
- Prefer keeping detail in the actionable/specific section over the overview section
- FAQ should add NEW value, not restate the article body
- Introductions and overviews should be brief teasers, not comprehensive summaries
- When merging sections, preserve all unique information from both
- Never remove information entirely - only remove redundant copies
