"""gem package manager implementation."""

import logging

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
