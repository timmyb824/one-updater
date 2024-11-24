"""snap package manager implementation."""

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
