# Test MCPs

Test all configured MCP servers and display connection status.

## Usage
```
/test-mcps
```

## What it does
Tests connectivity to all configured MCP servers:
- Notion (hosted)
- JIRA (hosted)
- GitHub (hosted)
- Slack (local, if configured)

## Output
Displays a red/green status for each MCP with:
- ✅ Connection successful
- ❌ Connection failed with error details

---

You are testing all configured MCP servers. For each server in `.mcp.json`:

1. **Notion** - Call `mcp__notion__notion-search` with query "test"
2. **JIRA** - Call `mcp__jira__atlassianUserInfo`
3. **GitHub** - Call `mcp__github__search_repositories` with query "test" and perPage=1
4. **Slack** (if configured) - Call `mcp__slack__list_channels` with types "public_channel"

Present results in this format:

```
🔍 Testing MCP Connections
==========================

✅ Notion - Connected
✅ JIRA - Connected (user: aaron@thanx.com)
✅ GitHub - Connected
❌ Slack - Not configured or failed to connect
   Error: [error details]

Summary: 3/4 MCPs operational
```

**Important**:
- Test all MCPs even if one fails
- Show specific error messages for failures
- Don't make assumptions - actually call each MCP
- If a server isn't in `.mcp.json`, skip it with "Not configured"
