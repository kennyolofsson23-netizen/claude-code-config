"""Tests for auto-format.py hook."""

import importlib.util
import io
import json
import os
import subprocess
import sys

import pytest

HOOK_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "hooks", "auto-format.py")
)


def run_hook(
    monkeypatch,
    stdin_data,
    file_exists=True,
    ext=".py",
    prettier_config_dirs=None,
    pkg_json_content=None,
    subprocess_error=False,
):
    """Run the hook and return (exit_code, subprocess_calls).

    prettier_config_dirs: set of directory paths that contain a prettier config file
    pkg_json_content: dict mapping directory paths to package.json content strings
    """
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(stdin_data)))

    calls = []

    def mock_subprocess_run(cmd, **kwargs):
        calls.append(cmd)
        if subprocess_error:
            raise OSError("formatter not found")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", mock_subprocess_run)

    file_path = stdin_data.get("tool_input", {}).get("file_path", "")

    # Mock os.path.isfile — only the target file_path
    original_isfile = os.path.isfile
    monkeypatch.setattr(
        "os.path.isfile",
        lambda p: (
            file_exists
            if os.path.normpath(p) == os.path.normpath(file_path)
            else original_isfile(p)
        ),
    )

    # Mock os.path.splitext to return the configured ext
    monkeypatch.setattr(
        "os.path.splitext", lambda p: (p.rsplit(".", 1)[0] if "." in p else p, ext)
    )

    # Mock os.path.exists for prettier config detection
    prettier_dirs = prettier_config_dirs or set()
    pkg_jsons = pkg_json_content or {}

    def mock_exists(p):
        p_norm = os.path.normpath(p)
        # Check if it's a prettier config or package.json
        dirname = os.path.dirname(p_norm)
        basename = os.path.basename(p_norm)
        if basename == "package.json" and dirname in pkg_jsons:
            return True
        if basename.startswith(".prettierrc") or basename.startswith("prettier.config"):
            return dirname in prettier_dirs
        return False

    monkeypatch.setattr("os.path.exists", mock_exists)

    # Mock open for package.json reads
    original_open = open

    def mock_open_fn(path, *args, **kwargs):
        p_norm = os.path.normpath(path)
        dirname = os.path.dirname(p_norm)
        if os.path.basename(p_norm) == "package.json" and dirname in pkg_jsons:
            return io.StringIO(pkg_jsons[dirname])
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", mock_open_fn)

    spec = importlib.util.spec_from_file_location("auto_format", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)

    with pytest.raises(SystemExit) as exc_info:
        spec.loader.exec_module(mod)

    return exc_info.value.code, calls


# --- Early exits ---


class TestEarlyExits:
    def test_exits_0_no_file_path(self, monkeypatch):
        code, calls = run_hook(monkeypatch, {"tool_input": {}})
        assert code == 0
        assert calls == []

    def test_exits_0_empty_file_path(self, monkeypatch):
        code, calls = run_hook(monkeypatch, {"tool_input": {"file_path": ""}})
        assert code == 0
        assert calls == []

    def test_exits_0_nonexistent_file(self, monkeypatch):
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "/tmp/nope.py"}},
            file_exists=False,
        )
        assert code == 0
        assert calls == []


# --- Python formatting ---


class TestPythonFormatting:
    def test_calls_black_for_py(self, monkeypatch):
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\app.py"}},
            file_exists=True,
            ext=".py",
        )
        assert code == 0
        assert len(calls) == 1
        assert "black" in calls[0]


# --- JS/TS formatting ---


class TestJsFormatting:
    def test_calls_prettier_for_ts_with_config(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\app.ts"}},
            file_exists=True,
            ext=".ts",
            prettier_config_dirs={dir_path},
        )
        assert code == 0
        assert len(calls) == 1
        assert "prettier" in calls[0][1]

    def test_calls_prettier_for_tsx(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\comp.tsx"}},
            file_exists=True,
            ext=".tsx",
            prettier_config_dirs={dir_path},
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)

    def test_calls_prettier_for_jsx(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\comp.jsx"}},
            file_exists=True,
            ext=".jsx",
            prettier_config_dirs={dir_path},
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)

    def test_calls_prettier_for_css(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\style.css"}},
            file_exists=True,
            ext=".css",
            prettier_config_dirs={dir_path},
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)

    def test_calls_prettier_for_json(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\data.json"}},
            file_exists=True,
            ext=".json",
            prettier_config_dirs={dir_path},
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)

    def test_no_prettier_without_config(self, monkeypatch):
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\app.ts"}},
            file_exists=True,
            ext=".ts",
            prettier_config_dirs=set(),
        )
        assert code == 0
        assert calls == []

    def test_finds_prettier_config_in_parent(self, monkeypatch):
        parent_dir = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\src\\app.ts"}},
            file_exists=True,
            ext=".ts",
            prettier_config_dirs={parent_dir},
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)

    def test_finds_prettier_via_package_json(self, monkeypatch):
        dir_path = os.path.normpath("C:\\code")
        code, calls = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\app.js"}},
            file_exists=True,
            ext=".js",
            pkg_json_content={
                dir_path: '{"name": "test", "prettier": {"semi": false}}'
            },
        )
        assert code == 0
        assert any("prettier" in c[1] for c in calls)


# --- Error handling ---


class TestErrorHandling:
    def test_exits_0_when_formatter_fails(self, monkeypatch):
        code, _ = run_hook(
            monkeypatch,
            {"tool_input": {"file_path": "C:\\code\\app.py"}},
            file_exists=True,
            ext=".py",
            subprocess_error=True,
        )
        assert code == 0
