#!/bin/bash
# SessionStart hook — injects context at the start of every fresh session

echo "=== SESSION START ==="

# Find and inject project lessons file
LESSONS=""
for candidate in "tasks/lessons.md" "lessons.md"; do
  if [ -f "$candidate" ]; then
    LESSONS="$candidate"
    break
  fi
done

if [ -n "$LESSONS" ]; then
  echo ""
  echo "=== PROJECT LESSONS (from $LESSONS) ==="
  cat "$LESSONS"
  echo ""
  echo "=== END LESSONS ==="
else
  echo "No tasks/lessons.md found in this project."
fi

# Show current todo if exists
if [ -f "tasks/todo.md" ]; then
  echo ""
  echo "=== CURRENT TODO ==="
  cat "tasks/todo.md"
  echo ""
  echo "=== END TODO ==="
fi

# Show repeated task patterns
if [ -f "tasks/patterns.log" ]; then
  echo ""
  echo "=== TASK PATTERNS (check for skill/agent candidates) ==="
  cat "tasks/patterns.log"
  echo ""
  echo "=== END PATTERNS ==="
  # Count duplicates and flag
  DUPES=$(awk -F'|' '{gsub(/^ +| +$/, "", $2); print $2}' "tasks/patterns.log" 2>/dev/null | sort | uniq -c | sort -rn | awk '$1 >= 2 {print "  ⚠ " $1 "x: " substr($0, index($0,$2))}')
  if [ -n "$DUPES" ]; then
    echo "ACTION REQUIRED — these task types appeared 2+ times, CREATE a skill or agent:"
    echo "$DUPES"
    echo ""
  fi
fi

# Inject live tool inventory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/inventory.sh"

echo ""
echo "REMINDERS:"
echo "- Plan mode for non-trivial tasks (3+ steps)"
echo "- Auto-invoke /qa after ANY code changes"
echo "- After completing tasks → append to tasks/patterns.log"
echo "- After corrections → update tasks/lessons.md IMMEDIATELY"
