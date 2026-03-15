# Claude Code God Setup

> The most comprehensive Claude Code configuration available. 29 skills, 9 plugins, 13 hooks, 8 agents, 8 commands — self-documenting, self-improving, and personalizable via a built-in interview prompt.

## Why This Exists

Most Claude Code users start with zero configuration. They type prompts, get okay results, and wonder why Claude takes shortcuts, forgets context, and makes them do QA manually.

This setup fixes all of that:

| Problem | How This Setup Solves It |
|---------|--------------------------|
| Claude takes shortcuts | 13 hooks enforce quality deterministically — can't skip tests, can't commit secrets, can't break formatting |
| Claude forgets what tools are available | `inventory.sh` scans all installed tools on every session start |
| Claude repeats the same mistakes | `meta-hookify.py` detects repeated corrections and suggests creating hooks |
| You have to manually QA everything | Auto-test hook runs matching tests on every code edit |
| You don't know what skills exist | Self-documenting — new skills auto-appear in the inventory |
| CLAUDE.md is either empty or bloated | 76 lines, every line passes the test: "would removing this cause a mistake?" |
| MCPs are slow and need auth | CLI-first architecture — use `gh`, `stripe`, `vercel`, `pgcli` directly |

## What's Included

| Category | Count | Highlights |
|----------|-------|------------|
| **Skills** | 29 | Security auditing, TDD, architecture (DDD/SDD), UI/UX design system, React best practices, database optimization, git workflows, research, SEO |
| **Plugins** | 9 | feature-dev, frontend-design, code-review (5 parallel agents), pr-review-toolkit, security-guidance, hookify, ralph-loop (autonomous iteration), superpowers (TDD/debugging), ui-ux-pro-max (50+ styles, 161 color palettes) |
| **Agents** | 8 | error-detective, fullstack-engineer, refactoring-specialist, task-coordinator, test-architect, pr-reviewer, qa, researcher |
| **Commands** | 8 | `/fix-issue` (GitHub issue to PR), `/tdd`, `/test-fix`, `/diagram`, `/checkpoint`, `/wrap-up`, `/orchestrate`, `/qa-setup` |
| **Hooks** | 13 | Auto-format, auto-test, secret blocking, commit guards, dev server blocking, self-documenting inventory, meta-hookification |
| **Rules** | 6 | Environment, Python, TypeScript, git safety, coding style, error handling |

## Quick Start

### Prerequisites

- [Claude Code](https://code.claude.com) installed and working
- Git, Node.js 18+, Python 3.10+
- GitHub CLI (`gh`) authenticated

### 1. Backup Your Existing Config (if any)

```bash
# Skip this if you're starting fresh
mv ~/.claude ~/.claude-backup
```

### 2. Clone

```bash
git clone https://github.com/kennyolofsson23-netizen/claude-code-config.git ~/.claude
```

### 3. Install Dependencies

```bash
# CLI tools
npm install -g prettier uipro-cli
pip install black pgcli

# Stripe CLI (optional)
# Windows:
winget install Stripe.StripeCli
# Mac:
# brew install stripe/stripe-cli/stripe
# Linux:
# curl -s https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public | gpg --dearmor | sudo tee /usr/share/keyrings/stripe.gpg && echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" | sudo tee -a /etc/apt/sources.list.d/stripe.list && sudo apt update && sudo apt install stripe
```

### 4. Install Plugins

```bash
# Marketplaces
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill

# Official Anthropic plugins
claude plugin install feature-dev@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install pr-review-toolkit@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
claude plugin install hookify@claude-plugins-official
claude plugin install ralph-loop@claude-plugins-official

# Community plugins
claude plugin install superpowers@superpowers-marketplace
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
```

### 5. Add MCPs

**Windows (Git Bash):**
```bash
claude mcp add -s user --transport stdio context7 -- cmd /c "npx -y @upstash/context7-mcp"
claude mcp add -s user --transport stdio playwright -- cmd /c "npx -y @playwright/mcp@latest"
claude mcp add -s user --transport stdio sequential-thinking -- cmd /c "npx -y @modelcontextprotocol/server-sequential-thinking"
claude mcp add -s user --transport http sentry https://mcp.sentry.dev/mcp
```

**Mac/Linux:**
```bash
claude mcp add -s user --transport stdio context7 -- npx -y @upstash/context7-mcp
claude mcp add -s user --transport stdio playwright -- npx -y @playwright/mcp@latest
claude mcp add -s user --transport stdio sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
claude mcp add -s user --transport http sentry https://mcp.sentry.dev/mcp
```

### 6. Configure settings.json

The `settings.json` file is gitignored (contains API keys). You need to create it with the hook wiring. Start a Claude Code session and run:

```
Read ~/.claude/hooks/ and wire all hooks into ~/.claude/settings.json following the pattern in the repo's hook files. Python hooks use the full Python path, JS hooks use node, bash hooks use bash.
```

Or copy `settings.json` from someone who already has it configured and update the paths.

### 7. Set API Keys (Optional)

Add to your `settings.json` under `"env"`:

```json
{
  "env": {
    "GEMINI_API_KEY": "your-key-here",
    "STRIPE_API_KEY": "your-key-here"
  }
}
```

- **GEMINI_API_KEY**: Free from [Google AI Studio](https://aistudio.google.com/apikey) — enables `nano-banana-pro` AI image generation
- **STRIPE_API_KEY**: From [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys) — enables Stripe CLI access

### 8. Verify Installation

Start a new Claude Code session and run:

```
/qa-setup
```

This tests every hook, skill, plugin, MCP, CLI, and rule.

### 9. Personalize

This is the most important step. Run the self-interview below.

## Personalize: Self-Interview

This setup is a foundation — it needs to be adapted to YOU. Copy this prompt into a Claude Code session after installing:

```
I just installed the Claude Code God Setup from github.com/kennyolofsson23-netizen/claude-code-config.

I need you to personalize it for me. Interview me with these questions ONE AT A TIME. Wait for my answer before asking the next question.

After all questions, summarize what you learned and show me the exact changes you'll make. Ask for my approval before writing anything.

Questions:

1. BACKGROUND: What's your background? (developer, designer, PM, founder, student, etc.) How many years of experience? What languages and frameworks do you know well vs learning?

2. PROJECTS: What are you building right now? Describe your project(s) — tech stack, stage (idea/MVP/launched), what it does, who it's for.

3. TEAM: Do you work solo or with a team? If team, what's their experience level? Will they also use this Claude setup?

4. FRUSTRATIONS: What's your biggest frustration with AI coding assistants? What specific mistakes does Claude make that waste your time? Give examples if you can.

5. QUALITY vs SPEED: How do you feel about code quality vs shipping speed? Do you want Claude to be thorough and slow, or fast and pragmatic? What's your test coverage target?

6. DESIGN: Do you use Figma or other design tools, or do you design in code? How important is UI/UX quality to you?

7. DEPLOYMENT: What's your deployment setup? (Vercel, AWS, Railway, Docker, etc.) How much deploy autonomy should Claude have — should it auto-deploy after tests pass, or always ask first?

8. TOOLS: What project management and communication tools do you use? (Linear, Jira, Notion, Slack, Discord, GitHub Issues, or just todo.md?)

9. TESTING: What's your testing philosophy? Unit-heavy? Integration? E2E? Property-based? What coverage target?

10. SCHEDULE: What timezone are you in? When do you typically code? (Full-time, evenings, weekends?)

11. GOALS: What's your end goal? (Learning, shipping a product, building a business, financial independence, career growth, fun?)

12. ENVIRONMENT: What OS are you on? (Windows/Mac/Linux) What shell? Any special dev environment setup?

Based on my answers, update:
- ~/.claude/CLAUDE.md — adapt the instructions to my workflow and priorities
- ~/.claude/rules/environment.md — my specific OS, paths, tools
- Memory files — save my profile for future sessions
- Remove any skills/rules/hooks that don't apply to my stack
- Add any project-specific rules I need
```

## Architecture

```
CLAUDE.md (76 lines)           <- What Claude must always know
├── inventory.sh               <- Self-documenting: live tool scan every session
├── meta-hookify.py            <- Self-improving: repeated corrections → hook suggestions
├── 13 hooks                   <- Deterministic: format, test, block, guard (can't be skipped)
├── 6 rules                    <- Path-scoped: load only for matching file types
├── 29 skills                  <- On-demand: descriptions loaded, full content when invoked
├── 9 plugins                  <- Auto-loaded: extend Claude's capabilities
├── 8 agents                   <- Specialist subagents for complex work
└── 8 commands                 <- Workflow automation (/fix-issue, /tdd, etc.)
```

### How It Works

**Every session start:**
1. `session-start.sh` injects project context (lessons, todos, patterns)
2. `inventory.sh` scans all installed tools and injects the live list
3. `meta-hookify.py` checks for repeated corrections that should become hooks
4. Claude reads CLAUDE.md (76 lines) and knows when to use what

**Every code edit:**
1. `auto-format.py` runs black (Python) or prettier (JS/TS)
2. `auto-test.js` finds and runs the matching test file
3. `security-guidance` plugin warns about security anti-patterns

**Every commit:**
1. `commit-guard.js` enforces conventional commit format (`type(scope): description`)
2. `pre-commit-secrets.py` scans staged files for API keys and secrets
3. `block-secrets.py` blocks .env and credential files

**Self-improvement loop:**
```
You correct Claude → lessons.md updated → meta-hookify detects pattern
→ /hookify creates hook → hook enforces deterministically → no more corrections needed
```

### Key Design Decisions

| Decision | Why |
|----------|-----|
| **CLI-first over MCPs** | CLIs are faster, no auth overhead, no protocol latency. MCPs only where no CLI exists |
| **Hooks over instructions** | CLAUDE.md instructions can be ignored. Hooks run automatically — deterministic enforcement |
| **76-line CLAUDE.md** | Anthropic says: bloated CLAUDE.md files cause Claude to ignore instructions. Every line must prevent a mistake |
| **Self-documenting inventory** | No manual updates when tools change. `inventory.sh` scans the filesystem |
| **Path-scoped rules** | Python rules only load when editing `.py` files. No wasted context |
| **Skills on-demand** | Only descriptions loaded at startup (~2% context). Full content loads when invoked |

## Adapting for Mac/Linux

This setup was built on Windows 11 with Git Bash. To adapt:

1. **`rules/environment.md`**: Change paths to your OS equivalents
   - Python: `python3` or `python`
   - Node: `node` (usually in PATH on Mac/Linux)
   - Remove the Stripe WinGet PATH workaround

2. **`hooks/auto-format.py`**: Change line 15-17 to your Python/Node/NPX paths
   ```python
   PYTHON = "python3"
   NODE = "node"
   NPX = "npx"
   ```

3. **MCPs**: Remove `cmd /c` wrapper from MCP commands (see Mac/Linux install above)

4. **settings.json**: Update hook commands from `"C:\\Users\\...\\python.exe"` to `"python3"`

## FAQ

**Q: Will this work with Claude Code on Mac/Linux?**
A: Yes, with minor path changes (see "Adapting for Mac/Linux" above).

**Q: Do I need all 29 skills?**
A: No. Run the self-interview and Claude will remove skills that don't match your stack. The inventory is self-documenting — it only shows what's installed.

**Q: Will this slow down Claude Code?**
A: No. Skills load descriptions only (~2% context). Full content loads on-demand. Hooks are fast scripts. The 76-line CLAUDE.md is smaller than most people's.

**Q: How do I add new skills later?**
A: Drop a `SKILL.md` into `~/.claude/skills/your-skill-name/`. It auto-appears in the inventory next session. No manual config needed.

**Q: How do I update when this repo gets new features?**
A: `cd ~/.claude && git pull`. New skills, hooks, and commands will auto-appear. Check the changelog for any settings.json changes.

**Q: What if a hook is blocking something I want to do?**
A: Each hook can be temporarily bypassed by the user when prompted. Or remove it from `settings.json` hooks config.

## Contributing

Found a useful skill, hook, or improvement? PRs welcome. Keep the principles:
- Every CLAUDE.md line must prevent a mistake
- Hooks over instructions for critical rules
- CLI-first over MCPs
- Test it before committing

## Credits

Built by [Kenny Olofsson](https://github.com/kennyolofsson23-netizen) with Claude.

Skills and tools sourced from:
- [Anthropic Official Plugins](https://github.com/anthropics/claude-code)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) (22k+ stars)
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace)
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (41k+ stars)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [secondsky/claude-skills](https://github.com/secondsky/claude-skills)
- [openclaw/skills](https://github.com/openclaw/skills)
