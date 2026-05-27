"""Tests for export/import CLI functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest
import yaml

from one_updater.cli import export_packages, import_packages
from one_updater.package_managers.brew import HomebrewManager
from one_updater.package_managers.cargo import CargoManager
from one_updater.package_managers.pipx import PipxManager
from one_updater.package_managers.registry import PackageManagerRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pm(available: bool, packages: list[str] | None) -> MagicMock:
    """Return a mock PackageManager with configured behaviour."""
    pm = MagicMock()
    pm.is_available.return_value = available
    pm.list_packages.return_value = packages
    pm.is_package_installed.side_effect = lambda name: name in (packages or [])
    pm.install_package.return_value = True
    return pm


# ---------------------------------------------------------------------------
# list_packages / install_package / is_package_installed — unit tests
# ---------------------------------------------------------------------------


class TestHomebrewMethods:
    """Unit tests for HomebrewManager export/import methods."""

    def test_list_packages_unavailable(self) -> None:
        """list_packages returns None when brew is not available."""
        mgr = HomebrewManager({})
        with patch.object(mgr, "is_available", return_value=False):
            assert mgr.list_packages() is None

    def test_list_packages_combines_formulae_and_casks(self) -> None:
        """list_packages concatenates formulae and cask results."""
        mgr = HomebrewManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(
                mgr,
                "run_command_with_output",
                side_effect=[
                    (True, "git\nvim\n", ""),
                    (True, "iterm2\n", ""),
                ],
            ),
        ):
            result = mgr.list_packages()
        assert result == ["git", "vim", "iterm2"]

    def test_install_package_calls_brew_install(self) -> None:
        """install_package delegates to brew install <name>."""
        mgr = HomebrewManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command", return_value=True) as mock_run,
        ):
            assert mgr.install_package("ripgrep") is True
            mock_run.assert_called_once_with(["brew", "install", "ripgrep"])

    def test_is_package_installed_true(self) -> None:
        """is_package_installed returns True when brew list succeeds."""
        mgr = HomebrewManager({})
        with patch.object(
            mgr, "run_command_with_output", return_value=(True, "git\n", "")
        ):
            assert mgr.is_package_installed("git") is True

    def test_is_package_installed_false(self) -> None:
        """is_package_installed returns False when brew list fails."""
        mgr = HomebrewManager({})
        with patch.object(mgr, "run_command_with_output", return_value=(False, "", "")):
            assert mgr.is_package_installed("no-such-pkg") is False


class TestPipxMethods:
    """Unit tests for PipxManager export/import methods."""

    def test_list_packages_parses_short_output(self) -> None:
        """list_packages extracts the first token from each line."""
        mgr = PipxManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(
                mgr,
                "run_command_with_output",
                return_value=(True, "black 23.3.0\ncowsay 6.0\n", ""),
            ),
        ):
            result = mgr.list_packages()
        assert result == ["black", "cowsay"]

    def test_is_package_installed_delegates_to_list(self) -> None:
        """is_package_installed checks membership in list_packages result."""
        mgr = PipxManager({})
        with patch.object(mgr, "list_packages", return_value=["black", "cowsay"]):
            assert mgr.is_package_installed("black") is True
            assert mgr.is_package_installed("ruff") is False

    def test_is_package_installed_none_returns_false(self) -> None:
        """is_package_installed returns False when list_packages is None."""
        mgr = PipxManager({})
        with patch.object(mgr, "list_packages", return_value=None):
            assert mgr.is_package_installed("black") is False


class TestCargoMethods:
    """Unit tests for CargoManager export/import methods."""

    def test_list_packages_parses_install_list(self) -> None:
        """list_packages extracts crate names from cargo install --list."""
        mgr = CargoManager({})
        output = "bat v0.23.0:\n" "    bat\n" "ripgrep v13.0.0:\n" "    rg\n"
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(
                mgr,
                "run_command_with_output",
                return_value=(True, output, ""),
            ),
        ):
            result = mgr.list_packages()
        assert result == ["bat", "ripgrep"]

    def test_install_package_calls_cargo_install(self) -> None:
        """install_package delegates to cargo install <name>."""
        mgr = CargoManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command", return_value=True) as mock_run,
        ):
            assert mgr.install_package("bat") is True
            mock_run.assert_called_once_with(["cargo", "install", "bat"])


# ---------------------------------------------------------------------------
# export_packages CLI function
# ---------------------------------------------------------------------------


class TestExportPackages:
    """Integration-style tests for the export_packages CLI function."""

    def test_export_to_stdout_yaml(self, capsys) -> None:
        """export_packages prints YAML to stdout when no output file given."""
        mock_pm = _make_pm(available=True, packages=["git", "vim"])

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)

        captured = capsys.readouterr()
        assert "git" in captured.out
        assert "vim" in captured.out

    def test_export_to_file_json(self, tmp_path) -> None:
        """export_packages writes valid JSON when fmt='json' and output given."""
        mock_pm = _make_pm(available=True, packages=["ripgrep"])
        out_file = str(tmp_path / "packages.json")

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            export_packages(
                managers=["cargo"],
                output=out_file,
                fmt="json",
                verbose=False,
            )

        with open(out_file, encoding="utf-8") as f:
            data = json.load(f)
        assert data == {"cargo": ["ripgrep"]}

    def test_export_skips_unavailable_manager(self, capsys) -> None:
        """export_packages skips unavailable managers silently (verbose=False)."""
        mock_pm = _make_pm(available=False, packages=None)

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)

        captured = capsys.readouterr()
        assert "No packages found" in captured.out

    def test_export_skips_unsupported_manager_with_warning(self, capsys) -> None:
        """export_packages warns and skips managers not in EXPORT_SUPPORTED."""
        export_packages(managers=["tldr"], output=None, fmt="yaml", verbose=False)
        captured = capsys.readouterr()
        assert "not export-supported" in captured.out

    def test_export_to_file_yaml(self, tmp_path) -> None:
        """export_packages writes valid YAML when fmt='yaml' and output given."""
        mock_pm = _make_pm(available=True, packages=["black", "ruff"])
        out_file = str(tmp_path / "packages.yaml")

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            export_packages(
                managers=["pipx"],
                output=out_file,
                fmt="yaml",
                verbose=False,
            )

        with open(out_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data == {"pipx": ["black", "ruff"]}


# ---------------------------------------------------------------------------
# import_packages CLI function
# ---------------------------------------------------------------------------


class TestImportPackages:
    """Integration-style tests for the import_packages CLI function."""

    def _write_export(self, tmp_path, data: dict, fmt: str = "yaml") -> str:
        """Write a mock export file and return its path."""
        if fmt == "json":
            path = tmp_path / "packages.json"
            path.write_text(json.dumps(data))
        else:
            path = tmp_path / "packages.yaml"
            path.write_text(yaml.dump(data))
        return str(path)

    def test_import_skips_already_installed(self, tmp_path) -> None:
        """import_packages skips packages that are already installed."""
        data = {"brew": ["git", "vim"]}
        file_path = self._write_export(tmp_path, data)

        mock_pm = _make_pm(available=True, packages=["git", "vim"])

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=False,
                verbose=False,
            )

        mock_pm.install_package.assert_not_called()

    def test_import_installs_missing_packages(self, tmp_path) -> None:
        """import_packages calls install_package for packages not installed."""
        data = {"brew": ["git", "ripgrep"]}
        file_path = self._write_export(tmp_path, data)

        mock_pm = _make_pm(available=True, packages=["git"])

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=False,
                verbose=False,
            )

        mock_pm.install_package.assert_called_once_with("ripgrep")

    def test_import_dry_run_does_not_install(self, tmp_path) -> None:
        """import_packages does not call install_package in dry-run mode."""
        data = {"cargo": ["bat", "fd"]}
        file_path = self._write_export(tmp_path, data)

        mock_pm = _make_pm(available=True, packages=[])

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=True,
                verbose=False,
            )

        mock_pm.install_package.assert_not_called()

    def test_import_reads_json_file(self, tmp_path) -> None:
        """import_packages auto-detects JSON format from .json extension."""
        data = {"pipx": ["black"]}
        file_path = self._write_export(tmp_path, data, fmt="json")

        mock_pm = _make_pm(available=True, packages=[])

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=False,
                verbose=False,
            )

        mock_pm.install_package.assert_called_once_with("black")

    def test_import_file_not_found_exits(self, tmp_path) -> None:
        """import_packages calls sys.exit when the file does not exist."""
        with pytest.raises(SystemExit):
            import_packages(
                file_path=str(tmp_path / "nonexistent.yaml"),
                managers=None,
                dry_run=False,
                verbose=False,
            )

    def test_import_manager_filter(self, tmp_path) -> None:
        """import_packages only processes managers listed in managers arg."""
        data = {"brew": ["git"], "cargo": ["bat"]}
        file_path = self._write_export(tmp_path, data)

        brew_pm = _make_pm(available=True, packages=[])
        cargo_pm = _make_pm(available=True, packages=[])

        def _get_manager(name: str, _cfg: dict):
            """Return the appropriate mock PM by name."""
            return brew_pm if name == "brew" else cargo_pm

        with patch.object(
            PackageManagerRegistry, "get_manager", side_effect=_get_manager
        ):
            import_packages(
                file_path=file_path,
                managers=["brew"],
                dry_run=False,
                verbose=False,
            )

        brew_pm.install_package.assert_called_once_with("git")
        cargo_pm.install_package.assert_not_called()

    def test_import_skips_unavailable_manager(self, tmp_path) -> None:
        """import_packages skips managers that are not available."""
        data = {"brew": ["git"]}
        file_path = self._write_export(tmp_path, data)

        mock_pm = _make_pm(available=False, packages=None)

        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=False,
                verbose=False,
            )

        mock_pm.install_package.assert_not_called()
