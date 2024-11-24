"""npm package manager implementation."""
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
