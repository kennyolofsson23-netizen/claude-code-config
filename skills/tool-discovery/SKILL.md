# Tool Discovery Skill

Periodically audit for new community-built Claude Code tools worth installing.

## Trigger

Activate when:
- User says "find new tools", "what's new", "update my setup", "tool discovery", "discover tools"
- Proactively before major tasks (check if last run was >7 days ago)
- User asks about a capability that might exist as a community tool

## Workflow

### 1. Inventory Current Setup

Read and catalog what's already installed:

```
~/.claude/skills/        → installed skills
~/.claude/agents/        → installed agents
~/.claude/plugins/       → installed plugins + installed_plugins.json
~/.claude/hooks/         → installed hooks
~/.claude/settings.json  → configured MCPs
```

Build a deduplicated list of installed tool names.

### 2. Search Sources

Search each source listed in `references/sources.md` using WebFetch and WebSearch:

1. **Awesome lists** — fetch README from each repo, parse tool entries
2. **GitHub trending** — search for repos tagged `claude-code`, `claude-mcp`, `claude-skill` created/updated recently
3. **npm** — search for packages with keywords: `claude-code-skill`, `claude-code-plugin`, `claude-mcp`
4. **GitHub search** — query: `claude code skill OR plugin OR agent OR mcp` sorted by recently updated

For each source, extract:
- Tool name
- One-line description
- Type (skill / agent / plugin / MCP / CLI)
- Install method
- Last updated date
- Stars / downloads (if available)

### 3. Filter

Apply these filters in order:

1. **Already installed** — skip anything matching current inventory
2. **General-purpose only** — skip framework-specific tools (e.g., "Laravel debugger", "Rails migration helper") unless the user's current project uses that framework
3. **CLI-first philosophy** — if a tool exists as both MCP and CLI, flag the CLI version. Prefer standalone CLIs over MCP wrappers when functionality is equivalent
4. **Quality threshold** — skip repos with <10 stars and no recent commits (>6 months stale)
5. **Security check** — flag tools that request broad permissions or shell access without justification

### 4. Categorize Results

Group findings into:
- **High value** — general-purpose, well-maintained, fills a gap in current setup
- **Worth watching** — interesting but early-stage or niche
- **CLI alternatives** — CLIs that could replace or supplement installed MCPs

### 5. Present Findings

Output a table per category:

```
## High Value

| Name | Type | What it does | Install | CLI Alt? | Stars |
|------|------|-------------|---------|----------|-------|
| ...  | ...  | ...         | ...     | ...      | ...   |

## Worth Watching

| Name | Type | What it does | Install | Stars | Note |
|------|------|-------------|---------|-------|------|
| ...  | ...  | ...         | ...     | ...   | ...  |

## CLI Alternatives to Installed MCPs

| Installed MCP | CLI Alternative | Difference | Install |
|---------------|----------------|------------|---------|
| ...           | ...            | ...        | ...     |
```

### 6. Install on Approval

When the user approves a tool:

- **Skills**: Clone/copy to `~/.claude/skills/<name>/`
- **Agents**: Copy to `~/.claude/agents/<name>.md`
- **Plugins**: Run the plugin's install command, update `installed_plugins.json`
- **MCPs**: Add config to `~/.claude/settings.json` under `mcpServers`
- **CLIs**: Install via npm/pip/cargo as appropriate, verify with `--version`

After install, verify the tool works by running a smoke test if possible.

### 7. Log

Append to `~/.claude/skills/tool-discovery/discovery-log.md`:

```
## YYYY-MM-DD
- Searched: [sources checked]
- Found: N new tools
- Installed: [list]
- Skipped: [list with reasons]
```

## Notes

- Rate-limit GitHub API calls — use WebFetch sparingly, batch where possible
- Cache results for 7 days in `~/.claude/skills/tool-discovery/cache/`
- If a tool looks useful but risky, suggest it but do NOT auto-install
- Always check if a discovered MCP has a simpler CLI equivalent before recommending
