"""bin package manager implementation."""

import operator
import os

from .base import PackageManager


class BinManager(PackageManager):
    """Manager for binaries installed with bin (https://github.com/marcosnils/bin)."""

    def is_available(self) -> bool:
        """Check if bin is available."""
        return self.run_command(["which", "bin"])

    def update(self) -> bool:
        """Update all binaries managed by bin, including bin itself."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["bin", "update"]))

    def upgrade(self) -> bool:
        """Upgrade all binaries managed by bin."""
        if not self.is_available():
            return False
        # bin update handles both update and upgrade
        return self.run_command(self.commands.get("upgrade", ["bin", "update"]))

    @staticmethod
    def _parse_bin_ls(stdout: str) -> list[dict[str, str]]:
        """Parse fixed-width ``bin ls`` table output into row dicts.

        Uses the header line to determine column start positions so that
        paths containing spaces are handled correctly.
        """
        lines = stdout.strip().splitlines()
        if not lines:
            return []
        header = lines[0]
        # Find start position of each known column header
        columns: list[tuple[str, int]] = []
        for name in ("Path", "Version", "URL", "Status"):
            pos = header.find(name)
            if pos == -1:
                return []
            columns.append((name, pos))
        columns.sort(key=operator.itemgetter(1))
        rows: list[dict[str, str]] = []
        for line in lines[1:]:
            if not line.strip():
                continue
            row: dict[str, str] = {}
            for i, (name, pos) in enumerate(columns):
                end = columns[i + 1][1] if i + 1 < len(columns) else len(line)
                row[name] = line[pos:end].strip()
            rows.append(row)
        return rows

    def list_packages(self) -> list[str] | None:
        """Return all binary install URLs managed by bin.

        The URL column from ``bin ls`` is used because ``bin install <URL>``
        is the command needed to re-install a binary on another machine.
        """
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["bin", "ls"])
        if not ok or not stdout:
            return []
        return [row["URL"] for row in self._parse_bin_ls(stdout) if row.get("URL")]

    def install_package(self, name: str) -> bool:
        """Install a binary with bin by URL.

        Args:
            name: The install URL (e.g. ``github.com/marcosnils/bin``).
        """
        if not self.is_available():
            return False
        return self.run_command(["bin", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a binary managed by bin is installed.

        Args:
            name: The install URL to check for.
        """
        packages = self.list_packages()
        return packages is not None and name in packages

    def list_managed_binaries(self) -> list[str]:
        """Return executable names that bin installs to bin directories.

        Parses the Path column from ``bin ls`` and returns the basename of
        each path so ``scan_unmanaged_binaries`` can filter them out.
        """
        if not self.is_available():
            return []
        ok, stdout, _ = self.run_command_with_output(["bin", "ls"])
        if not ok or not stdout:
            return []
        return [
            os.path.basename(row["Path"])
            for row in self._parse_bin_ls(stdout)
            if row.get("Path")
        ]
