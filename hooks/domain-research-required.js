#!/usr/bin/env node
/**
 * UserPromptSubmit hook: when the user asks about ATG/trav domain concepts,
 * inject a BLOCKING reminder that Claude MUST launch a trav-researcher agent
 * BEFORE explaining any domain mechanics.
 *
 * Root cause: Claude pattern-matches domain concepts to things it already knows
 * and confidently explains them wrong. This happened 5+ times with "reducerat
 * system" alone in a single session (2026-04-17). Memory files don't work —
 * Claude reads them and ignores them. This hook is the enforcement mechanism.
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

// ATG/trav domain terms that require research before explaining
const DOMAIN_TERMS = [
  'reducerat system',
  'reducerat spel',
  'reducering',
  'sänkt insats',
  'systemspel',
  'villkor',
  'utgångshäst',
  'gardering',
  'halvgardering',
  'helgardering',
  'streckfördelning',
  'radpris',
  'systemram',
  'allarättschans',
  'copema',
  'poängsystem',
  'abcd system',
  'abc reducering',
  'spelformer atg',
  'v-spel mekanik',
  'poolspel',
  'how does atg',
  'how does v75',
  'how does v85',
  'what is reducerat',
  'what is gardering',
]

// Negative filters — skip when clearly about code, not domain concepts
const NEGATIVE = [
  'git commit',
  'pytest',
  'fix the bug',
  'run the harness',
  'deploy',
  'typescript',
  'import error',
]

const hits = DOMAIN_TERMS.filter((k) => prompt.includes(k))
const negHits = NEGATIVE.filter((k) => prompt.includes(k))

if (hits.length === 0) process.exit(0)
if (negHits.length > hits.length) process.exit(0)

const reminder = `<system-reminder>
ATG DOMAIN CONCEPT DETECTED in this prompt (matched: ${hits.slice(0, 3).join(', ')}).

You MUST launch a trav-researcher agent BEFORE explaining ANY domain mechanics.
This is non-negotiable — you have been caught confidently explaining domain
concepts wrong 5+ times in a single session (2026-04-17, reducerat system).

DO NOT:
- Pattern-match to something you already know
- Explain the concept from memory or training data
- Say "I believe" or "I think" about ATG mechanics

DO:
1. Launch a trav-researcher agent with specific search queries
2. Wait for the research to complete
3. ONLY THEN explain, citing the sources

Memory files failed to prevent this. This hook exists because you ignore them.
If you explain a domain concept without research, Kenny WILL catch you and
you WILL be wrong. Again.
</system-reminder>`

process.stdout.write(reminder)
process.exit(0)
