"""bin package manager implementation."""

from .base import PackageManager


class BinManager(PackageManager):
    """Manager for binaries installed with bin (https://github.com/marcosnils/bin)."""

    def is_available(self) -> bool:
        """Check if bin is available."""
        return self.run_command(["which", "bin"])

    def update(self) -> bool:
        """Update all binaries managed by bin, including bin itself."""
        if not self.is_available():
            return False
        return self.run_command(self.commands.get("update", ["bin", "update"]))

    def upgrade(self) -> bool:
        """Upgrade all binaries managed by bin."""
        if not self.is_available():
            return False
        # bin update handles both update and upgrade
        return self.run_command(self.commands.get("upgrade", ["bin", "update"]))
