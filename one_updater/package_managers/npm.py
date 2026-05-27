"""npm package manager implementation."""

import json
from typing import Optional

from .base import PackageManager


class NpmManager(PackageManager):
    """Manager for npm packages."""

    def is_available(self) -> bool:
        """Check if npm is available."""
        return self.run_command(["which", "npm"])

    def update(self) -> bool:
        """Update npm package lists."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["npm", "update", "-g"]))

    def upgrade(self) -> bool:
        """Upgrade npm packages."""
        if not self.is_available():
            return False
        # npm update -g handles both update and upgrade
        return self.run_command(self.commands.get("upgrade", ["npm", "update", "-g"]))

    def list_packages(self) -> Optional[list[str]]:
        """Return all globally installed npm package names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(
            ["npm", "list", "-g", "--depth=0", "--json"]
        )
        if not ok or not stdout:
            return []
        try:
            data = json.loads(stdout)
            deps = data.get("dependencies", {})
            return [name for name in deps if name != "npm"]
        except (json.JSONDecodeError, AttributeError):
            return []

    def install_package(self, name: str) -> bool:
        """Install a global npm package by name."""
        if not self.is_available():
            return False
        return self.run_command(["npm", "install", "-g", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a global npm package is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
