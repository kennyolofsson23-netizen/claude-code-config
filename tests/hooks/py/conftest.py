"""Shared fixtures for Python hook tests."""

import json
import sys
import os
import io
import pytest

# Add hooks directory to sys.path so we can import hooks as modules
HOOKS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "hooks")
)


@pytest.fixture
def mock_stdin(monkeypatch):
    """Return a helper that sets sys.stdin to a StringIO with the given dict as JSON."""

    def _mock(data):
        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(data)))

    return _mock


@pytest.fixture
def hook_dir():
    """Return the absolute path to the hooks directory."""
    return HOOKS_DIR
