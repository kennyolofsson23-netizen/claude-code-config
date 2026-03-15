### Browser - Cloud browser sessions

Launch remote Chromium sessions for interactive page operations. Sessions persist across commands and agent-browser (40+ commands) is pre-installed in every sandbox.

#### Shorthand (Recommended)

Auto-launches a session if needed, auto-prefixes agent-browser — no setup required:

```bash
firecrawl browser "open https://example.com"
firecrawl browser "snapshot"
firecrawl browser "click @e5"
firecrawl browser "fill @e3 'search query'"
firecrawl browser "scrape" -o .firecrawl/browser-scrape.md
```

#### Execute mode

Explicit form with `execute` subcommand. Commands are still sent to agent-browser automatically:

```bash
firecrawl browser execute "open https://example.com" -o .firecrawl/browser-result.txt
firecrawl browser execute "snapshot" -o .firecrawl/browser-result.txt
firecrawl browser execute "click @e5"
firecrawl browser execute "scrape" -o .firecrawl/browser-scrape.md
```

#### Playwright & Bash modes

Use `--python`, `--node`, or `--bash` for direct code execution (no agent-browser auto-prefix):

```bash
# Playwright Python
firecrawl browser execute --python 'await page.goto("https://example.com")
print(await page.title())' -o .firecrawl/browser-result.txt

# Playwright JavaScript
firecrawl browser execute --node 'await page.goto("https://example.com"); await page.title()' -o .firecrawl/browser-result.txt

# Arbitrary bash in the sandbox
firecrawl browser execute --bash 'ls /tmp' -o .firecrawl/browser-result.txt

# Explicit agent-browser via bash (equivalent to default mode)
firecrawl browser execute --bash "agent-browser snapshot"
```

#### Session management

```bash
# Launch a session explicitly (shorthand does this automatically)
firecrawl browser launch-session -o .firecrawl/browser-session.json --json

# Launch with custom TTL and live view streaming
firecrawl browser launch-session --ttl 600 --stream -o .firecrawl/browser-session.json --json

# Execute against a specific session
firecrawl browser execute --session <id> "snapshot" -o .firecrawl/browser-result.txt

# List all sessions
firecrawl browser list --json -o .firecrawl/browser-sessions.json

# List only active sessions
firecrawl browser list active --json -o .firecrawl/browser-sessions.json

# Close last session
firecrawl browser close

# Close a specific session
firecrawl browser close --session <id>
```

**Browser Options:**

- `--ttl <seconds>` - Total session lifetime (default: 300)
- `--ttl-inactivity <seconds>` - Auto-close after inactivity
- `--stream` - Enable live view streaming
- `--python` - Execute as Playwright Python code
- `--node` - Execute as Playwright JavaScript code
- `--bash` - Execute bash commands in the sandbox (agent-browser pre-installed, CDP_URL auto-injected)
- `--session <id>` - Target specific session (default: last launched session)
- `-o, --output <path>` - Save to file

**Modes:** By default (no flag), commands are sent to agent-browser. `--python`, `--node`, and `--bash` are mutually exclusive.

**Notes:**

- Shorthand auto-launches a session if none exists — no need to call `launch-session` first
- Session auto-saves after launch — no need to pass `--session` for subsequent commands
- In Python/Node mode, `page`, `browser`, and `context` objects are pre-configured (no setup needed)
- Use `print()` to return output from Python execution

**Core agent-browser commands:**

| Command              | Description                            |
| -------------------- | -------------------------------------- |
| `open <url>`         | Navigate to a URL                      |
| `snapshot`           | Get accessibility tree with `@ref` IDs |
| `screenshot`         | Capture a PNG screenshot               |
| `click <@ref>`       | Click an element by ref                |
| `type <@ref> <text>` | Type into an element                   |
| `fill <@ref> <text>` | Fill a form field (clears first)       |
| `scrape`             | Extract page content as markdown       |
| `scroll <direction>` | Scroll up/down/left/right              |
| `wait <seconds>`     | Wait for a duration                    |
| `eval <js>`          | Evaluate JavaScript on the page        |
