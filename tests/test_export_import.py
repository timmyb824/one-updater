"""Tests for export/import CLI functionality."""

import json
from unittest.mock import MagicMock, patch

import pytest
import yaml

from one_updater.cli import (
    PackageImportError,
    export_packages,
    import_packages,
    scan_unmanaged_binaries,
)
from one_updater.package_managers.brew import HomebrewManager
from one_updater.package_managers.cargo import CargoManager
from one_updater.package_managers.pipx import PipxManager
from one_updater.package_managers.registry import PackageManagerRegistry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pm(
    available: bool,
    packages: list[str] | None,
    failed_packages: set[str] | None = None,
) -> MagicMock:
    """Return a mock PackageManager with configured behaviour."""
    pm = MagicMock()
    pm.is_available.return_value = available
    pm.list_packages.return_value = packages
    pm.is_package_installed.side_effect = lambda name: name in (packages or [])
    if failed_packages:
        pm.install_package.side_effect = lambda name: name not in failed_packages
    else:
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


class TestHomebrewNegativePaths:
    """Negative-path tests for HomebrewManager."""

    def test_install_package_unavailable_returns_false(self) -> None:
        """install_package returns False and skips run_command when unavailable."""
        mgr = HomebrewManager({})
        with (
            patch.object(mgr, "is_available", return_value=False),
            patch.object(mgr, "run_command") as mock_run,
        ):
            result = mgr.install_package("ripgrep")
        assert result is False
        mock_run.assert_not_called()


class TestPipxNegativePaths:
    """Negative-path tests for PipxManager."""

    def test_list_packages_command_failure_returns_empty(self) -> None:
        """list_packages returns [] when run_command_with_output fails."""
        mgr = PipxManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command_with_output", return_value=(False, "", "")),
        ):
            assert mgr.list_packages() == []

    def test_list_packages_empty_stdout_returns_empty(self) -> None:
        """list_packages returns [] when stdout is empty."""
        mgr = PipxManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command_with_output", return_value=(True, "", "")),
        ):
            assert mgr.list_packages() == []


class TestCargoNegativePaths:
    """Negative-path tests for CargoManager."""

    def test_list_packages_command_failure_returns_empty(self) -> None:
        """list_packages returns [] when run_command_with_output fails."""
        mgr = CargoManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command_with_output", return_value=(False, "", "")),
        ):
            assert mgr.list_packages() == []

    def test_list_packages_empty_stdout_returns_empty(self) -> None:
        """list_packages returns [] when stdout is empty."""
        mgr = CargoManager({})
        with (
            patch.object(mgr, "is_available", return_value=True),
            patch.object(mgr, "run_command_with_output", return_value=(True, "", "")),
        ):
            assert mgr.list_packages() == []


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
# scan_unmanaged_binaries
# ---------------------------------------------------------------------------


class TestScanUnmanagedBinaries:
    """Unit tests for the scan_unmanaged_binaries helper."""

    def test_nonexistent_dir_returns_empty(self) -> None:
        """Returns an empty list when the scan directory does not exist."""
        result = scan_unmanaged_binaries(
            set(), scan_dirs=["/nonexistent/__test_path__"]
        )
        assert result == []

    def test_executable_file_included(self, tmp_path) -> None:
        """An executable file not in managed_names appears in the result."""
        (tmp_path / "mytool").write_text("#!/bin/sh")
        (tmp_path / "mytool").chmod(0o755)
        result = scan_unmanaged_binaries(set(), scan_dirs=[str(tmp_path)])
        assert "mytool" in result

    def test_non_executable_file_excluded(self, tmp_path) -> None:
        """A non-executable regular file is not included."""
        (tmp_path / "readme.txt").write_text("docs")
        (tmp_path / "readme.txt").chmod(0o644)
        result = scan_unmanaged_binaries(set(), scan_dirs=[str(tmp_path)])
        assert "readme.txt" not in result

    def test_directory_entries_excluded(self, tmp_path) -> None:
        """Subdirectories are not included even if they are executable."""
        subdir = tmp_path / "subdir"
        subdir.mkdir(mode=0o755)
        result = scan_unmanaged_binaries(set(), scan_dirs=[str(tmp_path)])
        assert "subdir" not in result

    def test_managed_name_filtered_out(self, tmp_path) -> None:
        """Binaries whose names are in managed_names are excluded."""
        for name in ("gah", "neomd", "git"):
            exe = tmp_path / name
            exe.write_text("#!/bin/sh")
            exe.chmod(0o755)
        result = scan_unmanaged_binaries({"git"}, scan_dirs=[str(tmp_path)])
        assert "git" not in result
        assert "gah" in result
        assert "neomd" in result

    def test_results_are_sorted(self, tmp_path) -> None:
        """Results are returned in sorted alphabetical order."""
        for name in ("zzz", "aaa", "mmm"):
            exe = tmp_path / name
            exe.write_text("#!/bin/sh")
            exe.chmod(0o755)
        result = scan_unmanaged_binaries(set(), scan_dirs=[str(tmp_path)])
        assert result == sorted(result)

    def test_multiple_dirs_combined(self, tmp_path) -> None:
        """Binaries from multiple scan directories are merged and deduplicated."""
        dir_a = tmp_path / "a"
        dir_b = tmp_path / "b"
        dir_a.mkdir()
        dir_b.mkdir()
        for name, d in (("tool1", dir_a), ("tool2", dir_b), ("tool1", dir_b)):
            exe = d / name
            exe.write_text("#!/bin/sh")
            exe.chmod(0o755)
        result = scan_unmanaged_binaries(set(), scan_dirs=[str(dir_a), str(dir_b)])
        assert result == ["tool1", "tool2"]


# ---------------------------------------------------------------------------
# export_packages — unmanaged binary section
# ---------------------------------------------------------------------------


class TestExportPackagesUnmanagedBinaries:
    """Integration tests for the Other Tools Not Importable console section."""

    def test_unmanaged_tools_printed_to_console(self, capsys) -> None:
        """export_packages prints the section when unmanaged binaries are found."""
        mock_pm = _make_pm(available=True, packages=["git"])
        with (
            patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm),
            patch(
                "one_updater.cli.scan_unmanaged_binaries", return_value=["gah", "neomd"]
            ),
        ):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)
        captured = capsys.readouterr()
        assert "Other Tools Not Importable" in captured.out
        assert "gah" in captured.out
        assert "neomd" in captured.out

    def test_no_section_when_no_unmanaged_tools(self, capsys) -> None:
        """export_packages omits the section entirely when scan returns empty."""
        mock_pm = _make_pm(available=True, packages=["git"])
        with (
            patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm),
            patch("one_updater.cli.scan_unmanaged_binaries", return_value=[]),
        ):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)
        captured = capsys.readouterr()
        assert "Other Tools Not Importable" not in captured.out

    def test_managed_names_passed_to_scan(self, capsys) -> None:
        """Package names from all available PMs are forwarded to
        scan_unmanaged_binaries."""
        mock_pm = _make_pm(available=True, packages=["git", "vim"])
        captured_args: dict = {}

        def _capture_scan(managed_names: set, scan_dirs=None) -> list:
            """Record the managed_names argument and return an empty list."""
            captured_args["managed_names"] = set(managed_names)
            return []

        with (
            patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm),
            patch("one_updater.cli.scan_unmanaged_binaries", side_effect=_capture_scan),
        ):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)
        assert "git" in captured_args["managed_names"]
        assert "vim" in captured_args["managed_names"]

    def test_unmanaged_section_shown_even_when_no_packages_exported(
        self, capsys
    ) -> None:
        """The binary scan runs even when result is empty (no packages exported)."""
        mock_pm = _make_pm(available=False, packages=None)
        with (
            patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm),
            patch(
                "one_updater.cli.scan_unmanaged_binaries", return_value=["manualtool"]
            ),
        ):
            export_packages(managers=["brew"], output=None, fmt="yaml", verbose=False)
        captured = capsys.readouterr()
        assert "No packages found to export" in captured.out
        assert "Other Tools Not Importable" in captured.out
        assert "manualtool" in captured.out


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

    def test_import_file_not_found_raises(self, tmp_path) -> None:
        """import_packages raises PackageImportError when the file does not exist."""
        with pytest.raises(PackageImportError):
            import_packages(
                file_path=str(tmp_path / "nonexistent.yaml"),
                managers=None,
                dry_run=False,
                verbose=False,
            )

    def test_import_invalid_json_raises(self, tmp_path) -> None:
        """import_packages raises PackageImportError on malformed JSON."""
        path = tmp_path / "packages.json"
        path.write_text("{not valid json")
        with pytest.raises(PackageImportError):
            import_packages(
                file_path=str(path), managers=None, dry_run=False, verbose=False
            )

    def test_import_non_dict_top_level_raises(self, tmp_path) -> None:
        """import_packages raises PackageImportError when top-level is not a dict."""
        path = tmp_path / "packages.yaml"
        path.write_text("- pkg1\n- pkg2\n")
        with pytest.raises(PackageImportError):
            import_packages(
                file_path=str(path), managers=None, dry_run=False, verbose=False
            )

    def test_import_non_list_manager_value_warns(self, tmp_path, capsys) -> None:
        """import_packages warns and skips managers whose value is not a list."""
        data = {"brew": "git"}
        file_path = self._write_export(tmp_path, data, fmt="json")
        mock_pm = _make_pm(available=True, packages=[])
        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path, managers=None, dry_run=False, verbose=False
            )
        captured = capsys.readouterr()
        assert "expected list" in captured.out
        mock_pm.install_package.assert_not_called()

    def test_import_unsupported_managers_warn(self, tmp_path, capsys) -> None:
        """import_packages warns about managers not in EXPORT_SUPPORTED."""
        data = {"brew": ["git"], "tldr": ["foo"]}
        file_path = self._write_export(tmp_path, data, fmt="json")
        mock_pm = _make_pm(available=True, packages=[])
        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path, managers=None, dry_run=False, verbose=False
            )
        captured = capsys.readouterr()
        assert "tldr" in captured.out
        assert "EXPORT_SUPPORTED" in captured.out

    def test_import_install_failure_counted(self, tmp_path, capsys) -> None:
        """import_packages counts and displays failed installs."""
        data = {"cargo": ["bat", "fd"]}
        file_path = self._write_export(tmp_path, data)
        mock_pm = _make_pm(available=True, packages=[], failed_packages={"fd"})
        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path, managers=None, dry_run=False, verbose=False
            )
        captured = capsys.readouterr()
        assert "failed" in captured.out
        assert "installed" in captured.out

    def test_import_verbose_dry_run_shows_table_entries(self, tmp_path, capsys) -> None:
        """verbose+dry_run prints skipped and would-install rows in the table."""
        data = {"brew": ["git", "ripgrep"]}
        file_path = self._write_export(tmp_path, data)
        mock_pm = _make_pm(available=True, packages=["git"])
        with patch.object(PackageManagerRegistry, "get_manager", return_value=mock_pm):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=True,
                verbose=True,
            )
        captured = capsys.readouterr()
        assert "skipped (already installed)" in captured.out
        assert "would install" in captured.out

    def test_import_skip_excludes_managers(self, tmp_path) -> None:
        """import_packages honours the skip list."""
        data = {"brew": ["git"], "pipx": ["black"]}
        file_path = self._write_export(tmp_path, data)
        brew_pm = _make_pm(available=True, packages=[])
        pipx_pm = _make_pm(available=True, packages=[])

        def _get(name: str, _cfg: dict) -> MagicMock:
            """Return PM mock by name."""
            return brew_pm if name == "brew" else pipx_pm

        with patch.object(PackageManagerRegistry, "get_manager", side_effect=_get):
            import_packages(
                file_path=file_path,
                managers=None,
                dry_run=False,
                verbose=False,
                skip=["pipx"],
            )
        brew_pm.install_package.assert_called_once_with("git")
        pipx_pm.install_package.assert_not_called()

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
