"""pipx package manager implementation."""

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
