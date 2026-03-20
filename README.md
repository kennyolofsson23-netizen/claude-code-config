# Claude Code God Setup

> The most comprehensive Claude Code configuration available. 97 skills, 11 plugins, 15 hooks, 46 agents, 8 commands — self-documenting, self-improving, and personalizable via a built-in interview prompt. Includes a full content production pipeline, GEO/SEO audit suite, and cross-project learnings from production AI pipeline work.

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
| **Skills** | 97 | Security, TDD, architecture (DDD/SDD), UI/UX design, React, database, git, research, SEO (16 skills), GEO audit suite (14 skills), video (Remotion), voiceover (ElevenLabs), marketing suite, ads (6 platforms), email marketing, viral content, social carousels, accessibility (WCAG), performance, web quality |
| **Plugins** | 11 | feature-dev, frontend-design, code-review (5 parallel agents), pr-review-toolkit, security-guidance, hookify, ralph-loop (autonomous iteration), superpowers (TDD/debugging), ui-ux-pro-max (50+ styles, 161 palettes), last30days (trend research), accesslint |
| **Agents** | 46 | 8 core dev (architect, code-reviewer, feature-builder, fullstack-engineer, qa-runner, test-writer, error-detective, refactoring-specialist), 13 SEO/marketing (seo-content, seo-technical, geo-*, market-analyst, trend-scout), 8 quality/review (security, performance, UX, correctness), 4 creative (ui-designer, creative-visionary, devils-advocate, synthesizer), 3 business (distribution-analyst, growth-reviewer, monetization-strategist) + more |
| **Commands** | 8 | `/fix-issue` (GitHub issue to PR), `/tdd`, `/test-fix`, `/diagram`, `/checkpoint`, `/wrap-up`, `/orchestrate`, `/qa-setup` |
| **Hooks** | 15 | Auto-format, auto-lint, auto-test, secret blocking, commit guards, dev server blocking, MD creation blocking, agent schema validation, self-documenting inventory, meta-hookification, session lifecycle |
| **Rules** | 6 | Environment, Python, TypeScript, git safety, coding style, error handling |

## Quick Start

### One-Prompt Install (Recommended for Beginners)

If you have **Claude Code** and **Git** installed, paste this into a Claude Code session and let Claude do everything:

```
I need you to install Kenny's Claude Code God Setup for me. I'm a complete beginner — walk me through everything step by step. Don't assume I know anything.

Here's what I already have installed:
- Claude Code (this tool)
- Git Bash

Here's the plan — do each step one at a time, explain what you're doing, and wait for my OK before moving to the next:

1. BACKUP & CLONE: ~/.claude already exists (Claude Code creates it). You CANNOT clone into it directly.
   Instead:
   a. Clone the repo to a temp folder:
      git clone https://github.com/kennyolofsson23-netizen/claude-code-config.git /tmp/claude-god-setup
   b. Back up my existing ~/.claude to ~/.claude-backup:
      cp -r ~/.claude ~/.claude-backup
   c. Copy ALL files from the cloned repo into ~/.claude (overwrite, but preserve existing files like plugins/, .mcp.json, settings.json, settings.local.json):
      rsync -av --exclude='.git' /tmp/claude-god-setup/ ~/.claude/
      (If rsync isn't available, use: cp -rn /tmp/claude-god-setup/* ~/.claude/ && cp -rn /tmp/claude-god-setup/.* ~/.claude/ 2>/dev/null)
   d. Initialize git tracking in ~/.claude:
      cd ~/.claude && git init && git remote add origin https://github.com/kennyolofsson23-netizen/claude-code-config.git
   e. Clean up:
      rm -rf /tmp/claude-god-setup

2. DEPENDENCIES: Check what I already have installed (node, npm, python, pip). Install what's missing:
   - npm install -g prettier
   - pip install black
   Skip optional tools (pgcli, stripe, uipro-cli) — I can add them later.

3. PLUGINS: These are REAL Claude Code CLI commands — they work.
   Install the Claude Code plugins one by one. If any fail, tell me what went wrong and skip it — don't stop the whole process:

   First add ALL marketplaces (including the official one — it's NOT pre-installed):
   - claude plugin marketplace add anthropics/claude-plugins-official
   - claude plugin marketplace add obra/superpowers-marketplace
   - claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
   - claude plugin marketplace add mvanhorn/last30days-skill
   - claude plugin marketplace add accesslint/claude-marketplace

   Then install plugins:
   - claude plugin install feature-dev@claude-plugins-official
   - claude plugin install frontend-design@claude-plugins-official
   - claude plugin install code-review@claude-plugins-official
   - claude plugin install pr-review-toolkit@claude-plugins-official
   - claude plugin install security-guidance@claude-plugins-official
   - claude plugin install hookify@claude-plugins-official
   - claude plugin install ralph-loop@claude-plugins-official
   - claude plugin install superpowers@superpowers-marketplace
   - claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill
   - claude plugin install last30days@last30days-skill
   - claude plugin install accesslint@accesslint

4. MCPs: Detect my OS and install the MCP servers with the right syntax:
   - context7 (documentation lookup)
   - playwright (browser testing)
   - sequential-thinking (reasoning)
   - sentry (error tracking, HTTP transport)
   On Windows use the "cmd /c" wrapper. On Mac/Linux use npx directly.

5. SETTINGS: Read every file in ~/.claude/hooks/ and create my settings.json:
   - Auto-detect my Python, Node, and NPX paths
   - Wire ALL hooks to the correct event triggers using MY paths
   - Show me what you created

6. VERIFY: Tell me to close this session and reopen Claude Code, then run /qa-setup. Explain that some failures are normal (optional tools).

7. PERSONALIZE: After verification, run the self-interview from the README to tailor everything to me.

Important rules:
- Explain everything like I'm 5
- If something fails, tell me why and offer a fix — don't just stop
- Don't delete or skip anything without asking me
- After each step, tell me what just happened and what's next
```

That's it — Claude handles the rest. If you prefer to install manually, follow the steps below.

### Prerequisites (Manual Install)

- [Claude Code](https://code.claude.com) installed and working
- Git, Node.js 18+, Python 3.10+
- GitHub CLI (`gh`) authenticated

### 1. Backup & Clone

`~/.claude` already exists (Claude Code creates it automatically). You can't clone directly into it.

```bash
# Clone to a temp folder
git clone https://github.com/kennyolofsson23-netizen/claude-code-config.git /tmp/claude-god-setup

# Back up your existing config
cp -r ~/.claude ~/.claude-backup

# Copy setup files into ~/.claude (won't overwrite your settings.json, plugins/, etc.)
rsync -av --exclude='.git' /tmp/claude-god-setup/ ~/.claude/

# Set up git tracking for updates
cd ~/.claude && git init && git remote add origin https://github.com/kennyolofsson23-netizen/claude-code-config.git

# Clean up
rm -rf /tmp/claude-god-setup
```

> **Note:** If you don't have `rsync`, use: `cp -rn /tmp/claude-god-setup/* ~/.claude/ && cp -rn /tmp/claude-god-setup/.* ~/.claude/ 2>/dev/null`

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

> These are real Claude Code CLI commands (`claude plugin --help` to verify). If your Claude says they don't exist, update Claude Code to the latest version.

```bash
# Add ALL marketplaces first (including official — it's NOT pre-installed)
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill
claude plugin marketplace add mvanhorn/last30days-skill
claude plugin marketplace add accesslint/claude-marketplace

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
claude plugin install last30days@last30days-skill
claude plugin install accesslint@accesslint
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

The `settings.json` file is gitignored (contains API keys). You need to create it with the hook wiring. Start a Claude Code session and paste this exact prompt:

```
I just cloned the Claude Code God Setup into ~/.claude. I need you to set up my settings.json.

1. Read every file in ~/.claude/hooks/ to see what hooks exist
2. Detect my OS and find my Python, Node, and NPX paths (run "where python" or "which python3", "which node", "which npx")
3. Create ~/.claude/settings.json that wires ALL hooks to the correct event triggers, using MY system's paths
4. Make sure Python hooks use my full Python path, JS hooks use node, and bash hooks use bash
5. Show me what you created and explain any warnings
```

This lets Claude do the hard work of detecting your system and wiring everything up.

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

Start a **new** Claude Code session (close and reopen) and type:

```
/qa-setup
```

This runs a health check on every hook, skill, plugin, MCP, and CLI tool. Don't worry if a few things fail — most failures are optional tools you haven't installed yet. The important ones are hooks and core skills.

### 9. Personalize

**This is the most important step.** The self-interview below lets Claude tailor everything to your experience level and stack. It takes about 5 minutes — just answer honestly, "I don't know" is a perfectly valid answer.

## Personalize: Self-Interview

This setup is a foundation — it needs to be adapted to YOU. Copy this prompt into a Claude Code session after installing:

```
I just installed the Claude Code God Setup from github.com/kennyolofsson23-netizen/claude-code-config.

I need you to personalize it for me. Interview me with these questions ONE AT A TIME.
Wait for my answer before asking the next question.
Keep questions conversational — if I don't understand something, explain it simply.
It's totally fine if I answer "I don't know" or "whatever you recommend" — just pick sensible defaults for me.

After all questions, summarize what you learned and show me the exact changes you'll make in plain language. Ask for my approval before writing anything.

Questions:

1. ABOUT YOU: What do you do? (developer, designer, student, founder, just curious, etc.) How much coding experience do you have — beginner, intermediate, or experienced?

2. TECH STACK: What languages/frameworks do you use or want to learn? (e.g., Python, JavaScript, React, Node.js — or "I'm not sure yet")

3. PROJECTS: What are you building or planning to build? Even a rough idea is fine. (e.g., "a website for my business", "learning to code", "a SaaS app")

4. SOLO OR TEAM: Do you work alone or with others?

5. WHAT ANNOYS YOU: Have you used AI coding tools before? What went wrong or annoyed you? (e.g., "it kept making stuff up", "it was too slow", "never used one")

6. SPEED vs QUALITY: When Claude writes code for you, should it prioritize being fast and scrappy, or thorough and careful? (Most people start with "fast" and tighten up later — that's fine)

7. DESIGN: Do you care about how things look? Will you be building user interfaces, or mostly backend/data work?

8. DEPLOYMENT: Where do you host your projects? (Vercel, AWS, Netlify, Railway, "I don't know yet" — all valid answers)

9. GOALS: What's the dream? (Learn to code, ship a product, start a business, get a job, build something cool for fun?)

10. ENVIRONMENT: What computer are you on? (Windows/Mac/Linux) — Claude will auto-detect the rest

11. SKILL FOCUS: Which of these areas interest you? Pick all that apply:
    - Web development (frontend/backend)
    - Mobile apps
    - APIs and backend services
    - DevOps and infrastructure
    - Data science / ML
    - Marketing and content creation
    - SEO (search engine optimization)
    - Security
    - Design and UI/UX

Based on my answers:
1. Update ~/.claude/CLAUDE.md to match my workflow and skill level
2. Update ~/.claude/rules/environment.md with my OS and correct paths (auto-detect what you can)
3. Save my profile to memory so you remember me in future sessions
4. Tell me which skills/agents I probably won't need (see the "What to Customize" section in the README) — but don't delete anything without asking me first
5. If I'm a beginner, simplify CLAUDE.md — remove jargon, lower the test coverage target, add more explanatory comments
6. Add any project-specific rules I need
```

## What to Customize

### By Role

| If you are a... | Keep these | Consider removing | Active skills |
|-----------------|-----------|-------------------|:---:|
| **Frontend dev** | react-best-practices, tailwind-v4-shadcn, composition-patterns, performance, webapp-testing, ui-ux-pro-max plugin | All SEO/GEO skills, email-marketing-bible, claude-ads, postgres-best-practices | ~20 |
| **Backend dev** | postgres-best-practices, security-audit, owasp-llm-top10, property-based-testing, ddd | All GEO skills, frontend-design plugin, instagram-thread-carousel, postnitro-carousel | ~18 |
| **Fullstack dev** | Keep most, remove what you don't use after 2 weeks | GEO/SEO suite (unless doing marketing too) | ~35 |
| **Founder/indie hacker** | Keep everything — you'll use more than you think | Nothing yet — revisit after 2 weeks | ~50+ |
| **Marketer/content** | All SEO/GEO, content-to-social, create-viral-content, email-marketing-bible, claude-ads, social-content | ddd, sdd, property-based-testing, postgres-best-practices | ~30 |
| **Student** | best-practices, code-review, qa, security-audit, react-best-practices or postgres-best-practices | Marketing suite, GEO suite, ad platforms, email-marketing-bible | ~12 |

### What You MUST Customize

| File | What to change | Why |
|------|---------------|-----|
| `settings.json` | Hook commands, API keys, MCP config | Contains all wiring — created during install |
| `CLAUDE.md` | Your workflow preferences, test targets | This is YOUR instruction set |
| `rules/environment.md` | Already generic — personalize step adds your specifics | Auto-detects OS and paths |

### What You Can Leave Alone

- **`skills/`** — unused skills cost nothing (descriptions only, ~2% context)
- **`hooks/`** — all hooks are useful regardless of stack
- **`agents/`** — agents only activate when invoked
- **`docs/learnings.md`** — useful patterns for everyone

## Troubleshooting

### Windows
- **MCPs fail to start**: Use the `cmd /c` wrapper for all MCP commands (see step 5 above)
- **Python hooks fail**: Verify the full Python path in `settings.json` matches your install — run `where python` to find it
- **Git Bash can't find node/npm**: Use full paths like `"/c/Program Files/nodejs/node.exe"` or add to your `.bashrc`

### Mac/Linux
- **`python` not found**: Use `python3` everywhere — update `rules/environment.md`, `hooks/auto-format.py` lines 15-17, and `settings.json`
- **Permission denied on hooks**: Run `chmod +x hooks/*.sh scripts/*.sh`
- **NPX commands hang**: Clear the cache with `npx clear-npx-cache` and retry

### General
- **"Can't clone into ~/.claude — folder already exists"**: This is expected. `~/.claude` is created automatically by Claude Code. Follow step 1 above — clone to a temp folder, then copy files over
- **"Plugin commands don't exist"**: They do — `claude plugin` is a real CLI command. Run `claude plugin --help` to verify. If it's not there, update Claude Code: `claude update`
- **Plugin install fails**: Make sure you've added the marketplace first (`claude plugin marketplace add ...`), then install the plugin
- **`/qa-setup` reports failures**: Read the specific failure — most are missing CLI tools (install them) or missing API keys (optional — skip if you don't need that feature)
- **Which API keys are required?**: None are strictly required. `GEMINI_API_KEY` enables AI image generation. `STRIPE_API_KEY` enables Stripe CLI. `ELEVENLABS_API_KEY` enables voiceover. Everything else works without keys

## Architecture

```
CLAUDE.md (77 lines)           <- What Claude must always know
├── inventory.sh               <- Self-documenting: live tool scan every session
├── meta-hookify.py            <- Self-improving: repeated corrections → hook suggestions
├── 15 hooks                   <- Deterministic: format, test, lint, block, guard (can't be skipped)
├── 6 rules                    <- Path-scoped: load only for matching file types
├── 97 skills                  <- On-demand: descriptions loaded, full content when invoked
├── 11 plugins                 <- Auto-loaded: extend Claude's capabilities
├── 46 agents                  <- Specialist subagents for complex work
├── 8 commands                 <- Workflow automation (/fix-issue, /tdd, etc.)
├── 66 scripts                 <- Agentic SEO/GEO Python tools
└── 236 tests                  <- Hook test suite with CI/CD
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

### What's New (March 2026)

| Addition | Details |
|----------|---------|
| **GEO/SEO Suite** | 14 GEO skills (AI search optimization), 16 SEO skills, 13 specialized agents, 66 Python scripts for agentic audits |
| **46 Agents** | Up from 8 — specialized agents for SEO, marketing, growth, accessibility, quality review, and business analysis |
| **236 Tests + CI/CD** | Full test suite for all hooks (JS + Python), GitHub Actions on Windows |
| **Cross-Project Learnings** | Battle-tested patterns from production AI pipeline work (see `docs/learnings.md`) |
| **Accessibility** | AccessLint plugin, WCAG audit skill, contrast checking |
| **Auto-lint Hook** | ESLint + tsc run automatically on code edits |
| **Agent Schema Validation** | Hook validates YAML frontmatter on all agent files |

### Content Production Pipeline

Built-in content factory — research, create, and distribute:

| Step | Tool | Type |
|------|------|------|
| **Trend research** | Last 30 Days plugin | Reddit, X, TikTok, Brave, Bluesky |
| **AI images** | Nano Banana Pro | Gemini-powered generation (needs GEMINI_API_KEY) |
| **Video creation** | Remotion skill (37 rules) | React-based programmatic video |
| **Voiceover** | ElevenLabs MCP | 70+ languages, voice cloning (needs ELEVENLABS_API_KEY) |
| **Viral hooks** | Create Viral Content | 150+ hook formulas, thumbnail psychology |
| **Marketing strategy** | AI Marketing Suite | 15 skills, 5 agents — copy, email, landing, ads, SEO |
| **Ad campaigns** | claude-ads | 186 audit checks across Google, Meta, TikTok, LinkedIn, YouTube |
| **Email marketing** | Email Marketing Bible | 55K-word knowledge base, 19 industry playbooks |
| **Social carousels** | Instagram Thread Carousel + PostNitro | Thread-to-carousel PNGs, AI-generated slides |
| **Content repurposing** | Content-to-Social + Social Content | Transform any content into platform-optimized posts |

### Key Design Decisions

| Decision | Why |
|----------|-----|
| **CLI-first over MCPs** | CLIs are faster, no auth overhead, no protocol latency. MCPs only where no CLI exists |
| **Hooks over instructions** | CLAUDE.md instructions can be ignored. Hooks run automatically — deterministic enforcement |
| **77-line CLAUDE.md** | Anthropic says: bloated CLAUDE.md files cause Claude to ignore instructions. Every line must prevent a mistake |
| **Self-documenting inventory** | No manual updates when tools change. `inventory.sh` scans the filesystem |
| **Path-scoped rules** | Python rules only load when editing `.py` files. No wasted context |
| **Skills on-demand** | Only descriptions loaded at startup (~2% context). Full content loads when invoked |

## Adapting for Mac/Linux

This setup now auto-detects paths and works cross-platform. The only manual step:

1. **MCPs**: Use the Mac/Linux MCP commands (no `cmd /c` wrapper) — see install step 5 above
2. **`settings.json`**: Update hook commands from Windows Python path to `"python3"` — the install prompt handles this automatically

## FAQ

**Q: Will this work with Claude Code on Mac/Linux?**
A: Yes, with minor path changes (see "Adapting for Mac/Linux" above).

**Q: Do I need all 97 skills?**
A: No. See the "What to Customize" table for role-based guidance. Most users actively use 12-35 skills. Unused skills cost nothing — they're descriptions only (~2% context). Run the self-interview and Claude will tailor things to your stack.

**Q: Will this slow down Claude Code?**
A: No. Skills load descriptions only (~2% context). Full content loads on-demand. Hooks are fast scripts. The 77-line CLAUDE.md is smaller than most people's.

**Q: How do I add new skills later?**
A: Drop a `SKILL.md` into `~/.claude/skills/your-skill-name/`. It auto-appears in the inventory next session. No manual config needed.

**Q: Is it safe to clone this into ~/.claude?**
A: `~/.claude` is Claude Code's config folder. This repo only adds files (skills, hooks, agents, rules) — it doesn't modify Claude Code itself. Your `settings.json`, `plugins/`, and `.mcp.json` are gitignored and won't be overwritten. You can always restore from `~/.claude-backup`. Review the repo contents before installing if you want — it's all plaintext markdown and scripts.

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
