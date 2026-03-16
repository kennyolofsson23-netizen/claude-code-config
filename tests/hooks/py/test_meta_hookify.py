"""Tests for meta-hookify.py hook — pure functions + integration."""

import importlib.util
import io
import json
import os
import sys

import pytest

HOOK_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "hooks", "meta-hookify.py"
    )
)

# Load the module for unit testing pure functions
_spec = importlib.util.spec_from_file_location("meta_hookify", HOOK_PATH)


def _load_module():
    """Load meta-hookify module without executing main (no stdin needed for imports)."""
    mod = importlib.util.module_from_spec(_spec)
    # Patch stdin before loading so json.loads doesn't fail on import
    # But meta-hookify only reads stdin in main(), so we just need to handle
    # the module-level code (which doesn't read stdin)
    _spec.loader.exec_module(mod)
    return mod


# We can't import top-level because the module calls main() via __name__ == "__main__"
# Since we import via spec, __name__ will be "meta_hookify", not "__main__",
# so main() won't auto-execute. We can safely import the functions.


@pytest.fixture(scope="module")
def hookify_mod():
    """Load the meta-hookify module once for all tests."""
    return _load_module()


# === extract_keywords ===


class TestExtractKeywords:
    def test_basic_extraction(self, hookify_mod):
        result = hookify_mod.extract_keywords(
            "Always run database migrations before deploy"
        )
        assert "database" in result
        assert "migrations" in result
        assert "deploy" in result

    def test_filters_stop_words(self, hookify_mod):
        result = hookify_mod.extract_keywords("the quick brown fox and the lazy dog")
        assert "the" not in result
        assert "and" not in result
        assert "quick" in result
        assert "brown" in result

    def test_filters_short_words(self, hookify_mod):
        result = hookify_mod.extract_keywords("do it or go")
        # All these are <= 2 chars or stop words
        assert len(result) == 0

    def test_lowercases(self, hookify_mod):
        result = hookify_mod.extract_keywords("ALWAYS CHECK Database")
        # "always" is a stop word
        assert "always" not in result
        assert "check" in result
        assert "database" in result

    def test_empty_string(self, hookify_mod):
        assert hookify_mod.extract_keywords("") == set()

    def test_handles_hyphens_and_underscores(self, hookify_mod):
        result = hookify_mod.extract_keywords("pre-commit hook for auto_format")
        assert "pre-commit" in result
        assert "hook" in result
        assert "auto_format" in result


# === parse_lessons ===


class TestParseLessons:
    def test_returns_empty_for_nonexistent(self, hookify_mod, tmp_path):
        result = hookify_mod.parse_lessons(str(tmp_path / "nope.md"))
        assert result == []

    def test_parses_heading_with_rule(self, hookify_mod, tmp_path):
        f = tmp_path / "lessons.md"
        f.write_text(
            "# Lessons\n\n"
            "## 2026-01-01 — Database migration\n"
            "Context about the problem.\n"
            "Rule going forward: always run migrations with --dry-run first\n\n"
            "## 2026-01-02 — API timeout\n"
            "Rule going forward: set explicit timeout on all HTTP calls\n"
        )
        result = hookify_mod.parse_lessons(str(f))
        assert len(result) == 2
        title, keywords = result[0]
        assert "database" in title.lower() or "migration" in title.lower()
        assert "migrations" in keywords or "dry-run" in keywords

    def test_falls_back_to_body(self, hookify_mod, tmp_path):
        f = tmp_path / "lessons.md"
        f.write_text(
            "## 2026-01-01 — Testing lesson\n"
            "Always write integration tests for database queries\n"
        )
        result = hookify_mod.parse_lessons(str(f))
        assert len(result) == 1
        assert "integration" in result[0][1] or "database" in result[0][1]

    def test_empty_file(self, hookify_mod, tmp_path):
        f = tmp_path / "lessons.md"
        f.write_text("")
        result = hookify_mod.parse_lessons(str(f))
        assert result == []


# === find_similar_groups ===


class TestFindSimilarGroups:
    def test_empty_lessons(self, hookify_mod):
        assert hookify_mod.find_similar_groups([]) == []

    def test_single_lesson(self, hookify_mod):
        assert (
            hookify_mod.find_similar_groups([("title", {"database", "migration"})])
            == []
        )

    def test_groups_similar_lessons(self, hookify_mod):
        lessons = [
            ("DB migration 1", {"database", "migration", "prisma"}),
            ("DB migration 2", {"database", "migration", "schema"}),
            ("Unrelated", {"testing", "coverage", "jest"}),
        ]
        groups = hookify_mod.find_similar_groups(lessons)
        assert len(groups) == 1
        label, count, titles = groups[0]
        assert count == 2
        assert "DB migration 1" in titles
        assert "DB migration 2" in titles

    def test_no_groups_with_dissimilar(self, hookify_mod):
        lessons = [
            ("Topic A", {"alpha", "beta", "gamma"}),
            ("Topic B", {"delta", "epsilon", "zeta"}),
        ]
        groups = hookify_mod.find_similar_groups(lessons)
        assert groups == []

    def test_three_similar_lessons(self, hookify_mod):
        lessons = [
            ("Commit hook 1", {"commit", "hook", "lint"}),
            ("Commit hook 2", {"commit", "hook", "format"}),
            ("Commit hook 3", {"commit", "hook", "validate"}),
        ]
        groups = hookify_mod.find_similar_groups(lessons)
        assert len(groups) == 1
        assert groups[0][1] == 3

    def test_shared_label_uses_common_keywords(self, hookify_mod):
        lessons = [
            ("L1", {"database", "migration", "unique1"}),
            ("L2", {"database", "migration", "unique2"}),
        ]
        groups = hookify_mod.find_similar_groups(lessons)
        label = groups[0][0]
        assert "database" in label
        assert "migration" in label


# === parse_patterns_log ===


class TestParsePatternsLog:
    def test_nonexistent_file(self, hookify_mod, tmp_path):
        result = hookify_mod.parse_patterns_log(str(tmp_path / "nope.log"))
        assert result == []

    def test_counts_task_types(self, hookify_mod, tmp_path):
        f = tmp_path / "patterns.log"
        f.write_text(
            "2026-01-01 | bug-fix | fixed auth\n"
            "2026-01-02 | bug-fix | fixed db\n"
            "2026-01-03 | bug-fix | fixed api\n"
            "2026-01-04 | refactor | cleaned up\n"
        )
        result = hookify_mod.parse_patterns_log(str(f))
        assert len(result) == 1
        assert result[0] == ("bug-fix", 3)

    def test_ignores_below_threshold(self, hookify_mod, tmp_path):
        f = tmp_path / "patterns.log"
        f.write_text("2026-01-01 | deploy | v1\n" "2026-01-02 | deploy | v2\n")
        result = hookify_mod.parse_patterns_log(str(f))
        assert result == []

    def test_ignores_comments_and_blanks(self, hookify_mod, tmp_path):
        f = tmp_path / "patterns.log"
        f.write_text(
            "# Header\n"
            "\n"
            "2026-01-01 | test | t1\n"
            "2026-01-02 | test | t2\n"
            "2026-01-03 | test | t3\n"
        )
        result = hookify_mod.parse_patterns_log(str(f))
        assert len(result) == 1
        assert result[0][0] == "test"

    def test_empty_file(self, hookify_mod, tmp_path):
        f = tmp_path / "patterns.log"
        f.write_text("")
        result = hookify_mod.parse_patterns_log(str(f))
        assert result == []


# === main() integration ===


class TestMainIntegration:
    def _run_main(
        self,
        hookify_mod,
        monkeypatch,
        tmp_path,
        lessons_content=None,
        patterns_content=None,
        cwd=None,
    ):
        """Run main() directly, return (exit_code, stdout)."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        if lessons_content is not None:
            (tasks_dir / "lessons.md").write_text(lessons_content)
        if patterns_content is not None:
            (tasks_dir / "patterns.log").write_text(patterns_content)

        hook_input = {"cwd": str(tmp_path)}
        if cwd is not None:
            hook_input["cwd"] = cwd

        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(hook_input)))

        stdout_capture = io.StringIO()
        monkeypatch.setattr("sys.stdout", stdout_capture)

        try:
            hookify_mod.main()
            exit_code = 0  # main() returned normally (has candidates to report)
        except SystemExit as e:
            exit_code = e.code

        return exit_code, stdout_capture.getvalue()

    def test_exits_0_no_files(self, hookify_mod, monkeypatch, tmp_path):
        code, stdout = self._run_main(hookify_mod, monkeypatch, tmp_path)
        assert code == 0
        assert stdout.strip() == ""

    def test_exits_0_no_similar_lessons(self, hookify_mod, monkeypatch, tmp_path):
        code, stdout = self._run_main(
            hookify_mod,
            monkeypatch,
            tmp_path,
            lessons_content=(
                "## 2026-01-01 — Topic A\n"
                "Rule going forward: do alpha beta gamma\n\n"
                "## 2026-01-02 — Topic B\n"
                "Rule going forward: do delta epsilon zeta\n"
            ),
        )
        assert code == 0

    def test_outputs_hookification_candidates(self, hookify_mod, monkeypatch, tmp_path):
        code, stdout = self._run_main(
            hookify_mod,
            monkeypatch,
            tmp_path,
            lessons_content=(
                "## 2026-01-01 — Database migration error\n"
                "Rule going forward: always run database migration with dry-run\n\n"
                "## 2026-01-02 — Database migration failed\n"
                "Rule going forward: validate database migration before deploy\n"
            ),
        )
        # Should output JSON with hookification message
        result = json.loads(stdout)
        assert result["result"] == "continue"
        assert "HOOKIFICATION CANDIDATES" in result["message"]
        assert "database" in result["message"].lower()

    def test_outputs_skill_candidates(self, hookify_mod, monkeypatch, tmp_path):
        code, stdout = self._run_main(
            hookify_mod,
            monkeypatch,
            tmp_path,
            patterns_content=(
                "2026-01-01 | bug-fix | auth issue\n"
                "2026-01-02 | bug-fix | db issue\n"
                "2026-01-03 | bug-fix | api issue\n"
            ),
        )
        result = json.loads(stdout)
        assert "SKILL/AGENT CANDIDATES" in result["message"]
        assert "bug-fix" in result["message"]

    def test_uses_cwd_from_hook_input(self, hookify_mod, monkeypatch, tmp_path):
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        tasks_dir = custom_dir / "tasks"
        tasks_dir.mkdir()
        (tasks_dir / "patterns.log").write_text(
            "2026-01-01 | deploy | v1\n"
            "2026-01-02 | deploy | v2\n"
            "2026-01-03 | deploy | v3\n"
        )

        code, stdout = self._run_main(
            hookify_mod, monkeypatch, tmp_path, cwd=str(custom_dir)
        )
        result = json.loads(stdout)
        assert "deploy" in result["message"]

    def test_handles_invalid_stdin(self, hookify_mod, monkeypatch, tmp_path):
        """When stdin is invalid JSON, should not crash."""
        monkeypatch.setattr("sys.stdin", io.StringIO("not json"))

        stdout_capture = io.StringIO()
        monkeypatch.setattr("sys.stdout", stdout_capture)

        # Monkeypatch os.getcwd to point to tmp_path
        monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))

        try:
            hookify_mod.main()
            code = 0
        except SystemExit as e:
            code = e.code

        # Should exit 0 (no lessons/patterns to find)
        assert code == 0
