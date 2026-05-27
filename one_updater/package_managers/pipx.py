"""pipx package manager implementation."""

from typing import Optional

from .base import PackageManager


class PipxManager(PackageManager):
    """Manager for pipx packages."""

    def is_available(self) -> bool:
        """Check if pipx is available."""
        return self.run_command(["which", "pipx"])

    def update(self) -> bool:
        """Update pipx package lists."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["pipx", "upgrade-all"]))

    def upgrade(self) -> bool:
        """Upgrade pipx packages."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("upgrade", ["pipx", "upgrade-all"]))

    def list_packages(self) -> Optional[list[str]]:
        """Return all pipx-installed package names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["pipx", "list", "--short"])
        if not ok or not stdout:
            return []
        return [parts[0] for line in stdout.splitlines() if (parts := line.split())]

    def install_package(self, name: str) -> bool:
        """Install a pipx package by name."""
        if not self.is_available():
            return False
        return self.run_command(["pipx", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a pipx package is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
