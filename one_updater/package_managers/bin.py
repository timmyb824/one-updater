"""bin package manager implementation."""

import os

from .base import PackageManager

# Minimum number of columns expected in ``bin ls`` output (Path, Version, URL)
_MIN_LS_COLUMNS = 3


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
        packages: list[str] = []
        for line in stdout.strip().splitlines():
            parts = line.split()
            # Skip header line and lines with fewer than 3 columns
            if len(parts) < _MIN_LS_COLUMNS or parts[0] == "Path":
                continue
            # URL is the third column (index 2)
            packages.append(parts[2])
        return packages

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
        binaries: list[str] = []
        for line in stdout.strip().splitlines():
            parts = line.split()
            if len(parts) < _MIN_LS_COLUMNS or parts[0] == "Path":
                continue
            # Path is the first column; extract the executable name
            binaries.append(os.path.basename(parts[0]))
        return binaries
