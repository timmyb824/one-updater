"""Basic smoke tests for the one-updater CLI."""

import pytest

from one_updater.cli import cli


def test_cli_help(cli_runner):
    """Test that CLI help command works."""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output


def test_cli_version(cli_runner):
    """Test that version command works."""
    result = cli_runner.invoke(cli, ["version"])
    assert result.exit_code == 0


def test_cli_list_managers(cli_runner, test_config_path):
    """Test listing available package managers."""
    result = cli_runner.invoke(cli, ["-c", test_config_path, "list-managers"], obj={})
    assert result.exit_code == 0
    assert "pip" in result.output.lower()
    assert "brew" in result.output.lower()


def test_cli_update_specific(cli_runner, test_config_path):
    """Test update command with specific package manager."""
    # Just test command parsing, don't actually run update
    result = cli_runner.invoke(
        cli, ["-c", test_config_path, "update", "-m", "pip"], obj={}
    )
    # Update might fail since pip isn't actually available, but command should parse
    assert result.exit_code in [0, 1]


def test_cli_upgrade_specific(cli_runner, test_config_path):
    """Test upgrade command with specific package manager."""
    # Just test command parsing, don't actually run upgrade
    result = cli_runner.invoke(
        cli, ["-c", test_config_path, "upgrade", "-m", "pip"], obj={}
    )
    # Upgrade might fail since pip isn't actually available, but command should parse
    assert result.exit_code in [0, 1]


def test_cli_invalid_config(cli_runner):
    """Test CLI behavior with invalid config path."""
    result = cli_runner.invoke(cli, ["-c", "nonexistent.yaml", "list"], obj={})
    assert result.exit_code != 0
    assert "Error" in str(result.output) or "error" in str(result.output)


def test_cli_invalid_manager(cli_runner, test_config_path):
    """Test CLI behavior with invalid package manager."""
    result = cli_runner.invoke(
        cli, ["-c", test_config_path, "update", "-m", "nonexistent"], obj={}
    )
    assert result.exit_code != 0
    assert "Invalid package manager" in str(result.output) or "not found" in str(
        result.output
    )
