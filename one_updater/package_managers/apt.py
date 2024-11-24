"""apt package manager implementation."""

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
