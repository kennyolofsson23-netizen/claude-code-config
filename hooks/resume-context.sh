#!/bin/bash
# SessionStart hook (resume) — re-injects context when resuming a session
echo "=== SESSION RESUMED ==="

# Inject lessons
LESSONS=""
for candidate in "tasks/lessons.md" "lessons.md"; do
  if [ -f "$candidate" ]; then
    LESSONS="$candidate"
    break
  fi
done

if [ -n "$LESSONS" ]; then
  echo ""
  echo "=== PROJECT LESSONS ==="
  cat "$LESSONS"
  echo "=== END LESSONS ==="
fi

# Inject current todo
if [ -f "tasks/todo.md" ]; then
  echo ""
  echo "=== CURRENT TODO ==="
  cat "tasks/todo.md"
  echo "=== END TODO ==="
fi

# Show git state for context
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

# Show repeated task patterns
if [ -f "tasks/patterns.log" ]; then
  echo ""
  echo "=== TASK PATTERNS ==="
  DUPES=$(awk -F'|' '{gsub(/^ +| +$/, "", $2); print $2}' "tasks/patterns.log" 2>/dev/null | sort | uniq -c | sort -rn | awk '$1 >= 2 {print "  ⚠ " $1 "x: " substr($0, index($0,$2))}')
  if [ -n "$DUPES" ]; then
    echo "ACTION REQUIRED — create skill/agent for:"
    echo "$DUPES"
  else
    echo "No repeated patterns yet."
  fi
  echo "=== END PATTERNS ==="
fi

echo ""
echo "REMINDERS: TDD first | Auto-invoke skills | Log to tasks/patterns.log after tasks | Update lessons after corrections | Plan mode for 3+ steps"
