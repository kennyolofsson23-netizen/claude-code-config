#!/usr/bin/env python3
"""Fetch PR review comments and issue comments via gh CLI and output them in structured format.

Usage:
    python fetch_comments.py                # uses current branch PR
    python fetch_comments.py --pr 123       # specific PR number
    python fetch_comments.py --pr 123 --json
"""

import argparse
import json
import subprocess
import sys


def run_gh(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the result."""
    cmd = ["gh"] + args
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def resolve_pr(repo: str, pr: str | None) -> str:
    """Resolve the PR number. If not given, use the current branch's PR."""
    if pr:
        return pr
    result = run_gh(["pr", "view", "--json", "number"], cwd=repo)
    if result.returncode != 0:
        print("Error: No PR found for current branch. Specify --pr.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    return str(data["number"])


def fetch_review_threads(repo: str, pr: str) -> list[dict]:
    """Fetch review comments grouped by review thread."""
    result = run_gh(["pr", "view", pr, "--json", "reviewThreads,reviews"], cwd=repo)
    if result.returncode != 0:
        print(
            f"Warning: Could not fetch review threads: {result.stderr}", file=sys.stderr
        )
        return []

    data = json.loads(result.stdout)
    threads = []

    # Process review threads (inline comments on code)
    for thread in data.get("reviewThreads", []):
        comments = thread.get("comments", [])
        if not comments:
            continue

        first = comments[0]
        thread_data = {
            "type": "review_thread",
            "path": first.get("path", ""),
            "line": first.get("line")
            or first.get("startLine")
            or first.get("originalLine"),
            "is_resolved": thread.get("isResolved", False),
            "is_outdated": thread.get("isOutdated", False),
            "comments": [],
        }

        for comment in comments:
            thread_data["comments"].append(
                {
                    "author": comment.get("author", {}).get("login", "unknown"),
                    "body": comment.get("body", ""),
                    "created_at": comment.get("createdAt", ""),
                    "diff_hunk": comment.get("diffHunk", ""),
                }
            )

        threads.append(thread_data)

    return threads


def fetch_issue_comments(repo: str, pr: str) -> list[dict]:
    """Fetch top-level PR comments (non-review comments)."""
    result = run_gh(["pr", "view", pr, "--json", "comments"], cwd=repo)
    if result.returncode != 0:
        print(
            f"Warning: Could not fetch issue comments: {result.stderr}", file=sys.stderr
        )
        return []

    data = json.loads(result.stdout)
    comments = []

    for comment in data.get("comments", []):
        author = comment.get("author", {}).get("login", "unknown")
        # Skip bot comments
        if "[bot]" in author:
            continue

        comments.append(
            {
                "type": "issue_comment",
                "author": author,
                "body": comment.get("body", ""),
                "created_at": comment.get("createdAt", ""),
            }
        )

    return comments


def fetch_reviews(repo: str, pr: str) -> list[dict]:
    """Fetch review summaries (top-level review bodies, not inline comments)."""
    result = run_gh(["pr", "view", pr, "--json", "reviews"], cwd=repo)
    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    reviews = []

    for review in data.get("reviews", []):
        body = review.get("body", "").strip()
        if not body:
            continue
        reviews.append(
            {
                "type": "review",
                "author": review.get("author", {}).get("login", "unknown"),
                "state": review.get("state", ""),
                "body": body,
                "submitted_at": review.get("submittedAt", ""),
            }
        )

    return reviews


def format_text(
    pr: str, threads: list[dict], comments: list[dict], reviews: list[dict]
) -> str:
    """Format all comments as human-readable numbered text."""
    parts = [f"PR #{pr} — Review Comments & Threads\n{'='*50}\n"]

    counter = 1

    # Review threads (inline code comments)
    if threads:
        unresolved = [t for t in threads if not t["is_resolved"]]
        resolved = [t for t in threads if t["is_resolved"]]

        if unresolved:
            parts.append(f"\n## Unresolved Review Threads ({len(unresolved)})\n")
            for thread in unresolved:
                path = thread["path"]
                line = thread["line"] or "?"
                first_comment = thread["comments"][0]
                parts.append(f"  [{counter}] {path}:{line}")
                parts.append(f"      Author: {first_comment['author']}")

                if first_comment.get("diff_hunk"):
                    hunk_lines = first_comment["diff_hunk"].splitlines()
                    # Show last few lines of hunk for context
                    context_lines = (
                        hunk_lines[-5:] if len(hunk_lines) > 5 else hunk_lines
                    )
                    parts.append("      Code context:")
                    for hl in context_lines:
                        parts.append(f"        {hl}")

                for ci, c in enumerate(thread["comments"]):
                    prefix = "      >> " if ci == 0 else "         reply: "
                    body_preview = c["body"].replace("\n", " ")
                    if len(body_preview) > 200:
                        body_preview = body_preview[:200] + "..."
                    parts.append(f"{prefix}{c['author']}: {body_preview}")
                parts.append("")
                counter += 1

        if resolved:
            parts.append(f"\n## Resolved Threads ({len(resolved)}) — skipped\n")

    # Top-level review bodies
    if reviews:
        parts.append(f"\n## Review Summaries ({len(reviews)})\n")
        for review in reviews:
            state_label = review["state"].replace("_", " ").title()
            parts.append(f"  [{counter}] {review['author']} ({state_label})")
            body_preview = review["body"].replace("\n", " ")
            if len(body_preview) > 300:
                body_preview = body_preview[:300] + "..."
            parts.append(f"      {body_preview}")
            parts.append("")
            counter += 1

    # General PR comments
    if comments:
        parts.append(f"\n## General Comments ({len(comments)})\n")
        for comment in comments:
            parts.append(
                f"  [{counter}] {comment['author']} ({comment['created_at'][:10]})"
            )
            body_preview = comment["body"].replace("\n", " ")
            if len(body_preview) > 300:
                body_preview = body_preview[:300] + "..."
            parts.append(f"      {body_preview}")
            parts.append("")
            counter += 1

    if counter == 1:
        parts.append("  No comments or review threads found.")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Fetch PR review comments via gh CLI.")
    parser.add_argument("--repo", default=".", help="Path to the repo (default: .)")
    parser.add_argument(
        "--pr", default=None, help="PR number (default: current branch)"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Output as JSON"
    )
    args = parser.parse_args()

    pr_number = resolve_pr(args.repo, args.pr)

    threads = fetch_review_threads(args.repo, pr_number)
    comments = fetch_issue_comments(args.repo, pr_number)
    reviews = fetch_reviews(args.repo, pr_number)

    if args.json_output:
        output = {
            "pr": pr_number,
            "review_threads": threads,
            "issue_comments": comments,
            "reviews": reviews,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text(pr_number, threads, comments, reviews))


if __name__ == "__main__":
    main()
