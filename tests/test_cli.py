"""Basic tests for the one-updater CLI."""

import io
import sys
from unittest.mock import patch

import pytest

from one_updater.cli import main


def test_cli_list_managers(monkeypatch, test_config_path):
    """Test that list-managers command works with a config file."""
    stdout = io.StringIO()
    stderr = io.StringIO()

    with patch("sys.stdout", new=stdout), patch("sys.stderr", new=stderr):
        monkeypatch.setattr(
            sys, "argv", ["one-updater", "list-managers", "-c", test_config_path]
        )

        try:
            main()
        except SystemExit as e:
            assert e.code == 0

        output = stdout.getvalue() + stderr.getvalue()

        # Check that both package managers are listed
        assert "brew" in output.lower()
        assert "pip" in output.lower()
        assert "enabled" in output.lower()
