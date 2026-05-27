"""vagrant package manager implementation."""

from typing import Optional

from .base import PackageManager


class VagrantPluginManager(PackageManager):
    """Manager for vagrant packages."""

    def is_available(self) -> bool:
        """Check if vagrant is available."""
        return self.run_command(["which", "vagrant"])

    def update(self) -> bool:
        if not self.is_available():
            return False
        return self.run_command(["vagrant", "plugin", "update"])

    def upgrade(self) -> bool:
        """Upgrade vagrant plugins."""
        if not self.is_available():
            return False
        return self.run_command(["vagrant", "plugin", "update"])

    def list_packages(self) -> Optional[list[str]]:
        """Return all installed vagrant plugin names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(["vagrant", "plugin", "list"])
        if not ok or not stdout:
            return []
        return [
            parts[0]
            for line in stdout.splitlines()
            if line
            and not line[0].isspace()
            and (parts := line.split())
            and not parts[0].startswith("-")
        ]

    def install_package(self, name: str) -> bool:
        """Install a vagrant plugin by name."""
        if not self.is_available():
            return False
        return self.run_command(["vagrant", "plugin", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a vagrant plugin is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
