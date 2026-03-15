# Claude Code God Setup

The most comprehensive Claude Code configuration available. Built for solo founders and developers who want Claude as their autonomous engineering team.

## What's Included

| Category | Count | What |
|----------|-------|------|
| **Skills** | 29 | Security, testing, architecture, design, database, git, research, UI/UX |
| **Plugins** | 9 | feature-dev, frontend-design, code-review, pr-review-toolkit, security-guidance, hookify, ralph-loop, superpowers, ui-ux-pro-max |
| **Agents** | 8 | error-detective, fullstack-engineer, refactoring-specialist, task-coordinator, test-architect, pr-reviewer, qa, researcher |
| **Commands** | 8 | /fix-issue, /tdd, /test-fix, /diagram, /checkpoint, /wrap-up, /orchestrate, /qa-setup |
| **Hooks** | 13 | Auto-format, auto-test, secret blocking, commit guards, dev server blocking, self-documenting inventory, meta-hookification |
| **Rules** | 6 | Environment, Python, TypeScript, git safety, coding style, error handling |
| **CLIs** | 5 | gh, stripe, vercel, pgcli, playwright |
| **MCPs** | 4 | Context7, Playwright, Sequential Thinking, Sentry |

## Architecture

```
CLAUDE.md (76 lines)          <- Global instructions, every line prevents a mistake
├── inventory.sh              <- Self-documenting: scans all tools on every session start
├── meta-hookify.py           <- Self-improving: detects repeated corrections, suggests hooks
├── 13 hooks                  <- Deterministic enforcement (format, test, block, guard)
├── 6 rules                   <- Path-scoped, load only when touching matching files
├── 29 skills                 <- On-demand, descriptions only until invoked
├── 9 plugins                 <- Auto-loaded capabilities
├── 8 agents                  <- Specialist subagents for complex work
└── 8 commands                <- Workflow automation (/fix-issue, /tdd, etc.)
```

### Key Design Principles

- **CLI-first**: Always prefer CLI tools over MCPs. Faster, more reliable, no auth overhead
- **Self-documenting**: `inventory.sh` scans the filesystem on every session — new tools auto-appear
- **Self-improving**: `meta-hookify.py` detects repeated corrections and suggests hooks
- **Enterprise quality**: 100% test coverage target, TDD always, zero shortcuts
- **Context-efficient**: 76-line CLAUDE.md, every line passes the test "would removing this cause a mistake?"
- **Deterministic enforcement**: Critical rules are hooks (run automatically), not instructions (might be ignored)

## Installation

### Prerequisites
- [Claude Code](https://claude.com/code) installed
- Git, Node.js, Python 3.11+
- Windows 11 with Git Bash (adaptable to Mac/Linux — change paths in `rules/environment.md`)

### Quick Install

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/claude-code-config.git ~/.claude

# 2. Install CLI tools
npm install -g prettier uipro-cli
pip install black pgcli
winget install Stripe.StripeCli  # Windows
# brew install stripe/stripe-cli/stripe  # Mac

# 3. Install plugins
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin install feature-dev@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install pr-review-toolkit@claude-plugins-official
claude plugin install security-guidance@claude-plugins-official
claude plugin install hookify@claude-plugins-official
claude plugin install ralph-loop@claude-plugins-official
claude plugin install superpowers@superpowers-marketplace
claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill

# 4. Add MCPs (adapt cmd /c for Mac/Linux)
claude mcp add -s user --transport stdio context7 -- cmd /c "npx -y @upstash/context7-mcp"
claude mcp add -s user --transport stdio playwright -- cmd /c "npx -y @playwright/mcp@latest"
claude mcp add -s user --transport stdio sequential-thinking -- cmd /c "npx -y @modelcontextprotocol/server-sequential-thinking"
claude mcp add -s user --transport http sentry https://mcp.sentry.dev/mcp

# 5. Set API keys in settings.json (already gitignored)
# Add GEMINI_API_KEY for nano-banana-pro image generation
# Add STRIPE_API_KEY for Stripe CLI access

# 6. Personalize — run the self-interview (see below)
```

### After Install

1. Start a new Claude Code session
2. Verify everything works: `/qa-setup`
3. Run the self-interview prompt below to personalize

## Personalize: Self-Interview Prompt

Copy this into your first Claude Code session after installing. Claude will interview you and adapt the entire setup to your specific needs, workflow, and goals.

```
I just installed the Claude Code God Setup. I need you to personalize it for me.

Interview me with these questions one at a time. Wait for my answer before asking the next one. After all questions, update the following files based on my answers:
- ~/.claude/CLAUDE.md (adapt instructions to my workflow)
- Memory files in the appropriate project memory directory
- Any rules that need adjusting

Questions to ask me:

1. What's your background? (developer, designer, PM, founder, student, etc.) What languages and frameworks do you know?

2. What are you building? Describe your current project(s) — tech stack, stage, what it does.

3. Do you work solo or with a team? If team, what's their experience level?

4. What's your biggest frustration with AI coding assistants? What do they get wrong most often for you?

5. How do you feel about code quality vs shipping speed? Where's your sweet spot?

6. Do you use any design tools (Figma, Sketch) or do you design in code?

7. What's your deployment setup? (Vercel, AWS, Railway, etc.) How much deploy autonomy should Claude have?

8. Do you use any project management tools? (Linear, Jira, Notion, GitHub Issues, just todo.md?)

9. What's your testing philosophy? (unit-heavy, integration-heavy, E2E, "just test the important stuff"?)

10. What timezone are you in? When do you typically work on this?

11. What's your goal? (learning, shipping a product, financial independence, fun, career growth?)

After the interview, summarize what you learned and show me the changes you'll make to the setup. Ask for approval before writing.
```

## Directory Structure

```
~/.claude/
├── CLAUDE.md                  # Global instructions (76 lines)
├── README.md                  # This file
├── .gitignore                 # Excludes secrets, cache, personal data
│
├── agents/                    # Specialist subagents
│   ├── error-detective.md     # Stack trace analysis, root cause
│   ├── fullstack-engineer.md  # End-to-end feature delivery
│   ├── pr-reviewer.md         # PR review automation
│   ├── qa.md                  # Test execution
│   ├── refactoring-specialist.md  # Systematic refactoring
│   ├── researcher.md          # Research and investigation
│   ├── task-coordinator.md    # Multi-agent orchestration
│   └── test-architect.md      # Test strategy design
│
├── commands/                  # Slash commands (/command-name)
│   ├── checkpoint.md          # Save session progress
│   ├── diagram.md             # Generate Mermaid diagrams
│   ├── fix-issue.md           # GitHub issue → branch → fix → PR
│   ├── orchestrate.md         # Multi-step workflow execution
│   ├── qa-setup.md            # Full setup health check
│   ├── tdd.md                 # Red-Green-Refactor cycle
│   ├── test-fix.md            # Diagnose and fix failing tests
│   └── wrap-up.md             # Structured session end
│
├── hooks/                     # Deterministic enforcement (13 hooks)
│   ├── auto-format.py         # PostToolUse: black + prettier
│   ├── auto-test.js           # PostToolUse: run matching test on edit
│   ├── block-dangerous.py     # PreToolUse: blocks rm -rf, force push, etc.
│   ├── block-dev-server.js    # PreToolUse: blocks orphaned dev servers
│   ├── block-md-creation.js   # PreToolUse: warns on random .md creation
│   ├── block-secrets.py       # PreToolUse: blocks .env, credentials
│   ├── commit-guard.js        # PreToolUse: enforces conventional commits
│   ├── inventory.sh           # SessionStart: self-documenting tool scan
│   ├── meta-hookify.py        # SessionStart: detects correction patterns
│   ├── post-compact.sh        # PostCompact: re-injects context
│   ├── pre-commit-secrets.py  # PreToolUse: scans staged files for secrets
│   ├── resume-context.sh      # SessionStart: resume context injection
│   ├── session-start.sh       # SessionStart: lessons + todo + inventory
│   └── stop-verify.py         # Stop: warns about unchecked todos
│
├── rules/                     # Path-scoped rules (auto-load by file type)
│   ├── coding-style.md        # File/function size limits
│   ├── environment.md         # OS, paths, CLI locations
│   ├── error-handling.md      # Anti-patterns to avoid
│   ├── git-safety.md          # Branch rules, no force push
│   ├── python.md              # pytest, black, utf-8
│   └── typescript.md          # tsc, pnpm, prettier
│
├── skills/                    # 29 on-demand skills (see inventory)
│   ├── audit-context-building/
│   ├── code-review/
│   ├── composition-patterns/
│   ├── ddd/
│   ├── design-review/
│   ├── design-system-creation/
│   ├── firecrawl/
│   ├── gh-address-comments/
│   ├── gh-fix-ci/
│   ├── interaction-design/
│   ├── kaizen/
│   ├── nano-banana-pro/
│   ├── postgres-best-practices/
│   ├── property-based-testing/
│   ├── qa/
│   ├── react-best-practices/
│   ├── reflexion/
│   ├── research/
│   ├── sdd/
│   ├── security-audit/
│   ├── security-review/
│   ├── security-threat-model/
│   ├── semgrep-rule-creator/
│   ├── seo-content/
│   ├── skill-creator/
│   ├── tailwind-v4-shadcn/
│   ├── tool-discovery/
│   ├── web-design-guidelines/
│   └── webapp-testing/
│
└── settings.json              # Hooks config + API keys (GITIGNORED)
```

## How It Works

### Every Session
1. `session-start.sh` fires → injects `tasks/lessons.md`, `tasks/todo.md`, `tasks/patterns.log`
2. `inventory.sh` fires → scans all skills, agents, commands, plugins, hooks, rules, CLIs
3. `meta-hookify.py` fires → checks for repeated corrections that should become hooks
4. CLAUDE.md loads → 76 lines of instructions that tell Claude *when* to use *what*
5. Claude sees the full inventory and auto-invokes matching tools

### Every Code Edit
1. `auto-format.py` → runs black (Python) or prettier (JS/TS)
2. `auto-test.js` → finds and runs the matching test file
3. `security-guidance` plugin → warns about security anti-patterns

### Every Commit
1. `commit-guard.js` → enforces conventional commit format
2. `pre-commit-secrets.py` → scans for leaked secrets
3. `block-secrets.py` → blocks .env and credential files

### Self-Improvement Loop
```
Correction → lessons.md → meta-hookify detects pattern → /hookify creates hook → deterministic enforcement
```

## Credits

Built by Kenny Olofsson with Claude. Skills sourced from:
- [Anthropic Official Plugins](https://github.com/anthropics/claude-code)
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills)
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- [obra/superpowers-marketplace](https://github.com/obra/superpowers-marketplace)
- [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills)
- [secondsky/claude-skills](https://github.com/secondsky/claude-skills)
- [openclaw/skills](https://github.com/openclaw/skills)
