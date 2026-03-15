# Tool Discovery Sources

Reference list of repos, registries, and search queries to check for new Claude Code tools.

## Awesome Lists (Primary)

| Repo | URL | What to look for |
|------|-----|-------------------|
| awesome-claude-code-toolkit | https://github.com/rohitg00/awesome-claude-code-toolkit | Skills, plugins, MCPs, workflows |
| awesome-agent-skills | https://github.com/VoltAgent/awesome-agent-skills | Agent skills compatible with Claude Code |
| awesome-claude-code | https://github.com/heshengtao/awesome-claude-code | Tools, extensions, integrations |
| awesome-mcp-servers | https://github.com/punkpeye/awesome-mcp-servers | MCP servers (filter for general-purpose) |
| awesome-mcp-servers (wong2) | https://github.com/wong2/awesome-mcp-servers | MCP servers, alternative list |
| awesome-claude | https://github.com/saharmor/awesome-claude | Broader Claude ecosystem tools |

## GitHub Search Queries

Run these via `gh search repos` or WebSearch:

```
claude-code skill               (sort: updated)
claude-code plugin              (sort: updated)
claude-code agent               (sort: updated)
claude-code hook                (sort: updated)
claude mcp server               (sort: stars, updated recently)
claude code extension tool      (sort: updated)
"claude code" "SKILL.md"        (find skill repos by convention)
"claude code" "settings.json"   (find MCP configs)
```

## npm Registry

Search keywords:
- `claude-code-skill`
- `claude-code-plugin`
- `claude-mcp`
- `@anthropic` (official packages)
- `@modelcontextprotocol` (official MCP packages)

URL pattern: `https://www.npmjs.com/search?q=keywords:<keyword>&ranking=maintenance`

## PyPI Registry

Search keywords:
- `claude-code`
- `mcp-server`
- `claude-mcp`

URL: `https://pypi.org/search/?q=<keyword>&o=-created`

## Community Hubs

| Source | URL | Notes |
|--------|-----|-------|
| Claude Code Discussions | https://github.com/anthropics/claude-code/discussions | Official repo discussions |
| Claude Code Issues | https://github.com/anthropics/claude-code/issues | Feature requests often link tools |
| MCP Registry | https://github.com/modelcontextprotocol/servers | Official MCP server directory |
| Smithery | https://smithery.ai/ | MCP server marketplace |
| Glama MCP | https://glama.ai/mcp/servers | MCP server directory |
| r/ClaudeAI | https://www.reddit.com/r/ClaudeAI/ | Community posts about tools |
| X/Twitter | Search: "claude code skill" OR "claude code mcp" | Community announcements |

## Individual Tool Repos (Known Good)

Track these for updates:

| Tool | Repo | Type | Status |
|------|------|------|--------|
| Context7 | https://github.com/upstash/context7 | MCP | Installed |
| Playwright MCP | https://github.com/anthropics/mcp-playwright | MCP | Installed |
| Greptile | https://github.com/greptileai/greptile | MCP | Installed |
| Serena | https://github.com/oraios/serena | MCP | Installed |
| Firecrawl | https://github.com/ArcadeAI/firecrawl | Skill | Installed |

## Search Cadence

- **Awesome lists**: Check weekly (they aggregate frequently)
- **GitHub search**: Check bi-weekly
- **npm/PyPI**: Check monthly
- **Community hubs**: Check when user requests or before major tasks
