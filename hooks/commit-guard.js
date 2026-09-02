let raw = "";
try {
  raw = require("fs").readFileSync(0, "utf8");
} catch (_) {}
const data = JSON.parse(raw || "{}");
const toolInput = data.tool_input || {};
const command = toolInput.command || "";

if (!command.includes("git commit")) process.exit(0);

// ── Message extraction ──────────────────────────────────────────────────────
// A naive /-m\s+["']([^"']+)["']/ stops at the FIRST inner quote, so the very
// common heredoc form
//     git commit -m "$(cat <<'EOF'
//     feat(x): real subject
//     EOF
//     )"
// used to yield the message `$(cat <<` and get rejected as non-conventional.
// Extraction now handles heredocs, and is quote-aware for everything else.

const HEREDOC = /<<-?\s*(['"]?)([A-Za-z_][A-Za-z0-9_]*)\1\s*\r?\n([\s\S]*?)\r?\n[ \t]*\2[ \t]*(?:\r?\n|$)/;

function readQuoted(s, i) {
  const q = s[i];
  let out = "";
  i += 1;
  while (i < s.length) {
    const c = s[i];
    // Backslash escapes only apply inside double quotes in POSIX shells.
    if (c === "\\" && q === '"' && i + 1 < s.length) {
      out += s[i + 1];
      i += 2;
      continue;
    }
    if (c === q) return out;
    out += c;
    i += 1;
  }
  return null; // unterminated quote — cannot trust the parse
}

function readUnquoted(s, i) {
  let out = "";
  while (i < s.length && !/\s/.test(s[i])) {
    out += s[i];
    i += 1;
  }
  return out || null;
}

function extractMessage(cmd) {
  // 1. Heredoc body wins — it is the literal message text, whether it arrives
  //    via `-m "$(cat <<'EOF' … EOF)"` or `git commit -F- <<'EOF' … EOF`.
  const here = cmd.match(HEREDOC);
  if (here) return here[3];

  // 2. Otherwise find -m / --message and read its argument quote-aware.
  const flag = cmd.match(/(?:^|\s)(?:-m|--message)(=|\s+)/);
  if (!flag) return null;
  const start = flag.index + flag[0].length;
  const ch = cmd[start];
  if (ch === '"' || ch === "'") return readQuoted(cmd, start);
  return readUnquoted(cmd, start);
}

const message = extractMessage(command);
if (message === null) process.exit(0);

// Only the subject line is subject to the conventional-commit rules.
const msg = message.split(/\r?\n/)[0].trim();
if (!msg) process.exit(0);

// An unresolved command substitution means the real subject is not knowable
// statically — skip rather than block a commit we cannot actually read.
if (/\$\(|\$\{/.test(msg)) process.exit(0);

const errors = [];

const TYPES = "feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert";
const conventionalPattern = new RegExp(`^(${TYPES})(\\(.+\\))?!?:\\s.+`);
if (!conventionalPattern.test(msg)) {
  errors.push("Message does not follow conventional commit format: type(scope): description");
}

if (msg.length > 72) {
  errors.push(`Subject line is ${msg.length} chars (max 72)`);
}

if (msg.endsWith(".")) {
  errors.push("Subject line should not end with a period");
}

// ── Description casing ──────────────────────────────────────────────────────
// The lowercase rule still catches real sloppiness ("fix(web): Fixed the bug"),
// but must not fire on acronyms or proper nouns that are legitimately
// capitalised: "feat(api): ATG payouts…", "fix(stripe): Stripe webhooks…".
const KNOWN_NAMES = new Set([
  "Alembic", "Anthropic", "Chrome", "Claude", "Cloudflare", "Docker", "ESLint",
  "Expo", "FastAPI", "Firefox", "Gmail", "GitHub", "Google", "Groq", "Isotonic",
  "Jest", "Kenny", "Klarna", "Llama", "Loopia", "Next", "Next.js", "NextAuth",
  "Node", "OpenAI", "Playwright", "Plausible", "Postgres", "PostgreSQL",
  "Prettier", "Pydantic", "Python", "Railway", "React", "Redis", "Resend",
  "SQLAlchemy", "Safari", "Sentry", "Slack", "Stripe", "Tailwind", "Turborepo",
  "Uvicorn", "Vercel", "Vitest", "Webpack", "Windows", "XGBoost", "CatBoost",
  // Domain / proper nouns
  "Benter", "Bergen", "Elitloppet", "Nordic", "Solvalla", "Stockholm",
  "Swedish", "Travmaskinen", "Åby",
]);

// A leading all-caps run of 2+ chars: ATG, URL, ML, CI, V85, GS75, JWT, SQL…
const ACRONYM = /^[A-ZÅÄÖ][A-ZÅÄÖ0-9]+(?![a-zåäö])/;

const description = msg.replace(new RegExp(`^(${TYPES})(\\(.+\\))?!?:\\s`), "");
const firstChar = description[0];
// Only judge casing when the description actually starts with a capital
// LETTER — digits, backticks and quotes are not a casing mistake.
if (firstChar && /[A-ZÅÄÖ]/.test(firstChar)) {
  const firstToken = description.split(/\s+/)[0].replace(/[,.;:!?)\]]+$/, "");
  const isAcronym = ACRONYM.test(firstToken);
  const isKnownName = KNOWN_NAMES.has(firstToken) || KNOWN_NAMES.has(firstToken.replace(/'s$/, ""));
  if (!isAcronym && !isKnownName) {
    errors.push("Description should start with lowercase letter (acronyms and proper nouns are allowed)");
  }
}

if (errors.length > 0) {
  console.error("BLOCKED: Commit message issues:\n" + errors.map((e) => "  - " + e).join("\n"));
  process.exit(2);
} else {
  process.exit(0);
}
