"""gem package manager implementation."""

import logging
from typing import Optional

from .base import PackageManager


class GemManager(PackageManager):
    """Manager for gem packages."""

    def is_available(self) -> bool:
        """Check if gem is available."""
        return self.run_command(["which", "gem"])

    def update(self) -> bool:
        """Update RubyGems system."""
        if not self._check_available("update"):
            return False
        # First update RubyGems itself
        success = self.run_command(
            self.commands.get("update", ["gem", "update", "--system"])
        )
        if not success:
            logging.error("Failed to update RubyGems system")
        return success

    def upgrade(self) -> bool:
        """Upgrade installed gems."""
        if not self._check_available("upgrade"):
            return False
        # Update all installed gems
        return self.run_command(self.commands.get("upgrade", ["gem", "update"]))

    def list_packages(self) -> Optional[list[str]]:
        """Return all locally installed gem names."""
        if not self.is_available():
            return None
        ok, stdout, _ = self.run_command_with_output(
            ["gem", "list", "--local", "--no-versions"]
        )
        if not ok or not stdout:
            return []
        return [line.strip() for line in stdout.splitlines() if line.strip()]

    def install_package(self, name: str) -> bool:
        """Install a gem by name."""
        if not self.is_available():
            return False
        return self.run_command(["gem", "install", name])

    def is_package_installed(self, name: str) -> bool:
        """Check whether a gem is installed."""
        packages = self.list_packages()
        return packages is not None and name in packages
