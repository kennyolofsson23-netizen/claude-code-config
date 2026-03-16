"""Tests for pre-commit-secrets.py hook."""

import importlib.util
import io
import json
import os
import subprocess
import sys

import pytest

HOOK_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "hooks", "pre-commit-secrets.py"
    )
)


def run_hook(
    monkeypatch, stdin_data, git_files="", git_diff_content="", subprocess_error=False
):
    """Run the hook as a module and return the exit code and stderr output."""
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(stdin_data)))

    stderr_capture = io.StringIO()
    monkeypatch.setattr("sys.stderr", stderr_capture)

    call_log = []

    def mock_subprocess_run(cmd, **kwargs):
        call_log.append(cmd)
        if subprocess_error:
            raise OSError("git not found")

        result = subprocess.CompletedProcess(cmd, 0)
        if "--name-only" in cmd:
            result.stdout = git_files
        elif "-U0" in cmd:
            result.stdout = git_diff_content
        else:
            result.stdout = ""
        result.stderr = ""
        return result

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    spec = importlib.util.spec_from_file_location("pre_commit_secrets", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)

    with pytest.raises(SystemExit) as exc_info:
        spec.loader.exec_module(mod)

    return exc_info.value.code, stderr_capture.getvalue(), call_log


# --- Non-triggering commands ---


class TestNonCommitCommands:
    def test_exits_0_for_ls(self, monkeypatch):
        code, _, _ = run_hook(monkeypatch, {"tool_input": {"command": "ls -la"}})
        assert code == 0

    def test_exits_0_for_git_push(self, monkeypatch):
        code, _, _ = run_hook(
            monkeypatch, {"tool_input": {"command": "git push origin main"}}
        )
        assert code == 0

    def test_exits_0_for_git_status(self, monkeypatch):
        code, _, _ = run_hook(monkeypatch, {"tool_input": {"command": "git status"}})
        assert code == 0

    def test_exits_0_for_empty_command(self, monkeypatch):
        code, _, _ = run_hook(monkeypatch, {"tool_input": {"command": ""}})
        assert code == 0

    def test_exits_0_for_no_command(self, monkeypatch):
        code, _, _ = run_hook(monkeypatch, {"tool_input": {}})
        assert code == 0

    def test_exits_0_for_no_tool_input(self, monkeypatch):
        code, _, _ = run_hook(monkeypatch, {})
        assert code == 0


# --- Clean commits ---


class TestCleanCommits:
    def test_exits_0_no_staged_files(self, monkeypatch):
        code, _, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'clean'"}},
            git_files="",
        )
        assert code == 0

    def test_exits_0_safe_files(self, monkeypatch):
        code, _, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'safe'"}},
            git_files="src/app.py\nREADME.md\npackage.json",
            git_diff_content="+console.log('hello')",
        )
        assert code == 0


# --- Blocked files ---


class TestBlockedFiles:
    def test_blocks_env(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'oops'"}},
            git_files=".env",
            git_diff_content="",
        )
        assert code == 2
        assert "BLOCKED" in stderr
        assert ".env" in stderr

    def test_blocks_env_local(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'oops'"}},
            git_files=".env.local",
            git_diff_content="",
        )
        assert code == 2

    def test_blocks_credentials_json(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'oops'"}},
            git_files="credentials.json",
            git_diff_content="",
        )
        assert code == 2
        assert "credentials.json" in stderr

    def test_blocks_nested_env(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'oops'"}},
            git_files="config/subfolder/.env",
            git_diff_content="",
        )
        assert code == 2

    def test_blocks_png(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'oops'"}},
            git_files="screenshot.png",
            git_diff_content="",
        )
        assert code == 2
        assert "IMAGE" in stderr

    def test_blocks_jpg(self, monkeypatch):
        code, _, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'img'"}},
            git_files="photo.jpg",
            git_diff_content="",
        )
        assert code == 2


# --- Secret content patterns ---


class TestSecretPatterns:
    # Build test strings dynamically to avoid triggering the hook on this file
    _API_KEY_DIFF = "+api" + "_key" + ' = "sk_live_' + "a" * 24 + '"'
    _PRIVATE_KEY_DIFF = "+-----BEGIN " + "RSA PRIVATE" + " KEY-----"
    _SK_DIFF = '+STRIPE_KEY = "' + "sk-" + "a" * 24 + '"'
    _PASSWORD_DIFF = "+password" + ' = "my' + "supersecret" + 'password"'

    def test_blocks_api_key_in_diff(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'key'"}},
            git_files="config.py",
            git_diff_content=self._API_KEY_DIFF,
        )
        assert code == 2
        assert "API key" in stderr

    def test_blocks_private_key(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'key'"}},
            git_files="deploy.sh",
            git_diff_content=self._PRIVATE_KEY_DIFF,
        )
        assert code == 2
        assert "Private key" in stderr

    def test_blocks_sk_pattern(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'key'"}},
            git_files="app.py",
            git_diff_content=self._SK_DIFF,
        )
        assert code == 2
        assert "secret key" in stderr

    def test_blocks_password_pattern(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'pw'"}},
            git_files="settings.py",
            git_diff_content=self._PASSWORD_DIFF,
        )
        assert code == 2


# --- Multiple violations ---


class TestMultipleViolations:
    def test_reports_all_violations(self, monkeypatch):
        code, stderr, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'bad'"}},
            git_files=".env\nscreenshot.png\ncredentials.json",
            git_diff_content="+api" + "_key" + ' = "sk_live_' + "a" * 24 + '"',
        )
        assert code == 2
        assert "SECRET" in stderr
        assert "IMAGE" in stderr
        assert "API key" in stderr


# --- Exception handling ---


class TestExceptionHandling:
    def test_exits_0_when_subprocess_fails(self, monkeypatch):
        code, _, _ = run_hook(
            monkeypatch,
            {"tool_input": {"command": "git commit -m 'test'"}},
            subprocess_error=True,
        )
        assert code == 0
