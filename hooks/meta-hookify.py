"""
meta-hookify.py — SessionStart hook
Detects repeated corrections in tasks/lessons.md and suggests hookification.
Also checks tasks/patterns.log for repeated task types suggesting skill/agent creation.
"""

import json
import os
import re
import sys
from collections import defaultdict

# Stop words to ignore when extracting keywords
STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
    "can",
    "could",
    "to",
    "of",
    "in",
    "for",
    "on",
    "with",
    "at",
    "by",
    "from",
    "as",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "out",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "don",
    "now",
    "and",
    "but",
    "or",
    "if",
    "that",
    "this",
    "it",
    "its",
    "use",
    "using",
    "always",
    "never",
    "make",
    "sure",
    "every",
    "any",
    "about",
    "up",
    "down",
    "also",
    "they",
    "them",
    "their",
    "what",
    "which",
    "who",
    "whom",
    "you",
    "your",
    "we",
    "our",
    "i",
    "me",
    "my",
    "he",
    "him",
    "his",
    "she",
    "her",
    "don't",
    "doesn't",
    "didn't",
    "won't",
    "wouldn't",
    "shouldn't",
    "couldn't",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "hasn't",
    "haven't",
    "hadn't",
}

# Minimum keyword length to consider
MIN_KEYWORD_LEN = 3


def extract_keywords(text):
    """Extract significant keywords from a text line."""
    words = re.findall(r"[a-z][a-z0-9_-]+", text.lower())
    return {w for w in words if w not in STOP_WORDS and len(w) >= MIN_KEYWORD_LEN}


def parse_lessons(filepath):
    """Parse lessons.md and return list of (title, rule_keywords) tuples."""
    if not os.path.isfile(filepath):
        return []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lessons = []
    # Split by heading pattern: ## date — title
    entries = re.split(r"(?m)^## .+", content)
    headings = re.findall(r"(?m)^## (.+)", content)

    for i, heading in enumerate(headings):
        body = entries[i + 1] if i + 1 < len(entries) else ""
        # Extract "Rule going forward:" line
        rule_match = re.search(r"(?i)rule\s+going\s+forward\s*:\s*(.+?)(?:\n|$)", body)
        if rule_match:
            rule_text = rule_match.group(1).strip()
        else:
            # Fall back to full body if no explicit rule line
            rule_text = body.strip()

        title_keywords = extract_keywords(heading)
        rule_keywords = extract_keywords(rule_text)
        combined = title_keywords | rule_keywords
        if combined:
            lessons.append((heading.strip(), combined))

    return lessons


def find_similar_groups(lessons):
    """Group lessons by shared keywords and return groups with 2+ members."""
    n = len(lessons)
    if n < 2:
        return []

    # Build adjacency based on keyword overlap
    # Two lessons are "similar" if they share 2+ significant keywords
    groups = []
    used = set()

    for i in range(n):
        if i in used:
            continue
        group = [i]
        for j in range(i + 1, n):
            if j in used:
                continue
            shared = lessons[i][1] & lessons[j][1]
            if len(shared) >= 2:
                group.append(j)
                used.add(j)
        if len(group) >= 2:
            used.add(i)
            # Find the best label: most common shared keywords
            all_kw = lessons[group[0]][1]
            for idx in group[1:]:
                all_kw = all_kw & lessons[idx][1]
            label = " ".join(sorted(all_kw)[:4]) if all_kw else lessons[group[0]][0]
            groups.append((label, len(group), [lessons[g][0] for g in group]))

    return groups


def parse_patterns_log(filepath):
    """Parse patterns.log and find task types appearing 3+ times."""
    if not os.path.isfile(filepath):
        return []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    type_counts = defaultdict(int)
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            task_type = parts[1].strip()
            if task_type:
                type_counts[task_type] += 1

    return [(t, c) for t, c in type_counts.items() if c >= 3]


def main():
    # Read hook input from stdin (Claude Code protocol)
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        hook_input = {}

    # Determine project root — use CWD
    cwd = hook_input.get("cwd", os.getcwd())

    lessons_path = os.path.join(cwd, "tasks", "lessons.md")
    patterns_path = os.path.join(cwd, "tasks", "patterns.log")

    lessons = parse_lessons(lessons_path)
    similar_groups = find_similar_groups(lessons)
    pattern_candidates = parse_patterns_log(patterns_path)

    # Nothing to report
    if not similar_groups and not pattern_candidates:
        sys.exit(0)

    output_lines = []
    output_lines.append("")
    output_lines.append("=== HOOKIFICATION CANDIDATES ===")

    for label, count, titles in similar_groups:
        if count >= 3:
            verb = "DEFINITELY create a hook"
        else:
            verb = "consider creating a hook"
        output_lines.append(
            f'  ⚠ Pattern detected: {count} lessons about "{label}" — {verb}'
        )
        for t in titles:
            output_lines.append(f"    - {t}")

    if pattern_candidates:
        output_lines.append("")
        output_lines.append("=== SKILL/AGENT CANDIDATES (from patterns.log) ===")
        for task_type, count in sorted(pattern_candidates, key=lambda x: -x[1]):
            if count >= 5:
                verb = "IMMEDIATELY create a skill or agent"
            else:
                verb = "strongly consider creating a skill or agent"
            output_lines.append(
                f'  ⚠ Task type "{task_type}" appeared {count}x — {verb}'
            )

    output_lines.append("=== END HOOKIFICATION ===")
    output_lines.append("")

    # Output as JSON per Claude Code hook protocol
    result = {"result": "continue", "message": "\n".join(output_lines)}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
