"""Homebrew package manager implementation."""

from .base import PackageManager


class HomebrewManager(PackageManager):
    """Manager for Homebrew packages."""

    def is_available(self) -> bool:
        """Check if Homebrew is installed."""
        return self.run_command(["which", "brew"])

    def update(self) -> bool:
        """Update Homebrew package lists."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["brew", "update"]))

    def upgrade(self) -> bool:
        """Upgrade Homebrew packages."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("upgrade", ["brew", "upgrade"]))
