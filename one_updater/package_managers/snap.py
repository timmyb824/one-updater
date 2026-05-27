"""snap package manager implementation."""

from typing import Optional

from .base import PackageManager


class SnapManager(PackageManager):
    """Manager for snap packages."""

    def is_available(self) -> bool:
        """Check if snap is available."""
        return self.run_command(["which", "snap"])

    def update(self) -> bool:
        """Update snap package lists."""
        if not self.is_available():
            return False
        # snap refresh handles both update and upgrade
        return self.run_command(
            self.commands.get("update", ["sudo", "snap", "refresh"])
        )

    def upgrade(self) -> bool:
        """Upgrade snap packages."""
        if not self.is_available():
            return False
        # snap refresh handles both update and upgrade
        return self.run_command(
            self.commands.get("upgrade", ["sudo", "snap", "refresh"])
        )

    def list_packages(self) -> Optional[list[str]]:
        """Return all installed snap package names (excluding snapd)."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["snap", "list", "--color=never"])
        if not ok or not stdout:
            return []
        lines = stdout.splitlines()
        packages = []
        for line in lines[1:]:  # skip header row
            parts = line.split()
            if parts and parts[0] != "snapd":
                packages.append(parts[0])
        return packages

    def install_package(self, name: str) -> bool:
        """Install a snap package by name."""
        if not self.is_available():
            return False
        return self.run_command(["sudo", "snap", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a snap package is installed."""
        ok, _, _ = self.run_command_with_output(["snap", "list", name])
        return ok
