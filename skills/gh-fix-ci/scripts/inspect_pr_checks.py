#!/usr/bin/env python3
"""Inspect failing PR checks via gh CLI, fetch GitHub Actions logs, extract failure snippets.

Usage:
    python inspect_pr_checks.py --repo "." --pr "123"
    python inspect_pr_checks.py --repo "." --pr "https://github.com/org/repo/pull/123" --json
    python inspect_pr_checks.py --repo "." --max-lines 200 --context 40

Exits non-zero when failures remain (for automation).
"""

import argparse
import json
import os
import re
import subprocess
import sys


def run_gh(args: list[str], cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the result."""
    cmd = ["gh"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return result


def resolve_pr(repo: str, pr: str | None) -> str:
    """Resolve the PR number. If not given, use the current branch's PR."""
    if pr:
        # Extract number from URL if needed
        match = re.search(r"/pull/(\d+)", pr)
        if match:
            return match.group(1)
        return pr

    result = run_gh(["pr", "view", "--json", "number"], cwd=repo)
    if result.returncode != 0:
        print("Error: No PR found for current branch. Specify --pr.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    return str(data["number"])


def get_repo_owner_name(repo: str) -> tuple[str, str]:
    """Get owner/name from the repo directory."""
    result = run_gh(["repo", "view", "--json", "owner,name"], cwd=repo)
    if result.returncode != 0:
        # Fallback: parse from git remote
        git_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            cwd=repo,
        )
        url = git_result.stdout.strip()
        match = re.search(r"[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
        if match:
            return match.group(1), match.group(2)
        print("Error: Could not determine repo owner/name.", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def get_failing_checks(repo: str, pr: str) -> list[dict]:
    """Get failing check runs for a PR."""
    # Try with common fields first
    fields = "name,state,conclusion,detailsUrl,startedAt,completedAt"
    result = run_gh(["pr", "checks", pr, "--json", fields], cwd=repo)

    if result.returncode != 0:
        # Fallback: try minimal fields
        fields = "name,state,conclusion,detailsUrl"
        result = run_gh(["pr", "checks", pr, "--json", fields], cwd=repo)
        if result.returncode != 0:
            # Last resort: try bucket instead of conclusion
            fields = "name,state,bucket,link"
            result = run_gh(["pr", "checks", pr, "--json", fields], cwd=repo)
            if result.returncode != 0:
                print(f"Error fetching checks: {result.stderr}", file=sys.stderr)
                sys.exit(1)

    checks = json.loads(result.stdout)

    # Filter to failures
    failing = []
    for check in checks:
        state = check.get("state", "").upper()
        conclusion = check.get("conclusion", check.get("bucket", "")).upper()

        is_failure = (
            state == "FAILURE"
            or conclusion in ("FAILURE", "FAIL", "TIMED_OUT", "CANCELLED")
            or check.get("bucket", "").lower() == "fail"
        )
        if is_failure:
            failing.append(check)

    return failing


def extract_run_id(details_url: str) -> str | None:
    """Extract GitHub Actions run ID from a details URL."""
    if not details_url:
        return None
    match = re.search(r"/actions/runs/(\d+)", details_url)
    return match.group(1) if match else None


def get_run_logs(repo: str, run_id: str, max_lines: int, context: int) -> str:
    """Fetch logs for a GitHub Actions run and extract the failure snippet."""
    # First get run info
    result = run_gh(
        [
            "run",
            "view",
            run_id,
            "--json",
            "name,workflowName,conclusion,status,url,jobs",
        ],
        cwd=repo,
    )

    run_info = ""
    if result.returncode == 0:
        data = json.loads(result.stdout)
        run_info = (
            f"Workflow: {data.get('workflowName', 'unknown')}\n"
            f"Status: {data.get('status', 'unknown')}\n"
            f"Conclusion: {data.get('conclusion', 'unknown')}\n"
        )

    # Fetch the log
    result = run_gh(["run", "view", run_id, "--log-failed"], cwd=repo)

    if result.returncode != 0:
        # Fallback to full log
        result = run_gh(["run", "view", run_id, "--log"], cwd=repo)
        if result.returncode != 0:
            return run_info + f"Could not fetch logs: {result.stderr}"

    log_lines = result.stdout.splitlines()

    # Extract the most relevant failure snippet
    snippet = extract_failure_snippet(log_lines, max_lines, context)
    return run_info + snippet


def extract_failure_snippet(lines: list[str], max_lines: int, context: int) -> str:
    """Extract the most relevant failure snippet from log lines."""
    if not lines:
        return "(no log output)"

    # Look for common error patterns
    error_patterns = [
        r"error[:\s]",
        r"FAIL",
        r"failed",
        r"Error:",
        r"ERROR",
        r"AssertionError",
        r"TypeError",
        r"SyntaxError",
        r"exit code [1-9]",
        r"Process completed with exit code",
        r"##\[error\]",
    ]

    error_indices = []
    for i, line in enumerate(lines):
        for pattern in error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                error_indices.append(i)
                break

    if error_indices:
        # Take context around the last cluster of errors (usually most relevant)
        last_error = error_indices[-1]
        start = max(0, last_error - context)
        end = min(len(lines), last_error + context + 1)

        # Cap at max_lines
        snippet_lines = lines[start:end]
        if len(snippet_lines) > max_lines:
            snippet_lines = snippet_lines[-max_lines:]

        return "\n".join(snippet_lines)

    # No error patterns found - return the tail
    tail = lines[-max_lines:]
    return "\n".join(tail)


def format_text(checks_results: list[dict]) -> str:
    """Format results as human-readable text."""
    if not checks_results:
        return "All checks passed. No failures found."

    parts = []
    for i, check in enumerate(checks_results, 1):
        parts.append(f"{'='*60}")
        parts.append(f"FAILING CHECK #{i}: {check['name']}")
        parts.append(f"{'='*60}")
        if check.get("url"):
            parts.append(f"URL: {check['url']}")
        if check.get("is_external"):
            parts.append(f"External provider (out of scope). Details: {check['url']}")
        else:
            parts.append(f"\n{check.get('logs', '(no logs available)')}")
        parts.append("")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Inspect failing PR checks and fetch GitHub Actions logs."
    )
    parser.add_argument("--repo", default=".", help="Path to the repo (default: .)")
    parser.add_argument(
        "--pr", default=None, help="PR number or URL (default: current branch)"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="Output as JSON"
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=100,
        help="Max log lines per check (default: 100)",
    )
    parser.add_argument(
        "--context",
        type=int,
        default=20,
        help="Context lines around errors (default: 20)",
    )
    args = parser.parse_args()

    # Resolve PR
    pr_number = resolve_pr(args.repo, args.pr)

    # Get failing checks
    failing = get_failing_checks(args.repo, pr_number)

    if not failing:
        msg = f"PR #{pr_number}: All checks passed."
        if args.json_output:
            print(json.dumps({"pr": pr_number, "failures": [], "message": msg}))
        else:
            print(msg)
        sys.exit(0)

    # Process each failing check
    results = []
    for check in failing:
        name = check.get("name", "unknown")
        details_url = check.get("detailsUrl", check.get("link", ""))
        run_id = extract_run_id(details_url)

        entry = {
            "name": name,
            "url": details_url,
            "is_external": run_id is None and bool(details_url),
        }

        if run_id:
            entry["run_id"] = run_id
            entry["logs"] = get_run_logs(
                args.repo, run_id, args.max_lines, args.context
            )
        elif details_url:
            entry["logs"] = f"External check - details at: {details_url}"
        else:
            entry["logs"] = "(no details URL available)"

        results.append(entry)

    # Output
    if args.json_output:
        output = {
            "pr": pr_number,
            "total_failing": len(results),
            "failures": results,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"PR #{pr_number}: {len(results)} failing check(s)\n")
        print(format_text(results))

    sys.exit(1)


if __name__ == "__main__":
    main()
