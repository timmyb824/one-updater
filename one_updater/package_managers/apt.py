"""apt package manager implementation."""

from typing import Optional

from .base import PackageManager


class AptManager(PackageManager):
    """Manager for apt packages."""

    def is_available(self) -> bool:
        """Check if apt is available."""
        return self.run_command(["which", "apt"])

    def update(self) -> bool:
        """Update apt package lists."""
        if not self._check_available("update"):
            return False
        return self.run_command(self.commands.get("update", ["sudo", "apt", "update"]))

    def upgrade(self) -> bool:
        """Upgrade apt packages."""
        if not self._check_available("upgrade"):
            return False
        return self.run_command(
            self.commands.get("upgrade", ["sudo", "apt", "upgrade", "-y"])
        )

    def list_packages(self) -> Optional[list[str]]:
        """Return all explicitly installed apt packages."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["apt-mark", "showmanual"])
        if not ok or not stdout:
            return []
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def install_package(self, name: str) -> bool:
        """Install an apt package by name."""
        if not self.is_available():
            return False
        return self.run_command(["sudo", "apt-get", "install", "-y", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether an apt package is installed."""
        ok, _, _ = self.run_command_with_output(["dpkg", "-s", name])
        return ok
