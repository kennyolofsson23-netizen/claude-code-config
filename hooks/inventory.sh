#!/bin/bash
# Generates a live inventory of all installed skills, agents, commands, plugins, hooks, and rules.
# Called by session-start.sh and post-compact.sh to inject current tooling context.

CLAUDE_HOME="$HOME/.claude"

echo "=== INSTALLED TOOLS INVENTORY ==="

# Skills
SKILLS_DIR="$CLAUDE_HOME/skills"
if [ -d "$SKILLS_DIR" ]; then
  SKILLS=$(ls -1 "$SKILLS_DIR" 2>/dev/null | tr '\n' ', ' | sed 's/,$//')
  echo "Skills ($(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l | tr -d ' ')): $SKILLS"
fi

# Agents
AGENTS_DIR="$CLAUDE_HOME/agents"
if [ -d "$AGENTS_DIR" ]; then
  AGENTS=$(ls -1 "$AGENTS_DIR" 2>/dev/null | sed 's/\.md$//' | tr '\n' ', ' | sed 's/,$//')
  echo "Agents ($(ls -1 "$AGENTS_DIR" 2>/dev/null | wc -l | tr -d ' ')): $AGENTS"
fi

# Commands
CMDS_DIR="$CLAUDE_HOME/commands"
if [ -d "$CMDS_DIR" ]; then
  CMDS=$(ls -1 "$CMDS_DIR" 2>/dev/null | sed 's/\.md$//' | tr '\n' ', ' | sed 's/,$//')
  echo "Commands ($(ls -1 "$CMDS_DIR" 2>/dev/null | wc -l | tr -d ' ')): $CMDS"
fi

# Plugins (from settings.json)
SETTINGS="$CLAUDE_HOME/settings.json"
if [ -f "$SETTINGS" ]; then
  PLUGINS=$(grep -o '"[^"]*@[^"]*": true' "$SETTINGS" 2>/dev/null | sed 's/"//g; s/@.*:.*//; s/: true//' | tr '\n' ', ' | sed 's/,$//')
  PLUGIN_COUNT=$(grep -c '"[^"]*@[^"]*": true' "$SETTINGS" 2>/dev/null)
  if [ -n "$PLUGINS" ]; then
    echo "Plugins ($PLUGIN_COUNT): $PLUGINS"
  fi
fi

# Hooks
HOOKS_DIR="$CLAUDE_HOME/hooks"
if [ -d "$HOOKS_DIR" ]; then
  HOOKS=$(ls -1 "$HOOKS_DIR" 2>/dev/null | grep -E '\.(py|js|sh)$' | grep -v 'inventory.sh' | tr '\n' ', ' | sed 's/,$//')
  HOOK_COUNT=$(ls -1 "$HOOKS_DIR" 2>/dev/null | grep -E '\.(py|js|sh)$' | grep -v 'inventory.sh' | wc -l | tr -d ' ')
  echo "Hooks ($HOOK_COUNT): $HOOKS"
fi

# Rules
RULES_DIR="$CLAUDE_HOME/rules"
if [ -d "$RULES_DIR" ]; then
  RULES=$(ls -1 "$RULES_DIR" 2>/dev/null | sed 's/\.md$//' | tr '\n' ', ' | sed 's/,$//')
  echo "Rules ($(ls -1 "$RULES_DIR" 2>/dev/null | wc -l | tr -d ' ')): $RULES"
fi

# CLIs
echo -n "CLIs: "
CLIS=""
command -v gh >/dev/null 2>&1 && CLIS="${CLIS}gh, "
command -v stripe >/dev/null 2>&1 && CLIS="${CLIS}stripe, "
command -v vercel >/dev/null 2>&1 && CLIS="${CLIS}vercel, "
command -v pgcli >/dev/null 2>&1 && CLIS="${CLIS}pgcli, "
command -v npx >/dev/null 2>&1 && CLIS="${CLIS}npx playwright, "
echo "${CLIS%, }"

echo "=== END INVENTORY ==="
echo ""
echo "Auto-invoke matching tools. Read SKILL.md for any unfamiliar skill before use."
