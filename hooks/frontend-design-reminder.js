#!/usr/bin/env node
/**
 * UserPromptSubmit hook: when the user asks for frontend/UI work, inject a
 * blocking reminder that the `frontend-design` skill MUST be invoked via the
 * Skill tool BEFORE writing any UI code.
 *
 * Triggers on prompts containing UI keywords. Outputs a system reminder that
 * Claude will see at the top of its next turn.
 */

const fs = require('fs')

let input = ''
try {
  input = fs.readFileSync(0, 'utf-8')
} catch {
  process.exit(0)
}

let payload
try {
  payload = JSON.parse(input)
} catch {
  process.exit(0)
}

const prompt = (payload.prompt || '').toLowerCase()
const cwd = (payload.cwd || process.cwd() || '').replace(/\\/g, '/')

// Structural conventions of a specific codebase — NOT visual style. These are
// facts about how a repo is wired (what the root layout already does, which
// utility classes exist), so they only apply inside that repo. Visual
// direction is a per-project design decision and is deliberately not fixed here.
const PROJECT_CONVENTIONS = [
  {
    match: (c) => /\/v85(\/|$)/i.test(c),
    name: 'V85 / Travmaskinen web app',
    lines: [
      'Root layout already sets background and min-height — do not wrap a page in `min-h-screen` or `bg-*`.',
      'Reuse the existing `glass-surface` and `history-table` classes from globals.css instead of re-implementing them.',
      'Numeric/tabular data uses the `font-data` stack with `tabular-nums`.',
    ],
  },
]

const project = PROJECT_CONVENTIONS.find((p) => p.match(cwd))

// Keywords that indicate frontend work. Match aggressively — false positives
// are cheap (one extra skill load), false negatives are what we're fixing.
const KEYWORDS = [
  'page',
  'ui',
  'frontend',
  'front-end',
  'design',
  'redesign',
  'restyle',
  'style',
  'styling',
  'css',
  'tailwind',
  'component',
  'layout',
  'hero',
  'card',
  'button',
  'modal',
  'navbar',
  'footer',
  'sidebar',
  'theme',
  'dark mode',
  'light mode',
  'responsive',
  'mobile',
  'animation',
  'motion',
  'framer',
  'glass',
  'gradient',
  'react',
  'next.js',
  'nextjs',
  'tsx',
  'jsx',
  'shadcn',
  'pretty',
  'beautiful',
  'looks',
  'look like',
  'design language',
]

// Negative filters — skip when the prompt is clearly not about building UI
const NEGATIVE = [
  'backend',
  'database',
  'sql',
  'api endpoint',
  'pytest',
  'python script',
]

// Match on word boundaries, not raw substrings. A plain includes() fires 'ui'
// inside build/quiet/guide/liquid, 'card' inside discard, 'react' inside
// reaction — which made this hook trigger on almost every prompt.
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
const matchesWord = (k) =>
  new RegExp(`(^|[^a-z0-9])${escapeRe(k)}([^a-z0-9]|$)`, 'i').test(prompt)

const hits = KEYWORDS.filter(matchesWord)
const negHits = NEGATIVE.filter(matchesWord)

// Need at least one positive hit and not be dominated by backend talk
if (hits.length === 0) process.exit(0)
if (negHits.length > hits.length) process.exit(0)

const projectBlock = project
  ? `\nConventions of this codebase (${project.name}) — structural, not stylistic:\n` +
    project.lines.map((l) => `- ${l}`).join('\n') + '\n'
  : ''

const reminder = `<system-reminder>
Frontend work detected in this prompt (matched: ${hits.slice(0, 5).join(', ')}).

Before writing or editing .tsx / .jsx / .css / Tailwind code, invoke the
\`frontend-design\` skill.

Choose the visual direction deliberately rather than defaulting. The
\`ui-ux-pro-max\` skill ships a searchable local catalog — 50 active styles, 192
palettes, 74 font pairings, 17 motion presets — so pick a direction from it, or
follow the design language this project has already established.

Avoid the default AI-UI signature unless the project's design language genuinely
calls for it. These read as generic because they are the statistical centre of
the training data, not because they are good choices:
- dark background with a violet-to-cyan gradient
- glassmorphism / backdrop-blur cards
- Inter for everything
- rounded-xl on every surface
- staggered fade-up entrance animations on page load

Typography and a colour palette derived from the subject matter differentiate a
design far more than any effect does.
${projectBlock}</system-reminder>`

// stdout from a UserPromptSubmit hook is appended to the user's prompt as
// additional context that Claude sees.
process.stdout.write(reminder)
process.exit(0)
