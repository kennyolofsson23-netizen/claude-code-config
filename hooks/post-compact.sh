#!/bin/bash
# PostCompact hook — re-injects critical context after compaction

echo "CONTEXT COMPACTED — Critical reminders:"
echo "- Re-read any files you were actively editing before continuing"
echo "- Check tasks/todo.md for current task status"
echo "- Run tests to verify current state before making more changes"
echo "- TDD is the #1 rule — prove everything works"
echo "- Check git status to see what's been modified"

# Inject live tool inventory (survives compaction)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/inventory.sh"

# Re-inject lessons if available
LESSONS=""
for candidate in "tasks/lessons.md" "lessons.md"; do
  if [ -f "$candidate" ]; then
    LESSONS="$candidate"
    break
  fi
done

if [ -n "$LESSONS" ]; then
  echo ""
  echo "=== PROJECT LESSONS (re-injected post-compact) ==="
  cat "$LESSONS"
  echo "=== END LESSONS ==="
fi

# Re-inject todo if available
if [ -f "tasks/todo.md" ]; then
  echo ""
  echo "=== CURRENT TODO ==="
  cat "tasks/todo.md"
  echo "=== END TODO ==="
fi

# Show repeated task patterns
if [ -f "tasks/patterns.log" ]; then
  echo ""
  echo "=== TASK PATTERNS (survives compaction) ==="
  DUPES=$(awk -F'|' '{gsub(/^ +| +$/, "", $2); print $2}' "tasks/patterns.log" 2>/dev/null | sort | uniq -c | sort -rn | awk '$1 >= 2 {print "  ⚠ " $1 "x: " substr($0, index($0,$2))}')
  if [ -n "$DUPES" ]; then
    echo "ACTION REQUIRED — create skill/agent for:"
    echo "$DUPES"
  fi
  echo "=== END PATTERNS ==="
fi

# Show git state
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo ""
  echo "=== GIT STATE ==="
  echo "Branch: $(git branch --show-current 2>/dev/null)"
  CHANGES=$(git status --porcelain 2>/dev/null | head -20)
  if [ -n "$CHANGES" ]; then
    echo "Modified files:"
    echo "$CHANGES"
  else
    echo "Working tree clean"
  fi
  echo "=== END GIT ==="
fi
