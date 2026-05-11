# /market-research:refresh-modules

Refreshes the bundled Modules DB snapshot from the [Technical Partner Strategy](https://www.notion.so/8662d31182004bc5a3f2b547f9ba6dd7) page in Notion. Out-of-band maintenance command. The bundled snapshot lives at `dAIna/claude-commands/market-research/knowledge/modules.json`.

## When to run

When the Technical Partner Strategy page has changed. The page hasn't changed since Oct 2022 per its header, so refreshes are expected to be rare.

## Behavior

1. Fetch the database to get its view URL:

```
mcp__claude_ai_Notion__notion-fetch
  id: https://www.notion.so/baead8ad993a410c84ebb8d033d881e4
```

Extract the view URL from the response (format: `https://www.notion.so/baead8ad993a410c84ebb8d033d881e4?v=<view-id>`).

2. Query the view to get all rows:

```
mcp__claude_ai_Notion__notion-query-database-view
  view_url: <view-url-from-step-1>
```

3. Transform the response rows into this shape and save to `/tmp/modules-rows.json`:

```json
[
  {
    "Module": "...",
    "Category": [...],
    "State": [...],
    "Features": "...",
    "Example Partners": "..."
  }
]
```

Note: some `Example Partners` cells contain `‣` markers (Notion's unresolved relation references). Keep these as-is in the JSON; the snapshot writer treats them as "no usable partner seed".

4. Run the snapshot writer:

```bash
python3 /Users/diana/conductor/workspaces/dAIna/claude-commands/market-research/scripts/refresh-modules.py \
  --data /tmp/modules-rows.json
```

5. Verify the result:

```bash
python3 -m json.tool /Users/diana/conductor/workspaces/dAIna/claude-commands/market-research/knowledge/modules.json | head -40
```

6. Show diff against previous version:

```bash
cd /Users/diana/conductor/workspaces/dAIna/claude-commands
git diff market-research/knowledge/modules.json
```

7. If the diff looks correct, commit:

```bash
git add market-research/knowledge/modules.json
git commit -m "chore(market-research): refresh Modules DB snapshot"
```

If the diff is large or unexpected, surface it to the user before committing.
