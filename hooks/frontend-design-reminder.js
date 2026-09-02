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

const hits = KEYWORDS.filter((k) => prompt.includes(k))
const negHits = NEGATIVE.filter((k) => prompt.includes(k))

// Need at least one positive hit and not be dominated by backend talk
if (hits.length === 0) process.exit(0)
if (negHits.length > hits.length) process.exit(0)

const reminder = `<system-reminder>
FRONTEND WORK DETECTED in this prompt (matched: ${hits.slice(0, 5).join(', ')}).

You MUST invoke the \`frontend-design\` skill via the Skill tool BEFORE writing
or editing ANY .tsx / .jsx / .css / Tailwind code in this turn. This is non-
negotiable — every prior frontend task that skipped this skill produced generic,
off-brand output that had to be redone.

The skill enforces:
- Travmaskinen dark ATG aesthetic (dark-950 bg, brand-500 purple, accent-500 cyan)
- glass-surface system + history-table class from globals.css
- Hero + atmosphere background blend pattern (see HeroRaceDay.tsx)
- framer-motion staggerContainer / fadeInUp entrance animations
- font-heading (Inter) for titles, font-data (Barlow Condensed) tabular-nums for numbers
- NEVER wrap pages in min-h-screen / bg-* — root layout already handles this

Invoke the skill NOW, before any other action.
</system-reminder>`

// stdout from a UserPromptSubmit hook is appended to the user's prompt as
// additional context that Claude sees.
process.stdout.write(reminder)
process.exit(0)
